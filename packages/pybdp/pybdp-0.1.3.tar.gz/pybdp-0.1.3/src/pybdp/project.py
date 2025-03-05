from jsonschema import validate
from .schema import schema
from .toolbox import load_toolbox
from .workbench import load_workbench
from .convenience import find_duplicates


class Project:
    def __init__(self, json: dict):
        self.raw_data = json

        # Load toolbox
        self.toolbox = load_toolbox(json["Toolbox"])

        # Bring in mapping and objects to the project level
        self.blocks = self.toolbox.blocks
        self.spaces = self.toolbox.spaces
        self.blocks_map = self.toolbox.blocks_map
        self.spaces_map = self.toolbox.spaces_map
        self.toolbox_map = self.toolbox.toolbox_map

        # Load workbench
        self.workbench = load_workbench(
            json["Workbench"], self.blocks_map, self.spaces_map
        )

        self.processors = self.workbench.processors
        self.wires = self.workbench.wires
        self.systems = self.workbench.systems

        self.processors_map = self.workbench.processors_map
        self.wires_map = self.workbench.wires_map
        self.systems_map = self.workbench.systems_map

        self._validate_unique_ids()

        # Build out composite processors
        for processor in self.processors:
            processor._load_subsytem(self.systems_map, self.processors_map)

    def _validate_unique_ids(self):
        duplicates = find_duplicates(
            self.blocks + self.spaces + self.processors + self.wires + self.systems
        )
        assert (
            len(duplicates) == 0
        ), f"Overlapping IDs between the toolbox and workbench found: {duplicates}"

    def __repr__(self):
        return """< Project
Toolbox:

{}

Workbench:

{} >""".format(
            self.toolbox, self.workbench
        )


def load_project(json: dict):
    validate(json, schema)
    return Project(json)
