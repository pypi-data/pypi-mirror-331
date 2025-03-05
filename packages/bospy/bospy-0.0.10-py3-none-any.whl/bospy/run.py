import os

envVars:dict[str,str]
args:list[str] = []
kwargs:dict[str, str] = {}

def LoadArgs():
    # collect all the args
    i = 1
    while True:
        try:
            arg = os.environ.pop("arg:{}".format(i))
            args.append(arg)
            i += 1
        except KeyError:
            break

def LoadKwargs():
    # collect all the args
    for k, v in os.environ.items():
        if "kwarg:" in k:
            kwargs[k[6:]] = os.environ.pop(k)

def LoadEnv():
    LoadArgs()
    LoadKwargs()

LoadEnv()