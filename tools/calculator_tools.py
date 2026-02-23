import ast
import operator
import re
from typing import Type

from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class CalculatorInput(BaseModel):
    operation: str = Field(
        ...,
        description="A mathematical expression like 200*7 or 5000/2*10"
    )


class CalculatorTool(BaseTool):
    name: str = "Make a calculation"
    description: str = (
        "Useful to perform mathematical calculations like addition, "
        "subtraction, multiplication, division, powers, and modulus."
    )
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, operation: str):
        try:
            allowed_operators = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
                ast.Mod: operator.mod,
                ast.USub: operator.neg,
                ast.UAdd: operator.pos,
            }

            if not re.match(r'^[0-9+\-*/().% ]+$', operation):
                return "Error: Invalid characters in mathematical expression"

            tree = ast.parse(operation, mode='eval')

            def _eval_node(node):
                if isinstance(node, ast.Expression):
                    return _eval_node(node.body)
                elif isinstance(node, ast.Constant):
                    return node.value
                elif isinstance(node, ast.Num):
                    return node.n
                elif isinstance(node, ast.BinOp):
                    left = _eval_node(node.left)
                    right = _eval_node(node.right)
                    op = allowed_operators.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(left, right)
                elif isinstance(node, ast.UnaryOp):
                    operand = _eval_node(node.operand)
                    op = allowed_operators.get(type(node.op))
                    if op is None:
                        raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
                    return op(operand)
                else:
                    raise ValueError(f"Unsupported node type: {type(node).__name__}")

            return _eval_node(tree)

        except (SyntaxError, ValueError, ZeroDivisionError, TypeError) as e:
            return f"Error: {str(e)}"
        except Exception:
            return "Error: Invalid mathematical expression"