#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs

"""

>>> import Plan
>>> import json
>>> x = Plan.Plan('20162')
>>> print(json.dumps(x.__dict__, indent=4))
"""

class Plan:
    def __init__(self, plan_id):
        self.plan_id = plan_id
        self.entries = list_files('planning', self.plan_id)

def get_html(catalog, planning_id):
    url = f"http://idocsweb.kildarecoco.ie/iDocsWebDPSS/listFiles.aspx?catalog={catalog}&id={planning_id}"
    r = requests.get(url)
    return r.content

def text_and_link(x):
    
    try:
        text = x.get_text()
    except TypeError:
        text = None

    try:
        link = x.a['href']
    except (TypeError, AttributeError):
        link = None

    return { 'text': text, 'link': link }

def doc_data(docline):
    datablock = docline.find_all('td')
    headers = ['type', 'comment', 'files', 'size', 'jpeg', 'djvu']
    return dict(zip(headers, [ text_and_link(x) for x in datablock ]))

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
