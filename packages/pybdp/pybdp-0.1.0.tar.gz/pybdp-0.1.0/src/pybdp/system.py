from .convenience import find_duplicates
from pprint import pprint


class System:
    def __init__(self, json: dict, processors_map: dict, wires_map: dict):
        self.raw_data = json
        self.id = json["ID"]
        self.name = json["Name"]
        if "Description" in json:
            self.description = json["Description"]
        else:
            self.description = None

        self._load_processors(json["Processors"], processors_map)
        self._load_wires(json["Wires"], wires_map)
        self._add_processor_port_terminal_maps()
        self._check_ports()
        self.processors_map = processors_map

    def _load_processors(self, processors, processors_map):
        bad_processors = [
            processor for processor in processors if processor not in processors_map
        ]
        assert (
            len(bad_processors) == 0
        ), "The system {} references processor IDs of {} which are not valid processor IDs".format(
            self.name, bad_processors
        )
        self.processors = [processors_map[processor] for processor in processors]

        # CHECK DUPLICATES
        duplicate_processors = find_duplicates(self.processors)
        assert (
            len(duplicate_processors) == 0
        ), f"Duplicate references to the same processor IDs found in system {self.name} (only load processors once in a system): {duplicate_processors}"

    def _add_processor_port_terminal_maps(self):
        self.processor_ports_map = {}
        self.processor_terminals_map = {}
        for processor in self.processors:
            self.processor_ports_map[processor] = [
                [] for _ in range(len(processor.ports))
            ]
            self.processor_terminals_map[processor] = [
                [] for _ in range(len(processor.terminals))
            ]

        for wire in self.wires:
            self.processor_terminals_map[wire.source["Processor"]][
                wire.source["Index"]
            ].append(wire)
            self.processor_ports_map[wire.target["Processor"]][
                wire.target["Index"]
            ].append(wire)

    def _load_wires(self, wires, wires_map):
        bad_wires = [wire for wire in wires if wire not in wires_map]
        assert (
            len(bad_wires) == 0
        ), "The system {} references wire IDs of {} which are not valid wire IDs".format(
            self.name, bad_wires
        )
        self.wires = [wires_map[wire] for wire in wires]

        # CHECK DUPLICATES
        duplicate_wire = find_duplicates(self.wires)
        assert (
            len(duplicate_wire) == 0
        ), f"Duplicate references to the same wire IDs found in system {self.name} (only load wires once in a system): {duplicate_wire}"

    def _check_ports(self):
        # Check only one wire into each port
        filled_ports = set()
        for wire in self.wires:
            payload = (wire.target["Processor"].id, wire.target["Index"])
            assert (
                payload not in filled_ports
            ), "For system {} there are multiple wires pointing into the processor ID + index of {}, {}".format(
                self.name, payload[0], payload[1]
            )
            filled_ports.add(payload)

    def __repr__(self):
        return "< System Name: {} ID: {} Processors: {} Wires: {} >".format(
            self.name,
            self.id,
            [x.name for x in self.processors],
            [x.id for x in self.wires],
        )

    def get_open_ports(self):
        out = []
        for processor in self.processor_ports_map:
            for i, port_list in enumerate(self.processor_ports_map[processor]):
                if len(port_list) == 0:
                    out.append([processor, i, processor.ports[i]])
        return out

    def get_available_terminals(self, open_only=False):
        out = []
        for processor in self.processor_terminals_map:
            for i, terminal_list in enumerate(self.processor_terminals_map[processor]):
                if open_only:
                    if len(terminal_list) == 0:
                        out.append([processor, i, processor.terminals[i]])
                else:
                    out.append([processor, i, processor.terminals[i]])
        return out

    def is_connected(self):
        processors = set([x.id for x in self.processors])

        q = [processors.pop()]
        while len(q) > 0:
            cur = q.pop()
            cur = self.processors_map[cur]
            wires = [
                x
                for x in self.wires
                if x.source["Processor"].id == cur.id
                or x.target["Processor"].id == cur.id
            ]
            for y in wires:
                x = y.target["Processor"].id
                if x in processors:
                    q.append(x)
                    processors.remove(x)
                x = y.source["Processor"].id
                if x in processors:
                    q.append(x)
                    processors.remove(x)
        return len(processors) == 0

    def is_directed(self):
        processors = set([x.id for x in self.processors])
        while len(processors) > 0:
            q = [processors.pop()]
            visited = []
            while len(q) > 0:
                cur = q.pop()
                visited.append(cur)
                cur = self.processors_map[cur]
                wires = [x for x in self.wires if x.source["Processor"].id == cur.id]
                for x in wires:
                    x = x.target["Processor"].id
                    if x in processors:
                        q.append(x)
                        processors.remove(x)
                    if x in visited:
                        return False
        return True

    def is_valid(self):
        condition1 = len(self.get_open_ports()) == 0
        condition2 = self.is_connected()
        return condition1 and condition2

    def is_dynamical(self):
        return not self.is_directed()

    def get_connected_components(self):
        processors = set([x.id for x in self.processors])
        clusters = []
        while len(processors) > 0:
            cluster = []
            q = [processors.pop()]
            while len(q) > 0:
                cur = q.pop()
                cur = self.processors_map[cur]
                cluster.append(cur)
                wires = [
                    x
                    for x in self.wires
                    if x.source["Processor"].id == cur.id
                    or x.target["Processor"].id == cur.id
                ]
                for y in wires:
                    x = y.target["Processor"].id
                    if x in processors:
                        q.append(x)
                        processors.remove(x)
                    x = y.source["Processor"].id
                    if x in processors:
                        q.append(x)
                        processors.remove(x)
            clusters.append(cluster)
        return clusters

    def get_hierarchy(self):
        out = {}
        for processor in self.processors:
            if processor.is_primitive():
                out[processor.id] = processor
            else:
                out[processor.id] = processor.subsystem.get_hierarchy()
        return out

    def get_spaces(self, nested=False):
        if not nested:
            spaces = set().union(
                *(
                    [x.ports for x in self.processors]
                    + [x.terminals for x in self.processors]
                )
            )
            spaces = list(spaces)
        else:
            spaces = set()
            for processor in self.processors:
                if processor.is_primitive():
                    spaces.update(processor.ports)
                    spaces.update(processor.terminals)
                else:
                    spaces.update(processor.subsystem.get_spaces(nested=True))
            spaces = list(spaces)
        return spaces

    def get_subsystems(self):
        return [x.subsystem for x in self.processors if not x.is_primitive()]

    def make_processor_lazy(self):
        # Get open ports and terminals
        ports = self.get_open_ports()
        terminals = self.get_available_terminals(open_only=True)

        # Get spaces
        domain = list(map(lambda x: x[2].id, ports))
        codomain = list(map(lambda x: x[2].id, terminals))

        block_id = self.id + "-CP Block"
        processor_id = self.id + "-CP"

        block_scaffold = {
            "ID": block_id,
            "Name": self.name + "-CP Block",
            "Description": "A lazy loaded composite processor block for {}".format(
                self.name
            ),
            "Domain": domain,
            "Codomain": codomain,
        }

        port_mappings = []
        for d in ports:
            port_mappings.append({"Processor": d[0].id, "Index": d[1]})
        terminal_mappings = []
        for d in terminals:
            terminal_mappings.append({"Processor": d[0].id, "Index": d[1]})

        processor_scaffold = {
            "ID": processor_id,
            "Name": self.name + "-CP",
            "Description": "A lazy loaded composite processor block for {}".format(
                self.name
            ),
            "Parent": block_id,
            "Ports": domain,
            "Terminals": codomain,
            "Subsystem": {
                "System ID": self.id,
                "Port Mappings": port_mappings,
                "Terminal Mappings": terminal_mappings,
            },
        }

        print("-----Add the following to your JSON-----")
        print()
        print("Add to blocks:")
        pprint(block_scaffold)
        print()
        print("Add to processors:")
        pprint(processor_scaffold)

    def create_mermaid_graphic(
        self,
        out="",
        system_i=0,
        top_level=True,
        processor_map={},
        ports_map={},
        terminals_map={},
        processor_i=0,
        recursive=False,
    ):

        out += "subgraph GS{}[{}]\n".format(system_i, self.name)
        system_i += 1

        for p in self.processors:
            if recursive:
                out, processor_i, system_i = p.create_mermaid_graphic_composite(
                    out=out,
                    processor_i=processor_i,
                    processor_map=processor_map,
                    ports_map=ports_map,
                    terminals_map=terminals_map,
                    top_level=False,
                    system_i=system_i,
                )
            else:
                out, processor_i, system_i = p.create_mermaid_graphic(
                    out=out,
                    processor_i=processor_i,
                    processor_map=processor_map,
                    ports_map=ports_map,
                    terminals_map=terminals_map,
                    top_level=False,
                    system_i=system_i,
                )

        for wire in self.wires:
            out = wire.create_mermaid_graphic(out, terminals_map, ports_map)

        out += "end\n"
        if top_level:
            out = """```mermaid
---
config:
    layout: elk
---
graph LR
{}
```""".format(
                out
            )

        return out, processor_i, system_i


def load_system(json, processors_map, wires_map):
    return System(json, processors_map, wires_map)
