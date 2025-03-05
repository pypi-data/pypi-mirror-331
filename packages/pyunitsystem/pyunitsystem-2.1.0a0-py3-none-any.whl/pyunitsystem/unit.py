import enum
import warnings


class Unit(enum.Enum):
    """
    Base class for all Unit.
    Children class are also expected to inherit from silx Enum class
    """

    @classmethod
    def from_str(cls, value: str):
        raise NotImplementedError("Base class")

    @classmethod
    def from_value(cls, value):
        warnings.warn(
            "This function is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,  # To show the warning at the call site, rather than here
        )
        if isinstance(value, str):
            return cls.from_str(value=value)
        else:
            return cls(value)
