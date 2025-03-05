#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from enum import unique
from mindbridgeapi.enumerations.deprecated_enum import DeprecatedStrEnum


@unique
class SystemLibrary(DeprecatedStrEnum):
    """This is Deprecated, use mbapi.LibraryItem instead to get these IDs"""

    MINDBRIDGE_FOR_PROFIT = (
        "5cc9076887f13cb8a7a1926b",
        "Use mbapi.LibraryItem.MINDBRIDGE_FOR_PROFIT instead",
    )
    MINDBRIDGE_NOT_FOR_PROFIT = (
        "5cc90bbd87f13cb8a7a1926d",
        "Use mbapi.LibraryItem.MINDBRIDGE_NOT_FOR_PROFIT instead",
    )
    MINDBRIDGE_NOT_FOR_PROFIT_WITH_FUNDS = (
        "5cc90b8f87f13cb8a7a1926c",
        "Use mbapi.LibraryItem.MINDBRIDGE_NOT_FOR_PROFIT_WITH_FUNDS instead",
    )
    MINDBRIDGE_REVIEW = (
        "5f2c22489db6c9ff301b16cb",
        "Use mbapi.LibraryItem.MINDBRIDGE_NOT_FOR_PROFIT instead",
    )
