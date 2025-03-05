#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#

from typing import Optional, Union
from pydantic import ConfigDict, Field, model_validator
from mindbridgeapi.common_validators import _warning_if_extra_fields
from mindbridgeapi.generated_pydantic_model.model import (
    ApiTaskHistoryEntryRead,
    ApiTaskHistoryRead,
)


class _ApiTaskHistoryEntryRead(ApiTaskHistoryEntryRead):
    new_value: Optional[Union[str, list[str], dict[str, str]]] = (
        Field().merge_field_infos(ApiTaskHistoryEntryRead.model_fields["new_value"])  # type: ignore[assignment]
    )
    previous_value: Optional[Union[str, list[str], dict[str, str]]] = (
        Field().merge_field_infos(  # type: ignore[assignment]
            ApiTaskHistoryEntryRead.model_fields["previous_value"]
        )
    )


class TaskHistoryItem(ApiTaskHistoryRead):
    changes: Optional[list[_ApiTaskHistoryEntryRead]] = Field().merge_field_infos(
        ApiTaskHistoryRead.model_fields["changes"]
    )  # type: ignore[assignment]

    model_config = ConfigDict(
        extra="allow",
        validate_assignment=True,
        validate_default=True,
        validate_return=True,
    )
    _ = model_validator(mode="after")(_warning_if_extra_fields)
