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

from functools import cached_property
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pydantic
from typing_extensions import Annotated
from typing_extensions import TypedDict

from foundry._core import ApiClient
from foundry._core import ApiResponse
from foundry._core import Auth
from foundry._core import Config
from foundry._core import RequestInfo
from foundry._core import StreamingContextManager
from foundry._core.utils import maybe_ignore_preview
from foundry._errors import handle_unexpected
from foundry.v1.ontologies.models._action_type_api_name import ActionTypeApiName
from foundry.v1.ontologies.models._apply_action_request import ApplyActionRequest
from foundry.v1.ontologies.models._apply_action_request_dict import ApplyActionRequestDict  # NOQA
from foundry.v1.ontologies.models._apply_action_response import ApplyActionResponse
from foundry.v1.ontologies.models._batch_apply_action_response import (
    BatchApplyActionResponse,
)  # NOQA
from foundry.v1.ontologies.models._data_value import DataValue
from foundry.v1.ontologies.models._ontology_rid import OntologyRid
from foundry.v1.ontologies.models._parameter_id import ParameterId
from foundry.v1.ontologies.models._validate_action_response import ValidateActionResponse  # NOQA


class ActionClient:
    """
    The API client for the Action Resource.

    :param auth: Your auth configuration.
    :param hostname: Your Foundry hostname (for example, "myfoundry.palantirfoundry.com"). This can also include your API gateway service URI.
    :param config: Optionally specify the configuration for the HTTP session.
    """

    def __init__(
        self,
        auth: Auth,
        hostname: str,
        config: Optional[Config] = None,
    ):
        self._auth = auth
        self._hostname = hostname
        self._config = config
        self._api_client = ApiClient(auth=auth, hostname=hostname, config=config)
        self.with_streaming_response = _ActionClientStreaming(
            auth=auth, hostname=hostname, config=config
        )
        self.with_raw_response = _ActionClientRaw(auth=auth, hostname=hostname, config=config)

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> ApplyActionResponse:
        """
        Applies an action using the given parameters. Changes to the Ontology are eventually consistent and may take
        some time to be visible.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: ApplyActionResponse
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/apply",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        ).decode()

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply_batch(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> BatchApplyActionResponse:
        """
        Applies multiple actions (of the same Action Type) using the given parameters.
        Changes to the Ontology are eventually consistent and may take some time to be visible.

        Up to 20 actions may be applied in one call. Actions that only modify objects in Object Storage v2 and do not
        call Functions may receive a higher limit.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) and
        [notifications](/docs/foundry/action-types/notifications/) are not currently supported by this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param requests:
        :type requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: BatchApplyActionResponse
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/applyBatch",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "requests": requests,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "requests": List[Union[ApplyActionRequest, ApplyActionRequestDict]],
                    },
                ),
                response_type=BatchApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        ).decode()

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def validate(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> ValidateActionResponse:
        """
        Validates if an action can be run with the given set of parameters.
        The response contains the evaluation of parameters and **submission criteria**
        that determine if the request is `VALID` or `INVALID`.
        For performance reasons, validations will not consider existing objects or other data in Foundry.
        For example, the uniqueness of a primary key or the existence of a user ID will not be checked.
        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint. Unspecified parameters will be given a default value of `null`.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: ValidateActionResponse
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/validate",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ValidateActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        ).decode()


class _ActionClientRaw:
    """
    The API client for the Action Resource.

    :param auth: Your auth configuration.
    :param hostname: Your Foundry hostname (for example, "myfoundry.palantirfoundry.com"). This can also include your API gateway service URI.
    :param config: Optionally specify the configuration for the HTTP session.
    """

    def __init__(
        self,
        auth: Auth,
        hostname: str,
        config: Optional[Config] = None,
    ):
        self._auth = auth
        self._hostname = hostname
        self._config = config
        self._api_client = ApiClient(auth=auth, hostname=hostname, config=config)

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> ApiResponse[ApplyActionResponse]:
        """
        Applies an action using the given parameters. Changes to the Ontology are eventually consistent and may take
        some time to be visible.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: ApiResponse[ApplyActionResponse]
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/apply",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply_batch(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> ApiResponse[BatchApplyActionResponse]:
        """
        Applies multiple actions (of the same Action Type) using the given parameters.
        Changes to the Ontology are eventually consistent and may take some time to be visible.

        Up to 20 actions may be applied in one call. Actions that only modify objects in Object Storage v2 and do not
        call Functions may receive a higher limit.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) and
        [notifications](/docs/foundry/action-types/notifications/) are not currently supported by this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param requests:
        :type requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: ApiResponse[BatchApplyActionResponse]
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/applyBatch",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "requests": requests,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "requests": List[Union[ApplyActionRequest, ApplyActionRequestDict]],
                    },
                ),
                response_type=BatchApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def validate(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> ApiResponse[ValidateActionResponse]:
        """
        Validates if an action can be run with the given set of parameters.
        The response contains the evaluation of parameters and **submission criteria**
        that determine if the request is `VALID` or `INVALID`.
        For performance reasons, validations will not consider existing objects or other data in Foundry.
        For example, the uniqueness of a primary key or the existence of a user ID will not be checked.
        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint. Unspecified parameters will be given a default value of `null`.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: ApiResponse[ValidateActionResponse]
        """

        return self._api_client.call_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/validate",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ValidateActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )


class _ActionClientStreaming:
    """
    The API client for the Action Resource.

    :param auth: Your auth configuration.
    :param hostname: Your Foundry hostname (for example, "myfoundry.palantirfoundry.com"). This can also include your API gateway service URI.
    :param config: Optionally specify the configuration for the HTTP session.
    """

    def __init__(
        self,
        auth: Auth,
        hostname: str,
        config: Optional[Config] = None,
    ):
        self._auth = auth
        self._hostname = hostname
        self._config = config
        self._api_client = ApiClient(auth=auth, hostname=hostname, config=config)

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> StreamingContextManager[ApplyActionResponse]:
        """
        Applies an action using the given parameters. Changes to the Ontology are eventually consistent and may take
        some time to be visible.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: StreamingContextManager[ApplyActionResponse]
        """

        return self._api_client.stream_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/apply",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def apply_batch(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> StreamingContextManager[BatchApplyActionResponse]:
        """
        Applies multiple actions (of the same Action Type) using the given parameters.
        Changes to the Ontology are eventually consistent and may take some time to be visible.

        Up to 20 actions may be applied in one call. Actions that only modify objects in Object Storage v2 and do not
        call Functions may receive a higher limit.

        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) and
        [notifications](/docs/foundry/action-types/notifications/) are not currently supported by this endpoint.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read api:ontologies-write`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param requests:
        :type requests: List[Union[ApplyActionRequest, ApplyActionRequestDict]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: StreamingContextManager[BatchApplyActionResponse]
        """

        return self._api_client.stream_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/applyBatch",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "requests": requests,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "requests": List[Union[ApplyActionRequest, ApplyActionRequestDict]],
                    },
                ),
                response_type=BatchApplyActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )

    @maybe_ignore_preview
    @pydantic.validate_call
    @handle_unexpected
    def validate(
        self,
        ontology_rid: OntologyRid,
        action_type: ActionTypeApiName,
        *,
        parameters: Dict[ParameterId, Optional[DataValue]],
        request_timeout: Optional[Annotated[pydantic.StrictInt, pydantic.Field(gt=0)]] = None,
    ) -> StreamingContextManager[ValidateActionResponse]:
        """
        Validates if an action can be run with the given set of parameters.
        The response contains the evaluation of parameters and **submission criteria**
        that determine if the request is `VALID` or `INVALID`.
        For performance reasons, validations will not consider existing objects or other data in Foundry.
        For example, the uniqueness of a primary key or the existence of a user ID will not be checked.
        Note that [parameter default values](/docs/foundry/action-types/parameters-default-value/) are not currently supported by
        this endpoint. Unspecified parameters will be given a default value of `null`.

        Third-party applications using this endpoint via OAuth2 must request the
        following operation scopes: `api:ontologies-read`.

        :param ontology_rid: ontologyRid
        :type ontology_rid: OntologyRid
        :param action_type: actionType
        :type action_type: ActionTypeApiName
        :param parameters:
        :type parameters: Dict[ParameterId, Optional[DataValue]]
        :param request_timeout: timeout setting for this request in seconds.
        :type request_timeout: Optional[int]
        :return: Returns the result object.
        :rtype: StreamingContextManager[ValidateActionResponse]
        """

        return self._api_client.stream_api(
            RequestInfo(
                method="POST",
                resource_path="/v1/ontologies/{ontologyRid}/actions/{actionType}/validate",
                query_params={},
                path_params={
                    "ontologyRid": ontology_rid,
                    "actionType": action_type,
                },
                header_params={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body={
                    "parameters": parameters,
                },
                body_type=TypedDict(
                    "Body",
                    {  # type: ignore
                        "parameters": Dict[ParameterId, Optional[DataValue]],
                    },
                ),
                response_type=ValidateActionResponse,
                request_timeout=request_timeout,
                throwable_errors={},
            ),
        )
