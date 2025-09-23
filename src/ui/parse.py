import ast
import re
import json
from .branch import Panel, ScrollablePanel, VList, HList
from .leaf import Button, CheckBox, Slider, Text, H1
from .base import UiElement, Group




branch_elements = ['>miml<', '>group<', '>txt<', '>vlist<', '>scroll-panel<', '>hlist<', '>panel<']
leaf_elements = ['>h1<', '>slider<', '>checkbox<']

def get_tag_attributes(tag: str):
    attrs = {}

    if not tag.endswith(')'): return {} 
    if not '<(' in tag: return {}

    string_to_parse = tag.split('<(')[1][0:-1] # cutting the inside of the tags parenthesis 
    list_to_parse = string_to_parse.split(",")
    list_to_parse = [x.strip() for x in list_to_parse]
    for item in list_to_parse:
        print(f"item : {item}")
        key = item.split('=')[0].strip()
        value = item.split('=')[1].strip()
        value = value.replace(';', ',') if value.find(';') else value
        attrs[key] = value

    print("blabla"*12)

    print(attrs)

    return attrs if attrs else {}

    
def parse_miml(miml_txt: str, DEBUG: bool = False):

    DEBUG = True
    parse_list = re.split(r"(>[\/]?\w+<(?:\([^\)]+\))?)", miml_txt)
    # cleaning the list from empty strings etc
    parse_list = [x.strip() for x in parse_list if x.strip()]

    print(parse_list)
    # okay so the things we are going to need are 2 stacks 2 lists for typing
    stack = []  # lets try to solve this with one stack 

    root = {"type": '>panel<', 'kids': [], 'attributes': {}}

    # branches will be like 
    # kids will be like

    for element in parse_list:
        # loop variables 
        e_type = 'content'  # this can be [content, closing_tag, opening_tag, attr_tag  (a tag that has attributes)
        attrs = {}

        # checking element info
        if element.startswith('>'):
            if element[1] == '/':
                e_type = 'closing_tag'
            else:
                e_type = 'opening_tag'
        attrs = get_tag_attributes(element) if e_type == 'opening_tag' else {}

        # main parsing logic 
        if e_type == 'opening_tag': 
            tag = element.split('(')[0]
            obj = {'type': tag, 'kids': [], 'attributes': attrs}
            stack.append(obj)

            # ~~~~~~~~~~~
            if DEBUG:
                if element in branch_elements:
                    print(f"\033[96m~branch_elment - {element}\033[0m")
                elif element in leaf_elements:
                    print(f"\033[92m~leaf_element - {element}\033[0m")
                else:
                    print(f"\033[91m~leaf_element - {element}\033[0m")
                    
                if attrs:
                    print(f"\033[93m--> attributes ({attrs})\033[0m")


        elif e_type == 'closing_tag':
            tag = element.replace('>/', '>')
            kid = stack.pop()
            papa = stack[-1] if stack else root 
            papa['kids'].append(kid)

            # ~~~~~~~~~~~
            if DEBUG:
                if tag in branch_elements:
                    print(f"\033[96m~branch_elment_closure - {element}\033[0m")
                elif tag in leaf_elements:
                    print(f"\033[92m~leaf_element_closure - {element}\033[0m")

        else:  # if its just content    
            stack[-1]['kids'].append(element)

            # ~~~~~~~~~~~
            if DEBUG:
                print(f"\033[95m~str_element - {element}\033[0m")

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if stack and stack[0]['type'] == '>miml<':
        root['kids'] += stack[0]['kids']
    else:
        root['kids'] += stack

    if DEBUG:
        print(stack)
        print("root")
        print('~'*13)
        print(json.dumps(root, indent=4))
    return root['kids'][0] if root['kids'][0]['type'] == '>miml<' else root


miml_txt = """>miml<
>h1< this is our testing header >/h1<
>txt< this is testing txt >/txt<
>txt< lets write something that has something >txt<(color=red, name=imp) important >/txt< in it okay >/txt<
>slider< sfx >/slider<
>slider< sound >/slider<
>list<
    >checkbox< show fps>/checkbox<
    >checkbox< debug >checkbox<
>/list<
>/miml<
"""

ui_tree = parse_miml(miml_txt, True)

# now we have to convert the ui_tree to a ui group

# the classes we need to make
# group
# panel (scrollable & not scrollable)
# list (vertical and horizontal flow)
# txt
# slider 
# checkbox
# button
CLASSES = {
        '>group<': Group,
        '>panel<': Panel,
        '>hlist<': HList,
        '>txt<': Text,
        '>h1<': H1,
        '>slider<': Slider,
        '>checkbox<': CheckBox,
        '>btn<': Button,
        '>miml<': ScrollablePanel,
        '>vlist<': VList
        }
# now im supposed to traverse the ui_tree dict and create a panel object that contains everything
# lets make sure i have the classes ready first 
debug_panel = """>miml<
>panel<
  >vlist<(size=[100; 100])
    >txt< Debug Panel>/txt< >txt<\n>/txt<
    >txt< this is a test for the miml language we are trying to build debug panel with it >/txt<
  >/vlist<
>/panel<
>/miml<
"""
debug_txt = """>miml<(size=(100; 100))
>txt<(font_size='big') Testing Miml >/txt<
>scroll-panel<
  >vlist<(v_gap=8)
    >btn< test btn >/btn<
    >slider< test slider >/slider<
    >checkbox< test checkbox >/checkbox<
    now the testing text element hehe
  >/vlist<
>/scroll-panel<
>/miml<
"""
parse_miml(debug_panel)
#def mimalize(miml, classes=classes):
#    ui_tree = parse_miml(miml)
#    root_class = classes[ui_tree['type']]
#    root = root_class(**ui_tree['attributes'])

def cast_attr_value(value: str):
    """
    Try to cast a string value into int, float, bool, list, tuple, or leave as str.
    Uses `ast.literal_eval` for safe parsing of Python literals.
    """
    if value is None:
        return None

    value = value.strip()

    # try numbers
    if value.isdigit():
        return int(value)

    try:
        return float(value)
    except ValueError:
        pass

    # booleans
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # try safe literal evaluation (handles lists, tuples, dicts, strings, etc.)
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        pass

    # fallback: keep as string
    return value


def mimlize(miml: str, classes=CLASSES, parent=None):
    """
    Convert MIML text into actual UI tree objects.
    """
    ui_tree = parse_miml(miml, DEBUG=False)

    def build(node):
        if isinstance(node, str):
            # This case only happens if parse_miml() returned raw text
            return node.strip()  # <-- return plain string now, not Text()

        node_type = node["type"].split('<(')
        node_type = node_type[0] if len(node_type) == 1 else node_type[0] + '<'
        attrs = node["attributes"] or {}
        kids = node["kids"]

        # check if leaf text content exists
        if len(kids) == 1 and isinstance(kids[0], str):
            attrs["text"] = kids[0].strip()
            kids = []  # no nested children anymore

        # cast attributes
        casted_attrs = {k: cast_attr_value(v) for k, v in attrs.items()}


        # look up class
        if node_type not in classes or classes[node_type] is None:
            raise ValueError(f"Unknown element type: {node_type}")

        cls = classes[node_type]
        obj = cls(**casted_attrs)

        # recurse into children (non-leaf)
        for kid in kids:
            child_obj = build(kid)
            if child_obj and hasattr(obj, 'children'):
                obj.add_child(child_obj)

        return obj

    output = build(ui_tree)
    if parent:
        output.parent = parent
        if hasattr(output, 'children'):
            for kid in output:
                kid.root = parent.root
                if kid.name:
                    if parent.named_children.get(kid.name):
                        parent.named_children[kid.name].append(kid)
                    else:
                        parent.named_children[kid.name] = [kid]            
        parent.add_child(output)

    return output 



