import json
import click
from src.engine.database import Database
from src.replication.replica import Replica
from src.replication.sync_manager import SyncManager
from src.cli.output import print_table

@click.group()
@click.option('--replica', default='a')
@click.option('--fk-policy', default='tombstone', type=click.Choice(['cascade','tombstone','orphan']))
@click.pass_context
def cli(ctx, replica, fk_policy):
    ctx.ensure_object(dict)
    ctx.obj['replica'] = replica
    ctx.obj['fk_policy'] = fk_policy

@cli.command()
@click.argument('table')
@click.argument('data_json')
@click.pass_context
def insert(ctx, table, data_json):
    db = Database(ctx.obj['replica'], fk_policy=ctx.obj['fk_policy'])
    db.insert(table, json.loads(data_json))
    print(f"[{ctx.obj['replica']}] inserted into {table}")

@cli.command()
@click.argument('table')
@click.argument('row_id')
@click.argument('data_json')
@click.pass_context
def update(ctx, table, row_id, data_json):
    db = Database(ctx.obj['replica'], fk_policy=ctx.obj['fk_policy'])
    db.update(table, row_id, json.loads(data_json))
    print(f"[{ctx.obj['replica']}] updated {table}:{row_id}")

@cli.command()
@click.argument('table')
@click.argument('row_id')
@click.pass_context
def delete(ctx, table, row_id):
    db = Database(ctx.obj['replica'], fk_policy=ctx.obj['fk_policy'])
    db.delete(table, row_id)
    print(f"[{ctx.obj['replica']}] deleted {table}:{row_id}")

@cli.command()
@click.argument('table')
@click.pass_context
def query(ctx, table):
    db = Database(ctx.obj['replica'])
    print_table(db.query(table), f"[{ctx.obj['replica']}] No live rows in {table}.")

@cli.command()
@click.argument('replica_a')
@click.argument('replica_b')
def sync(replica_a, replica_b):
    ra = Replica(replica_a)
    rb = Replica(replica_b)
    SyncManager().sync(ra, rb)
    Database(replica_a)
    Database(replica_b)
    print(f"Synced {replica_a} <-> {replica_b}")

@cli.command(name='sync-remote')
@click.argument('local_replica')
@click.argument('remote_replica')
@click.argument('remote_url')
def sync_remote(local_replica, remote_replica, remote_url):
    from src.network.client import NetworkClient
    client = NetworkClient(remote_url)
    client.sync(local_replica, remote_replica)
    Database(local_replica)
    print(f"Successfully synced local '{local_replica}' <-> remote '{remote_replica}' at {remote_url}")

@cli.command()
@click.argument('replica_id')
def gc(replica_id):
    db = Database(replica_id)
    print(f"[{replica_id}] GC complete. Tombstones removed: {db.gc()}")
