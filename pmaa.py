import os.path
import struct

from common import ParameterType  # , CurveType


class ResParameterArchive:
    _formats = (('2I', 8), ('4x', 4), ('4x', 4), ('2I', 8))
    _format = ''.join(map(lambda x: x[0], _formats))
    _size = sum(map(lambda x: x[1], _formats))

    def __init__(self):
        self.typeVersion = 0
        self.type = ''

    def read(self, data, pos=0):
        basePos = pos

        bom = '<' if struct.unpack_from('I', data, pos + self._formats[0][1])[0] & 0x01000001 else '>'

        (signature,
         version,
         self.typeVersion,
         typeLength) = struct.unpack_from(bom + self._format, data, pos); pos += self._size

        assert signature == 0x504D4141  # PMAA
        assert version == 1

        self.type = data[pos:pos + typeLength].rstrip(b'\0').decode(); pos += typeLength

        return bom, pos - basePos


class Curve:
    _formats = (('2I', 8), ('3f', 12))

    def __init__(self):
        self.numUse = 0
        self.curveType = 0
        self.values = None

    def read(self, data, pos, bom):
        (self.numUse,
         self.curveType) = struct.unpack_from(bom + self._formats[0][0], data, pos); pos += self._formats[0][1]

        assert self.numUse % 3 == 0
        numUse = self.numUse // 3
        assert numUse <= 10

        self.values = tuple(struct.unpack_from(bom + self._formats[1][0], data, pos + i * self._formats[1][1]) for i in range(numUse)); pos += numUse * self._formats[1][1]
        assert (bom == '<' and data[pos:pos + (10 - numUse) * self._formats[1][1]] == b'\x00\x00\x80?' * (3 * (10 - numUse))) or \
               (bom == '>' and data[pos:pos + (10 - numUse) * self._formats[1][1]] == b'?\x80\x00\x00' * (3 * (10 - numUse)))

        return self._formats[0][1] + 10 * self._formats[1][1]

    # def __str__(self):
    #     return ' '.join(map(str, (self.numUse, CurveType(self.curveType), self.values)))


class ResParameter:
    _format = '3I'
    _size = 3 * 4

    def __init__(self):
        self.type = None
        self.nameHash = 0
        self.value = None

    def read(self, data, pos, bom):
        basePos = pos

        (dataSize,
         _type,
         self.nameHash) = struct.unpack_from(bom + self._format, data, pos); pos += self._size

        assert _type <= ParameterType.curve4
        self.type = ParameterType(_type)

        if _type == ParameterType.bool:
            self.value = struct.unpack_from('?', data, pos)[0]; pos += 1

        elif _type == ParameterType.f32:
            self.value = struct.unpack_from(bom + 'f', data, pos)[0]; pos += 4

        elif _type == ParameterType.int:
            self.value = struct.unpack_from(bom + 'i', data, pos)[0]; pos += 4

        elif _type == ParameterType.vec2:
            self.value = struct.unpack_from(bom + '2f', data, pos); pos += 2 * 4

        elif _type == ParameterType.vec3:
            self.value = struct.unpack_from(bom + '3f', data, pos); pos += 3 * 4

        elif _type == ParameterType.vec4:
            self.value = struct.unpack_from(bom + '4f', data, pos); pos += 4 * 4

        elif _type == ParameterType.color:
            self.value = struct.unpack_from(bom + '4f', data, pos); pos += 4 * 4

        elif _type == ParameterType.string32:
            length = dataSize - (pos - basePos)
            self.value = struct.unpack_from('%ds' % length, data, pos)[0]; pos += length

        elif _type == ParameterType.string64:
            length = dataSize - (pos - basePos)
            self.value = struct.unpack_from('%ds' % length, data, pos)[0]; pos += length

        elif _type <= ParameterType.curve4:
            self.value = []
            for i in range(_type - ParameterType.curve1 + 1):
                curve = Curve()
                pos += curve.read(data, pos, bom)
                self.value.append(curve)

        else:  # Should not reach here
            self.value = None

        # print(self.type, dataSize, pos - basePos)
        assert pos - basePos == dataSize
        return dataSize


class ResParameterObj:
    _format = '4I'
    _size = 4 * 4

    def __init__(self):
        self.param = []
        self.nameHash = 0
        self._c = 0

    def read(self, data, pos, bom):
        basePos = pos

        (dataSize,
         num,
         self.nameHash,
         self._c) = struct.unpack_from(bom + self._format, data, pos); pos += self._size

        self.param.clear()
        for _ in range(num):
            childParam = ResParameter()
            pos += childParam.read(data, pos, bom)
            self.param.append(childParam)

        assert pos - basePos == dataSize
        return dataSize


class ResParameterList:
    _format = '4I'
    _size = 4 * 4

    def __init__(self):
        self.nameHash = 0
        self.lists = []
        self.objs = []

    def read(self, data, pos, bom):
        basePos = pos

        (dataSize,
         self.nameHash,
         listNum,
         objNum) = struct.unpack_from(bom + self._format, data, pos); pos += self._size

        self.lists.clear()
        for _ in range(listNum):
            childList = ResParameterList()
            pos += childList.read(data, pos, bom)
            self.lists.append(childList)

        self.objs.clear()
        for _ in range(objNum):
            childObj = ResParameterObj()
            pos += childObj.read(data, pos, bom)
            self.objs.append(childObj)

        assert pos - basePos == dataSize
        return dataSize


def readPMAA(path):
    pathNoExt, ext = os.path.splitext(path)
    name = os.path.basename(pathNoExt)

    with open(path, 'rb') as inf:
        inb = inf.read()

    pos = 0

    pmaa = ResParameterArchive()
    bom, size = pmaa.read(inb, pos)

    pos += size

    rootList = ResParameterList()
    rootList.read(inb, pos, bom)

    # print(".b%s" % pmaa.type)
    # print(ext)

    assert ext == (".b%s" % pmaa.type)

    return name, pmaa, rootList


if __name__ == '__main__':
    path = r'D:\NSMBU v1.3.0\content\Common\env\env_pack\CS_All.bagllmap'
    name, pmaa, rootList = readPMAA(path)
    print(name, pmaa.type, pmaa.typeVersion)
