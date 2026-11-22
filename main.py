#Họ và tên: Nguyễn Đức Hưng
#MSSV: 202418913
from dataclasses import FrozenInstanceError

from campus_safety_hub.alerts import AlertEvent, IAlertObserver, SensorMonitor
from campus_safety_hub.emergency import (
    Alarm,
    DoorController,
    EmergencyMediator,
    IEmergencyMediator,
    VentilationController,
)
from campus_safety_hub.observers import (
    AuditLogObserver,
    DashboardObserver,
    EmailAlertObserver,
    EmergencyBridgeObserver,
)
from campus_safety_hub.sensors import ISensor, LegacySmokeDetector, SmokeSensorAdapter


class FaultyObserver(IAlertObserver):
    def update(self, alert_event: AlertEvent) -> None:
        raise RuntimeError("faulty observer crashed")


class OneShotObserver(IAlertObserver):
    def __init__(self, monitor: SensorMonitor) -> None:
        self._monitor = monitor

    def update(self, alert_event: AlertEvent) -> None:
        print(f"[ONE-SHOT] Received {alert_event.severity}, detaching itself")
        self._monitor.detach(self)


class EventCaptureObserver(IAlertObserver):
    def __init__(self) -> None:
        self.last_event: AlertEvent | None = None

    def update(self, alert_event: AlertEvent) -> None:
        self.last_event = alert_event


def main() -> None:
    legacy = LegacySmokeDetector(735)
    sensor: ISensor = SmokeSensorAdapter(legacy)
    print(sensor.read_value())
    print(sensor.get_unit())
    print()

    alarm = Alarm()
    door = DoorController()
    vent = VentilationController()
    mediator: IEmergencyMediator = EmergencyMediator(alarm, door, vent)

    monitor = SensorMonitor()
    dashboard = DashboardObserver()
    email = EmailAlertObserver("security@campus.local")
    audit = AuditLogObserver()
    bridge = EmergencyBridgeObserver(mediator)

    monitor.attach(dashboard)
    monitor.attach(email)
    monitor.attach(audit)
    monitor.attach(bridge)
    monitor.attach(dashboard)

    print("--- Kịch bản 1: 45% -> không cảnh báo ---")
    legacy.set_smoke_level(450)
    monitor.check_sensor("Lab-A1", sensor)

    print("--- Kịch bản 2: 60% -> WARNING (mediator không được kích hoạt) ---")
    legacy.set_smoke_level(600)
    monitor.check_sensor("Lab-A1", sensor)

    print("--- Kịch bản 3: 73.5% -> CRITICAL (còi, mở cửa, tắt thông gió) ---")
    legacy.set_smoke_level(735)
    monitor.check_sensor("Lab-A1", sensor)

    print("--- Kịch bản 4: detach email rồi kiểm tra lại ---")
    monitor.detach(email)
    monitor.check_sensor("Lab-A1", sensor)

    print("--- Kịch bản 5: reset còi -> ALARM_RESET ---")
    alarm.reset()

    print("--- Kịch bản 6: observer lỗi không làm hỏng observer khác ---")
    faulty = FaultyObserver()
    monitor.detach(dashboard)
    monitor.attach(faulty)
    monitor.attach(dashboard)
    legacy.set_smoke_level(550)
    monitor.check_sensor("Lab-B2", sensor)
    monitor.detach(faulty)

    print("--- Kịch bản 7: observer tự detach trong update ---")
    one_shot = OneShotObserver(monitor)
    monitor.attach(one_shot)
    legacy.set_smoke_level(620)
    monitor.check_sensor("Lab-C3", sensor)
    print("Gửi lần 2 (one-shot không còn nhận):")
    monitor.check_sensor("Lab-C3", sensor)

    print("--- Kịch bản 8: AlertEvent bất biến ---")
    capture = EventCaptureObserver()
    monitor.attach(capture)
    monitor.check_sensor("Lab-D4", sensor)
    monitor.detach(capture)
    try:
        capture.last_event.severity = "X"
    except FrozenInstanceError:
        print("FrozenInstanceError: không thể sửa AlertEvent")

    print("--- Audit log ---")
    for line in audit.get_logs():
        print(line)


if __name__ == "__main__":
    main()
