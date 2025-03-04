
import click
from maamgr.core import MaaMgr
from pprint import pprint
@click.group(invoke_without_command=True)
@click.argument("name", type=str, required=False)
@click.option("-u", "--update", is_flag=True, help="Check for update")
@click.pass_context
def cli(ctx, name, update):
    MaaMgr.init(auto_update=update)
    if name:
        ctx.obj = MaaMgr(name)

@cli.command()
@click.pass_context
def cat(ctx):
    maamgr : MaaMgr = ctx.obj
    pprint(maamgr.pkg.cat())

@cli.command()
@click.argument("path", type=str)
@click.pass_context
def start(ctx, path):
    maamgr : MaaMgr = ctx.obj
    maamgr.call(path)

@cli.command()
@click.argument("args", type=str, nargs=-1)
@click.pass_context
def patch(ctx, args):
    print(args)
    for arg in args:
        if "->" not in arg:
            raise click.UsageError("Invalid argument: " + arg + " <must be in the format 'source->destination'>")

    maamgr : MaaMgr = ctx.obj
    maamgr.patchfile(*args)

@cli.command()
@click.argument("path", type=str)
@click.argument("key", type=str)
@click.argument("value", type=str)
@click.pass_context
def kv(ctx, path, key, value):
    maamgr : MaaMgr = ctx.obj
    maamgr.patchValue(path, key, value)

if __name__ == "__main__":
    cli()
