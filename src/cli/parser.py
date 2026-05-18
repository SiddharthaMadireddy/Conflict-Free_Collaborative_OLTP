import click

def common_options(func):
    func = click.option('--fk-policy', default='tombstone', type=click.Choice(['cascade', 'tombstone', 'orphan']))(func)
    func = click.option('--replica', default='a')(func)
    return func
