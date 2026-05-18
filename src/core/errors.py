class EngineError(Exception):
    pass
class SchemaError(EngineError):
    pass
class UniqueConstraintError(EngineError):
    pass
class ForeignKeyError(EngineError):
    pass
class RowNotFoundError(EngineError):
    pass
class PolicyError(EngineError):
    pass
class GCError(EngineError):
    pass
