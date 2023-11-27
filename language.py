from language_utils import gen_boolean, gen_color, gen_date, gen_email, \
    gen_javascript, gen_number, gen_style, gen_text, gen_url, gen_name, \
    gen_target, gen_drop, gen_dir, gen_flag, gen_wtarget, gen_access_key, \
    gen_duration
from utils import rndstr, choice
from mutations import Mutations


class HTMLTag:
    def __init__(self, name, self_closing=False):
        self.name = name
        self.self_closing = self_closing
        self.attributes = []
        self.children = []
        self.id = rndstr(8)
        self.nameattr = rndstr(10)
        self.rndchrpos = {}
        self.mutator: Mutations = None
        self.content = rndstr(10)
        self.ids = []
        self.names = []

    def set_mutator(self, mutator):
        self.mutator = mutator

    def add_attribute(self, attr):
        attr.root = self
        self.attributes.append(attr)

    def __str__(self) -> str:
        # self mutate
        if self.mutator:
            # mutate attributes
            for attr in self.attributes:
                attr.__str__()
                if attr.attr == AttrType.ATTR_TAG_SPECIFIC and attr.kind != HTMLTagAttributeType.TypeFlag:
                    cases = [
                        lambda x: self.mutator.mutate_attr(x),
                        lambda x: self.mutator.mutate_value(x),
                    ]
                    choice(cases)(attr)
                elif attr.attr == AttrType.ATTR_EVENT:
                    self.mutator.mutate_js(attr.value)
            self.mutator.mutate_tag(tag=self)

        tag = ""
        if self.self_closing:
            tag = f"<{self.name}"
            tag += f" name=\"{self.nameattr}\" "
            tag += f" id=\"{self.id}\" "
            for attr in self.attributes:
                tag += f"{attr} "
            tag += "/>"
        else:
            tag = f"<{self.name}"
            tag += f" name=\"{self.nameattr}\" "
            tag += f" id=\"{self.id}\" "
            for attr in self.attributes:
                tag += f"{attr} "
            tag += ">"
            if len(self.children) == 0:
                tag += f"{self.content}"
            for child in self.children:
                tag += f"{child}"
            tag += f"</{self.name}>"

        for pos in self.rndchrpos:
            tag = tag[:pos] + self.rndchrpos[pos] + tag[pos:]

        return tag


class HTMLTagAttributeType:
    TypeText = 0
    TypeBoolean = 1
    TypeNumber = 2
    TypeColor = 3
    TypeJS = 4
    TypeStlye = 5
    TypeURL = 6
    TypeEmail = 7
    TypeDate = 8
    TypeTarget = 9
    TypeName = 10
    TypeFlag = 11
    TypeDrop = 12
    TypeDir = 13
    TypeWindowTarget = 14
    TypeAccessKey = 15
    TypeDuration = 16


Generators = {
    HTMLTagAttributeType.TypeText: gen_text,
    HTMLTagAttributeType.TypeBoolean: gen_boolean,
    HTMLTagAttributeType.TypeNumber: gen_number,
    HTMLTagAttributeType.TypeColor: gen_color,
    HTMLTagAttributeType.TypeJS: gen_javascript,
    HTMLTagAttributeType.TypeStlye: gen_style,
    HTMLTagAttributeType.TypeURL: gen_url,
    HTMLTagAttributeType.TypeEmail: gen_email,
    HTMLTagAttributeType.TypeDate: gen_date,
    HTMLTagAttributeType.TypeTarget: gen_target,
    HTMLTagAttributeType.TypeName: gen_name,
    HTMLTagAttributeType.TypeFlag: gen_flag,
    HTMLTagAttributeType.TypeDrop: gen_drop,
    HTMLTagAttributeType.TypeDir:  gen_dir,
    HTMLTagAttributeType.TypeWindowTarget: gen_wtarget,
    HTMLTagAttributeType.TypeAccessKey: gen_access_key,
    HTMLTagAttributeType.TypeDuration: gen_duration,
}


class AttrType:
    ATTR_NONE = -1
    ATTR_GLOBAL = 0
    ATTR_EVENT = 1
    ATTR_TAG_SPECIFIC = 2


class HTMLAttribute:
    def __init__(self, name, value_type, glob=True, root=None):
        self.root = root
        self.name = name
        self.kind = value_type
        if self.kind == HTMLTagAttributeType.TypeJS:
            self.attr = AttrType.ATTR_EVENT
        else:
            if glob:
                self.attr = AttrType.ATTR_GLOBAL
            else:
                self.attr = AttrType.ATTR_TAG_SPECIFIC

    def __str__(self) -> str:
        if self.kind == HTMLTagAttributeType.TypeTarget or self.kind == HTMLTagAttributeType.TypeName:
            self.value = Generators[self.kind](self.root)
        else:
            self.value = Generators[self.kind]()
        if not self.value:
            return self.name
        else:
            return f'{self.name}="{self.value}"'
