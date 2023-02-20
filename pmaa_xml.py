from common import ParameterType


class Header:
    def __init__(self):
        self.type = ''
        self.version = 0

    def set(self, resArchive):
        self.type = resArchive.type
        self.version = resArchive.typeVersion

    def getAsDict(self):
        return {
            "@type": self.type,
            "@version": str(self.version),
            "@date": "time stamp : 2012/05/19 01:21:19"
        }


class Parameter:
    def __init__(self):
        self.name = ''
        self.type = None
        self.value = None

    def set(self, res):
        self.name = "0x%08X" % res.nameHash
        self.type = res.type
        self.value = res.value

    def getAsDict(self):
        _type = self.type
        assert isinstance(_type, ParameterType)

        _dict = {
            "@name": self.name,
            "@type": _type.name
        }

        if _type == ParameterType.bool:
            _dict["@value"] = "true" if self.value else "false"

        elif _type == ParameterType.f32:
            _dict["@value"] = "%.6f" % self.value

        elif _type == ParameterType.int:
            _dict["@value"] = "%d" % self.value

        elif _type == ParameterType.vec2:
            _dict["@value"] = "%.6f %.6f" % self.value

        elif _type == ParameterType.vec3:
            _dict["@value"] = "%.6f %.6f %.6f" % self.value

        elif _type == ParameterType.vec4:
            _dict["@value"] = "%.6f %.6f %.6f %.6f" % self.value

        elif _type == ParameterType.color:
            _dict["@value"] = "%.6f %.6f %.6f %.6f" % self.value

        elif _type == ParameterType.string32:
            _dict["@value"] = self.value.split(b'\0')[0].decode()

        elif _type == ParameterType.string64:
            _dict["@value"] = self.value.split(b'\0')[0].decode()

        elif _type <= ParameterType.curve4:
            assert len(self.value) == (_type - ParameterType.curve1 + 1)
            _dict["#text"] = ''.join(''.join(('\n', "%d %d\n" % (curve.numUse, curve.curveType), ''.join(("%f %f %f\n" % value) for value in curve.values))) for curve in self.value)
            # text = []
            # for curve in self.value:
            #     text.append("%d %d\n" % (curve.numUse, curve.curveType))
            #     for value in curve.values:
            #         text.append("%f %f %f\n" % value)
            # _dict["#text"] = '\n'.join(text)

        else:  # Should not happen
            pass

        return _dict


class ParameterArray:
    def __init__(self):
        self.name = ''
        self.childParams = []

    def set(self, resObj):
        self.name = "0x%08X" % resObj.nameHash

        self.childParams.clear()
        for child in resObj.param:
            child2 = Parameter()
            child2.set(child)
            self.childParams.append(child2)

    def getAsDict(self):
        _dict = {
            "@name": self.name
        }

        if self.childParams:
            _dict["param"] = [child.getAsDict() for child in self.childParams]

        return _dict


class ParameterList:
    def __init__(self):
        self.name = ''
        self.childLists = []
        self.childArrays = []

    def set(self, resList):
        self.name = "0x%08X" % resList.nameHash

        self.childLists.clear()
        for child in resList.lists:
            child2 = ParameterList()
            child2.set(child)
            self.childLists.append(child2)

        self.childArrays.clear()
        for child in resList.objs:
            child2 = ParameterArray()
            child2.set(child)
            self.childArrays.append(child2)

    def getAsDict(self):
        _dict = {
            "@name": self.name
        }

        if self.childLists:
            _dict["param_list"] = [child.getAsDict() for child in self.childLists]

        if self.childArrays:
            _dict["param_array"] = [child.getAsDict() for child in self.childArrays]

        return _dict


def pmaaToDict(pmaa, rootList):
    _dict = {
        "root": {}
    }

    header = Header()
    header.set(pmaa)

    _dict["root"]["header"] = header.getAsDict()

    root = ParameterList()
    root.set(rootList)

    _dict["root"]["data"] = {"param_list": root.getAsDict()}

    return _dict


if __name__ == '__main__':
    from pmaa import readPMAA
    path = r'D:\NSMBU v1.3.0\content\Common\env\env_pack\b_Isiyama.baglenv'
    name, pmaa, rootList = readPMAA(path)
    result = pmaaToDict(pmaa, rootList)
    import xmltodict
    result_xml = xmltodict.unparse(result, pretty=True)
    with open(name + '.' + pmaa.type, 'w') as outf:
        outf.write(result_xml)
