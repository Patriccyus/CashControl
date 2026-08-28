import sys


def main() -> None:
    if "--cli" in sys.argv:
        from app.interface.cli import main as iniciar_cli

        iniciar_cli()
    else:
        from app.interface.gui_app import main as iniciar_gui

        iniciar_gui()


if __name__ == "__main__":
    main()
