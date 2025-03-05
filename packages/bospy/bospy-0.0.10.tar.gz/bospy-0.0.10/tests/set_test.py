from bospy import bos

from typing import Any

def SetTest(bosPtUri:str, value:str):
    ok = bos.Set(bosPtUri, value)
    if ok:
        print(bosPtUri, "<-", value, "(ok)")
    else:
        print(bosPtUri, "<-", value, "(SetError)")

def SetMultipleTest(keys:list[str], values:list[Any]):
    R = bos.Set(keys, values, full_response=True)
    for r in R:
        bosPtUri = r.Key
        valueStr = r.ValueStr # drivers are not required to provide this in response
        if r.Ok:
            print(bosPtUri, "<-", valueStr, "(ok)")
        else:
            print(bosPtUri, "<-", valueStr, "(SetError)")

if __name__ == "__main__":
    # print("sysmod address: ", bos.SYSMOD_ADDR)
    # print("devctrl address:", bos.DEVCTRL_ADDR)
    
    pt1 = "bos://localhost/dev/1/pts/1"
    SetTest(pt1, 420)

    pt2 = "bos://localhost/dev/1/pts/2"
    pt3 = "bos://localhost/dev/1/pts/4"
    pt4 = "bos://localhost/dev/1/pts/5"
    SetMultipleTest(
        [pt2, pt3, pt4],
        [18, 80, True],
        )
    
    # if n pts and 1 value are passed, the value is assigned to all n pts
    SetMultipleTest(
         [pt2, pt3], 
         20
    )

    pt5 = "bos://localhost/dev/2/pts/2"
    SetTest(pt5, False)
