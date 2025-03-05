from pyunitsystem.unit import Unit


class TimeSystem(Unit):
    """Unit system for time in SI units (seconds)"""

    SECOND = 1.0
    MINUTE = 60.0 * SECOND
    HOUR = 60.0 * MINUTE
    DAY = 24.0 * HOUR
    MILLI_SECOND = SECOND * 1e-3
    MICRO_SECOND = SECOND * 1e-6
    NANO_SECOND = SECOND * 1e-9

    @classmethod
    def from_str(cls, value: str):
        assert isinstance(value, str)
        if value.lower() in ("s", "second"):
            return TimeSystem.SECOND
        elif value.lower() in ("m", "minute"):
            return TimeSystem.MINUTE
        elif value.lower() in ("h", "hour"):
            return TimeSystem.HOUR
        elif value.lower() in (
            "d",
            "day",
        ):
            return TimeSystem.DAY
        elif value.lower() in ("ns", "nanosecond", "nano-second"):
            return TimeSystem.NANO_SECOND
        elif value.lower() in ("microsecond", "micro-second"):
            return TimeSystem.MICRO_SECOND
        elif value.lower() in ("millisecond", "milli-second"):
            return TimeSystem.MILLI_SECOND
        else:
            raise ValueError(f"Cannot convert: {value}")

    def __str__(self):
        if self == TimeSystem.SECOND:
            return "second"
        elif self == TimeSystem.MINUTE:
            return "minute"
        elif self == TimeSystem.HOUR:
            return "hour"
        elif self == TimeSystem.DAY:
            return "day"
        elif self == TimeSystem.MILLI_SECOND:
            return "millisecond"
        elif self == TimeSystem.MICRO_SECOND:
            return "microsecond"
        elif self == TimeSystem.NANO_SECOND:
            return "nanosecond"
        else:
            raise ValueError("Cannot convert: to time system")


second = TimeSystem.SECOND
