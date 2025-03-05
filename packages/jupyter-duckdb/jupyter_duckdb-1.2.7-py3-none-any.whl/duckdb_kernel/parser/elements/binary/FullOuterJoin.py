from typing import Tuple, Dict

from duckdb_kernel.db import Table
from ..RABinaryOperator import RABinaryOperator
from ...util.RenamableColumnList import RenamableColumnList


class FullOuterJoin(RABinaryOperator):
    @staticmethod
    def symbols() -> Tuple[str, ...]:
        return chr(10199), 'fjoin', 'ojoin'

    def to_sql(self, tables: Dict[str, Table]) -> Tuple[str, RenamableColumnList]:
        # execute subqueries
        lq, lcols = self.left.to_sql(tables)
        rq, rcols = self.right.to_sql(tables)

        # find matching columns
        join_cols, all_cols = lcols.intersect(rcols)

        replacements = {c1: c2 for c1, c2 in join_cols}
        select_cols = [
            f'COALESCE({c.current_name}, {replacements.get(c).current_name})' if c in replacements else c.current_name
            for c in all_cols]
        select_clause = ', '.join(select_cols)

        on_clause = ' AND '.join(f'{l.current_name} = {r.current_name}' for l, r in join_cols)

        # create sql
        return f'SELECT {select_clause} FROM ({lq}) {self._name()} FULL OUTER JOIN ({rq}) {self._name()} ON {on_clause}', all_cols
