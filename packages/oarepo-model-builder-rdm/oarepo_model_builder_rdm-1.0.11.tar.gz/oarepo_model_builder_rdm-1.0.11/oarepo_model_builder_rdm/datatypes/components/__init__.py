from .draft_record import RDMDraftParentComponent
from .ext_resource import RDMExtResourceModelComponent
from .marshmallow import RDMMarshmallowModelComponent
from .record import RDMRecordModelComponent
from .search_options import RDMSearchOptionsModelComponent
from .service import RDMServiceComponent
from .ui_marshmallow import RDMUIMarshmallowModelComponent

RDM_COMPONENTS = [
    RDMServiceComponent,
    RDMRecordModelComponent,
    RDMExtResourceModelComponent,
    RDMDraftParentComponent,
    RDMMarshmallowModelComponent,
    RDMSearchOptionsModelComponent,
    RDMUIMarshmallowModelComponent,
]
