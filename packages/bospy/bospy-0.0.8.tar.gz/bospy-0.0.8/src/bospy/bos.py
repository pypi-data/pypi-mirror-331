from . import comms_pb2_grpc
from . import comms_pb2
import grpc

import datetime as dt
import sys
import os

from typing import Any

""" Provides the wrapper functions used to access openBOS points in Python
"""

VERSION = "0.0.4"

SYSMOD_ADDR = os.environ.get('SYSMOD_ADDR')
DEVCTRL_ADDR = os.environ.get('DEVCTRL_ADDR')
HISTORY_ADDR = os.environ.get('HISTORY_ADDR')

# uri -> name cache
point_name_cache = {}

# apply defaults
if SYSMOD_ADDR is None:
    SYSMOD_ADDR = "localhost:2821"
if DEVCTRL_ADDR is None:
    DEVCTRL_ADDR = "localhost:2822"
if HISTORY_ADDR is None:
    HISTORY_ADDR = "localhost:2833"

# client calls for the sysmod rpc calls
def NameToPoint(names:str|list[str], multiple_matches:bool=False) -> None | list[str]:
    if isinstance(names, str):
        names = [names]
    else:
        multiple_matches = True

    response: comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.NameToPoint(comms_pb2.GetRequest(
            Keys=names
        ))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query,
                                              response.Error))
    # cast as a more user-friendly type
    if multiple_matches:
        return response.Values
    elif len(response.Values) == 1:
        return response.Values[0]
    else:
        return None
    
def GetName(pt:str) -> None | str:
    response: comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.GetName(comms_pb2.GetRequest(
            Keys=[pt]
        ))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query,
                                              response.Error))
    if len(response.Values) > 0:
        return response.Values[0]
    else:
        return None

def TypeToPoint(types:str|list[str]) -> None | str | list[str]:
    if isinstance(types, str):
        types = [types]
    response: comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.TypeToPoint(comms_pb2.GetRequest(
            Keys=types))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query,
                                              response.Error))
    # cast as a more user-friendly type
    return response.Values

def LocationToPoint(locations:str|list[str]) -> None | str | list[str]:
    print(locations, type(locations))
    if isinstance(locations, str):
        locations = [locations]
    response: comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.LocationToPoint(comms_pb2.GetRequest(
            Keys=locations))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query,
                                              response.Error))
    return response.Values

def QueryPoints(query:str=None, names:str|list[str]=None, types:str|list[str]=None,
                locations:str|list[str]=None, inherit_device_loc:bool=True,
                parent_types:str|list[str]=None):
    """ if query, types, and locations are all none. This returns all pts in sysmod.
    """

    if isinstance(names, str):
        names = [names]
    if isinstance(types, str):
        types = [types]
    if isinstance(locations, str):
        locations = [locations]
    if isinstance(parent_types, str):
        parent_types = [parent_types]

    response: comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        if query is None:
            response = stub.QueryPoints(comms_pb2.PointQueryRequest(
                Names=names,
                Types=types,
                Locations=locations,
                ConsiderDeviceLoc=inherit_device_loc,
                ParentTypes=parent_types,
            ))
        else:
            response = stub.QueryPoints(comms_pb2.PointQueryRequest(
                Query=query,
            ))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query,
                                              response.Error))                              
    return sorted(response.Values)

def QueryDevices(query:str=None, names:str|list[str]=None, types:str|list[str]=None, 
                locations:str|list[str]=None, child_types:str|list[str]=None) -> list[str]:
    
    if isinstance(names, str):
        names = [names]
    if isinstance(types, str):
        types = [types]
    if isinstance(locations, str):
        locations = [locations]
    if isinstance(child_types, str):
        child_types = [child_types]

    response:comms_pb2.QueryResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        if query is None:
            response = stub.QueryDevices(comms_pb2.DeviceQueryRequest(
                Names=names,
                Types=types,
                Locations=locations,
                ChildTypes=child_types,
            ))
        else:
            response = stub.QueryDevices(comms_pb2.PointQueryRequest(
                Query=query,
            ))
        if response.Error > 0:
            print("get '{}' error: {}".format(response.Query, response.Error))
    return sorted(response.Values)

def MakeDevice(name:str, types:str|list[str]=None, locations:str|list[str]=None, 
               driver:str=None, properties:list[tuple]=None) -> str:
    """ takes the name, types, locations, driver, and any other properties you 
        wish to associate with the device.
        driver is of the format "bos://localhost/drives/[0-9]+".
        otherProperties is a list of 3-tuples of the format (subject:str, predicate:str, object:str)
    """
    if isinstance(types, str):
        types = [types]
    if isinstance(locations, str):
        locations = [locations]
    if properties:
        properties = [comms_pb2.Triple(Subject=p[0], Predicate=p[1], Object=p[2]) for p in properties]
    
    response:comms_pb2.MakeResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.MakeDevice(comms_pb2.MakeDeviceRequest(
            Name=name,
            Types=types,
            Locations=locations,
            Driver=driver,
            OtherProperties=properties,
        ))
    if response.ErrorMsg != "":
        return "error: {}".format(response.Error, response.ErrorMsg)
    return response.Url

def MakePoint(name:str, device:str, types:str|list[str]=None, locations:str|list[str]=None, 
              xref:str=None, properties:list[tuple]=None, ) -> str:
    """ takes the name, types, locations, and any other properties you 
        wish to associate with the device.
        otherProperties is a list of 3-tuples of the format (subject:str, predicate:str, object:str)
    """
    if isinstance(types, str):
        types = [types]
    if isinstance(locations, str):
        locations = [locations]
    if properties:
        properties = [comms_pb2.Triple(Subject=p[0], Predicate=p[1], Object=p[2]) for p in properties]
    
    response:comms_pb2.MakeResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.MakePoint(comms_pb2.MakePointRequest(
            Device=device,
            Name=name,
            Types=types,
            Locations=locations,
            Xref=xref,
            OtherProperties=properties,
        ))
    if response.ErrorMsg != "":
        return "error: {}".format(response.Error, response.ErrorMsg)
    return response.Url

def MakeDriver(name:str, host:str, port:int, image:str=None, container:str=None) -> comms_pb2.MakeResponse:
    """ name    of the driver
        host    the hostname (preferred) or IP that the service can be found at
        port    starts at 50061 by convention
        
        [optional]
        image       name of the image to pull if not on system
        container   name of the container if it doesn't match the hostname
    """
    response: comms_pb2.MakeResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.MakeDriver(comms_pb2.MakeDriverRequest(
            Name=name,
            Host=host,
            Port=str(port),
            Image=image,
            Container=container,
        ))
    if response.ErrorMsg != "":
        return "error: {}".format(response.Error, response.ErrorMsg)
    return response.Url

def Delete(sub:str="", pred:str="", obj:str=""):
    if sub == "" and pred == "" and obj == "":
        print("must provide at least one of subject, predicate, or object")
        return
    response:comms_pb2.DeleteResponse
    with grpc.insecure_channel(SYSMOD_ADDR) as channel:
        stub = comms_pb2_grpc.SysmodStub(channel)
        response = stub.Delete(comms_pb2.DeleteRequest(
            Triple=comms_pb2.Triple(
                Subject=sub,
                Predicate=pred,
                Object=obj,
            )
        ))
    return

# History rpc calls
def SetSampleRate(pts:str|list[str], rates:str|list[str]) -> bool:
    if isinstance(pts, str):
        pts = [pts]
    if isinstance(rates, str):
        rates = [rates]

    pairs = []
    if len(pts) == len(rates):
        pairs = [comms_pb2.SetPair(Key=k, Value=rates[i]) for i, k in enumerate(pts)]
    elif len(rates) == 1:
        pairs = [comms_pb2.SetPair(Key=k, Value=rates[0]) for k in pts]
    else:
        print("unable invalid combination of pts ({}) and rates {}".format(len(pts), len(rates)))
        return False
    
    response: comms_pb2.SetResponse
    with grpc.insecure_channel(HISTORY_ADDR) as channel:
        stub = comms_pb2_grpc.HistoryStub(channel)
        response = stub.SetSampleRate(comms_pb2.SetRequest(
            Pairs=pairs
        ))
        if response.Error > 0:
            print("SetSampleRates: error code {}".format(response.Error))
            return False
    #  trigger a refresh
    RefreshRates()
    return True

def RefreshRates():
    response: comms_pb2.RefreshRatesResponse
    with grpc.insecure_channel(HISTORY_ADDR) as channel:
        stub = comms_pb2_grpc.HistoryStub(channel)
        response = stub.RefreshRates(comms_pb2.RefreshRatesRequest())
        if response.Error > 0:
            print("RefreshRates: error code {}".format(response.Error))
            return False
    return True

def GetHistory(pts:str|list[str], start:str=None, end:str=None, limit:int=14400, 
               pandas:bool=False, tz:str=None, group_by_id:bool=True, 
               get_names:bool=False, resample_to:str=None) -> list[comms_pb2.HisRow] | None:
    if isinstance(pts, str):
        pts = [pts]
    if start is None:
        start = ""
    if end is None:
        end = ""
    response: comms_pb2.HistoryResponse
    with grpc.insecure_channel(HISTORY_ADDR) as channel:
        stub = comms_pb2_grpc.HistoryStub(channel)
        response = stub.GetHistory(comms_pb2.HistoryRequest(
            Start=start, 
            End=end,
            Keys=pts,
            Limit=limit,
        ))
        if response.Error > 0:
            print("GetHistory: error code {}".format(response.Error))
            return None
    R = [[r.Timestamp, r.Value, r.Id] for r in response.Rows]
    if pandas:
        import pandas as pd
        df = pd.DataFrame(R, columns=['time', 'value', 'id'])
        df['time'] = pd.to_datetime(df['time'], utc=True)
        if tz:
            from pytz import timezone
            _tz = timezone(tz)
            df['time'] = df['time'].dt.tz_convert(_tz)
        if group_by_id:
            xf = pd.DataFrame()
            G = df.groupby('id')
            columns = ['time']
            for i, g in enumerate(G.groups):
                if i == 0:
                    xf = G.get_group(g)[['time', 'value']]
                    columns.append(G.get_group(g).iloc[0]['id'])
                else:
                    xf = pd.merge_ordered(xf, G.get_group(g)[['time', 'value']], on='time')
                    columns.append(G.get_group(g).iloc[0]['id'])
            xf.columns = columns
            df = xf
        df.set_index('time', inplace=True)
        if resample_to:
            df = df.resample(resample_to).mean()
        if get_names:
            df.columns = [GetName(pt) for pt in df.columns]
        return df
    return R

# devctrl rpc calls
class GetValue(object):
    def __init__(self, key, value):
        self.Key:str = key
        self.Value = value

class GetResponse(object):
    def __init__(self):
        self.Values:list[GetValue] = []


def NewGetValues(resp:comms_pb2.GetResponse) -> list[GetValue]:
    V:list[GetValue] = []
    for pair in resp.Pairs:
        p = GetValue(
            key=pair.Key,
            value=GetTypedValue(pair),
        )
        V.append(p)
    return V


class SetResponse(object):
    def __init__(self):
        self.Key:str = None
        self.ValueStr:str = None
        self.Ok:bool = False


def NewSetResponse(responses:comms_pb2.SetResponse) -> list[SetResponse]:
    R:list[SetResponse] = []
    for p in responses.Pairs:
        r = SetResponse()
        if p.Key is not None:
            r.Key = p.Key
        if p.Value is not None:
            r.ValueStr = p.Value
        r.Ok = p.Ok
        R.append(r)
    return R


def Ping(addr:str) -> bool:
    response: comms_pb2.Empty
    with grpc.insecure_channel(addr) as channel:
        stub = comms_pb2_grpc.HealthCheckStub(channel)
        response = stub.Ping(comms_pb2.Empty())
    if response is not None:
        return True
    else:
        return False


def CheckLatency(addr:str, num_pings:int=5) -> dt.timedelta | None:
    running_total:dt.timedelta
    for i in range(num_pings):
        start = dt.datetime.now()
        ok = Ping(addr)
        end = dt.datetime.now()
        if not ok:
            return None
        diff = end-start
        if i == 0:
            running_total = diff
        else:
            running_total = running_total + diff
    return running_total / num_pings
        

def Get(keys:str|list[str], full_response=False) -> list[GetResponse] | dict[str, object]:
    if type(keys) == str:
        keys = [keys]

    response: comms_pb2.GetResponse
    with grpc.insecure_channel(DEVCTRL_ADDR) as channel:
        stub = comms_pb2_grpc.GetSetRunStub(channel)
        response = stub.Get(comms_pb2.GetRequest(Keys=keys))
    R = NewGetValues(response)
    if full_response:
        return R
    D = {}
    for r in R:
        D[r.Key] = r.Value
    return D

def Set(keys:str|list[str], values:str|list[str], full_response=False) -> SetResponse | dict[str, bool] | bool:
    if isinstance(keys, str):
        keys = [keys]
    if isinstance(values, (str, float, int, bool)):
        values = [values]

    # validate the number of keys and values
    if len(keys) != len(values) :
        if len(keys) >= 1 and len(values) == 1:
            values = [values[0]] * len(keys)
        else:
            print("error: unable to broadcast values to match number of keys")
            print("\thave {} keys and {} values".format(len(keys), len(values)))
            return False

    # by now now we must have an equal number of keys and values, format them
    pairs = [comms_pb2.SetPair(Key=k, Value=str(values[i])) for i, k in enumerate(keys)]

    response: comms_pb2.SetResponse
    with grpc.insecure_channel(DEVCTRL_ADDR) as channel:
        stub = comms_pb2_grpc.GetSetRunStub(channel)
        response = stub.Set(comms_pb2.SetRequest(Pairs=pairs))
        if response.Error > 0:
            print("SET_ERROR_{}: {}".format(response.Error, response.ErrorMsg))
            return False
    r = NewSetResponse(response)
    if full_response:
        return r
    return True

def GetTypedValue(v:comms_pb2.GetPair|comms_pb2.SetPair):
    """ a helper function that uses the appropriate fields from a comms_pb2.GetReponse
    to return a typed value.
    """
    return DecodeValue(v.Value, v.Dtype)


def DecodeValue(s:str, dtype:comms_pb2.Dtype=comms_pb2.UNSPECIFIED):
    if (dtype == comms_pb2.DOUBLE) or (dtype == comms_pb2.FLOAT):
        return float(s)
    if (dtype == comms_pb2.INT32) or (dtype == comms_pb2.INT64) or (dtype == comms_pb2.UINT32) or (dtype == comms_pb2.UINT64):
        return int(s)
    if (dtype == comms_pb2.BOOL):
        if s.lower() == "true":
            return True
        return False
    if (dtype == comms_pb2.STRING):
        return s
    else:
        return UntypedString(s)
    

class UntypedString(str):
    """ Used to show that a value received by Get or GetMultiple was cast to a 
    native python type but that the function did not receive dtype information 
    (i.e., the Dtype=UNSPECIFIED)
    """

class PointUri(str):
    """ Used to indicate that a value is not just a str but specifically a point uri.
    """


if __name__ == "__main__":
    """ running this file will do a health check on the devctrl and sysmod services.
    """
    devctrl_addr = os.environ.get('DEVCTRL_ADDR')
    if devctrl_addr is None:
        print("environment variable DEVCTRL_ADDR not set. Try running:")
        print("\t$ source serivces/config-env")
        sys.exit(1)

    # make sure devCtrl is running
    try:
        resp = CheckLatency(devctrl_addr)
    except Exception as e:
        print("devctrl did not respond at {}\n\tis it running?".format(devctrl_addr))
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        sys.exit(1)
    else:
        print("devctrl running. RTT = {:.2f} ms".format(resp.total_seconds()*1000))

    sysmod_addr = os.environ.get('SYSMOD_ADDR')
    if sysmod_addr is None:
        print("environment variable DEVCTRL_ADDR not set. Try running:")
        print("\t$ source serivces/config-env")
        sys.exit(1)

    # make sure devCtrl is running
    try:
        resp = CheckLatency(sysmod_addr)
    except Exception as e:
        print("devCtrl did not respond at {}\n\tis it running?".format(sysmod_addr))
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        print(message)
        sys.exit(1)
    else:
        print("sysmod running. RTT = {:.2f} ms".format(resp.total_seconds()*1000))
