#!/usr/bin/python
"""
USAGE:
 kcc -s <address>
 kcc -p <plan_id>

"""

from .plan import KCCPlan, search
from sys import argv, stderr
import json
import argparse


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


def build_parser(prog) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog, description="Kildare CoCo planning CLI")
    p.add_argument(
        "-s", "--search", metavar="QUERY", help="Search by address or keyword"
    )
    p.add_argument("-p", "--plan", metavar="QUERY", help="Search by Plan ID")
    return p


def main(argv=None) -> int:
    parser = build_parser(prog="kcc")
    args = parser.parse_args(argv)

    if args.search is not None:
        return show_search(args.search)

    if args.plan is not None:
        return show_plan(args.plan)

    # no command given -> show help and use a non-zero exit
    build_parser().print_help(stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(argv))
