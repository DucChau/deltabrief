"""Click CLI entry point for deltabrief."""
from __future__ import annotations
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

import click

from .parser import load_commits
from .hotspots import compute_hotspots
from .heatmap import compute_heatmap
from .renderer import render_terminal, render_markdown


@click.group()
@click.version_option()
def main():
    """deltabrief — generate a structured git briefing from your commit history."""


@main.command()
@click.argument("repo_path", default=".", type=click.Path(exists=True))
@click.option("--since", default="yesterday", help="Lookback: 'yesterday', '3d', '1w', or ISO date")
@click.option("--branch", default=None, help="Branch to analyze (default: current)")
@click.option("--author", default=None, help="Filter to a specific author")
@click.option("--top", default=10, help="Number of hotspot files to show")
def brief(repo_path, since, branch, author, top):
    """Generate a rich terminal briefing from git history."""
    since_dt = _parse_since(since)
    commits = load_commits(repo_path, since_dt, branch=branch, author=author)
    if not commits:
        click.echo(f"No commits found since {since_dt.strftime('%Y-%m-%d %H:%M')}.")
        sys.exit(0)
    hotspots = compute_hotspots(commits, top=top)
    heatmap = compute_heatmap(commits)
    render_terminal(commits, hotspots, heatmap, since_dt)


@main.command()
@click.argument("repo_path", default=".", type=click.Path(exists=True))
@click.option("--since", default="yesterday")
@click.option("--output", default="briefing.md", help="Output Markdown file path")
@click.option("--top", default=10)
def export(repo_path, since, output, top):
    """Export a Markdown briefing to a file."""
    since_dt = _parse_since(since)
    commits = load_commits(repo_path, since_dt)
    if not commits:
        click.echo("No commits found.")
        sys.exit(0)
    hotspots = compute_hotspots(commits, top=top)
    heatmap = compute_heatmap(commits)
    md = render_markdown(commits, hotspots, heatmap, since_dt)
    Path(output).write_text(md)
    click.echo(f"Briefing written to {output}")


@main.command()
@click.argument("repo_path", default=".", type=click.Path(exists=True))
@click.option("--since", default="1w")
def authors(repo_path, since):
    """Show author contribution heat map."""
    since_dt = _parse_since(since)
    commits = load_commits(repo_path, since_dt)
    heatmap = compute_heatmap(commits)
    from rich.console import Console
    from rich.table import Table
    console = Console()
    table = Table(title=f"Author Contributions since {since_dt.strftime('%Y-%m-%d')}")
    table.add_column("Author", style="cyan")
    table.add_column("Commits", justify="right", style="green")
    table.add_column("Types", style="yellow")
    for author_name, data in sorted(heatmap.items(), key=lambda x: -x[1]["count"]):
        types_str = ", ".join(f"{k}:{v}" for k, v in sorted(data["types"].items(), key=lambda x: -x[1]))
        table.add_row(author_name, str(data["count"]), types_str)
    console.print(table)


def _parse_since(since: str):
    """Parse a since string into a timezone-aware datetime."""
    now = datetime.now(tz=timezone.utc)
    since = since.strip().lower()
    if since == "yesterday":
        return (now - timedelta(days=1)).replace(hour=0, minute=0, second=0)
    if since.endswith("d"):
        return now - timedelta(days=int(since[:-1]))
    if since.endswith("w"):
        return now - timedelta(weeks=int(since[:-1]))
    if since.endswith("h"):
        return now - timedelta(hours=int(since[:-1]))
    try:
        dt = datetime.fromisoformat(since)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        raise click.BadParameter(f"Cannot parse since value: {since}")
