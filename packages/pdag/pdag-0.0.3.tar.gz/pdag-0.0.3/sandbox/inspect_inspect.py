from typing import Annotated

import numpy as np

import pdag._experimental as pdag


class C:
    @staticmethod
    def sqrt(x: Annotated[float, pdag.RealParameter()]) -> float:
        return float(np.sqrt(x))


if __name__ == "__main__":
    import inspect

    from rich import print

    function_body = inspect.getsource(C.sqrt)
    print(function_body)
    source_lines = inspect.getsourcelines(C.sqrt)
    print(source_lines)
