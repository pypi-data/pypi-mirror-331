import re
import os

point_re = re.compile(r'(?P<prefix>^bos://[A-Za-z0-9.-]+/dev/)(?P<point>[0-9]+/pts/[0-9]+$)')
dev_point_re = re.compile(r'(?P<device>[0-9]+)/pts/(?P<point>[0-9]+)')

brick_type_re = re.compile(r'^(?P<prefix>https://brickschema.org/schema/Brick#)(?P<type>[A-Za-z0-9_]+)')

def SimplifyPoint(pts:list[str]) -> list[str]:
    if type(pts) == str:
        pts = [pts]
    for i, p in enumerate(pts):
        m = point_re.match(p)
        if m is not None:
            prefix = m.groupdict()['prefix']
            pt_str = pts[i][len(prefix):]
            m2 = dev_point_re.match(pt_str)
            parts = [m2.groupdict()['device'], m2.groupdict()['point']]
            pts[i] = ".".join(parts)
    if len(pts) == 1:
        return pts[0]
    return pts

def SimplifyBrickType(_type:str):
    m = brick_type_re.match(_type)
    if m is not None:
        prefix = m.groupdict()['prefix']
        type_str = _type[len(prefix):]
        return "brick:" + type_str
    return _type

if __name__ == "__main__":
    p1 = "bos://localhost/dev/1/pts/5"
    p2 = "bos://localhost/dev/1/pts/5"
    p3 = "https://google.com/dev/1/pts/5"
    for p in [p1, p2, p3]:
        m = point_re.match(p)
        if m is None:
            print("not a match")
        else:
            print(m.groupdict())

    print(SimplifyPoint(p1))
    print(SimplifyPoint([p1]))
    print(SimplifyPoint([p1, p2]))

    t1 = "https://brickschema.org/schema/Brick#Air_Temperature_Sensor"
    t2 = "https://rec.com/schema/rec#Control_Zone"
    print(SimplifyBrickType(t1))
    print(SimplifyBrickType(t2))