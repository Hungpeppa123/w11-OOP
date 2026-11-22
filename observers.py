#Họ và tên: Nguyễn Đức Hưng
#MSSV: 202418913
from .alerts import AlertEvent, IAlertObserver
from .emergency import IEmergencyMediator


class DashboardObserver(IAlertObserver):
    def update(self, alert_event: AlertEvent) -> None:
        print(
            f"[DASHBOARD] {alert_event.sensor_name}: "
            f"{alert_event.value:.1f}{alert_event.unit} "
            f"[{alert_event.severity}]"
        )


class EmailAlertObserver(IAlertObserver):
    def __init__(self, recipient: str) -> None:
        if recipient is None or not recipient.strip():
            raise ValueError("recipient must not be empty")
        self._recipient = recipient

    def update(self, alert_event: AlertEvent) -> None:
        print(
            f"[EMAIL -> {self._recipient}] Subject: "
            f"{alert_event.severity} alert at {alert_event.sensor_name} "
            f"({alert_event.value:.1f}{alert_event.unit})"
        )


class AuditLogObserver(IAlertObserver):
    def __init__(self) -> None:
        self._logs: list[str] = []

    def update(self, alert_event: AlertEvent) -> None:
        line = (
            f"{alert_event.occurred_at:%Y-%m-%d %H:%M:%S} | "
            f"{alert_event.sensor_name} | "
            f"{alert_event.value:.1f}{alert_event.unit} | "
            f"{alert_event.severity}"
        )
        self._logs.append(line)
        print(f"[AUDIT] {line}")

    def get_logs(self) -> tuple[str, ...]:
        return tuple(self._logs)


class EmergencyBridgeObserver(IAlertObserver):
    def __init__(self, mediator: IEmergencyMediator) -> None:
        if mediator is None:
            raise ValueError("mediator must not be None")
        self._mediator = mediator

    def update(self, alert_event: AlertEvent) -> None:
        if alert_event.severity == "CRITICAL":
            self._mediator.notify(self, "FIRE_DETECTED")
