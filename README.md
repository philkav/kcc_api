# kcc_api
API for requesting public data from Kildare County Council

## Howto
* Instantiate a plan object:

```
import plan
p = plan.KCCPlan('20162')
```

* Search by address:

```
import plan
for p in plan.search(address='westfield'):
    print(p)
```

## CLI Sample
In the Project base directory, you can run a sample of the program like so.
There are two options, search (-s) and plan (-p):


#### Install it
```➜  kcc_api git:(master) ✗ uv pip install -e .
Audited 1 package in 17ms
```


#### Display help section
```
➜  kcc_api git:(master) ✗ uv run kcc
usage: kcc_api [-h] [-s QUERY] [-p QUERY]

Kildare CoCo planning CLI

options:
  -h, --help          show this help message and exit
  -s, --search QUERY  Search by address or keyword
  -p, --plan QUERY    Search by Plan ID
```


#### Perform Search on an address
```➜  kcc_api git:(master) ✗ uv run kcc -s westfield
<KCCPlan: 20101 [Westfield, Green Lane, Leixlip, Co. Kildare.]>
<KCCPlan: 18662 [The Court Westfield Green Lane, Leixlip Co. Kildare]>
<KCCPlan: 19831 [Westfield,  Green Lane, Leixlip, Co. Kildare.]>
<KCCPlan: 18661 [Westfield Green Lane Leixlip Co. Kildare]>
<KCCPlan: 171375 [Westfield,  Greenlane,  Leixlip,  Co.Kildare]>
<KCCPlan: 18663 [The Mews Westfield Green Lane, Leixlip Co. Kildare]>
...
```


#### Load a Plan by ID
```
➜  kcc_api git:(master) ✗ uv run kcc -p 2578
{
    "FileNumber": "2578",
    "LocalAuthority": "Kildare County Council",
    "DateReceived": "22/04/2025",
    "Type": "PERMISSION",
    "SubmissionsBy": "26/05/2025",
    ...
}
<Attachment: [Comment: # Files] (link: None)>
<Attachment: [ : 1] (link: https://idocsweb.kildarecoco.ie/iDocsWebDPSS/ViewFiles.aspx?docid=3197994&format=djvu)>
<Attachment: [Referrals and Criteria 28/04/2025: 1] (link: https://idocsweb.kildarecoco.ie/iDocsWebDPSS/ViewFiles.aspx?docid=3197995&format=djvu)>
<Attachment: [Uisce Eireann: 1] (link: https://idocsweb.kildarecoco.ie/iDocsWebDPSS/ViewFiles.aspx?docid=3199652&format=djvu)>
...
```
