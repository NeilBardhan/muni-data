import typer
from muni_data import __app_name__, __version__

app = typer.Typer(
    add_completion=False,
    invoke_without_command=True,
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

def _version_callback(value):
    if value:
        typer.echo("{a} v{v}".format(a = __app_name__, v = __version__))
        raise typer.Exit()

@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
    version = typer.Option(
        None,
        '--version',
        '-v',
        help= "Show the application's version and exit.",
        callback=_version_callback,
        is_eager=True,
    )
):
    return