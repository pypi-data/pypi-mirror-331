#
#  Copyright MindBridge Analytics Inc. all rights reserved.
#
#  This material is confidential and may not be copied, distributed,
#  reversed engineered, decompiled or otherwise disseminated without
#  the prior written consent of MindBridge Analytics Inc.
#
from importlib.metadata import version


def get_package_name() -> str:
    return "mindbridge-api-python-client"


def get_version() -> str:
    return version(get_package_name())
