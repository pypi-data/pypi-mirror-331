from oarepo_model_builder.datatypes import ModelDataType
from oarepo_model_builder.datatypes.components import SearchOptionsModelComponent
from oarepo_model_builder.datatypes import DataTypeComponent

class RDMSearchOptionsModelComponent(DataTypeComponent):
    eligible_datatypes = [ModelDataType]
    depends_on = [SearchOptionsModelComponent]

    def before_model_prepare(self, datatype, *, context, **kwargs):
        if datatype.root.profile == "record":
            module = datatype.definition["module"]["qualified"]
            record_search_prefix = datatype.definition["module"]["prefix"]
            datatype.definition["search-options"]["versions"] = {"class":f"{module}.{record_search_prefix}VersionsSearchOptions","base-classes": ["invenio_rdm_records.services.config.RDMSearchVersionsOptions"]}

            if "base-classes" in datatype.definition["record"] and "invenio_records_resources.services.SearchOptions{InvenioSearchOptions}" in datatype.definition["search-options"]["base-classes"]:
                datatype.definition["search-options"]["base-classes"].remove("invenio_records_resources.services.SearchOptions{InvenioSearchOptions}")
                datatype.definition["search-options"]["base-classes"].append("oarepo_runtime.services.search.I18nRDMSearchOptions")
            else:
                datatype.definition["search-options"]["base-classes"] = ["oarepo_runtime.services.search.I18nRDMSearchOptions"]

        elif datatype.root.profile == "draft":
            if "base-classes" in datatype.definition["record"] and "invenio_drafts_resources.services.records.config.SearchDraftsOptions{InvenioSearchDraftsOptions}" in datatype.definition["search-options"]["base-classes"]:
                datatype.definition["search-options"]["base-classes"].remove("invenio_drafts_resources.services.records.config.SearchDraftsOptions{InvenioSearchDraftsOptions}")
                datatype.definition["search-options"]["base-classes"].append("oarepo_runtime.services.search.I18nRDMDraftsSearchOptions")
            else:
                datatype.definition["search-options"]["base-classes"] = ["oarepo_runtime.services.search.I18nRDMDraftsSearchOptions"]

