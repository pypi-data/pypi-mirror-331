# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2021 AMOSSYS. All rights reserved.
#
# This file is part of Cyber Range AMOSSYS.
#
# Cyber Range AMOSSYS can not be copied and/or distributed without the express
# permission of AMOSSYS.
#
from enum import Enum
from typing import List
from typing import TypeVar

from pydantic import Field
from pydantic.types import StringConstraints
from typing_extensions import Annotated

PositiveEqualInt = Annotated[int, Field(ge=0)]

NotEmptyStr = Annotated[str, StringConstraints(min_length=1)]

T = TypeVar("T")

NotEmptyList = Annotated[List[T], Field(min_length=1)]


class RoleEnum(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"
    ANALYST = "analyst"
    AD = "ad"
    FILE_SERVER = "file_server"
    INTERNET = "internet"
    SQUID = "squid"
    MAIL_SERVER = "mail_server"
    LOG_COLLECTOR = "log_collector"
    PROBE = "probe"
    REDTEAM_INFRASTRUCTURE = "redteam_infrastructure"
    MONITORING = "monitoring"

    @staticmethod
    def from_str(label: str) -> Enum:
        if label == "client":
            return RoleEnum.CLIENT
        if label == "admin":
            return RoleEnum.ADMIN
        if label == "ad":
            return RoleEnum.AD
        if label == "file_server":
            return RoleEnum.FILE_SERVER
        if label == "internet":
            return RoleEnum.INTERNET
        if label == "squid":
            return RoleEnum.SQUID
        if label == "mail_server":
            return RoleEnum.MAIL_SERVER
        if label == "log_collector":
            return RoleEnum.LOG_COLLECTOR
        if label == "probe":
            return RoleEnum.PROBE
        if label == "redteam_infrastructure":
            return RoleEnum.REDTEAM_INFRASTRUCTURE
        if label == "monitoring":
            return RoleEnum.MONITORING
        raise NotImplementedError
