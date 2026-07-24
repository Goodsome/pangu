from d4_automation.interfaces.cli.run_blue_gate import run_blue_gate
import typer

app = typer.Typer(
    name="d4-bot",
    help="D4 Robot CLI",
    add_completion=False,
)
app.command("blue-gate")(run_blue_gate)


def main():
    app()


if __name__ == "__main__":
    main()
