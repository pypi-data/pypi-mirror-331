import ast
from textwrap import dedent

from rich import print


def strip_staticmethod_decorator(function_body: str) -> str:
    lines = function_body.split("\n")
    if lines[0].strip() == "@staticmethod":
        lines = lines[1:]
    return "\n".join(lines)


# function_lines = [
#     "    @staticmethod\n",
#     "    def sqrt(x: Annotated[float, pdag.RealParameter()]) -> float:\n",
#     "        return float(np.sqrt(x))\n",
# ]

function_lines = [
    "    @staticmethod\n",
    "    def square(x):\n",
    "        return x * x\n",
]

function_body = dedent("".join(function_lines))
print(function_body)
tree = ast.parse(function_body)
print(ast.dump(tree, indent=2))

namespace = {}
exec(function_body, namespace)

print(namespace)
function_restored = namespace["square"]
print(function_restored(3))
