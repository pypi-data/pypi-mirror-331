from .space import load_space
from .block import load_block
from .convenience import find_duplicates


class Toolbox:
    def __init__(self, json: dict):
        self.raw_data = json
        self.blocks = [load_block(block) for block in json["Blocks"]]
        self.spaces = [load_space(space) for space in json["Spaces"]]

        self._validate_unique_ids()

        self.blocks_map = {block.id: block for block in self.blocks}
        self.spaces_map = {space.id: space for space in self.spaces}
        self.toolbox_map = self.blocks_map | self.spaces_map

        self._load_space_references()

    def _validate_unique_ids(self):
        duplicate_blocks = find_duplicates(self.blocks)
        assert (
            len(duplicate_blocks) == 0
        ), f"Duplicate block IDs found: {duplicate_blocks}"

        duplicate_spaces = find_duplicates(self.spaces)
        assert (
            len(duplicate_spaces) == 0
        ), f"Duplicate space IDs found: {duplicate_spaces}"

        duplicate_both = find_duplicates(self.blocks + self.spaces)
        assert (
            len(duplicate_both) == 0
        ), f"Overlapping block and space IDs found: {duplicate_both}"

    def _load_space_references(self):
        for block in self.blocks:
            # Assert the space IDs are valid
            for space in block.domain:
                assert (
                    space in self.spaces_map
                ), f"Space ID {space} referenced in {block.name} domain not found in spaces"

            for space in block.codomain:
                assert (
                    space in self.spaces_map
                ), f"Space ID {space} referenced in {block.name} codomain not found in spaces"

            # Link the spaces
            block.domain = [self.spaces_map[space] for space in block.domain]
            block.codomain = [self.spaces_map[space] for space in block.codomain]

    def __repr__(self):
        return """< Toolbox
Blocks: {}
Spaces: {} >""".format(
            [x.name for x in self.blocks],
            [x.name for x in self.spaces],
        )


def load_toolbox(json: dict):
    return Toolbox(json)
