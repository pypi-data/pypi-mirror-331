from bospy import bos, utils

simple_output = True

def NameTest(name:str):
    pt = bos.NameToPoint(name)
    if simple_output:
        pt = utils.SimplifyPoint(pt)
    print("== point(s) named {} ==".format(name))
    print("\t", pt)
    return pt
    
def NameTest2(name:str):
    pts = bos.NameToPoint(name, multiple_matches=True)
    if simple_output:
        pts = utils.SimplifyPoint(pts)
    print("== point(s) named {} ==".format(name))
    print("\t", pts)
    return pts

def PointNameTest(pt:str):
    name = bos.PointToName(pt)
    if simple_output:
        pt = utils.SimplifyPoint(pt)
    print("== Name of {} ==".format(pt))
    print("\t", name)
    return name

def TypeTest(_type:str):
    pts = bos.TypeToPoint(_type)
    if simple_output:
        pts = utils.SimplifyPoint(pts)
        _type = utils.SimplifyBrickType(_type)
    print("== point(s) typed {} ==".format(_type))
    print("\t", pts)
    return pts

def LocationTest(location:str):
    pts = bos.LocationToPoint(location)
    if simple_output:
        pts = utils.SimplifyPoint(pts)
    print("== point(s) located in '{}' ==".format(location))
    print("\t", " ".join(pts))
    return pts

def QueryAllTest():
    bos.QueryPoints()

def QueryTest(types:str|list[str]=None, locations:str|list[str]=None):
    if type(locations) == str:
        locations = [locations]
    if type(types) == str:
        types == [types]
    pts = bos.QueryPoints(types, locations)
    if simple_output:
        pts = [utils.SimplifyPoint(pt) for pt in pts]
        types = [utils.SimplifyBrickType(types) for t in types]
    print("== point(s) located in '{}' with type {} ==".format(locations[0], types[0]))
    print("\t", " ".join(pts))
    return pts

if __name__ == "__main__":
    name1 = "air_temp" # will only return 1 point
    name2 = "voltage"     # will return more than 1 point

    NameTest(name1)
    NameTest2(name2)

    ptUri1 = "bos://localhost/dev/1/pts/3"
    PointNameTest(ptUri1)

    type1 = "https://brickschema.org/schema/Brick#Air_Temperature_Sensor"
    TypeTest(type1)

    location1 = "home"
    LocationTest(location1)

    # location2 = "lab"
    QueryTest(type1, location1)