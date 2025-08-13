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

