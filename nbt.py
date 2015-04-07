import gzip
import struct
import sys

class EndTag(Exception):
    pass

class Tag(object):
    def __init__(self, tag_type, tag_name, payload, ltype=None):
        self.type = tag_type
        self.name = tag_name
        self.payload = payload
        self.ltype = ltype
    def __str__(self):
        return self.type + ("<" + self.ltype + ">" if self.ltype is not None else "") + '("' + self.name + '"): ' + str(self.payload)
    __repr__ = __str__
    def __getitem__(self, item):
        if self.type in ("TAG_List", "TAG_Compound"):
            return self.payload[item]
        else:
            raise TypeError("'" + self.type + "' object is not subscriptable")
    def __setitem__(self, item, value):
        print("nbt.__setitem__ called")
        if isinstance(value, Tag):
            print("isinstance of Tag")
            self.payload[item] = value
        elif self.payload[item].type in ("TAG_Float", "TAG_Double"):
            if isinstance(value, int) or isinstance(value, float):
                self.payload[item].payload = float(value)
            else:
                raise TypeError("Can't assign type " + type(value) + " value to numeric tag")
        elif self.payload[item].type in ("TAG_Byte", "TAG_Short", "TAG_Int", "TAG_Long"):
            if isinstance(value, int) or isinstance(value, float) and value.is_integer():
                self.payload[item].payload = int(value)
        elif self.payload[item].type in ("TAG_Byte_Array", "TAG_Int_Array"):
            if isinstance(value, list):
                if all(isinstance(x, float) and x.is_integer or isinstance(x,int) for x in value):
                    self.payload[item].payload = list(map(int,value))
                else:
                    raise TypeError("Arrays must contain only integers")
            else:
                raise TypeError("Can't assign type " + type(value) + "to array tag")
        elif self.payload[item].type == "TAG_String":
            if isinstance(value, str):
                self.payload[item].payload = value
            else:
                raise TypeError("Can't assign type " + type(value) + " value to TAG_String")
        elif self.payload[item].type == "TAG_List":
            if isinstance(value, list) and all(isinstance(x,nbt.Tag) and x.name == "" and x.type == self.payload[item].ltype for x in value):
                self.payload[item].payload = value
        elif self.payload[item].type == "TAG_Compound":
            if isinstance(value, dict) and all(isinstance(x,nbt.Tag) for x in value):
                self.payload[item].payload = value
        else:
            raise TypeError("Can't assign type " + type(value) + " value to wait what?")

numToType = {
        0: "TAG_End",
        1: "TAG_Byte",
        2: "TAG_Short",
        3: "TAG_Int",
        4: "TAG_Long",
        5: "TAG_Float",
        6: "TAG_Double",
        7: "TAG_Byte_Array",
        8: "TAG_String",
        9: "TAG_List",
        10:"TAG_Compound",
        11:"TAG_Int_Array"
        }

typeToNum = {
        "TAG_End": 0,
        "TAG_Byte": 1,
        "TAG_Short": 2,
        "TAG_Int": 3,
        "TAG_Long": 4,
        "TAG_Float": 5,
        "TAG_Double": 6,
        "TAG_Byte_Array": 7,
        "TAG_String": 8,
        "TAG_List": 9,
        "TAG_Compound": 10,
        "TAG_Int_Array": 11
        }

def getList(file_object, tag_type, tag_size):
    # return [(lambda x: (x[0], x[2]))(getTag(file_object, tag_type)) for _ in range(tag_size)]
    return [getTag(file_object, tag_type) for _ in range(tag_size)]

def getCompound(file_object):
    cmpnd = {}
    while True:
        try:
            tag = getTag(file_object)
            cmpnd[tag.name] = tag
        except EndTag:
            break
    return cmpnd

def writeList(file_object, lst, ltype):
    file_object.write(struct.pack('b',typeToNum[ltype]))
    file_object.write(struct.pack('>i',len(lst)))
    for element in lst:
        writeTag(file_object, element, ltype)

def writeCompound(file_object, obj):
    for key in obj:
        writeTag(file_object, obj[key])
    # write TAG_End
    file_object.write(struct.pack('b',0))

def writeTag(file_object, data, tag_type=None):
    if tag_type is None:
        tag_type = data.type
        tag_name = data.name
        payload = data.payload
        file_object.write(struct.pack('b',typeToNum[tag_type]))
        if tag_type == "TAG_End":
            return
        file_object.write(struct.pack('>h',len(tag_name)))
        file_object.write(tag_name.encode("utf-8"))
    else:
        payload = data.payload
        pass
    if tag_type == "TAG_Byte":
        file_object.write(struct.pack('b',payload))
    elif tag_type == "TAG_Short":
        file_object.write(struct.pack('>h',payload))
    elif tag_type == "TAG_Int":
        file_object.write(struct.pack('>i',payload))
    elif tag_type == "TAG_Long":
        file_object.write(struct.pack('>q',payload))
    elif tag_type == "TAG_Float":
        file_object.write(struct.pack('>f',payload))
    elif tag_type == "TAG_Double":
        file_object.write(struct.pack('>d',payload))
    elif tag_type == "TAG_Byte_Array":
        file_object.write(struct.pack('>i',len(payload)))
        for element in payload:
            file_object.write(struct.pack('b',payload))
    elif tag_type == "TAG_String":
        file_object.write(struct.pack('>H',len(payload)))
        file_object.write(payload.encode("utf-8"))
    elif tag_type == "TAG_List":
        writeList(file_object, payload, data.ltype)
    elif tag_type == "TAG_Compound":
        writeCompound(file_object, payload)
    elif tag_type == "TAG_Int_Array":
        file_object.write(struct.pack('>i',len(payload)))
        for element in payload:
            file_object.write(struct.pack('>i',payload))

def getTag(file_object, tag_type=None):
    ltype=None
    if tag_type is None:
        raw_type = struct.unpack('b', file_object.read(1))[0]
        tag_type = numToType[raw_type]
        if tag_type == "TAG_End":
            raise EndTag
        length = struct.unpack('>h', file_object.read(2))[0]
        name = file_object.read(length).decode("utf-8")
    else:
        name = ""
        pass
    if tag_type == "TAG_Byte":
        payload = struct.unpack('b', file_object.read(1))[0]
    elif tag_type == "TAG_Short":
        payload = struct.unpack('>h', file_object.read(2))[0]
    elif tag_type == "TAG_Int":
        payload = struct.unpack('>i', file_object.read(4))[0]
    elif tag_type == "TAG_Long":
        payload = struct.unpack('>q', file_object.read(8))[0]
    elif tag_type == "TAG_Float":
        payload = struct.unpack('>f', file_object.read(4))[0]
    elif tag_type == "TAG_Double":
        payload = struct.unpack('>d', file_object.read(8))[0]
    elif tag_type == "TAG_Byte_Array":
        payload_size = struct.unpack('>i', file_object.read(4))[0]
        payload = [struct.unpack('b', file_object.read(1))[0] for _ in range(payload_size)]
    elif tag_type == "TAG_String":
        payload_size = struct.unpack('>h', file_object.read(2))[0]
        payload = file_object.read(payload_size).decode("utf-8")
    elif tag_type == "TAG_List":
        payload_type = numToType[struct.unpack('b', file_object.read(1))[0]]
        payload_size = struct.unpack('>i', file_object.read(4))[0]
        payload = getList(file_object, payload_type, payload_size)
        ltype = payload_type
    elif tag_type == "TAG_Compound":
        payload = getCompound(file_object)
    elif tag_type == "TAG_Int_Array":
        payload_size = struct.unpack('>i', file_object.read(4))[0]
        payload = [struct.unpack('>i', file_object.read(4))[0] for _ in range(payload_size)]
    else:
        payload = "ERROR, tag_type = " + tag_type
    return Tag(tag_type, name, payload, ltype)

def read(filename):
    with gzip.open(filename, "rb") as f:
        return getTag(f)

def write(filename, nbtdata):
    with gzip.open(filename, "wb") as f:
        writeTag(f, nbtdata)

if __name__ == "__main__":
    with gzip.open(sys.argv[1], "rb") as f:
        decoded = getTag(f)
        print(decoded)
        with gzip.open("out.nbt", "wb") as fw:
            writeTag(fw, decoded)
