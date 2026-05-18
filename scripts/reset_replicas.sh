#!/bin/bash
rm -rf data/replica_a data/replica_b
mkdir -p data/replica_a/{oplog,snapshots,indexes}
mkdir -p data/replica_b/{oplog,snapshots,indexes}
echo "Replicas reset."
