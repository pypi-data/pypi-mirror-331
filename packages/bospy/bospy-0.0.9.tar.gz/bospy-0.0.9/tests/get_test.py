from bospy import bos, utils

def GetTest(bosPtUri:str):
    values = bos.Get(bosPtUri)
    for k, v in values.items():
        print(k, "->", v, "({})".format(type(v)))
    
def GetMultipleTest(bosPtUris:list[str]):
    R = bos.Get(bosPtUris)
    for key, value in R.items():
        print(key, "->", value, "({})".format(type(value)))

if __name__ == "__main__":
    print("sysmod address: ", bos.SYSMOD_ADDR)
    print("devctrl address:", bos.SYSMOD_ADDR)
    
    test1_url = "bos://localhost/dev/1/pts/1"
    GetTest(test1_url)

    test2_url = "bos://localhost/dev/1/pts/2"
    test3_url = "bos://localhost/dev/1/pts/3"
    test4_url = "bos://localhost/dev/1/pts/4"

    GetTest([test2_url, test3_url, test4_url])
    