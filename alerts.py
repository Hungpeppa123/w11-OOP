#Họ và tên: Nguyễn Đức Hưng
#MSSV: 202418913
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from .sensors import ISensor


@dataclass(frozen=True)
class AlertEvent:
    sensor_name: str
    value: float
    unit: str
    severity: str
    occurred_at: datetime


class IAlertObserver(ABC):
    @abstractmethod
    def update(self, alert_event: AlertEvent) -> None: ...


class SensorMonitor:
    def __init__(self) -> None:
        self._observers: list[IAlertObserver] = []

    def attach(self, observer: IAlertObserver) -> None:
        if observer is None:
            raise ValueError("observer must not be None")
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: IAlertObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def check_sensor(self, sensor_name: str, sensor: ISensor) -> None:
        value = sensor.read_value()
        if value >= 70:
            severity = "CRITICAL"
        elif value >= 50:
            severity = "WARNING"
        else:
            return

        alert_event = AlertEvent(
            sensor_name,
            value,
            sensor.get_unit(),
            severity,
            datetime.now(),
        )
        self._notify(alert_event)

    def _notify(self, alert_event: AlertEvent) -> None:
        for observer in list(self._observers):
            try:
                observer.update(alert_event)
            except Exception as ex:
                print(f"[ERROR] {type(observer).__name__} failed: {ex}")
