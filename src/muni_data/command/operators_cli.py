from rich.pretty import pretty_repr
from typer import Option, Typer
from muni_data.main import main
from muni_data.etl.utils import log_info

app = Typer(invoke_without_command=True)

@app.callback()
def operators():
    pipeline_status = main()
    if pipeline_status[1] == 200:
        log_info("Pipeline succeeded.")
    else:
        log_info("Pipeline failed.")