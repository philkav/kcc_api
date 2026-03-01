# kcc_api

A Python library and CLI for accessing public planning application data from the
[Kildare County Council Planning Portal](http://webgeo.kildarecoco.ie/planningenquiry/).

You can search for planning applications by address, applicant name, or description,
and retrieve the full details and associated documents for any individual application.

---

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended)

---

## Installation

```bash
uv pip install -e .
```

---

## Quick Start (API)

### Search for planning applications

```python
from kcc_api.plan import Search

for plan in Search(address='westfield'):
    print(plan)
```

You can search by any combination of `address`, `name` (applicant), or `description`:

```python
Search(name='murphy')
Search(description='solar panel')
Search(name='murphy', address='naas')
```

Results are returned sorted by date received (oldest first).

### Load a plan by ID

```python
from kcc_api.plan import KCCPlan

plan = KCCPlan(2578)
print(plan.FileNumber)       # '2578'
print(plan.DateReceived)     # '22/04/2025'
print(plan.Type)             # 'PERMISSION'
print(plan.SubmissionsBy)    # '26/05/2025'
print(plan.LocalAuthority)   # 'Kildare County Council'
```

### Fetch attached documents

Attachments are not loaded by default — call `fetch_attachments()` to retrieve them:

```python
plan = KCCPlan(2578)
plan.fetch_attachments()

for attachment in plan.attachments:
    print(attachment)
    print(attachment.link)   # Direct URL to the document (djvu or jpeg)
```

---

## CLI Usage

#### Display help

```
➜ uv run kcc
usage: kcc [-h] [-n QUERY] [-a QUERY] [-d QUERY] [-p QUERY]

Kildare CoCo planning CLI

options:
  -h, --help              show this help message and exit
  -n, --name QUERY        Search by Submitter Name
  -a, --address QUERY     Search by Address
  -d, --description QUERY Search by Description
  -p, --plan QUERY        Search by Plan ID
```

#### Search by address

```
➜ uv run kcc -a westfield
<KCCPlan: (22/03/2010) [20101] Westfield, Green Lane, Leixlip, Co. Kildare.>
<KCCPlan: (14/09/2018) [18662] The Court Westfield Green Lane, Leixlip Co. Kildare>
<KCCPlan: (11/10/2019) [19831] Westfield,  Green Lane, Leixlip, Co. Kildare.>
...
```

#### Load a plan by ID

```
➜ uv run kcc -p 2578
{
    "FileNumber": "2578",
    "LocalAuthority": "Kildare County Council",
    "DateReceived": "22/04/2025",
    "Type": "PERMISSION",
    "SubmissionsBy": "26/05/2025",
    ...
}
<Attachment: [Referrals and Criteria 28/04/2025: 1] (link: https://idocsweb.kildarecoco.ie/...)>
<Attachment: [Uisce Eireann: 1] (link: https://idocsweb.kildarecoco.ie/...)>
...
```

---

## Data Model

### `KCCPlan`

| Field | Description |
|---|---|
| `FileNumber` | Planning application reference number |
| `LocalAuthority` | Always `Kildare County Council` |
| `DateReceived` | Date the application was received (`dd/mm/yyyy`) |
| `Type` | Application type, e.g. `PERMISSION`, `RETENTION` |
| `SubmissionsBy` | Deadline for public submissions (`dd/mm/yyyy`) |
| `DevelopmentAddress` | Address of the proposed development (list of strings) |

### `Attachment`

| Attribute | Description |
|---|---|
| `type` | Document category |
| `comment` | Document label or description |
| `files` | Number of files |
| `link` | Direct URL to the document (prefers djvu, falls back to jpeg) |
