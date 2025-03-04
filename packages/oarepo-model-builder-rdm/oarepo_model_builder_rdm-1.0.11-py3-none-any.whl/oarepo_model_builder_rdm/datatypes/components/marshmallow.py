from typing import Any

from oarepo_model_builder.datatypes import DataTypeComponent, ModelDataType
from oarepo_model_builder.datatypes.components import MarshmallowModelComponent


class RDMMarshmallowModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [MarshmallowModelComponent]

    def before_model_prepare(
        self, datatype: Any, *, context: dict[str, Any], **kwargs: Any
    ):
        if datatype.root.profile == "record":
            marshmallow_base_classes = datatype.definition["marshmallow"][
                "base-classes"
            ]
            if (
                "oarepo_runtime.services.schema.marshmallow.BaseRecordSchema"
                in marshmallow_base_classes
            ):
                idx = marshmallow_base_classes.index(
                    "oarepo_runtime.services.schema.marshmallow.BaseRecordSchema"
                )
                marshmallow_base_classes[idx] = (
                    "oarepo_runtime.services.schema.marshmallow.RDMBaseRecordSchema"
                )
