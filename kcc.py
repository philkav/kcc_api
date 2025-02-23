import requests
import json
from datetime import datetime
from typing import Optional, Dict, TypedDict
from rich.console import Console
from rich.table import Table


class PlanningResult(TypedDict):
	FileNumber: str
	LocalAuthority: str
	DateReceived: str
	Type: str
	SubmissionsBy: str
	DueDate: str
	Decision: str
	DecisionDateMO: str
	ApplicationStatus: str
	GrantDate: str
	FurtherInfoRequested: str
	FurtherInfoReceived: str
	ReportFileLocation: str
	ApplicantName: str
	DevelopmentDescription: str
	DevelopmentAddress: str
	EngineeringArea: int
	Planner: str
	NumberofAppealstoAnBordPleanala: str


class PlanningSearch:
	BASE_URL = "https://webgeo.kildarecoco.ie/planningenquiry/Public/GetPlanningFileNameAddressResult"

	def __init__(self, name: Optional[str] = None, address: Optional[str] = None, devDesc: Optional[str] = None, startDate: Optional[str] = None, endDate: Optional[str] = None):
		self.params = {
			"name": name or "",
			"address": address or "",
			"devDesc": devDesc or "",
			"startDate": startDate or "",
			"endDate": endDate or "" 
		}
		self.results: List[PlanningResult] = None

	def __repr__(self):
		return self.BASE_URL + "?name={name}&address={address}&devDesc={devDesc}&startDate={startDate}&endDate={endDate}".format_map(self.params)
	
	def sanitize_input(self, datadict):
		clean_data = []
		for plan in datadict:
			clean_dict = {}
			for k, v in plan.items():
				if isinstance(v, str):
					clean_dict[k] = v.strip() if isinstance(v, str) else v
			clean_data.append(clean_dict)		
		return sorted(clean_data, key=lambda x: datetime.strptime(x["DateReceived"], "%d/%m/%Y"))

	def fetch_results(self):
		try:
			response = requests.get(self.BASE_URL, params=self.params, timeout=10)
			response.raise_for_status()
			self.results = self.sanitize_input(response.json())
		except requests.RequestException as e:
			print(f"Failed to fetch data: {e}")
			self.results = {}
	
	def to_table(self):
		planning_search_table = Table("File", "Applicant Name", "Address", "Type", "Date Received")
		for res in self.results:
			planning_search_table.add_row(
				res.get('FileNumber'),
				res.get('ApplicantName'),
				res.get('DevelopmentAddress'),
				res.get('Type'),
				res.get('DateReceived')
			)

		return planning_search_table

	
if __name__ == "__main__":
	from sys import argv
	console = Console()

	address = str(argv[1])

	p = PlanningSearch(address=address)
	p.fetch_results()
	table = p.to_table()

	console.print(table)

