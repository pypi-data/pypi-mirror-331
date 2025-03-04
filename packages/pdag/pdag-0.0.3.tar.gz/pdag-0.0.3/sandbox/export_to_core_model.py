from typing import Annotated, Literal

from rich import print

import pdag


class SquareRootModel(pdag.Model):
    """A model for square root."""

    x = pdag.RealParameter("x")
    y = pdag.RealParameter("y")
    z = pdag.CategoricalParameter("z", categories={"pos", "neg"})
    w = pdag.RealParameter("w")

    @pdag.relationship
    @staticmethod
    def sqrt(
        *,
        x_arg: Annotated[float, pdag.ParameterRef("x")],
        z_arg: Annotated[Literal["neg", "pos"], pdag.ParameterRef("z")],
    ) -> Annotated[float, pdag.ParameterRef("y")]:
        if z_arg == "pos":
            return float(x_arg**0.5)
        return -float(x_arg**0.5)


print(SquareRootModel.to_core_model())
import inspect

source = inspect.getsource(SquareRootModel)
print(repr(source))
