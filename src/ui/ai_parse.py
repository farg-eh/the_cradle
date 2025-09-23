import ast
from .branch import Panel, ScrollablePanel, VList, HList
from .leaf import Button, CheckBox, Slider, Text
from .base import UiElement, Group

# Your UI class registry (fill this with your actual classes)
#classes = {
#    "panel": None,   # e.g. Panel
#    "vlist": None,   # e.g. VList
#    "text": Text,    # Text element
    # add others here...
#}

classes = {
        '>group<': Group,
        '>panel<': Panel,
        '>list<': HList,
        '>txt<': Text,
        '>slider<': Slider,
        '>checkbox<': CheckBox,
        '>btn<': Button
        }

def parse_miml(miml: str, DEBUG=False):
    """
    Very simple MIML parser → returns a nested dict representation.
    Example:
        >panel<
            v_gap=8
            >text< "Hello"
    """
    lines = [line.strip() for line in miml.strip().splitlines() if line.strip()]
    stack = []
    root = None

    for line in lines:
        if line.startswith(">") and "<" in line:
            # element
            tag = line.split("<")[0][1:]  # get word after '>'
            attrs = {}

            # parse inline attrs: key=value
            parts = line.split()
            for part in parts[1:]:
                if "=" in part:
                    k, v = part.split("=", 1)
                    attrs[k.strip()] = v.strip()

            node = {"type": tag, "attributes": attrs, "kids": []}

            if stack:
                stack[-1]["kids"].append(node)
            else:
                root = node

            stack.append(node)

            # inline text content `"something"`
            if '"' in line or "'" in line:
                text = line.split("<")[-1].strip()
                if text:
                    node["kids"].append(text.strip("\"'"))

        elif line.startswith(">end<"):
            stack.pop()

        else:
            # plain text line
            if stack:
                stack[-1]["kids"].append(line)

    return root


def cast_attr_value(value: str):
    """
    Try to cast attribute string values into proper Python types:
    - "123" → int
    - "3.14" → float
    - "True"/"False" → bool
    - "'hello'" or '"hello"' → str
    - fallback → original string
    """
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value


def mimalize(miml: str, classes=classes):
    """
    Convert MIML text into actual UI tree objects.
    """
    ui_tree = parse_miml(miml, DEBUG=False)

    def build(node):
        if isinstance(node, str):
            # raw string → Text object
            return Text(text=node.strip())

        node_type = node["type"]
        attrs = node["attributes"] or {}
        kids = node["kids"]

        # cast attributes
        casted_attrs = {k: cast_attr_value(v) for k, v in attrs.items()}

        # look up class
        if node_type not in classes or classes[node_type] is None:
            raise ValueError(f"Unknown element type: {node_type}")

        cls = classes[node_type]
        obj = cls(**casted_attrs)

        # recurse into children
        for kid in kids:
            child_obj = build(kid)
            if child_obj:
                obj.add_child(child_obj)

        return obj

    return build(ui_tree)
