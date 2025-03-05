#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Optional, Union
from pydantic import ConfigDict, Field, field_validator, model_validator
from mindbridgeapi.common_validators import (
    _convert_userinfo_to_useritem,
    _warning_if_extra_fields,
)
from mindbridgeapi.generated_pydantic_model.model import (
    ApiTransactionIdPreviewIndicatorRead,
    ApiTransactionIdPreviewRead,
    ApiTransactionIdPreviewRowRead,
)


class _ApiTransactionIdPreviewRowRead(ApiTransactionIdPreviewRowRead):
    detail_rows: Optional[list[dict[str, str]]] = Field().merge_field_infos(
        ApiTransactionIdPreviewRowRead.model_fields["detail_rows"]
    )  # type: ignore[assignment]


class _ApiTransactionIdPreviewIndicatorRead(ApiTransactionIdPreviewIndicatorRead):
    data: Optional[list[_ApiTransactionIdPreviewRowRead]] = Field().merge_field_infos(
        ApiTransactionIdPreviewIndicatorRead.model_fields["data"]
    )  # type: ignore[assignment]
    value: Optional[Union[int, float, str, dict[str, int]]] = Field().merge_field_infos(
        ApiTransactionIdPreviewIndicatorRead.model_fields["value"]
    )  # type: ignore[assignment]


class TransactionIdPreviewItem(ApiTransactionIdPreviewRead):
    entry_previews: Optional[list[_ApiTransactionIdPreviewRowRead]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiTransactionIdPreviewRead.model_fields["entry_previews"]
        )
    )
    indicators: Optional[dict[str, _ApiTransactionIdPreviewIndicatorRead]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiTransactionIdPreviewRead.model_fields["indicators"]
        )
    )

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _a = model_validator(mode="after")(_warning_if_extra_fields)
    _b = field_validator("*")(_convert_userinfo_to_useritem)
