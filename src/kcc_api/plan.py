#!/usr/bin/python3
import logging
import requests
import time  # used by make_request() retry logic
from datetime import datetime
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin


logger = logging.getLogger(__name__)


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
        self, url: str, method: str = "GET", headers: dict | None = None, params: dict | None = None
    ):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.params = params or {}

    @property
    def request(self) -> requests.PreparedRequest:
        return requests.Request(
            method=self.method, url=self.url, headers=self.headers, params=self.params
        ).prepare()

    def make_request(self) -> requests.Response:
        prepared = self.request
        logger.debug("[%s] %s", self.method, prepared.url)
        with requests.Session() as s:
            response = s.send(prepared)
            while response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2))
                logger.debug("[429] Rate limited, retrying in %ss...", retry_after)
                time.sleep(retry_after)
                response = s.send(prepared)
        logger.debug("[%s] %s", response.status_code, prepared.url)
        return response

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url!r}, method={self.method!r})"

    def __str__(self):
        return f"<{self.__class__.__name__}: [{self.method}] {self.url}>"

    def sanitize(self, item: str | None):
        return item.replace(' ', '+') if item else ""


class AddressSearchEndpoint(Endpoint):
    def __init__(self, name: str | None, address: str | None, description: str | None, start_date: datetime | None = None, end_date: datetime | None = None):
        self.url = KCCURL.address_search
        super().__init__(
            self.url,
            params={
                "name": self.sanitize(name),
                "address": self.sanitize(address),
                "devDesc": self.sanitize(description),
                "startDate": start_date.strftime("%d/%m/%Y") if start_date else "",
                "endDate": end_date.strftime("%d/%m/%Y") if end_date else "",
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

    def __getitem__(self, index):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"AttachmentHTMLParser({self._data!r})"

    def __str__(self):
        return f"<AttachmentHTMLParser: {len(self._data)} attachment(s)>"

    def extract_text_and_link(self, block: str):
        text = block.get_text()
        url = block.a["href"] if block.a else None
        return {"text": text, "url": url}

    def _parsehtml(self, content: str):
        soup = bs(content, features="html.parser")
        headers = ["comment", "num_files", "filesize", "size", "jpeg", "djvu"]
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
            if media in self:
                self._link = getattr(self, media).get("url", None)
                return urljoin(self.base_url, self._link) if self._link else None
        return None

    def __iter__(self):
        return iter(self._datadict.keys())

    def __contains__(self, k):
        return k in self._datadict

    def __getattr__(self, k):
        if k in self._datadict:
            return self._datadict[k]
        raise AttributeError(k)

    def to_json(self):
        return {
            "comment": self.comment.get("text"),
            "num_files": self.num_files.get("text"),
            "filesize": self.filesize.get("text"),
            "link": self.link,
        }

    def __repr__(self):
        return f"Attachment({self._datadict!r})"

    def __str__(self):
        return f"<Attachment: [{self.comment.get('text', 'None')} ({self.num_files.get('text', 'None')} files)] ({self.link})>"


class KCCPlan:
    def __init__(self, plan_id: int, data: dict | None = None):
        self.plan_id = plan_id
        self.attachments = None
        if data is not None:
            if isinstance(data.get("DevelopmentAddress"), str):
                data["DevelopmentAddress"] = [data["DevelopmentAddress"]]
            self.data = data
        else:
            self.endpoint = PlanningFileEndpoint(self.plan_id)
            request = self.endpoint.make_request()
            self.data = request.json() if request.ok else None

    def __getattr__(self, k):
        if self.data is not None and k in self.data:
            return self.data[k]
        raise AttributeError(k)

    def __bool__(self):
        return self.data is not None

    @property
    def date_received(self) -> datetime | None:
        if self.data is None:
            return None
        return datetime.strptime(self.DateReceived, "%d/%m/%Y")

    def __eq__(self, other):
        if isinstance(other, KCCPlan):
            return self.plan_id == other.plan_id
        if isinstance(other, int):
            return self.plan_id == other
        return NotImplemented

    def __hash__(self):
        return hash(self.plan_id)

    def __repr__(self):
        return f"KCCPlan(plan_id={self.plan_id!r})"

    def __str__(self):
        return f"<KCCPlan: ({self.DateReceived}) [{self.data.get('FileNumber')}] {' '.join(self.DevelopmentAddress).strip()}>"

    def fetch_attachments(self):
        plan_attachments_endpoint = PlanningAttachmentsEndpoint(self.plan_id)
        plan_attachments_request = plan_attachments_endpoint.make_request()
        if plan_attachments_request.ok:
            raw_request_data = plan_attachments_request.text
            self.attachments = AttachmentHTMLParser(raw_request_data)
            return True
        else:
            return False

    def to_json(self):
        return {"data": self.data, "attachments": [x.to_json() for x in self.attachments] if self.attachments else []}


class Search:
    def __init__(self, name: str = None, address: str = None, description: str = None, start_date: datetime | None = None, end_date: datetime | None = None):
        self.endpoint = AddressSearchEndpoint(name, address, description, start_date, end_date)
        self._data = []
        self._fetch()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __getitem__(self, index):
        return self._data[index]

    def __contains__(self, item):
        return item in self._data

    def to_json(self):
        return [p.to_json() for p in self._data]

    def __repr__(self):
        return f"Search({self._data!r})"

    def __str__(self):
        return f"<Search: {len(self._data)} result(s)>"

    def _fetch(self):
        request = self.endpoint.make_request()
        results = request.json()
        self._data = [KCCPlan(p["FileNumber"], data=p) for p in results]
        self._data.sort(key=lambda obj: obj.date_received or datetime.min)

