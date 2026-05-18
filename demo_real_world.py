import json
from adapters.myteam import Engine

def run_real_world_demo():
    print("=== INITIALIZING COLLABORATIVE PROJECT MANAGEMENT ENGINE ===")
    engine = Engine()
    
    # Initialize 3 independent distributed peers
    for peer in ['Lead_A', 'PM_B', 'Dev_C']:
        engine.open_peer(peer, fk_policy='tombstone')
        
    # Apply a completely new Real-World Schema (Projects & Tasks)
    ddl_statements = [
        """CREATE TABLE projects (
          id    TEXT PRIMARY KEY,
          code  TEXT NOT NULL UNIQUE,
          name  TEXT
        );""",
        """CREATE TABLE tasks (
          id          TEXT PRIMARY KEY,
          project_id  TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
          title       TEXT NOT NULL,
          assignee    TEXT,
          status      TEXT NOT NULL
        );"""
    ]
    
    for peer in ['Lead_A', 'PM_B', 'Dev_C']:
        engine.apply_schema(peer, ddl_statements)
        
    print("\n[Scenario 1] Lead A creates Project 'ENG' and Task 't1'")
    engine.execute('Lead_A', "INSERT INTO projects (id, code, name) VALUES ('p1', 'ENG', 'Backend V2 Refactor')")
    engine.execute('Lead_A', "INSERT INTO tasks (id, project_id, title, assignee, status) VALUES ('t1', 'p1', 'Setup WebSocket Server', 'Alice', 'TODO')")
    
    # Sync Lead_A to Dev_C so Dev_C has the task
    engine.sync('Lead_A', 'Dev_C')
    
    print("[Scenario 2] PM B (Offline) creates a conflicting Project with the SAME unique code 'ENG'")
    engine.execute('PM_B', "INSERT INTO projects (id, code, name) VALUES ('p2', 'ENG', 'Enterprise Marketing Campaign')")
    
    print("[Scenario 3] Dev C (Offline) starts working on Task 't1' and updates status")
    engine.execute('Dev_C', "UPDATE tasks SET status='IN_PROGRESS' WHERE id='t1'")
    
    print("[Scenario 4] Lead A (Offline) decides to cancel the engineering project and deletes 'p1'")
    engine.execute('Lead_A', "DELETE FROM projects WHERE id='p1'")
    
    print("\n=== EXECUTING GLOBAL P2P MERGE & RESOLUTION ===")
    # Sync all peers together
    engine.sync('Lead_A', 'PM_B')
    engine.sync('PM_B', 'Dev_C')
    engine.sync('Dev_C', 'Lead_A') # Fully converged loop
    
    print("\n=== FINAL CONVERGED GLOBAL STATE ===")
    final_state = engine.snapshot_state('Lead_A')
    print(json.dumps(final_state, indent=2))
    
    print("\n=== VERIFYING CONVERGENCE ACROSS PEERS ===")
    hash_a = engine.snapshot_hash('Lead_A')
    hash_b = engine.snapshot_hash('PM_B')
    hash_c = engine.snapshot_hash('Dev_C')
    print(f"Lead_A Hash: {hash_a[:16]}...")
    print(f"PM_B   Hash: {hash_b[:16]}...")
    print(f"Dev_C  Hash: {hash_c[:16]}...")
    assert hash_a == hash_b == hash_c, "Peers diverged!"
    print("SUCCESS: All peers reached 100% bit-identical convergence on the real-world schema!")

if __name__ == '__main__':
    run_real_world_demo()
