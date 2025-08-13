from plan import KCCPlan, search
import json
from sys import argv


def main(args):
    ### Showcase the search function
    for p in search(address="Westfield"):
        print(p)

    ### Display the data for any planids that were passed
    for i in args[1:]:
        x = KCCPlan(int(i))
        x.endpoint.fetch_attachments()
        print(json.dumps(x.data, indent=4))
        for item in x.endpoint.attachments.data:
            print(item)


if __name__ == "__main__":
    main(argv)
