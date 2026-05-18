from src.query.materialized_view import MaterializedView

def build_state(op_log, schemas, fk_defs, fk_policy):
    mv = MaterializedView(schemas, fk_defs, fk_policy)
    return mv.build(op_log.all_ops())
