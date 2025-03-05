class Block:
    def __init__(self, json: dict):
        self.raw_data = json
        self.id = json["ID"]
        self.name = json["Name"]
        if "Description" in json:
            self.description = json["Description"]
        else:
            self.description = None
        self.domain = json["Domain"]
        self.codomain = json["Codomain"]

    def __repr__(self):
        return "< Block ID: {} Name: {} {}->{}>".format(
            self.id,
            self.name,
            [x.name for x in self.domain],
            [x.name for x in self.codomain],
        )


def load_block(json: dict):
    return Block(json)
