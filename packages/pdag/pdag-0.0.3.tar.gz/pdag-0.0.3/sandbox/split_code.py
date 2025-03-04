import ast

import asttokens

source = '''# Some code before the class definition
import pdag

class SquareRootModel(pdag.Model):
    """A model for square root."""

    x: pdag.RealParameter("x")
    y: pdag.RealParameter("y")
    z: pdag.CategoricalParameter("z", categories={"pos", "neg"})
    w: pdag.RealParameter("w")

    @pdag.relationship
    @staticmethod
    def sqrt(
        *,
        x_arg: float,
        z_arg: str
    ) -> tuple:
        return x_arg ** 0.5

# Some code after the class definition
x = 0
'''

# Parse the source with asttokens for accurate token positions.
at = asttokens.ASTTokens(source, parse=True)
# Find the class definition node by name.
class_node = next(node for node in at.tree.body if isinstance(node, ast.ClassDef) and node.name == "SquareRootModel")

# Determine the starting and ending positions.
start_line = class_node.first_token.start[0]
end_line = class_node.last_token.end[0]

# Split the code by lines.
lines = source.splitlines()
pre_classdef = "\n".join(lines[: start_line - 1])
classdef = "\n".join(lines[start_line - 1 : end_line])
post_classdef = "\n".join(lines[end_line:])

print("PRE-CLASSDEF:\n", pre_classdef)
print("CLASSDEF:\n", classdef)
print("POST-CLASSDEF:\n", post_classdef)
