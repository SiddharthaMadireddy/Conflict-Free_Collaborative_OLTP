#!/bin/bash
set -e
bash scripts/reset_replicas.sh
python src/main.py --replica a --fk-policy tombstone insert users '{"id":"u1","username":"alice","name":"Alice"}'
python src/main.py sync a b
python src/main.py --replica a --fk-policy tombstone delete users u1
python src/main.py --replica b --fk-policy tombstone insert posts '{"id":"p1","user_id":"u1","title":"Hello World","body":"My first post"}'
python src/main.py sync a b
python src/main.py --replica a query users
python src/main.py --replica a query posts
python src/main.py gc a
