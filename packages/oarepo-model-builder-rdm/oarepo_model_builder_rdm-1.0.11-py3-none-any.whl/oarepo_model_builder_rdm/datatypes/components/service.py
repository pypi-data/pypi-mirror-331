from oarepo_model_builder.datatypes import DataTypeComponent
from oarepo_model_builder.datatypes.components.model import ServiceModelComponent
from oarepo_model_builder.datatypes.model import ModelDataType
from oarepo_model_builder_files.datatypes.components import ParentRecordComponent

class RDMServiceComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [ServiceModelComponent, ParentRecordComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):

        if not datatype.profile in ["record", "draft"]:
            return
        components_to_remove = [
            '{{oarepo_runtime.services.files.FilesComponent}}',
            '{{invenio_drafts_resources.services.records.components.DraftFilesComponent}}',
            '{{oarepo_runtime.services.components.OwnersComponent}}'
        ]
        datatype.service_config["components"] = [
            component for component in datatype.service_config["components"]
            if component not in components_to_remove
        ]
        if "base-classes" in datatype.definition["service"] and "invenio_records_resources.services.RecordService{InvenioRecordService}" in \
                datatype.definition["service"]["base-classes"]:
            datatype.definition["service"]["base-classes"].remove(
                "invenio_records_resources.services.RecordService{InvenioRecordService}")
            datatype.definition["service"]["base-classes"].append(
                "invenio_rdm_records.services.services.RDMRecordService")
        else:
            datatype.definition["service"]["base-classes"] = [
                "invenio_rdm_records.services.services.RDMRecordService"]

        if "base-classes" in datatype.definition["service-config"] and "invenio_records_resources.services.RecordServiceConfig{InvenioRecordServiceConfig}" in \
                datatype.definition["service-config"]["base-classes"]:
            datatype.definition["service-config"]["base-classes"].remove(
                "invenio_records_resources.services.RecordServiceConfig{InvenioRecordServiceConfig}")
            datatype.definition["service-config"]["base-classes"].append(
                "invenio_rdm_records.services.config.RDMRecordServiceConfig")
        else:
            datatype.definition["service-config"]["base-classes"] = ["oarepo_runtime.services.config.service.PermissionsPresetsConfigMixin",
                                                                 "invenio_rdm_records.services.config.RDMRecordServiceConfig"]
