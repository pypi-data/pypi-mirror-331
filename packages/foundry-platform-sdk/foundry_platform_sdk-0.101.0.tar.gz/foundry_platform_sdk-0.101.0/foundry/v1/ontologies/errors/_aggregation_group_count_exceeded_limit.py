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

from typing_extensions import NotRequired
from typing_extensions import TypedDict

from foundry._errors import BadRequestError


class AggregationGroupCountExceededLimitParameters(TypedDict):
    """
    The number of groups in the aggregations grouping exceeded the allowed limit. This can typically be fixed by
    adjusting your query to reduce the number of groups created by your aggregation. For instance:
    - If you are using multiple `groupBy` clauses, try reducing the number of clauses.
    - If you are using a `groupBy` clause with a high cardinality property, try filtering the data first
      to reduce the number of groups.
    """

    __pydantic_config__ = {"extra": "allow"}  # type: ignore

    groupsCount: NotRequired[int]

    groupsLimit: NotRequired[int]


@dataclass
class AggregationGroupCountExceededLimit(BadRequestError):
    name: Literal["AggregationGroupCountExceededLimit"]
    parameters: AggregationGroupCountExceededLimitParameters
    error_instance_id: str


__all__ = ["AggregationGroupCountExceededLimit"]
