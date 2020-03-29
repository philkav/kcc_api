#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs
import json
from tabulate import tabulate

def get_html(catalog, planning_id):
    url = f"http://idocsweb.kildarecoco.ie/iDocsWebDPSS/listFiles.aspx?catalog={catalog}&id={planning_id}"
    r = requests.get(url)
    return r.content

def doc_data(docline):
    datablock = docline.find_all('td')
    headers = ['type', 'comment', 'files', 'size']
    return dict(zip(headers, [ str(x.get_text()) for x in datablock[0:4] ]))

def extract_from_html(html_data):
    soup = bs(html_data, features='html.parser')
    docs = [] 
    for doc in soup.find(id="DocumentsDG").find_all('tr'):
        docs.append(doc_data(doc))
    return docs

def list_files(catalog, planning_id):
    html_data = get_html(catalog, planning_id)
    data = extract_from_html(html_data)
    return data


if __name__ == '__main__':
    """ CLI USAGE: planner.py PLANNING_ID """
    from sys import argv
    catalog = 'planning'
    planning_id = 20162
    if len(argv) > 1:
        planning_id = argv[1]

    print(f"Checking planning for {planning_id}")

    file_info = list_files(catalog, planning_id)
    headers = file_info[0].values()
    print(tabulate([ x.values() for x in file_info[1:] ], headers=headers))


    """
    Host: idocsweb.kildarecoco.ie
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Cookie: ASP.NET_SessionId=11ef23h4d0hpsb0lvazlfiyn
    Upgrade-Insecure-Requests: 1
    Cache-Control: max-age=0
    """
