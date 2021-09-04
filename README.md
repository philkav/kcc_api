# kcc_api
API for requesting public data from Kildare County Council

## Howto
* Instantiate a plan object:


```
import Plan
p = Plan.Plan('20162')
```

* Search by address:

```
import Plan
for p in Plan.search_by_address('westfield'):
    print(p)
```

