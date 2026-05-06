from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_review_agent.engine import ReviewEngine
from ai_review_agent.models import ReviewRequest

app = typer.Typer(help="Pre-review AI project applications before formal submission.")
console = Console()


@app.command()
def review(
    file: Annotated[
        str,
        typer.Argument(help="Path to a proposal markdown/text file. Use '-' to read stdin."),
    ],
    title: Annotated[str, typer.Option(help="Optional project title.")] = "",
    token_plan: Annotated[str, typer.Option(help="Optional token plan.")] = "",
    grant_plan: Annotated[str, typer.Option(help="Optional grant or budget plan.")] = "",
    target_users: Annotated[str, typer.Option(help="Optional target users.")] = "",
) -> None:
    """Review a proposal and print a scorecard."""
    description = _read_input(file)
    result = ReviewEngine().review(
        ReviewRequest(
            title=title,
            description=description,
            token_plan=token_plan,
            grant_plan=grant_plan,
            target_users=target_users,
        )
    )

    console.print(
        Panel.fit(
            f"[bold]Overall score:[/bold] {result.overall_score}/100\n"
            f"[bold]Readiness:[/bold] {result.readiness.value}",
            title="AI Review Agent",
        )
    )

    table = Table(title="Dimension Scores")
    table.add_column("Dimension")
    table.add_column("Score", justify="right")
    table.add_column("Summary")
    for score in result.dimension_scores:
        table.add_row(score.name, str(score.score), score.summary)
    console.print(table)

    if result.issues:
        console.print("\n[bold yellow]Issues[/bold yellow]")
        for issue in result.issues:
            console.print(f"- [{issue.severity}] {issue.dimension}: {issue.message}")

    if result.suggestions:
        console.print("\n[bold cyan]Suggestions[/bold cyan]")
        for suggestion in result.suggestions:
            console.print(f"- {suggestion.dimension}: {suggestion.action}")

    console.print("\n[bold green]Rewritten Submission[/bold green]")
    console.print(result.rewritten_submission)


def _read_input(file: str) -> str:
    if file == "-":
        return typer.get_text_stream("stdin").read()
    return Path(file).read_text(encoding="utf-8")


@app.command()
def version() -> None:
    """Print the package version."""
    console.print("ai-review-agent 0.1.0")


if __name__ == "__main__":
    app()
