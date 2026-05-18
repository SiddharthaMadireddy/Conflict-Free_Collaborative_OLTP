# 🏴‍☠️ CRDT Relational Engine

<div align="center">
  <h3><b>A masterless, local-first, peer-to-peer relational database powered by Conflict-Free Replicated Data Types (CRDTs).</b></h3>
  <p><i>Engineered with passion and precision by <b>Pixel Pirates</b> for the Anvil P-01 L3 Evaluation.</i></p>
</div>

Traditional relational databases rely on central coordination (e.g., consensus protocols, single-leader replication) to maintain ACID guarantees. This engine demonstrates a fully decentralized, masterless architecture capable of offline-first operation, seamless multi-peer synchronization, and guaranteed 100% bit-identical state convergence across arbitrary network partitions.

---

## 🏛️ Key Architectural Pillars

### 1. True Cell-Level Concurrency (LWW-Registers)

Naive CRDT databases often implement Last-Writer-Wins (LWW) at the entire row level, causing concurrent updates to different columns (e.g., Peer A updating `name`, Peer B updating `email`) to overwrite and lose data.

- **Rows** are modeled as Observed-Remove Sets (OR-Sets) tracking Lamport clocks for `OP_INSERT` and `OP_DELETE`.
- **Cells** are modeled as independent LWW-Registers. Concurrency is resolved per-column using Lamport timestamps (`seq`), with deterministic tie-breaking via `actor_id`. This ensures non-overlapping concurrent column updates are flawlessly preserved.

### 2. Deterministic Uniqueness Protocol

Pure CRDTs cannot enforce global uniqueness without coordination. We implemented an explicit post-merge deterministic resolution protocol to enforce `UNIQUE` constraints (e.g., on `users.email`):

- During `MaterializedView` building, duplicate values across active rows are identified.
- A deterministic tie-breaker (using `row_id` ordering) selects a "winner".
- The conflicting column value of the "loser" is deterministically mutated (e.g., appended with `#conflict#<row_id>`). This makes the loser recoverable by the application layer without losing the entire row's data.

### 3. Flexible Foreign-Key (FK) Policies

The engine supports explicitly declared foreign key policies under network partitions:

- `cascade`: Children of a deleted parent are recursively deleted.
- `tombstone`: Children survive; their foreign key column continues to reference the logically deleted parent (referentially live in CRDT metadata).
- `orphan`: Children survive; their foreign key column is explicitly set to `NULL` or a documented sentinel.

### 4. Bounded Metadata Growth 

Vector clocks and operation logs that grow indefinitely per write are a known failure mode of naive CRDTs.

- The engine implements continuous Garbage Collection via OpLog compaction (`compact()`).
- Compaction identifies the minimal set of "winning" operations that contribute to the current state (latest delete, insert, and update per cell) and discards all superseded historical operations.
- Storage overhead per row is strictly bounded by the number of distinct peers that have written to its cells.

---

## 🚀 Quickstart & Real-World Demo

### Installation

Ensure you have Python 3.9+ installed. Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
```

### Running the Real-World Collaborative Demo

Experience the engine in action using a real-world Project Management schema (`projects` and `tasks`) across three simulated distributed peers (`Lead_A`, `PM_B`, and `Dev_C`):

```bash
python demo_real_world.py
```

This interactive demo simulates concurrent offline project creation, task status updates, project cancellations, and a full peer-to-peer global synchronization loop resulting in 100% converged state.

---

## 🧪 Automated Test Suite

The repository is fully equipped with comprehensive automated unit and integration test suites validating CRDT merge semantics, garbage collection, unique index resolution, and foreign key conflict handling.

### Running All Automated Tests (Unit & Integration)

Execute the complete test suite using Python's built-in `unittest` framework (or `pytest`):

```bash
python -m unittest discover tests
```

### Running the Developer Self-Check

For rapid verification during active development, run the local self-check utility against our adapter:

```bash
python self_check.py --adapter adapters.myteam:Engine --fk-policy tombstone --quick
```

---

## 📊 Official Anvil L3 Benchmark Evaluation

The engine has been rigorously evaluated against the Anvil P-01 L3 Final Benchmark suite, testing extreme concurrency, chaos sync orderings, randomized property preservation, and high-density stress workloads.

### Running the L3 Benchmark Runner

To execute the official Anvil L3 evaluation suite and generate the submission report:

```bash
python run.py \
  --adapter adapters.myteam:Engine \
  --fk-policy tombstone \
  --out l3_report.json
```

### Validated Benchmark Results

Our CRDT Relational Engine achieves a validated L3 Final Score of **`0.9000 / 1.0000 (90.0%)`**.

#### Detailed Score Breakdown

| Evaluation Axis                | Score / Weight      | Status    | Details                                               |
| :----------------------------- | :------------------ | :-------- | :---------------------------------------------------- |
| **Core Score (L1/L2)**         | **1.0000 / 1.0000** | **100%**  | All core invariants passed                            |
| ├── Convergence                | 0.25                | Passed    | All peers agree on canonical hash                     |
| ├── Uniqueness (`users.email`) | 0.15                | Passed    | Live emails distinct across concurrent inserts        |
| ├── Foreign Key (`tombstone`)  | 0.10                | Passed    | Declared FK policy (`tombstone`) verified             |
| ├── Cell-Level Strict          | 0.20                | Passed    | Concurrent column updates correctly merged            |
| ├── Order-Invariance (Chaos)   | 0.10                | Passed    | Permuted sync orders produce identical state          |
| └── Randomized Invariants      | 0.15                | Passed    | Quiescence, idempotence, and preservation verified    |
| **Stretch Score (L3 Hard)**    | **0.7500 / 1.0000** | **75.0%** | 3 out of 4 stretch scenarios passed                   |
| ├── Composite Uniqueness       | 0.25                | Passed    | Multi-column constraints correctly enforced           |
| ├── High-Density Uniqueness    | 0.25                | Passed    | Deterministic tie-breaking under heavy contention     |
| ├── Long-Run Stress            | 0.25                | Passed    | Maintained integrity across 1,500 operations          |
| └── Multi-Level FK Chain       | 0.00                | Failed    | Multi-level cascade expectation vs tombstone mismatch |
| **Composite Final Score**      | **0.9000 / 1.0000** | **90.0%** | **(60% Core + 40% Stretch)**                          |

The complete benchmark execution log and detailed assertion traces are saved in `l3_report.json`.

---

## 📁 Project Folder Structure

```text
crdt-relational-engine/
├── adapters/
│   └── myteam.py             # CRDT Relational Engine Adapter interface
├── Anvil-P-E/                # Official Anvil Benchmark Protocol & Council Releases
│   ├── bench-p01-crdt/       # P-01 benchmark suite & harness
│   ├── L3_PROTOCOL.md        # L3 evaluation protocol specifications
│   └── README.md
├── config/                   # Configuration files
├── docs/                     # Documentation files
├── examples/                 # Example scripts and usage
├── scenarios/                # Benchmark test scenarios
│   ├── stretch/              # L3 stretch scenarios (composite, multi-fk, high-density, long-run)
│   ├── cell_level.py         # Pure concurrent column merge scenario
│   ├── chaos.py              # Permuted sync orderings scenario
│   ├── randomized.py         # Property-based random traces scenario
│   └── reference.py          # Canonical 3-peer scenario
├── scripts/                  # Utility scripts
├── src/                      # Core CRDT Relational Engine Implementation
│   ├── constraints/          # Primary Key, Unique Index, and FK conflict resolvers
│   ├── core/                 # System constants and error definitions
│   ├── crdt/                 # LWW-Element-Set CRDT and row merging logic
│   ├── engine/               # Database engine and bootstrap logic
│   ├── gc/                   # Garbage collector for tombstoned rows
│   ├── ops/                  # Insert, Update, Delete operation definitions
│   ├── query/                # Materialized views and Query executor
│   ├── replication/          # Replica manager and Peer state tracker
│   ├── schema/               # Table, Column, and FK schema definitions
│   └── storage/              # Append-only OpLog, RowStore, MetadataStore, TombstoneStore
├── tests/                    # Unit and Integration test suite
│   ├── fixtures/             # Test data fixtures
│   ├── integration/          # Integration test suites (partition merge, sync, etc.)
│   └── unit/                 # Unit test suites (CRDT merge, GC, OpLog, etc.)
├── adapter.py                # Base Adapter abstract class
├── assertions.py             # Benchmark invariant checkers
├── demo_real_world.py        # Real-world usage demo script
├── harness.py                # Benchmark test harness
├── l3_report.json            # Generated L3 benchmark report & score
├── network_server.py         # Distributed peer networking server
├── requirements.txt          # Python dependencies
├── run.py                    # Main benchmark runner script
├── self_check.py             # Engine self-verification script
└── writeup.md                # Architectural writeup
```

---

## 🏴‍☠️ Team & License

### Built by Pixel Pirates

Engineered for high-concurrency, partition tolerance, and seamless local-first collaboration.

```text
   ____  _          _   ____  _           _
  |  _ \(_)__  ____| | |  _ \(_)_ __ __ _| |_ ___ ___
  | |_) | |\ \/ / _ \ | | |_) | | '__/ _` | __/ _ \ __|
  |  __/| | >  <  __/ | |  __/| | | | (_| | ||  __/\__ \
  |_|   |_|/_/\_\___|_| |_|   |_|_|  \__,_|\__\___||___/

```

### License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

Copyright (c) 2026 **Pixel Pirates**
