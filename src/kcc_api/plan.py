#!/usr/bin/python3
import requests
import json
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin


class KCCURL:
    ## Planning Enquiries
    planning_file = (
        "http://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileResult"
    )
    address_search = "http://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileNameAddressResult"

    ## File Search
    attachment_search = "https://idocsweb.kildarecoco.ie/iDocsWebDPSS/listFiles.aspx"
    attachment_filedir = "https://idocsweb.kildarecoco.ie/iDocsWebDPSS/"


class Endpoint:
    def __init__(
        self, url: str, method: str = "GET", headers: dict = {}, params: dict = {}
    ):
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params

    @property
    def request(self) -> requests.Request:
        return requests.Request(
            method=self.method, url=self.url, headers=self.headers, params=self.params
        ).prepare()

    def make_request(self) -> requests.Response:
        with requests.Session() as s:
            return s.send(self.request)


class AddressSearchEndpoint(Endpoint):
    def __init__(self, name: str, address: str, description: str):
        self.url = KCCURL.address_search
        super().__init__(
            self.url,
            params={
                "name": name,
                "address": address,
                "devDesc": description,
                "startDate": "",
                "endDate": "",
            },
        )


class PlanningAttachmentsEndpoint(Endpoint):
    def __init__(self, plan_id: int, catalog: str = "planning"):
        self.plan_id = plan_id
        self.catalog = catalog

        self.params = {"catalog": self.catalog, "id": self.plan_id}
        self.headers = {"User-Agent": "Mozilla/5.0"}

        self.url = KCCURL.attachment_search
        super().__init__(self.url, params=self.params, headers=self.headers)


class PlanningFileEndpoint(Endpoint):
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.url = KCCURL.planning_file

        super().__init__(self.url, params={"id": self.plan_id})


class AttachmentHTMLParser:
    def __init__(self, content: str):
        self._data = self._parsehtml(content)

    def __iter__(self):
        return iter(self._data)

    def extract_text_and_link(self, block: str):
        text = block.get_text()
        url = block.a["href"] if block.a else None
        return {"text": text, "url": url}

    def _parsehtml(self, content: str):
        soup = bs(content, features="html.parser")
        headers = ["type", "comment", "files", "size", "jpeg", "djvu"]
        data = []
        for doc in soup.find(id="DocumentsDG").find_all("tr"):
            datablock = doc.find_all(
                "td"
            )  ## Remove 1st item as it's just the column headings
            if len(datablock) > 1:
                d = dict(
                    zip(headers, [self.extract_text_and_link(x) for x in datablock[1:]])
                )
                data.append(Attachment(d))
        return data


class Attachment:
    def __init__(self, datadict: dict):
        self._datadict = datadict
        self.base_url = KCCURL.attachment_filedir

    @property
    def link(self):
        for media in ["djvu", "jpeg"]:
            if media in list(self):
                self._link = getattr(self, media).get("url", None)
                return urljoin(self.base_url, self._link) if self._link else None
        return None

    def __iter__(self):
        return iter(self._datadict.keys())

    def __getattr__(self, k):
        if k in self._datadict.keys():
            return self._datadict.get(k)
        raise KeyError

    def __str__(self):
        return f"<Attachment: [{self.type.get('text', 'None')}: {self.comment.get('text', 'None')}] ({self.link})>"


class KCCPlan:
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.endpoint = PlanningFileEndpoint(self.plan_id)
        self.request = self.endpoint.make_request()
        self.attachments = None
        if self.request.ok:
            self.data = self.request.json()
        else:
            self.data = None

    def __str__(self):
        return f"<KCCPlan: {self.data.get('FileNumber')} [{' '.join(self.data.get('DevelopmentAddress'))}]>"

    def fetch_attachments(self):
        plan_attachments_endpoint = PlanningAttachmentsEndpoint(self.plan_id)
        plan_attachments_request = plan_attachments_endpoint.make_request()
        if plan_attachments_request.ok:
            raw_request_data = plan_attachments_request.text
            self.attachments = AttachmentHTMLParser(raw_request_data)
            return True
        else:
            print(f"No attachments found for plan {str(self.plan_id)}")
            return None

    def to_json(self):
        return {"data": self.data, "attachments": [ x for x in self.attachments ]}


class Search:
    pass


def search(name: str = "", address: str = "", description: str = ""):
    """Returns a list of Plan Objects"""
    name = name.replace(" ", "+")
    address = address.replace(" ", "+")
    description = description.replace(" ", "+")

    address_search_endpoint = AddressSearchEndpoint(name, address, description)
    request = address_search_endpoint.make_request()
    if request.ok:
        return [KCCPlan(p["FileNumber"]) for p in request.json()]

    return None
