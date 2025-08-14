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

$ uv run python -m src.kcc_api -p 20162
 ... Will list all the relvant data and attachments for that Plan

$ uv run python -m src.kcc_api -s harpur
<KCCPlan: 2460757 [Harpur House, Harpur Lane, Leixlip, Co. Kildare]>
<KCCPlan: 2460055 [“Harpur Lane”, (Leixlip Gate), in the townlands of Kilmacredock Upper and Castletown Leixlip, Co Kildare]>
<KCCPlan: 23572 [Ground Floor Harpur House Harpur Lane Leixlip Co. Kildare]>
<KCCPlan: 2460745 [Harpur House Harpur Lane Leixlip Co. Kildare]>
<KCCPlan: 23606 [Ground Floor Harpur House Harpur Lane Leixlip Co. Kildare]>

