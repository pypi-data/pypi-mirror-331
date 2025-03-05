#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from enum import Enum, EnumMeta
from typing import Any
import warnings


class OnAccess(EnumMeta):
    """MetaClass to assist with DeprecatedStrEnum"""

    def __getattribute__(cls, name: str) -> Any:
        obj = super().__getattribute__(name)
        if isinstance(obj, Enum) and obj._on_access:  # type: ignore[attr-defined]
            obj._on_access()  # type: ignore[attr-defined]

        return obj

    def __getitem__(cls, name: str) -> Any:
        member: Any = super().__getitem__(name)
        if member._on_access:
            member._on_access()

        return member

    def __call__(  # type: ignore
        cls, value, names=None, *, module=None, qualname=None, type=None, start=1
    ):
        obj = super().__call__(
            value, names, module=module, qualname=qualname, type=type, start=start
        )
        if isinstance(obj, Enum) and obj._on_access:
            obj._on_access()

        return obj


class DeprecatedStrEnum(str, Enum, metaclass=OnAccess):
    """Depreciate specific enum values, to use add something like:
    MINDBRIDGE_REVIEW = "5f2c22489db6c9ff301b16cb", "use something else"
    """

    def __new__(cls, value: str, *args: str) -> Any:
        member = str.__new__(cls)
        member._value_ = value

        if args and len(args) > 1:
            raise ValueError

        if args and len(args) == 1:
            member._depreciation_arg = args[0]  # type: ignore[attr-defined]
            member._on_access = member.deprecate  # type: ignore[attr-defined]
        else:
            member._depreciation_arg = None  # type: ignore[attr-defined]
            member._on_access = None  # type: ignore[attr-defined]

        return member

    def deprecate(self) -> None:
        warnings.warn(
            f"{self.name!r} is deprecated; {self._depreciation_arg}",  # type: ignore[attr-defined]
            category=DeprecationWarning,
            stacklevel=3,
        )
