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

from typing import Dict

from typing_extensions import TypedDict

from foundry.v2.aip_agents.models._agent_metadata_dict import AgentMetadataDict
from foundry.v2.aip_agents.models._agent_rid import AgentRid
from foundry.v2.aip_agents.models._agent_version_string import AgentVersionString
from foundry.v2.aip_agents.models._parameter_dict import ParameterDict
from foundry.v2.aip_agents.models._parameter_id import ParameterId


class AgentDict(TypedDict):
    """Agent"""

    __pydantic_config__ = {"extra": "allow"}  # type: ignore

    rid: AgentRid
    """An RID identifying an AIP Agent created in [AIP Agent Studio](/docs/foundry/agent-studio/overview/)."""

    version: AgentVersionString
    """The version of this instance of the Agent."""

    metadata: AgentMetadataDict

    parameters: Dict[ParameterId, ParameterDict]
    """
    The types and names of variables configured for the Agent in [AIP Agent Studio](/docs/foundry/agent-studio/overview/) in the [application state](/docs/foundry/agent-studio/application-state/).
    These variables can be used to send custom values in prompts sent to an Agent to customize and control the Agent's behavior.
    """
