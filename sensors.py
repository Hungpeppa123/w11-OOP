#Họ và tên: Nguyễn Đức Hưng
#MSSV: 202418913
from abc import ABC, abstractmethod


class ISensor(ABC):
    @abstractmethod
    def read_value(self) -> float: ...

    @abstractmethod
    def get_unit(self) -> str: ...


class LegacySmokeDetector:
    def __init__(self, smoke_level: int) -> None:
        self.__smoke_level = smoke_level

    def get_smoke_level(self) -> int:
        return self.__smoke_level

    def get_description(self) -> str:
        return "Legacy smoke detector"

    def set_smoke_level(self, value: int) -> None:
        self.__smoke_level = max(0, min(value, 1000))


class SmokeSensorAdapter(ISensor):
    def __init__(self, legacy: LegacySmokeDetector) -> None:
        if legacy is None:
            raise ValueError("legacy must not be None")
        if not isinstance(legacy, LegacySmokeDetector):
            raise TypeError("legacy must be a LegacySmokeDetector")
        self._legacy = legacy

    def read_value(self) -> float:
        return self._legacy.get_smoke_level() / 10.0

    def get_unit(self) -> str:
        return "% smoke"
