#!/usr/bin/python
"""

USAGE:   uv run python main.py <PLANID> <PLANID>
EXAMPLE: uv run python main.py 20162

"""

from .plan import KCCPlan, search
from sys import argv, stderr
import json
import argparse

show_search = True
show_plans = True


def show_search(address):
    ### Showcase the search function
    for p in search(address=address):
        print(p)


def show_plan(plan_id):
    ### Display the data for any planids that were passed
    # Instantiate the Plan (Makes a network request)
    x = KCCPlan(int(plan_id))

    # Load the attachments (Makes another network request)
    x.fetch_attachments()

    # Display the Plan Metadata
    print(json.dumps(x.data, indent=4))

    # Display the Plan Attachments
    for item in x.attachments:
        print(item)

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="kcc_api", description="Kildare CoCo planning CLI")
    p.add_argument("-s", "--search", metavar="QUERY", help="Search by address or keyword")
    p.add_argument("-p", "--plan", metavar="QUERY", help="Search by Plan ID")
    return p

def main(argv=None) -> int:
    args = build_parser().parse_args(argv[1:])

    if args.search is not None:
        return show_search(args.search)

    if args.plan is not None:
        return show_plan(args.plan)

    # no command given -> show help and use a non-zero exit
    build_parser().print_help(stderr)
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
