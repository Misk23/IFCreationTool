import sys
from os.path import join, dirname
from textx import metamodel_from_file


opposite_direction = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
    "NW": "SE",
    "SE": "NW",
    "NE": "SW",
    "SW": "NE"
}


def print_contains(obj):
    contains = ""
    for c in obj.contains:
        contains += c.name + " "
    print(f"Inside you see {contains}")


def print_requirements(obj):
    requirements = ""
    for c in obj.requirements:
        requirements += c.name + " "
    print(f"You neeed {requirements} first")


class Object(object):

    def __init__(self, name):
        self.name = name
        self.description = ""
        self.contains = []
        self.requirements = []


class Section(object):

    def __init__(self, name):
        self.name = name
        self.description = ""
        self.contains = []
        self.requirements = []
        self.links = {}

    def print_directions(self):
        for direction in self.links:
            print(f"On {direction} there is {self.links[direction].name}")


class Player(object):

    def __init__(self):
        self.inventory = []
        self.current_section = None
        self.finish_section = None

    def print_player(self):
        inventory = ""
        for o in self.inventory:
            inventory += o.name + " "
        print(f"Player has {inventory} and is currently in {self.current_section.name}")

    def set_section(self, target_section):
        self.current_section = target_section
        print(f"{self.current_section.description}")
        if self.current_section == self.finish_section:
            print("\x1B[3mTHE END\x1B[23m")
            sys.exit()
        print_contains(self.current_section)
        self.current_section.print_directions()


class Game(object):

    def __init__(self):
        self.objects = []
        self.sections = []
        self.player = None
        self.start = None
        self.finish = None

    def load_objects(self, model):
        for o in model.objects:
            obj = Object(o.name)
            self.objects.append(obj)

    def load_sections(self, model):
        for s in model.sections:
            section = Section(s.name)
            self.sections.append(section)

    def load_common_properties(self, attr, model_attr):
        for index, a in enumerate(model_attr):
            for prop in a.properties:
                if prop.__class__.__name__ == "DescriptionProperty":
                    attr[index].description = prop.description

                if prop.__class__.__name__ == "ContainsProperty":
                    for contained_obj in prop.contains:
                        for obj in self.objects:
                            if contained_obj.name == obj.name:
                                attr[index].contains.append(obj)

                if prop.__class__.__name__ == "RequirementsProperty":
                    for required_obj in prop.requirements:
                        for obj in self.objects:
                            if required_obj.name == obj.name:
                                attr[index].requirements.append(obj)

    def load_object_properties(self, model):
        self.load_common_properties(self.objects, model.objects)

    def load_section_properties(self, model):
        self.load_common_properties(self.sections, model.sections)

        for index, s in enumerate(model.sections):
            for prop in s.properties:
                if prop.__class__.__name__ == "LinkProperty":
                    for section in self.sections:
                        if prop.link.name == section.name:
                            self.sections[index].links[prop.direction] = section
                            section.links[opposite_direction[prop.direction]] = self.sections[index]

    def load_player(self, model):
        self.player = Player()
        self.player.set_section(self.start)
        self.player.finish_section = self.finish

        if model.player:
            for prop in model.player.properties:
                if prop.__class__.__name__ == "InventoryProperty":
                    for inv_obj in prop.inventory:
                        for obj in self.objects:
                            if inv_obj.name == obj.name:
                                self.player.inventory.append(obj)

    def load_finish_and_start_sections(self, model):
        for s in self.sections:
            if model.start.name == s.name:
                self.start = s
            if model.finish.name == s.name:
                self.finish = s

    def build(self, model):
        self.load_objects(model)
        self.load_object_properties(model)
        self.load_sections(model)
        self.load_section_properties(model)
        self.load_finish_and_start_sections(model)
        self.load_player(model)

    def play(self, model):
        for c in model.commands:
            if c.__class__.__name__ == "OpenCommand":
                print(f"\x1B[3mOpen {c.object}\x1B[23m")
                found = False
                for obj in self.player.current_section.contains:
                    if obj.name == c.object:
                        found = True
                        if obj.contains:
                            for req in obj.requirements:
                                if req in self.player.inventory:
                                    obj.requirements.remove(req)
                            if obj.requirements:
                                print_requirements(obj)
                            else:
                                print_contains(obj)
                        else:
                            print(f"Nothing there")

                if not found:
                    print("You can't open that")

            if c.__class__.__name__ == "MoveCommand":
                print(f"\x1B[3mMove {c.direction}\x1B[23m")
                if c.direction in self.player.current_section.links:
                    target_section = self.player.current_section.links[c.direction]
                    for req in target_section.requirements:
                        if req in self.player.inventory:
                            target_section.requirements.remove(req)
                    if target_section.requirements:
                        print_requirements(target_section)
                    else:
                        self.player.set_section(target_section)
                else:
                    print("There is nothing there")

            if c.__class__.__name__ == "GoCommand":
                print(f"\x1B[3mGo {c.section}\x1B[23m")
                found = False
                for sec in self.player.current_section.links.values():
                    if sec.name == c.section:
                        target_section = sec
                        found = True
                        for req in target_section.requirements:
                            if req in self.player.inventory:
                                target_section.requirements.remove(req)
                        if target_section.requirements:
                            print_requirements(target_section)
                        else:
                            self.player.set_section(target_section)
                if not found:
                    print("You can't go there")

            if c.__class__.__name__ == "TakeCommand":
                print(f"\x1B[3mTake {c.object}\x1B[23m")
                found = False
                for obj in self.player.current_section.contains:
                    if obj.name == c.object:
                        self.player.inventory.append(obj)
                        self.player.current_section.contains.remove(obj)
                        print(f"You now have {c.object}")
                        found = True
                    else:
                        for cont_obj in obj.contains:
                            if cont_obj.name == c.object:
                                for req in obj.requirements:
                                    if req in self.player.inventory:
                                        obj.requirements.remove(req)
                                if obj.requirements:
                                    print_requirements(obj)
                                else:
                                    self.player.inventory.append(cont_obj)
                                    obj.contains.remove(cont_obj)
                                    print(f"You now have {c.object}")
                                    found = True
                if not found:
                    print("You can't take that")

            if c.__class__.__name__ == "DropCommand":
                print(f"\x1B[3mDrop {c.object}\x1B[23m")
                found = False
                for obj in self.player.inventory:
                    if obj.name == c.object:
                        found = True
                        self.player.inventory.remove(obj)
                        self.player.current_section.contains.append(obj)
                        print(f"You drop {c.object} in {self.player.current_section.name}")
                if not found:
                    print("You can't drop that")

            if c.__class__.__name__ == "LookCommand":
                print(f"\x1B[3mLook {c.object}\x1B[23m")
                found = False
                if c.object == "around":
                    print(f"{self.player.current_section.description}")
                    print_contains(self.player.current_section)
                    self.player.current_section.print_directions()
                    found = True

                for obj in self.player.current_section.contains:
                    if obj.name == c.object:
                        print(f"{obj.description}")
                        found = True
                if not found:
                    print("You can't see that")


def main():
    this_folder = dirname(__file__)
    creation_tool_mm = metamodel_from_file(join(this_folder, 'creationTool.tx'))
    game_mm = metamodel_from_file(join(this_folder, 'game.tx'))

    program_model = creation_tool_mm.model_from_file(join(this_folder, 'program.ct'))
    game_example_model = game_mm.model_from_file(join(this_folder, 'example.game'))

    game = Game()
    game.build(program_model)
    game.play(game_example_model)


if __name__ == "__main__":
    main()
