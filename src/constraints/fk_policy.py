from src.core.constants import FK_CASCADE, FK_TOMBSTONE, FK_ORPHAN
from src.core.errors import PolicyError

VALID_POLICIES = {FK_CASCADE, FK_TOMBSTONE, FK_ORPHAN}

def validate_policy(policy):
    if policy not in VALID_POLICIES:
        raise PolicyError(f'Invalid FK policy: {policy}')

def get_policy(metadata_store):
    policy = metadata_store.get_fk_policy()
    validate_policy(policy)
    return policy
