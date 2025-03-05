import services.wrappers.python.bos as c
import comms_pb2

if __name__ == "__main__":
    tests = [
        ("true", comms_pb2.BOOL),
        ("false", comms_pb2.BOOL),
        ("-1", comms_pb2.INT32),
        ("1", comms_pb2.UINT32),
        ("1.0", comms_pb2.FLOAT),
        ("string", comms_pb2.STRING),
        ("unspecified value", comms_pb2.UNSPECIFIED),
    ]

    answers = [
        bool,
        bool, 
        int, 
        int, 
        float, 
        str,
        str,
    ]

    assert len(tests) == len(answers)
    for i, case in enumerate(tests):
        typed_val = c.DecodeValue(*case)
        print("{} a {} ({})".format(case[0], type(typed_val), case[1]))
        assert type(typed_val) == answers[i]