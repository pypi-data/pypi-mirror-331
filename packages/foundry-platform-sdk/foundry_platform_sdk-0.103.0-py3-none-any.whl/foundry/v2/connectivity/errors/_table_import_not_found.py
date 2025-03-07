#  Copyright 2024 Palantir Technologies, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from typing_extensions import TypedDict

from foundry._errors import NotFoundError
from foundry.v2.connectivity.models._connection_rid import ConnectionRid
from foundry.v2.connectivity.models._table_import_rid import TableImportRid


class TableImportNotFoundParameters(TypedDict):
    """The given TableImport could not be found."""

    __pydantic_config__ = {"extra": "allow"}  # type: ignore

    tableImportRid: TableImportRid

    connectionRid: ConnectionRid


@dataclass
class TableImportNotFound(NotFoundError):
    name: Literal["TableImportNotFound"]
    parameters: TableImportNotFoundParameters
    error_instance_id: str


__all__ = ["TableImportNotFound"]
