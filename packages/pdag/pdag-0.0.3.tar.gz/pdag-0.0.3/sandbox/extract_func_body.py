from typing import Annotated, Literal

from rich import print

import pdag


class SquareRootModel(pdag.Model):
    """A model for square root."""

    x: Annotated[float, pdag.RealParameter("x")]
    y: Annotated[float, pdag.RealParameter("y")]
    z: Annotated[Literal["neg", "pos"], pdag.CategoricalParameter("z", categories=frozenset({"pos", "neg"}))]
    w: Annotated[float, pdag.RealParameter("w")]

    @pdag.relationship
    @staticmethod
    def sqrt(
        *,
        x_arg: Annotated[float, pdag.ParameterRef("x")],
        z_arg: Annotated[Literal["neg", "pos"], pdag.ParameterRef("z")],
    ) -> Annotated[float, pdag.ParameterRef("y")]:
        if z_arg == "pos":
            print("===")
            return float(x_arg**0.5)
        return -float(x_arg**0.5)


core_model = SquareRootModel.to_core_model()
print(core_model)
assert core_model.is_hydrated()
