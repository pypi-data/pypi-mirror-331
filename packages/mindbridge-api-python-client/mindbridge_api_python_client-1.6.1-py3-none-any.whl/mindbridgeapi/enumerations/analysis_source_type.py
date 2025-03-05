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
class AnalysisSourceType(DeprecatedStrEnum):
    """This is Deprecated, use mbapi.AnalysisSourceTypeItem instead to get these IDs"""

    # General Ledger (for-profit) - 4b8360d00000000000000000
    GENERAL_LEDGER_JOURNAL = (
        "4b8361d00000000000000000",
        "Use mbapi.AnalysisSourceTypeItem.GENERAL_LEDGER_JOURNAL instead",
    )
    OPENING_BALANCE = (
        "4b8361d00000000000000002",
        "Use mbapi.AnalysisSourceTypeItem.OPENING_BALANCE instead",
    )
    CLOSING_BALANCE = (
        "4b8361d00000000000000003",
        "Use mbapi.AnalysisSourceTypeItem.CLOSING_BALANCE instead",
    )
    CHART_OF_ACCOUNTS = (
        "4b8361d00000000000000004",
        "Use mbapi.AnalysisSourceTypeItem.CHART_OF_ACCOUNTS instead",
    )
    ADJUSTING_ENTRIES = (
        "4b8361d00000000000000016",
        "Use mbapi.AnalysisSourceTypeItem.ADJUSTING_ENTRIES instead",
    )
    RECLASSIFICATION_ENTRIES = (
        "4b8361d00000000000000017",
        "Use mbapi.AnalysisSourceTypeItem.RECLASSIFICATION_ENTRIES instead",
    )
    ELIMINATION_ENTRIES = (
        "4b8361d00000000000000018",
        "Use mbapi.AnalysisSourceTypeItem.ELIMINATION_ENTRIES instead",
    )

    # General Ledger (not-for-profit) - 4b8360d00000000000000001
    NOT_FOR_PROFIT_GENERAL_LEDGER_JOURNAL = (
        "4b8361d00000000000000051",
        "Use mbapi.AnalysisSourceTypeItem.NOT_FOR_PROFIT_GENERAL_LEDGER_JOURNAL "
        "instead",
    )
    NOT_FOR_PROFIT_OPENING_BALANCE = (
        "4b8361d00000000000000057",
        "Use mbapi.AnalysisSourceTypeItem.NOT_FOR_PROFIT_OPENING_BALANCE instead",
    )
    NOT_FOR_PROFIT_CLOSING_BALANCE = (
        "4b8361d00000000000000058",
        "Use mbapi.AnalysisSourceTypeItem.NOT_FOR_PROFIT_CLOSING_BALANCE instead",
    )

    # General Ledger (not-for-profit with funds) - 4b8360d00000000000000002
    GENERAL_LEDGER_JOURNAL_FUND = (
        "4b8361d00000000000000001",
        "Use mbapi.AnalysisSourceTypeItem.GENERAL_LEDGER_JOURNAL_FUND instead",
    )
    FUND_OPENING_BALANCE = (
        "4b8361d00000000000000059",
        "Use mbapi.AnalysisSourceTypeItem.FUND_OPENING_BALANCE instead",
    )
    FUND_CLOSING_BALANCE = (
        "4b8361d0000000000000005a",
        "Use mbapi.AnalysisSourceTypeItem.FUND_CLOSING_BALANCE instead",
    )
    FUND_CHART_OF_ACCOUNTS = (
        "4b8361d00000000000000005",
        "Use mbapi.AnalysisSourceTypeItem.FUND_CHART_OF_ACCOUNTS instead",
    )

    # Accounts Payable - 4b8360d00000000000000003
    ACCOUNTS_PAYABLE_DETAIL = (
        "4b8361d00000000000000006",
        "Use mbapi.AnalysisSourceTypeItem.ACCOUNTS_PAYABLE_DETAIL instead",
    )
    CLOSING_PAYABLES_LIST = (
        "4b8361d00000000000000010",
        "Use mbapi.AnalysisSourceTypeItem.CLOSING_PAYABLES_LIST instead",
    )
    VENDOR_OPENING_BALANCES = (
        "4b8361d00000000000000007",
        "Use mbapi.AnalysisSourceTypeItem.VENDOR_OPENING_BALANCES instead",
    )
    VENDOR_LIST = (
        "4b8361d00000000000000008",
        "Use mbapi.AnalysisSourceTypeItem.VENDOR_LIST instead",
    )
    OPEN_PAYABLES_LIST = (
        "4b8361d00000000000000009",
        "Use mbapi.AnalysisSourceTypeItem.OPEN_PAYABLES_LIST instead",
    )

    # Accounts Receivable - 4b8360d00000000000000004
    ACCOUNTS_RECEIVABLE_DETAIL = (
        "4b8361d00000000000000011",
        "Use mbapi.AnalysisSourceTypeItem.ACCOUNTS_RECEIVABLE_DETAIL instead",
    )
    CLOSING_RECEIVABLES_LIST = (
        "4b8361d00000000000000014",
        "Use mbapi.AnalysisSourceTypeItem.CLOSING_RECEIVABLES_LIST instead",
    )
    CUSTOMER_OPENING_BALANCES = (
        "4b8361d00000000000000012",
        "Use mbapi.AnalysisSourceTypeItem.CUSTOMER_OPENING_BALANCES instead",
    )
    CUSTOMER_LIST = (
        "4b8361d00000000000000039",
        "Use mbapi.AnalysisSourceTypeItem.CUSTOMER_LIST instead",
    )
    OPEN_RECEIVABLES_LIST = (
        "4b8361d00000000000000013",
        "Use mbapi.AnalysisSourceTypeItem.OPEN_RECEIVABLES_LIST instead",
    )

    # Additional Analysis Data
    ADDITIONAL_ANALYSIS_DATA = (
        "4b8361d00000000000000015",
        "Use mbapi.AnalysisSourceTypeItem.ADDITIONAL_ANALYSIS_DATA instead",
    )

    # Other
    FUND_ADJUSTING_ENTRIES = (
        "4b8361d00000000000000019",
        "Use mbapi.AnalysisSourceTypeItem.FUND_ADJUSTING_ENTRIES instead",
    )
    FUND_ELIMINATION_ENTRIES = (
        "4b8361d00000000000000020",
        "Use mbapi.AnalysisSourceTypeItem.FUND_ELIMINATION_ENTRIES instead",
    )
    FUND_RECLASSIFICATION_ENTRIES = (
        "4b8361d00000000000000021",
        "Use mbapi.AnalysisSourceTypeItem.FUND_RECLASSIFICATION_ENTRIES instead",
    )
