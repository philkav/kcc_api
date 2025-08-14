#!/usr/bin/python
"""

USAGE:   uv run python main.py <PLANID> <PLANID>
EXAMPLE: uv run python main.py 20162

"""

from plan import KCCPlan, search
import json
from sys import argv

show_search = True
show_plans = True


def showcase_search():
    ### Showcase the search function
    print("\n=== Showcasing the Search function ===")
    for p in search(address="Westfield"):
        print(p)


def showcase_plans(args):
    ### Display the data for any planids that were passed
    print("\n=== Showcasing the Plan Class ===")
    for i in args:
        # Instantiate the Plan (Makes a network request)
        x = KCCPlan(int(i))

        # Load the attachments (Makes another network request)
        x.fetch_attachments()

        # Display the Plan Metadata
        print(json.dumps(x.data, indent=4))

        # Display the Plan Attachments
        for item in x.attachments:
            print(item)


def main(args):
    if show_search:
        showcase_search()

    if show_plans:
        showcase_plans(argv[1:])


if __name__ == "__main__":
    main(argv)
