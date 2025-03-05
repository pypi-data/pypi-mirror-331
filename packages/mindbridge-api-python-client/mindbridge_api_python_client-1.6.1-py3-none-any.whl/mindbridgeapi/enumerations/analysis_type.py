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
class AnalysisType(DeprecatedStrEnum):
    """This is Deprecated, use mbapi.AnalysisTypeItem instead to get these IDs"""

    GENERAL_LEDGER = (
        "4b8360d00000000000000000",
        "Use mbapi.AnalysisTypeItem.GENERAL_LEDGER instead",
    )
    NOT_FOR_PROFIT_GENERAL_LEDGER = (
        "4b8360d00000000000000001",
        "Use mbapi.AnalysisTypeItem.NOT_FOR_PROFIT_GENERAL_LEDGER instead",
    )
    NOT_FOR_PROFIT_GENERAL_LEDGER_FUND = (
        "4b8360d00000000000000002",
        "Use mbapi.AnalysisTypeItem.NOT_FOR_PROFIT_GENERAL_LEDGER_FUND instead",
    )
    ACCOUNTS_PAYABLE_V2 = (
        "4b8360d00000000000000003",
        "Use mbapi.AnalysisTypeItem.ACCOUNTS_PAYABLE_V2 instead",
    )
    ACCOUNTS_RECEIVABLE_V2 = (
        "4b8360d00000000000000004",
        "Use mbapi.AnalysisTypeItem.ACCOUNTS_RECEIVABLE_V2 instead",
    )
