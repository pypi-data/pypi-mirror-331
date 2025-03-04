import ast
from pathlib import Path
from textwrap import dedent

import pdag

output_path = Path(__file__).parent / "model.py"

x = pdag.RealParameter("x")

core_model = pdag.CoreModel(
    name="SquareRootModel",
    parameters={
        "x": pdag.RealParameter("x"),
        "y": pdag.RealParameter("y"),
        "z": pdag.CategoricalParameter("z", categories={"pos", "neg"}),
    },
    collections={},
    relationships={
        "sqrt": pdag.FunctionRelationship(
            name="sqrt",
            inputs={"x_arg": "x", "z_arg": "z"},
            outputs=["y"],
            output_is_scalar=True,
            function_body=dedent(
                """\
                if z_arg == 'pos':
                    return float(x_arg**0.5)
                return -float(x_arg**0.5)
                """,
            ),
        ),
    },
)

print(core_model)

class_def = pdag.core_model_to_dataclass_notation_ast(core_model)

print(ast.dump(class_def, indent=2))
# Wrap the class definition in a Module node
module = ast.Module(body=[class_def], type_ignores=[])

# Fix missing location info (lineno, col_offset, etc.)
module = ast.fix_missing_locations(module)

# Convert the AST back to source code (requires Python 3.9+)
source_code = ast.unparse(module)

print(source_code)

# Write the generated source code to a file
with output_path.open("w") as f:
    f.write(source_code)
