from utils import choice, rndunicode, choice_percent


class Mutations:
    def __init__(self, strongness=0):
        self.strongness = strongness

    def mutate_attr(self, attr):
        cases = {
            70: lambda x: x,
            10: self.mutate_attr_newline,
            10: self.mutate_attr_unicode,
            10: self.mutate_attr_unicode_rnd_pos,
        }

        return choice_percent(cases)(attr)

    def mutate_value(self, attr):
        cases = {
            70: lambda x: x,
            20: self.mutate_value_newline,
            10: self.mutate_value_unicode,
        }

        return choice_percent(cases)(attr)

    def mutate_tag(self, tag):
        cases = {
            95: lambda x: x,
            5: self.mutate_tag_insert_random_pos,
        }

        return choice_percent(cases)(tag)

    def mutate_js(self, js: str):
        cases = {
            95: lambda x: x,
            5: self.mutate_js_insert_random_pos,
        }

        return choice_percent(cases)(js)

    @staticmethod
    def mutate_attr_newline(attr):
        attr.name = f"{attr.name}\n"
        return attr

    @staticmethod
    def mutate_attr_unicode(attr):
        attr.name = f"{attr.name}{rndunicode()}"
        return attr

    @staticmethod
    def mutate_attr_unicode_rnd_pos(attr):
        pos = choice(range(len(attr.name)))
        attr.name = f"{attr.name[:pos]}{rndunicode()}{attr.name[pos:]}"
        return attr

    @staticmethod
    def mutate_value_newline(attr):
        # find a random position in the value
        # and insert a newline
        if (attr.value is None):
            print("attr.value is None")
            print(attr)
            exit(0)
        pos = choice(range(len(attr.value)))
        attr.value = f"{attr.value[:pos]}\n{attr.value[pos:]}"
        return attr

    @staticmethod
    def mutate_value_unicode(attr):
        pos = choice(range(len(attr.value)))
        attr.value = f"{attr.value[:pos]}{rndunicode()}{attr.value[pos:]}"
        return attr

    @staticmethod
    def mutate_tag_insert_random_pos(tag):
        pos = choice(range(0, len(str(tag))))

        chars = {
            50: lambda: "\n",
            20: lambda: rndunicode(),
            20: lambda: choice([" ", "\t"]),
            10: lambda: choice(["\\", "'", "/", '"']),
        }

        nmutations = choice(range(1, 4))

        for _ in range(nmutations):
            mut = choice_percent(chars)
            tag.rndchrpos[pos] = mut()

        return tag

    @staticmethod
    def mutate_js_insert_random_pos(js: str):
        pos = choice(range(len(js)))
        chars = {
            70: lambda: "\n",
            20: lambda: choice([" ", "\t"]),
            10: lambda: choice(["\\", "'", "/", '"']),
        }

        nmutations = choice(range(1, 4))

        for _ in range(nmutations):
            js = f"{js[:pos]}{choice_percent(chars)()}{js[pos:]}"
        return js
