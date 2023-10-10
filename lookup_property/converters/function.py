from __future__ import annotations

import ast
import itertools
from functools import partial, wraps
from typing import TYPE_CHECKING

from lookup_property import expression_to_ast

if TYPE_CHECKING:
    from lookup_property.typing import Expr, ModelMethod, State


__all__ = [
    "ast_module_to_function",
    "ast_to_module",
    "query_expression_ast_module",
]


def query_expression_ast_module(expression: Expr, function_name: str, state: State) -> ast.Module:
    return_value = expression_to_ast(expression, state)
    return ast_to_module(function_name=function_name, return_value=return_value, state=state)


def ast_to_module(function_name: str, return_value: ast.AST, state: State) -> ast.Module:
    function_body: list[ast.Import | ast.Return | ast.If | ast.Try] = [
        ast.Import(names=[ast.alias(name=import_name)]) for import_name in state.imports
    ]

    if isinstance(return_value, (ast.If, ast.Try)):
        function_body.append(return_value)
    else:
        function_body.append(ast.Return(value=return_value))

    module = ast.Module(
        body=[
            ast.FunctionDef(
                name=function_name,
                args=ast.arguments(
                    args=[
                        ast.arg(arg=name, annotation=None, type_comment=None)
                        for name in itertools.chain(["self"], state.extra_kwargs)
                    ],
                    defaults=[],
                    vararg=None,
                    kwarg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    posonlyargs=[],
                ),
                body=function_body,
                kwarg=[],
                kw_defaults=[],
                vararg=[],
                kwonlyargs=[],
                decorator_list=[],
            ),
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    return module


def ast_module_to_function(module: ast.Module, function_name: str, filename: str, state: State) -> ModelMethod:
    compiled = compile(source=module, filename=filename, mode="exec")
    namespace: dict[str, ModelMethod] = {}
    eval(compiled, namespace)  # noqa: S307, PGH001
    func = namespace[function_name]
    if state.extra_kwargs:
        func = wraps(func)(partial(func, **state.extra_kwargs))
    return func
