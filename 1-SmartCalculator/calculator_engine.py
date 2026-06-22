"""Safe mathematical expression evaluator used by the calculator and graph."""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable


class CalculatorError(ValueError):
    """A readable error raised for unsupported or invalid expressions."""


class CalculatorEngine:
    def __init__(self) -> None:
        self.memory = 0.0
        self.angle_mode = "DEG"
        self.operators: dict[type[ast.operator], Callable] = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Pow: operator.pow,
            ast.Mod: operator.mod,
        }
        self.unary_operators = {
            ast.UAdd: operator.pos,
            ast.USub: operator.neg,
        }

    @property
    def functions(self) -> dict[str, Callable]:
        to_radians = math.radians if self.angle_mode == "DEG" else lambda value: value
        return {
            "sqrt": math.sqrt,
            "sin": lambda value: math.sin(to_radians(value)),
            "cos": lambda value: math.cos(to_radians(value)),
            "tan": lambda value: math.tan(to_radians(value)),
            "asin": lambda value: self._from_radians(math.asin(value)),
            "acos": lambda value: self._from_radians(math.acos(value)),
            "atan": lambda value: self._from_radians(math.atan(value)),
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "abs": abs,
            "round": round,
            "floor": math.floor,
            "ceil": math.ceil,
            "fact": self._factorial,
        }

    @property
    def constants(self) -> dict[str, float]:
        return {"pi": math.pi, "e": math.e, "tau": math.tau, "ans": self.memory}

    def _from_radians(self, value: float) -> float:
        return math.degrees(value) if self.angle_mode == "DEG" else value

    @staticmethod
    def _factorial(value: float) -> int:
        if int(value) != value or value < 0:
            raise CalculatorError("Faktoriál vyžaduje nezáporné celé číslo.")
        return math.factorial(int(value))

    def calculate(self, expression: str, variables: dict[str, float] | None = None) -> float:
        normalized = (
            expression.strip()
            .replace("×", "*")
            .replace("÷", "/")
            .replace("^", "**")
            .replace("π", "pi")
            .replace("√", "sqrt")
            .replace(",", ".")
        )
        if not normalized:
            raise CalculatorError("Zadej výraz.")
        try:
            tree = ast.parse(normalized, mode="eval")
            result = self._eval(tree.body, variables or {})
            if isinstance(result, complex) or not math.isfinite(float(result)):
                raise CalculatorError("Výsledek není konečné reálné číslo.")
            self.memory = float(result)
            return result
        except CalculatorError:
            raise
        except ZeroDivisionError as exc:
            raise CalculatorError("Dělení nulou není povoleno.") from exc
        except (SyntaxError, TypeError, ValueError, OverflowError, KeyError) as exc:
            raise CalculatorError("Neplatný nebo nepodporovaný výraz.") from exc

    def _eval(self, node: ast.AST, variables: dict[str, float]) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            if node.id in self.constants:
                return self.constants[node.id]
            raise CalculatorError(f"Neznámá hodnota: {node.id}")
        if isinstance(node, ast.BinOp) and type(node.op) in self.operators:
            left, right = self._eval(node.left, variables), self._eval(node.right, variables)
            if isinstance(node.op, ast.Pow) and abs(right) > 1000:
                raise CalculatorError("Exponent je příliš velký.")
            return self.operators[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in self.unary_operators:
            return self.unary_operators[type(node.op)](self._eval(node.operand, variables))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in self.functions
            and not node.keywords
        ):
            return self.functions[node.func.id](*[self._eval(arg, variables) for arg in node.args])
        raise CalculatorError("Tato operace není podporována.")

    @staticmethod
    def format_result(value: float) -> str:
        if isinstance(value, int) or float(value).is_integer():
            return f"{int(value):,}".replace(",", " ")
        return f"{value:.12g}"
