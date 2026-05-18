# Conflict-Free Collaborative OLTP System Writeup

This document defends the architectural choices made in the implementation of the conflict-free collaborative OLTP system.

## Lattice Choices Per Type

The database implements cell-level conflict resolution using a Last-Writer-Wins (LWW) Register approach for individual columns. 
- **Rows**: Handled via an Observed-Remove Set (OR-Set) semantics. A row exists if its latest `OP_INSERT` sequence exceeds its latest `OP_DELETE` sequence (based on Lamport clocks). 
- **Cells**: Handled as LWW-Registers. Each column update carries an `actor_id` and a `seq` (Lamport timestamp). Concurrency is resolved by picking the value with the highest `seq`. Ties are deterministically broken using the `actor_id`. This prevents whole-row Last-Writer-Wins, preserving updates to distinct cells (e.g., `name` vs. `email`) across concurrent peers.

## Uniqueness Protocol

Pure CRDTs cannot enforce global uniqueness without coordination. We implemented an explicit post-merge deterministic resolution protocol to enforce `UNIQUE` constraints (e.g., on `users.email`):
- During `MaterializedView` building, after standard CRDT resolution, we identify duplicate values in unique columns across all active (non-deleted) rows.
- A deterministic tie-breaker (using `row_id` ordering) selects a "winner".
- The "loser" row is not silently dropped. Instead, its conflicting column value is deterministically mutated (e.g., appended with `#conflict#<row_id>`). This makes the loser recoverable by the application layer without losing the entire row's data.
- If a row holding a unique value is deleted (e.g., `u1` is deleted), the value becomes available again, and concurrent inserts (e.g., `u3`) can successfully claim it.

## Foreign-Key (FK) Protocol

The engine supports explicitly declared foreign key policies. For this reference scenario, the `tombstone` policy is used:
- When a parent row (e.g., `users` with `id=u1`) is deleted, the child row (`orders` with `user_id=u1`) is evaluated.
- Under the `tombstone` policy, the child row survives. Its `user_id` column continues to reference `u1`.
- `u1` is logically deleted (not returned in query results) but referentially live in the CRDT metadata (its `OP_DELETE` is tracked). This provides a reliable semantic for local-first systems where dropping the child might cause unacceptable data loss.

## Sync Protocol

The sync protocol is pairwise and bidirectional. 
- Peers exchange their raw operation logs (which are compacted, see below).
- Any operations missing from the local log are appended.
- Because operations are monotonic and conflict resolution is purely state-based and deterministic, applying operations in any order yields the exact same final materialized state (convergence is invariant under sync ordering).

## Metadata-Growth Analysis

Vector clocks and operation logs that grow indefinitely per write are a known failure mode of naive CRDTs. 
- To guarantee bounded metadata ($O(\text{writers})$ per row), the engine implements continuous Garbage Collection via a `compact()` method on the `OpLog`.
- `compact()` iterates over the entire operation log and identifies the minimal set of "winning" operations that contribute to the current state (the latest `OP_DELETE`, the latest `OP_INSERT`, and the latest `OP_UPDATE` per cell).
- All superseded operations are dropped.
- To prevent Lamport clock regressions when losing operations are dropped, the true watermark (maximum observed sequence per actor) is persisted independently in `watermark.json.wm`.
- As a result, the storage overhead per row is strictly bounded by the number of distinct peers that have written to its cells, ensuring sustainable long-term operation.
