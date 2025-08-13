#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup as bs


class Endpoint:
    def __init__(
        self, url: str, method: str = "GET", headers: dict = {}, params: dict = {}
    ):
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params

    def make_request(self):
        return requests.request(
            method=self.method, url=self.url, headers=self.headers, params=self.params
        )


class AddressSearchEndpoint(Endpoint):
    def __init__(self, name: str, address: str, description: str):
        self.url = "http://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileNameAddressResult"
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

        self.url = "https://idocsweb.kildarecoco.ie/iDocsWebDPSS/listFiles.aspx"
        super().__init__(self.url, params=self.params, headers=self.headers)


class PlanningFileEndpoint(Endpoint):
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.url = (
            "http://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileResult"
        )
        self.attachments = None
        super().__init__(self.url, params={"id": self.plan_id})

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


class AttachmentHTMLParser:
    def __init__(self, content: str):
        self.data = self._parsehtml(content)

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
        self.type = datadict["type"]
        self.comment = datadict["comment"]
        self.files = datadict["files"]
        self.size = datadict["size"]
        self.jpeg = datadict["jpeg"]
        self.djvu = datadict["djvu"]
        self.base_url = "https://idocsweb.kildarecoco.ie/iDocsWebDPSS/"
        self.link = self.djvu.get("url", None)
        self.link_url = self.base_url + self.link if self.link else None

    def __str__(self):
        return f"<Attachment: [{self.type.get('text', 'None')}: {self.comment.get('text', 'None')}] (link: {self.link_url})>"


class KCCPlan:
    def __init__(self, plan_id: int):
        self.endpoint = PlanningFileEndpoint(plan_id)
        self.request = self.endpoint.make_request()
        if self.request.ok:
            self.data = self.request.json()
        else:
            self.data = None

    def __str__(self):
        return f"<KCCPlan: {self.data.get('FileNumber')} [{' '.join(self.data.get('DevelopmentAddress'))}]>"


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
