from pyspark.sql import DataFrame

from spl_transpiler.runtime.base import enforce_types, Expr


@enforce_types
def rename(df: DataFrame, **renames: Expr) -> DataFrame:
    for new_name, old_expr in renames.items():
        df = df.withColumnRenamed(old_expr.to_pyspark_expr(), new_name)
    return df
