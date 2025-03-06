from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, overload, override

import isodate

from ..compiler.types import (
    Datum,
    Function,
    Module,
    Resource,
)


class Interval(Datum):
    @property
    @override
    def name(self) -> str:
        return "interval"

    @override
    def can_handle_tag(self, tag: str) -> bool:
        return tag == "ti"

    @override
    def can_handle_value(self, value: str) -> bool:
        try:
            return self.parse(value) is not None
        except ValueError:
            pass
        return False

    @override
    def parse(self, value: str):
        try:
            return isodate.parse_duration(value)
        except TypeError:
            return super().parse(value)

    @override
    def get_imports(self) -> set:
        return set(["datetime"])

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "string", "format": "interval"}

    @override
    def to_json(self, value: timedelta):
        weeks = value.days // 7
        days = value.days % 7
        hours = value.seconds // 3600
        minutes = value.seconds % 3600 // 60
        seconds = value.seconds % 60
        return (
            "P"
            + (f"{weeks}W" if weeks > 0 else "")
            + (f"{days}D" if days > 0 else "")
            + ("T" if hours > 0 or minutes > 0 or seconds > 0 else "")
            + (f"{hours}H" if hours > 0 else "")
            + (f"{minutes}M" if minutes > 0 else "")
            + (f"{seconds}S" if seconds > 0 else "")
        )


class Timestamp(Datum):
    @property
    @override
    def name(self) -> str:
        return "timestamp"

    @override
    def can_handle_tag(self, tag: str) -> bool:
        return tag == "ts"

    @override
    def can_handle_value(self, value: str) -> bool:
        try:
            dt = self.parse(value)
            return dt is not None
        except ValueError:
            pass
        return False

    @override
    def parse(self, value: str) -> datetime | None:
        try:
            dt = isodate.parse_datetime(value)
        except AttributeError:
            return super().parse(value)

        tzinfo = dt.tzinfo
        if tzinfo is None:
            return None

        offset = tzinfo.utcoffset(None) or timedelta(0)
        tz = timezone(offset)
        return datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
            tzinfo=tz,
        )

    @override
    def get_imports(self) -> set:
        return set(["datetime"])

    @override
    def to_schema(self) -> dict[str, Any]:
        return {"type": "string", "format": "date-time"}

    @override
    def to_json(self, value):
        return value.isoformat()


class TimeAdd(Function):
    module = "operator"
    name = "add"
    num_args = 2

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        left, right = args
        result = None
        if left == Interval() and right == Timestamp():
            result = Timestamp()
        if left == Timestamp() and right == Interval():
            result = Timestamp()
        if left == Interval() and right == Interval():
            result = Interval()
        return result


def now():
    return datetime.now(timezone.utc)


class Now(Function):
    module = __module__
    name = "now"
    num_args = 0

    @overload
    def _calculate_return_type(self, args: list[Datum]) -> Datum | None: ...

    @overload
    def _calculate_return_type(self, args: list[Resource]) -> Resource | None: ...

    @override
    def _calculate_return_type(
        self,
        args: list[Datum] | list[Resource],
    ) -> Datum | Resource | None:
        return Timestamp()


restrict_module = Module(
    {o.name: o for o in [Interval(), Timestamp()]},
    {
        "time_add": TimeAdd(),
        "now": Now(),
    },
    {},
)
