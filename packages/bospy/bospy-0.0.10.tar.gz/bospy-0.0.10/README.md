# bospy
python wrappers for accessing bos services.

Points are accessed via "pointers". You get a pointer by using a query function like `NameToPoint` and pass the output to a function like `Get` or `Set`.

Pointers are the uri strings that uniquely identify each point in the `sysmod`. 

## `Get`
`Get(points)` takes one or more point uris and returns values for each uri passed.

Getting a single point by name:
``` python
name = 'BLDG3.AHU2.RM1.TEMP'
pt = NameToPoint(name)
value = Get(pt)
print(name, value)
```
Output:
``` shell
$ python get_example.py
BLDG3.AHU2.RM1.TEMP 18.0
```
Getting multiple values by location:
```python
pts = LocationToPoint('ROOM_1')
resp = Get(pts)
for k, v in resp.items()
    name = GetPointName(k)
    print(name, v)
```
Output
``` bash
$ python get_multiple_example.py
BLDG3.AHU2.RM1.TEMP 22.5
BLDG3.AHU2.RM1.SETPOINT 21.0
BLDG3.AHU2.RM1.DAMPER_POS 85.0
```

## `Set`
`Set(points, values)` takes 1 or more point uris and an equal number of values. You may also pass a single value to be written to all points. 

Usage:
``` python
pt = GetPointByName('BLDG3.AHU2.RM1.SETPOINT')
ok = Set(pt, 23)
if ok:
    print('success')
else:
    print('failed to write', key)
```
Output:
``` bash
$ python set_example.py
success
```
