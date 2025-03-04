from oarepo_model_builder.datatypes import ModelDataType
from oarepo_model_builder.datatypes.components import RecordModelComponent
from oarepo_model_builder.datatypes import DataTypeComponent
from oarepo_model_builder_drafts.datatypes.components import DraftRecordModelComponent

class RDMRecordModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [RecordModelComponent, DraftRecordModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "draft":
            if "base-classes" in datatype.definition["record"] and "invenio_records_resources.records.api.Record{InvenioRecord}" in datatype.definition["record"]["base-classes"]:
                datatype.definition["record"]["base-classes"].remove("invenio_records_resources.records.api.Record{InvenioRecord}")
                datatype.definition["record"]["base-classes"].append("invenio_rdm_records.records.api.RDMDraft")
            else:
                datatype.definition["record"]["base-classes"] = ["invenio_rdm_records.records.api.RDMDraft"]
            datatype.definition["record"]["fields"]["media_files"] = 'FilesField(key=MediaFilesAttrConfig["_files_attr_key"],bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],store=False,dump=False,file_cls={{invenio_rdm_records.records.api.RDMMediaFileDraft}},create=False,delete=False,)'
        elif datatype.root.profile == "record":
            if "base-classes" in datatype.definition["record"] and "invenio_drafts_resources.records.api.Draft{InvenioDraft}" in datatype.definition["record"]["base-classes"]:
                datatype.definition["record"]["base-classes"].remove("invenio_drafts_resources.records.api.Draft{InvenioDraft}")
                datatype.definition["record"]["base-classes"].append("invenio_rdm_records.records.api.RDMDraft")
            else:
                datatype.definition["record"]["base-classes"] = ["invenio_rdm_records.records.api.RDMDraft"]
            datatype.definition["record"]["base-classes"] = ["invenio_rdm_records.records.api.RDMRecord"]
            datatype.definition["record"]["fields"]["media_files"] = 'FilesField(key=MediaFilesAttrConfig["_files_attr_key"],bucket_id_attr=MediaFilesAttrConfig["_files_bucket_id_attr_key"],bucket_attr=MediaFilesAttrConfig["_files_bucket_attr_key"],store=False,dump=False,file_cls={{invenio_rdm_records.records.api.RDMMediaFileRecord}},create=False,delete=False,)'
