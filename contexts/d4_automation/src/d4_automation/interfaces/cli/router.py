import typer

from d4_automation.interfaces.cli.run_blue_gate import run_blue_gate

d4_automation_app = typer.Typer()

d4_automation_app.command("run-blue-gate")(run_blue_gate)