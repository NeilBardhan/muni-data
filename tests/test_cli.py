from typer.testing import CliRunner
from muni_data import __app_name__, __version__
from muni_data.command import cli

runner = CliRunner()

def test_version():
    result = runner.invoke(cli.app, ["--version", "True"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout