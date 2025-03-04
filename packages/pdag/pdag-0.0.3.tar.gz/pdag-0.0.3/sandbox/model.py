class SquareRootModel(pdag.Model):
    x: Annotated[float, pdag.RealParameter('x')]
    y: Annotated[float, pdag.RealParameter('y')]
    z: Annotated[Literal['neg', 'pos'], pdag.CategoricalParameter('z', categories=frozenset({'neg', 'pos'}))]

    @pdag.relationship
    @staticmethod
    def sqrt(*, x_arg: Annotated[float, pdag.Parameter('x')], z_arg: Annotated[Literal['neg', 'pos'], pdag.Parameter('z')]) -> Annotated[float, pdag.Parameter('y')]:
        if z_arg == 'pos':
            return float(x_arg ** 0.5)