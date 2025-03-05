from datetime import datetime
import time
import json
from typing import Any, Dict, Optional, cast
from typing_extensions import override

from masterpiece.mqtt import Mqtt, MqttMsg
from juham_core import JuhamCloudThread, JuhamThread


class SpotHintaFiThread(JuhamCloudThread):
    """Thread running SpotHinta.fi.

    Periodically fetches the spot electricity prices and publishes them
    to  'spot' topic.
    """

    _spot_topic: str = ""
    _url: str = ""
    _interval: float = 12 * 3600
    grid_cost_day: float = 0.0314
    grid_cost_night: float = 0.0132
    grid_cost_tax: float = 0.028272

    def __init__(self, client: Optional[Mqtt] = None) -> None:
        super().__init__(client)
        self._interval = 60

    def init(self, topic: str, url: str, interval: float) -> None:
        self._spot_topic = topic
        self._url = url
        self._interval = interval

    @override
    def make_weburl(self) -> str:
        return self._url

    @override
    def update_interval(self) -> float:
        return self._interval

    @override
    def process_data(self, rawdata: Any) -> None:
        """Publish electricity price message to Juham topic.

        Args:
            rawdata (dict): electricity prices
        """

        super().process_data(rawdata)
        data = rawdata.json()

        spot = []
        for e in data:
            ts = time.mktime(time.strptime(e["DateTime"], "%Y-%m-%dT%H:%M:%S%z"))
            hour = datetime.utcfromtimestamp(ts).strftime("%H")
            total_price: float
            grid_cost: float
            if int(hour) < 22 and int(hour) >= 6:
                grid_cost = self.grid_cost_day
            else:
                grid_cost = self.grid_cost_night
            total_price = e["PriceWithTax"] + grid_cost + self.grid_cost_tax
            h = {
                "Timestamp": ts,
                "hour": hour,
                "Rank": e["Rank"],
                "PriceWithTax": total_price,
                "GridCost": grid_cost + self.grid_cost_tax,
            }
            spot.append(h)
        self.publish(self._spot_topic, json.dumps(spot), 1, True)
        self.info(f"Spot electricity prices published for the next {len(spot)} days")


class SpotHintaFi(JuhamThread):
    """Spot electricity price for reading hourly electricity prices from
    https://api.spot-hinta.fi site.
    """

    worker_thread_id = SpotHintaFiThread.get_class_id()
    url = "https://api.spot-hinta.fi/TodayAndDayForward"
    update_interval = 12 * 3600

    def __init__(self, name: str = "rspothintafi") -> None:
        super().__init__(name)
        self.active_liter_lpm = -1
        self.update_ts = None
        self.spot_topic = self.make_topic_name("spot")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.spot_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.spot_topic:
            em = json.loads(msg.payload.decode())
            self.on_spot(em)
        else:
            super().on_message(client, userdata, msg)

    def on_spot(self, m: dict[Any, Any]) -> None:
        """Write hourly spot electricity prices to time series database.

        Args:
            m (dict): holding hourly spot electricity prices
        """
        pass

    @override
    def run(self) -> None:
        self.worker = cast(SpotHintaFiThread, self.instantiate(self.worker_thread_id))
        self.worker.init(self.spot_topic, self.url, self.update_interval)
        super().run()

    @override
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data["_spothintafi"] = {
            "topic": self.spot_topic,
            "url": self.url,
            "interval": self.update_interval,
        }
        return data

    @override
    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if "_spothintafi" in data:
            for key, value in data["_spothintafi"].items():
                setattr(self, key, value)
