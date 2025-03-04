from bospy import bos

def ValueByNameTest(name:str|list[str]):
    pts = bos.NameToPoint(name)
    values = bos.Get(pts)
    print(name, "->", values)

def SetByQueryTest(t:str, l:str):
    pts = bos.QueryPoints(t, l)
    results = bos.Set(pts, "true")
    print(results)

if __name__ == "__main__":

    name1 = "air_temp" # a name that returns 1 point
    ValueByNameTest(name1)

    name2 = "status"
    ValueByNameTest([name1, name2])

    loc1 = "home"
    type1 = "brick:On_Command"
    SetByQueryTest(t=type1, l=loc1)
