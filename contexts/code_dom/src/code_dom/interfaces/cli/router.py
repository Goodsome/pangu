import typer
from code_dom.interfaces.cli.listen import listen

code_dom_app = typer.Typer(name="code_dom", help="code document object model")
code_dom_app.command("listen")(listen)
