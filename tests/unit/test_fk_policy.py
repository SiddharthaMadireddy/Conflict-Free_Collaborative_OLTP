from src.core.types import Row
from src.schema.fk_schema import FKSchema
from src.constraints.foreign_keys import apply_fk_policy
from src.core.constants import FK_CASCADE, FK_TOMBSTONE, FK_ORPHAN, NULL_SENTINEL

FK = FKSchema('posts','user_id','users','id')

def test_cascade():
    children = [Row('p1','posts',{'id':'p1','user_id':'u1','title':'T'})]
    apply_fk_policy({'u1': Row('u1','users',{'id':'u1'}, deleted=True)}, children, FK, FK_CASCADE)
    assert children[0].deleted

def test_tombstone():
    children = [Row('p1','posts',{'id':'p1','user_id':'u1','title':'T'})]
    apply_fk_policy({'u1': Row('u1','users',{'id':'u1'}, deleted=True)}, children, FK, FK_TOMBSTONE)
    assert not children[0].deleted

def test_orphan():
    children = [Row('p1','posts',{'id':'p1','user_id':'u1','title':'T'})]
    apply_fk_policy({'u1': Row('u1','users',{'id':'u1'}, deleted=True)}, children, FK, FK_ORPHAN)
    assert children[0].data['user_id'] == NULL_SENTINEL
