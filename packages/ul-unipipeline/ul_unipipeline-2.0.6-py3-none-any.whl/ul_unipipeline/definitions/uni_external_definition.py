from uuid import UUID

from ul_unipipeline.definitions.uni_definition import UniDefinition


class UniExternalDefinition(UniDefinition):
    id: UUID
    name: str
