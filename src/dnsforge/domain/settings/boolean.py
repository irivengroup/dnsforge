from __future__ import annotations


class BooleanSetting:
    TRUE_VALUES = {"1", "true", "yes", "y", "on", "enabled"}
    FALSE_VALUES = {"0", "false", "no", "n", "off", "disabled", ""}

    @classmethod
    def parse(cls, value: str | None, default: bool = False) -> bool:
        if value is None:
            return default
        normalized = value.strip().strip("'\"").lower()
        if normalized in cls.TRUE_VALUES:
            return True
        if normalized in cls.FALSE_VALUES:
            return False
        raise ValueError(f"invalid boolean setting: {value}")
