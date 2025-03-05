import json
from typing import Any, Dict, Optional, cast
from typing_extensions import override
from masterpiece.mqtt import Mqtt, MqttMsg
from juham_core import Juham, timestamp, JuhamThread, JuhamCloudThread


class HomeWizardWaterMeterThread(JuhamCloudThread):
    """Thread that reads HomeWizard's water meter sensor."""

    def __init__(self, client: Optional[Mqtt] = None) -> None:
        """Construct HomeWizard water meter acquisition thread.

        Args:
            topic (str, optional): MQTT topic to post the sensor readings. Defaults to None.
            interval (float, optional): Interval specifying how often the sensor is read. Defaults to 60 seconds.
            url (str, optional): url for reading watermeter. Defaults to None.
        """
        super().__init__(client)

    def init(self, topic: str = "", url: str = "", interval: float = 60) -> None:
        """Initialize thread for reading HomeWizard sensor and publishing
        the readings to Mqtt network.

        Args:
            topic (str, optional): Mqtt topic to publish the readings
            url (str, optional): HomeWizard url for reading sensor data.
            interval (float, optional): Update interval. Defaults to 60.
        """
        self._sensor_topic = topic
        self._interval = interval
        self._device_url = url

    @override
    def make_weburl(self) -> str:
        return self._device_url

    @override
    def update_interval(self) -> float:
        return self._interval

    @override
    def process_data(self, data: Any) -> None:
        super().process_data(data)
        data = data.json()
        active_lpm = float(data["active_liter_lpm"])
        total_liter = float(data["total_liter"])
        ts = timestamp()
        msg: dict[str, float] = {
            "active_liter_lpm": active_lpm,
            "total_liter": total_liter,
            "ts": ts,
        }
        self.publish(self._sensor_topic, json.dumps(msg), qos=0, retain=False)


class HomeWizardWaterMeter(JuhamThread):
    """Homewizard watermeter sensor."""

    _HOMEWIZARD: str = "_homewizardwatermeter"
    workerThreadId = HomeWizardWaterMeterThread.get_class_id()
    url = "http://192.168.86.70/api/v1/data"
    update_interval = 30

    def __init__(
        self,
        name: str = "homewizardwatermeter",
        topic: str = "",
        url: str = "",
        interval: float = 60.0,
    ) -> None:
        """Create Homewizard water meter sensor.

        Args:
            name (str, optional): name identifying the sensor. Defaults to 'homewizardwatermeter'.
            topic (str, optional): Juham topic to publish water consumption readings. Defaults to None.
            url (str, optional): Homewizard url from which to acquire water consumption readings. Defaults to None.
            interval (float, optional): Frequency at which the watermeter is read. Defaults to None.
        """
        super().__init__(name)
        self.active_liter_lpm: float = -1
        self.update_ts: float = 0.0
        if topic != "":
            self.topic = topic
        if url != "":
            self.url = url
        if interval > 0.0:
            self.interval = interval
        self.sensor_topic = self.make_topic_name("watermeter")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            # no need to listen any topics
            # self.subscribe(self.sensor_topic)
            pass

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.sensor_topic:
            em = json.loads(msg.payload.decode())
            self.on_sensor(em)
        else:
            super().on_message(client, userdata, msg)

    def on_sensor(self, em: dict[str, Any]) -> None:
        """Placeholder, no need to process water meter data

        Args:
            em (dict): data from the sensor
        """
        pass

    @override
    def run(self) -> None:
        self.worker = cast(
            HomeWizardWaterMeterThread,
            Juham.instantiate(HomeWizardWaterMeter.workerThreadId),
        )
        self.worker.init(self.sensor_topic, self.url, self.update_interval)
        super().run()

    @override
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data[self._HOMEWIZARD] = {
            "topic": self.sensor_topic,
            "url": self.url,
            "interval": self.update_interval,
        }
        return data

    @override
    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if self._HOMEWIZARD in data:
            for key, value in data[self._HOMEWIZARD].items():
                setattr(self, key, value)
