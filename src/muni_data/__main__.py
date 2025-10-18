from muni_data.command.cli import app
from muni_data import __app_name__

def main():
    app(prog_name=__app_name__)

if __name__ == '__main__':
    main()