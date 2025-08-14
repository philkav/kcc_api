#!/usr/bin/python
"""
USAGE:
 kcc -s <address>
 kcc -p <plan_id>

"""

from .plan import KCCPlan, Search
from sys import argv, stderr
import json
import argparse


def show_search(address=None, name=None, description=None):
    ### Showcase the search class
    for p in Search(address=address, name=name, description=description):
        print(p)


def show_plan(plan_id):
    ### Display the data for any planids that were passed
    # Instantiate the Plan (Makes a network request)
    x = KCCPlan(int(plan_id))

    # Load the attachments (Makes another network request)
    x.fetch_attachments()

    # Display the Plan Metadata and attachments
    print(json.dumps(x.to_json(), indent=4, default=str))


def build_parser(prog) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog, description="Kildare CoCo planning CLI")
    p.add_argument("-n", "--name", metavar="QUERY", help="Search by Submitter Name")
    p.add_argument("-a", "--address", metavar="QUERY", help="Search by Address")
    p.add_argument("-d", "--description", metavar="QUERY", help="Search by Description")
    p.add_argument("-p", "--plan", metavar="QUERY", help="Search by Plan ID")
    return p


def main(argv=None) -> int | None:
    parser = build_parser(prog="kcc")
    args = parser.parse_args(argv)


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
