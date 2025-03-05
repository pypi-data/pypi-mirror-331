from documente_shared.domain.base_enum import BaseEnum


class DocumentProcessingStatus(BaseEnum):
    PENDING = 'PENDING'
    ENQUEUED = 'ENQUEUED'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    INCOMPLETE = 'INCOMPLETE'
    FAILED = 'FAILED'
    DELETED = 'DELETED'
    CANCELLED = 'CANCELLED'
    IN_REVIEW = 'IN_REVIEW'


class DocumentProcessingCategory(BaseEnum):
    CIRCULAR = 'CIRCULAR'
    DESGRAVAMEN = 'DESGRAVAMEN'

    @property
    def is_circular(self):
        return self == DocumentProcessingCategory.CIRCULAR

    @property
    def is_desgravamen(self):
        return self == DocumentProcessingCategory.DESGRAVAMEN


class DocumentProcessingSource(BaseEnum):
    AGENT_UI = 'AGENT_UI'
    AGENT_CRAWLER = 'AGENT_CRAWLER'
    PLATFORM_UI = 'PLATFORM_UI'
    PLATFORM_API = 'PLATFORM_API'
    AWS_CONSOLE = 'AWS_CONSOLE'
    LOCAL_MANUAL = 'LOCAL_MANUAL'

    @property
    def is_agent_ui(self):
        return self == DocumentProcessingSource.AGENT_UI

    @property
    def is_agent_crawler(self):
        return self == DocumentProcessingSource.AGENT_CRAWLER

    @property
    def is_platform_ui(self):
        return self == DocumentProcessingSource.PLATFORM_UI

    @property
    def is_platform_api(self):
        return self == DocumentProcessingSource.PLATFORM_API

    @property
    def is_aws_console(self):
        return self == DocumentProcessingSource.AWS_CONSOLE

    @property
    def is_local_manual(self):
        return self == DocumentProcessingSource.LOCAL_MANUAL


class DocumentProcessingSubCategory(BaseEnum):
    # Circulares
    CC_COMBINADA = 'CC_COMBINADA'
    CC_NORMATIVA = 'CC_NORMATIVA'
    CC_INFORMATIVA = 'CC_INFORMATIVA'
    CC_RETENCION_SUSPENSION_REMISION = 'CC_RETENCION_SUSPENSION_REMISION'

    # Desgravamenes
    DS_CREDISEGURO = 'DS_CREDISEGURO'

