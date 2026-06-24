from typing import Annotated
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from rich.console import Console
from typer import Argument
from codegen.code_metadata.application.dtos.dev_progress import DevProgress
from code_dom.application.dtos.file_metrics import FileMetrics
from codegen.code_metadata.application.queries.get_dev_progress import (
    GetDevProgressHandler,
)
from codegen.code_metadata.application.queries.get_dev_progress import (
    GetDevProgressQuery,
)

console = Console()


@inject
def _get_dev_progress(
    module_fqn: str,
    service: GetDevProgressHandler = Provide[
        "code_metadata_container.get_dev_progress"
    ],
) -> DevProgress:
    return service.execute(query=GetDevProgressQuery(module_fqn=module_fqn))


def get_dev_progress(fqn: Annotated[str, Argument()] = "codegen") -> None:
    """Show development progress: AST similarity and line diffs per file."""
    result = _get_dev_progress(module_fqn=fqn)
    result.order_by_type()
    if not result.records:
        console.print("[yellow]No component records found.[/yellow]")
        return
    console.print(
        f"  {'File':<40} {'Type':<20} {'AST':>6} {'Orig':>6} {'Gen':>6} {'Diff':>6}"
    )
    console.print("  " + "-" * 76)
    match_count = 0
    unknown_count = 0
    unmatch_records: list[FileMetrics] = []
    for r in result.records:
        if r.ast_similarity == 1:
            match_count += 1
            continue
        unmatch_records.append(r)
        if r.component_type == "unknown":
            unknown_count += 1
        diff_sign = "+" if r.line_diff > 0 else ""
        console.print(
            f"  {r.file_name:<40} {r.component_type:<20} "
            + f"{r.ast_similarity:>5.1%} {r.original_lines:>6} "
            + f"{r.generated_lines:>6} {diff_sign}{r.line_diff:>5}"
        )
    console.print(
        "\n[bold]Dev Progress[/bold]  |  "
        + f"Matched Files: {match_count}/{len(result.records)}  |  "
        + f"AST Similarity: {result.ast_progress:.1%}  |  "
        + f"Unknown Files: {unknown_count}/{len(result.records)}"
    )
    if len(unmatch_records) == 1:
        record = unmatch_records[0]
        console.print(f"  {record.file_name:<40} {record.component_type:<20} ")
        console.print("-" * 76)
        console.print(f"{record.original_code}")
        console.print("-" * 76)
        console.print(f"{record.generated_code}")
        console.print("-" * 76)
