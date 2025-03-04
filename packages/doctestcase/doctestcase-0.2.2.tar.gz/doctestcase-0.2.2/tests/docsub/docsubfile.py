from docsub import click
from doctestcase import to_markdown
from importloc import Location


@click.group()
def x() -> None:
    pass


@x.command()
@click.argument('case')
def case(case: str) -> None:
    text = to_markdown(Location(case).load(), title_depth=2)
    click.echo(text, nl=False)
