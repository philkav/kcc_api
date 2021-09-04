#!/usr/bin/env/python3
import requests
import json
import Plan

def search_by_address(search_term):
    """

        Returns a list of dicts of format:
        "FileNumber"
        "LocalAuthority"
        "DateReceived"
        "Type"
        "SubmissionsBy"
        "DueDate"
        "Decision"
        "DecisionDateMO"
        "ApplicationStatus"
        "GrantDate"
        "FurtherInfoRequested"
        "FurtherInfoReceived"
        "ReportFileLocation"
        "ApplicantName"
        "DevelopmentDescription":
    """

    print(f"Searching Term: {search_term}")
    search_term=search_term.replace(' ','+')
    Address_Search_URL = f"http://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileNameAddressResult?name=&address={search_term}&devDesc=&startDate=&endDate="
    r = requests.get(Address_Search_URL)
    if r.status_code == 200:
        return r.json()
    else:
        return None

if __name__ == "__main__":
    from sys import argv
    d = search_by_address(" ".join(argv[1:]))
    # print(json.dumps(d, indent=4))
    for entry in d:
        # print(f"{entry['FileNumber']:<10} {entry['ApplicantName']:<40} {entry['DevelopmentDescription'][:180]}")
        p = Plan.Plan(entry['FileNumber'])
        print(p)




