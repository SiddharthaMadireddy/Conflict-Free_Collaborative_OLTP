#!/bin/bash
python src/main.py --replica a insert users '{"id":"u1","username":"alice","name":"Alice"}'
python src/main.py --replica a insert users '{"id":"u2","username":"bob","name":"Bob"}'
python src/main.py sync a b
