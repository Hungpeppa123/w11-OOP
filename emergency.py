#Họ và tên: Nguyễn Đức Hưng
#MSSV: 202418913
from __future__ import annotations

from abc import ABC, abstractmethod


class IEmergencyMediator(ABC):
    @abstractmethod
    def notify(self, sender: object, event_name: str) -> None: ...


class Alarm:
    def __init__(self) -> None:
        self._mediator: IEmergencyMediator | None = None
        self._is_on = False

    def set_mediator(self, mediator: IEmergencyMediator) -> None:
        if mediator is None:
            raise ValueError("mediator must not be None")
        self._mediator = mediator

    def activate(self) -> None:
        if self._is_on:
            print("[ALARM] Already ON")
            return
        self._is_on = True
        print("[ALARM] ON")

    def reset(self) -> None:
        self._is_on = False
        print("[ALARM] OFF")
        if self._mediator is not None:
            self._mediator.notify(self, "ALARM_RESET")


class DoorController:
    def __init__(self) -> None:
        self._is_locked = True

    def unlock(self) -> None:
        self._is_locked = False
        print("[DOOR] Emergency exit UNLOCKED")

    def lock(self) -> None:
        self._is_locked = True
        print("[DOOR] Emergency exit LOCKED")


class VentilationController:
    def __init__(self) -> None:
        self._is_running = True

    def start(self) -> None:
        self._is_running = True
        print("[VENT] Ventilation STARTED")

    def stop(self) -> None:
        self._is_running = False
        print("[VENT] Ventilation STOPPED")


class EmergencyMediator(IEmergencyMediator):
    def __init__(
        self,
        alarm: Alarm,
        door: DoorController,
        vent: VentilationController,
    ) -> None:
        if alarm is None or door is None or vent is None:
            raise ValueError("alarm, door and vent must not be None")
        self._alarm = alarm
        self._door = door
        self._vent = vent
        self._alarm.set_mediator(self)

    def notify(self, sender: object, event_name: str) -> None:
        match event_name:
            case "FIRE_DETECTED":
                print(f"[MEDIATOR] FIRE_DETECTED from {type(sender).__name__}")
                self._alarm.activate()
                self._door.unlock()
                self._vent.stop()
            case "ALARM_RESET":
                print(f"[MEDIATOR] ALARM_RESET from {type(sender).__name__}")
                self._door.lock()
                self._vent.start()
            case _:
                print(f"[MEDIATOR] Unknown event: {event_name}")
