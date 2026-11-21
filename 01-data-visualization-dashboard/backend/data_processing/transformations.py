import ast
import operator
from typing import List, Dict, Any, Union
import numpy as np
import pandas as pd

# ----------------- Safe AST Expression Evaluator -----------------
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

ALLOWED_FUNCTIONS = {
    'abs': np.abs,
    'round': np.round,
    'sqrt': np.sqrt,
    'log': np.log,
    'log10': np.log10,
    'exp': np.exp,
    'sin': np.sin,
    'cos': np.cos,
}

class SafeExpressionEvaluator(ast.NodeVisitor):
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def evaluate(self, expr_str: str) -> pd.Series:
        try:
            tree = ast.parse(expr_str, mode='eval')
        except SyntaxError as e:
            raise ValueError(f"Invalid expression syntax: {e}")
        return self.visit(tree.body)

    def visit_BinOp(self, node: ast.BinOp):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Operator {op_type.__name__} is not permitted in expressions.")
        return ALLOWED_OPERATORS[op_type](left, right)

    def visit_UnaryOp(self, node: ast.UnaryOp):
        operand = self.visit(node.operand)
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError(f"Unary operator {op_type.__name__} is not permitted.")
        return ALLOWED_OPERATORS[op_type](operand)

    def visit_Constant(self, node: ast.Constant):
        if not isinstance(node.value, (int, float, bool, str)):
            raise ValueError(f"Constant of type {type(node.value)} is not allowed.")
        return node.value

    # Compatibility for older Python AST node Num/Str
    def visit_Num(self, node):
        return node.n

    def visit_Str(self, node):
        return node.s

    def visit_Name(self, node: ast.Name):
        col_name = node.id
        if col_name not in self.df.columns:
            raise ValueError(f"Column '{col_name}' does not exist in dataset.")
        return self.df[col_name]

    def visit_Call(self, node: ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only direct mathematical functions are allowed.")
        func_name = node.func.id
        if func_name not in ALLOWED_FUNCTIONS:
            raise ValueError(f"Function '{func_name}' is not in allowed mathematical functions list.")
        args = [self.visit(arg) for arg in node.args]
        return ALLOWED_FUNCTIONS[func_name](*args)

    def generic_visit(self, node):
        raise ValueError(f"Expression element '{type(node).__name__}' is forbidden.")

def evaluate_safe_expression(df: pd.DataFrame, expr_str: str) -> pd.Series:
    evaluator = SafeExpressionEvaluator(df)
    return evaluator.evaluate(expr_str)

# ----------------- Transformation Pipeline Engine -----------------

def apply_transformation_step(df: pd.DataFrame, step: Dict[str, Any]) -> pd.DataFrame:
    """Applies a single declarative transformation step to a DataFrame."""
    op = step.get("op")
    params = step.get("params", {})
    df_out = df.copy()

    if op == "filter":
        column = params.get("column")
        operator_str = params.get("operator")
        value = params.get("value")
        
        if column not in df_out.columns:
            raise ValueError(f"Filter column '{column}' not found.")
        
        col_series = df_out[column]
        if operator_str == "==":
            mask = (col_series == value)
        elif operator_str == "!=":
            mask = (col_series != value)
        elif operator_str == ">":
            mask = (pd.to_numeric(col_series, errors='coerce') > float(value))
        elif operator_str == ">=":
            mask = (pd.to_numeric(col_series, errors='coerce') >= float(value))
        elif operator_str == "<":
            mask = (pd.to_numeric(col_series, errors='coerce') < float(value))
        elif operator_str == "<=":
            mask = (pd.to_numeric(col_series, errors='coerce') <= float(value))
        elif operator_str == "contains":
            mask = col_series.astype(str).str.contains(str(value), case=False, na=False)
        elif operator_str == "in":
            val_list = value if isinstance(value, list) else [v.strip() for v in str(value).split(",")]
            mask = col_series.isin(val_list)
        elif operator_str == "is_null":
            mask = col_series.isna()
        elif operator_str == "not_null":
            mask = col_series.notna()
        else:
            raise ValueError(f"Unsupported filter operator '{operator_str}'")
        df_out = df_out[mask]

    elif op == "select_columns":
        columns = params.get("columns", [])
        valid_cols = [c for c in columns if c in df_out.columns]
        if not valid_cols:
            raise ValueError("No valid columns specified for select_columns")
        df_out = df_out[valid_cols]

    elif op == "drop_columns":
        columns = params.get("columns", [])
        df_out = df_out.drop(columns=[c for c in columns if c in df_out.columns], errors='ignore')

    elif op == "sort":
        columns = params.get("columns", [])
        ascending = params.get("ascending", True)
        if isinstance(columns, str):
            columns = [columns]
        valid_cols = [c for c in columns if c in df_out.columns]
        if valid_cols:
            df_out = df_out.sort_values(by=valid_cols, ascending=ascending)

    elif op == "cast_type":
        column = params.get("column")
        target_type = params.get("target_type")
        if column not in df_out.columns:
            raise ValueError(f"Column '{column}' not found.")
        
        if target_type == "integer":
            df_out[column] = pd.to_numeric(df_out[column], errors='coerce').fillna(0).astype(int)
        elif target_type == "float":
            df_out[column] = pd.to_numeric(df_out[column], errors='coerce').astype(float)
        elif target_type == "string":
            df_out[column] = df_out[column].astype(str)
        elif target_type == "boolean":
            df_out[column] = df_out[column].astype(bool)
        elif target_type in ["datetime", "date"]:
            df_out[column] = pd.to_datetime(df_out[column], errors='coerce')
        else:
            raise ValueError(f"Unsupported target type '{target_type}'")

    elif op == "parse_date":
        column = params.get("column")
        date_format = params.get("format")
        if column not in df_out.columns:
            raise ValueError(f"Column '{column}' not found.")
        df_out[column] = pd.to_datetime(df_out[column], format=date_format, errors='coerce')

    elif op == "fill_missing":
        column = params.get("column")
        strategy = params.get("strategy", "value")  # value, mean, median, mode
        fill_val = params.get("value")
        
        if column not in df_out.columns:
            raise ValueError(f"Column '{column}' not found.")
        
        if strategy == "mean":
            computed = pd.to_numeric(df_out[column], errors='coerce').mean()
            df_out[column] = df_out[column].fillna(computed)
        elif strategy == "median":
            computed = pd.to_numeric(df_out[column], errors='coerce').median()
            df_out[column] = df_out[column].fillna(computed)
        elif strategy == "mode":
            mode_series = df_out[column].mode()
            if not mode_series.empty:
                df_out[column] = df_out[column].fillna(mode_series.iloc[0])
        else:
            df_out[column] = df_out[column].fillna(fill_val)

    elif op == "drop_missing":
        columns = params.get("columns")
        if columns:
            valid_cols = [c for c in columns if c in df_out.columns]
            df_out = df_out.dropna(subset=valid_cols)
        else:
            df_out = df_out.dropna()

    elif op == "deduplicate":
        subset = params.get("columns")
        valid_subset = [c for c in subset if c in df_out.columns] if subset else None
        df_out = df_out.drop_duplicates(subset=valid_subset)

    elif op == "group_by_agg":
        group_cols = params.get("group_by", [])
        aggregations = params.get("aggregations", {})  # e.g., {"revenue": "sum", "orders": "mean"}
        if not group_cols or not aggregations:
            raise ValueError("group_by and aggregations parameters are required for group_by_agg")
        
        agg_dict = {}
        for col, agg_fn in aggregations.items():
            if col in df_out.columns:
                agg_dict[col] = agg_fn
        df_out = df_out.groupby(group_cols, as_index=False).agg(agg_dict)

    elif op == "derive_column":
        new_column = params.get("new_column")
        expression = params.get("expression")
        if not new_column or not expression:
            raise ValueError("new_column and expression are required for derive_column")
        result_series = evaluate_safe_expression(df_out, expression)
        df_out[new_column] = result_series

    else:
        raise ValueError(f"Unknown transformation operation: '{op}'")

    return df_out

def execute_pipeline(df: pd.DataFrame, steps: List[Dict[str, Any]]) -> pd.DataFrame:
    """Executes a full pipeline of transformation steps sequentially."""
    current_df = df
    for step in steps:
        current_df = apply_transformation_step(current_df, step)
    return current_df
