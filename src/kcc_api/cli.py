#!/usr/bin/python
"""
USAGE:
 kcc -s <address>
 kcc -p <plan_id>

"""

import logging
import argparse
from sys import argv, stderr

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.table import Table

from .plan import KCCPlan, Search

console = Console()


def show_search(address=None, name=None, description=None):
    results = Search(address=address, name=name, description=description)

    if not results:
        console.print("[yellow]No results found.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Date", style="dim", width=12)
    table.add_column("File No.", width=12)
    table.add_column("Address")
    table.add_column("Type", width=16)
    table.add_column("Decision", width=16)

    for p in results:
        table.add_row(
            p.DateReceived,
            str(p.FileNumber),
            " ".join(p.DevelopmentAddress).strip(),
            getattr(p, "Type", ""),
            getattr(p, "Decision", ""),
        )

    console.print(table)


def show_plan(plan_id):
    p = KCCPlan(int(plan_id))

    if not p:
        console.print(f"[red]No plan found for ID {plan_id}.[/red]")
        return

    p.fetch_attachments()

    address = " ".join(p.DevelopmentAddress).strip()
    metadata = (
        f"[bold]File No.:[/bold]     {p.FileNumber}\n"
        f"[bold]Date:[/bold]         {p.DateReceived}\n"
        f"[bold]Type:[/bold]         {getattr(p, 'Type', 'N/A')}\n"
        f"[bold]Decision:[/bold]     {getattr(p, 'Decision', 'N/A')}\n"
        f"[bold]Status:[/bold]       {getattr(p, 'ApplicationStatus', 'N/A')}\n"
        f"[bold]Applicant:[/bold]    {getattr(p, 'ApplicantName', 'N/A')}\n"
        f"[bold]Address:[/bold]      {address}\n"
        f"[bold]Description:[/bold]  {getattr(p, 'DevelopmentDescription', 'N/A')}"
    )
    console.print(Panel(metadata, title=f"Plan {p.FileNumber}", expand=False))

    if p.attachments:
        att_table = Table(show_header=True, header_style="bold cyan", title="Attachments")
        att_table.add_column("Comment", width=50, no_wrap=True)
        att_table.add_column("# Files", no_wrap=True)
        att_table.add_column("Size", width=10, no_wrap=True)
        att_table.add_column("Link", no_wrap=True)

        for a in p.attachments:
            att_table.add_row(
                a.comment.get("text", ""),
                a.num_files.get("text", ""),
                a.filesize.get("text", ""),
                a.link or "",
            )
        console.print(att_table)
    else:
        console.print("[yellow]No attachments found for this plan.[/yellow]")


def build_parser(prog) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog, description="Kildare CoCo planning CLI")
    p.add_argument("-n", "--name", metavar="QUERY", help="Search by Submitter Name")
    p.add_argument("-a", "--address", metavar="QUERY", help="Search by Address")
    p.add_argument("-d", "--description", metavar="QUERY", help="Search by Description")
    p.add_argument("-p", "--plan", metavar="QUERY", help="Search by Plan ID")
    p.add_argument("-v", "--verbose", action="store_true", help="Print each request URL as it is made")
    return p


def main(argv=None) -> int | None:
    parser = build_parser(prog="kcc")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        handlers=[RichHandler(show_path=False, show_time=False)],
    )

    # plan takes priority if provided
    if args.plan is not None:
        return show_plan(args.plan)

    # gather any provided search fields into one call
    search_kwargs = {
        k: v for k in ("address", "name", "description")
        if (v := getattr(args, k, None)) is not None
    }
    if search_kwargs:
        return show_search(**search_kwargs)

    # no command given -> show help and use a non-zero exit
    build_parser(prog="kcc").print_help(stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(argv))
