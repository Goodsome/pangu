import typer
from codegen.bootstrap.logging import setup_cli_logging
from codegen.bootstrap.setup import create_container
from codegen.code_metadata.interfaces.cli.get_directory_tree import get_directory_tree
from codegen.code_metadata.interfaces.cli.delete_component import delete_component
from codegen.code_metadata.interfaces.cli.ingest_project import ingest_project
from codegen.code_metadata.interfaces.cli.generate_code import generate_code
from codegen.code_metadata.interfaces.cli.get_dev_progress import get_dev_progress
from codegen.code_metadata.interfaces.cli.list_components import list_components
from codegen.code_metadata.interfaces.cli.reverse_code import reverse_code
from codegen.code_metadata.interfaces.cli.get_component import get_component
from codegen.code_metadata.interfaces.cli.get_module import get_module
from codegen.code_metadata.interfaces.cli.list_modules import list_modules
from codegen.code_metadata.interfaces.cli.get_code_node import get_code_node
from codegen.code_metadata.interfaces.cli.list_unused_nodes import list_unused_nodes
from codegen.code_metadata.interfaces.cli.trace import trace
from codegen.code_dom.interfaces.cli.get_file_document import get_file_document

app.command()(scaffold)
app.command()(reverse)
app.command()(schema)
app.command()(init)
app.command()(generate_code)
app.command()(get_dev_progress)
app.command()(reverse_code)
app.command()(list_components)
app.command()(get_component)
app.command()(get_module)
app.command()(list_modules)
app.command()(delete_component)
app.command()(ingest_project)
app.command()(get_file_document)
app.command()(get_code_node)
app.command()(list_unused_nodes)
app.command(name="tree")(tree_cmd)
app.command(name="trace")(trace)
