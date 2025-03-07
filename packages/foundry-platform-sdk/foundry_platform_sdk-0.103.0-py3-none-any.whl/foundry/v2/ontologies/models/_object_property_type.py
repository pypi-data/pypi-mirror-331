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

from typing import List
from typing import Literal
from typing import Union
from typing import cast

import pydantic
from typing_extensions import Annotated

from foundry.v2.core.models._attachment_type import AttachmentType
from foundry.v2.core.models._boolean_type import BooleanType
from foundry.v2.core.models._byte_type import ByteType
from foundry.v2.core.models._cipher_text_type import CipherTextType
from foundry.v2.core.models._date_type import DateType
from foundry.v2.core.models._decimal_type import DecimalType
from foundry.v2.core.models._double_type import DoubleType
from foundry.v2.core.models._float_type import FloatType
from foundry.v2.core.models._geo_point_type import GeoPointType
from foundry.v2.core.models._geo_shape_type import GeoShapeType
from foundry.v2.core.models._geotime_series_reference_type import GeotimeSeriesReferenceType  # NOQA
from foundry.v2.core.models._integer_type import IntegerType
from foundry.v2.core.models._long_type import LongType
from foundry.v2.core.models._marking_type import MarkingType
from foundry.v2.core.models._media_reference_type import MediaReferenceType
from foundry.v2.core.models._short_type import ShortType
from foundry.v2.core.models._string_type import StringType
from foundry.v2.core.models._timeseries_type import TimeseriesType
from foundry.v2.core.models._timestamp_type import TimestampType
from foundry.v2.core.models._vector_type import VectorType
from foundry.v2.ontologies.models._object_property_type_dict import (
    OntologyObjectArrayTypeDict,
)  # NOQA
from foundry.v2.ontologies.models._object_property_type_dict import StructFieldTypeDict
from foundry.v2.ontologies.models._object_property_type_dict import StructTypeDict
from foundry.v2.ontologies.models._struct_field_api_name import StructFieldApiName


class StructFieldType(pydantic.BaseModel):
    """StructFieldType"""

    api_name: StructFieldApiName = pydantic.Field(alias=str("apiName"))  # type: ignore[literal-required]

    data_type: ObjectPropertyType = pydantic.Field(alias=str("dataType"))  # type: ignore[literal-required]

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> StructFieldTypeDict:
        """Return the dictionary representation of the model using the field aliases."""
        return cast(StructFieldTypeDict, self.model_dump(by_alias=True, exclude_none=True))


class StructType(pydantic.BaseModel):
    """StructType"""

    struct_field_types: List[StructFieldType] = pydantic.Field(alias=str("structFieldTypes"))  # type: ignore[literal-required]

    type: Literal["struct"] = "struct"

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> StructTypeDict:
        """Return the dictionary representation of the model using the field aliases."""
        return cast(StructTypeDict, self.model_dump(by_alias=True, exclude_none=True))


class OntologyObjectArrayType(pydantic.BaseModel):
    """OntologyObjectArrayType"""

    sub_type: ObjectPropertyType = pydantic.Field(alias=str("subType"))  # type: ignore[literal-required]

    type: Literal["array"] = "array"

    model_config = {"extra": "allow", "populate_by_name": True}

    def to_dict(self) -> OntologyObjectArrayTypeDict:
        """Return the dictionary representation of the model using the field aliases."""
        return cast(OntologyObjectArrayTypeDict, self.model_dump(by_alias=True, exclude_none=True))


ObjectPropertyType = Annotated[
    Union[
        DateType,
        StructType,
        StringType,
        ByteType,
        DoubleType,
        GeoPointType,
        GeotimeSeriesReferenceType,
        IntegerType,
        FloatType,
        GeoShapeType,
        LongType,
        BooleanType,
        CipherTextType,
        MarkingType,
        AttachmentType,
        MediaReferenceType,
        TimeseriesType,
        OntologyObjectArrayType,
        ShortType,
        VectorType,
        DecimalType,
        TimestampType,
    ],
    pydantic.Field(discriminator="type"),
]
"""A union of all the types supported by Ontology Object properties."""
