import ast

from rich import print

class_def = '''\
# Some code before the class definition
import pdag

class SquareRootModel(pdag.Model):
    """A model for square root."""

    x = pdag.RealParameter("x")
    y = pdag.RealParameter("y")
    z = pdag.CategoricalParameter("z", categories={"pos", "neg"})

    @pdag.relationship
    @staticmethod
    def sqrt(
        *,
        x_arg: Annotated[float, pdag.ParameterRef("x")],
        z_arg: Annotated[Literal["neg", "pos"], pdag.ParameterRef("z")],
    ) -> Annotated[float, pdag.ParameterRef("y")]:
        if z_arg == "pos":
            return float(x_arg**0.5)

# Some code after the class definition
x = 0
'''

tree = ast.parse(class_def)
print(ast.dump(tree, indent=2))
