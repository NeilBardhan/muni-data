import typer
from typing import Optional
from muni_data import __app_name__, __version__
from .operators_cli import app as operators_app

app = typer.Typer()

app.add_typer(operators_app, name="operators")

def _version_callback(value):
    if value:
        typer.echo("{a} v{v}".format(a = __app_name__, v = __version__))
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        '--version',
        '-v',
        help= "Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
):
    return
