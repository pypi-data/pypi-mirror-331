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

from typing import cast

import pydantic

from foundry.v2.aip_agents.models._agent_rid import AgentRid
from foundry.v2.aip_agents.models._agent_version_string import AgentVersionString
from foundry.v2.aip_agents.models._session_dict import SessionDict
from foundry.v2.aip_agents.models._session_metadata import SessionMetadata
from foundry.v2.aip_agents.models._session_rid import SessionRid


class Session(pydantic.BaseModel):
    """Session"""

    rid: SessionRid

    """The Resource Identifier (RID) of the conversation session."""

    metadata: SessionMetadata

    """Metadata about the session."""

    agent_rid: AgentRid = pydantic.Field(alias=str("agentRid"))  # type: ignore[literal-required]

    """The Resource Identifier (RID) of the Agent associated with the session."""

    agent_version: AgentVersionString = pydantic.Field(alias=str("agentVersion"))  # type: ignore[literal-required]

    """
    The version of the Agent associated with the session.
    This can be set by clients on session creation.
    If not specified, defaults to use the latest published version of the Agent at session creation time.
    """

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> SessionDict:
        """Return the dictionary representation of the model using the field aliases."""
        return cast(SessionDict, self.model_dump(by_alias=True, exclude_none=True))
