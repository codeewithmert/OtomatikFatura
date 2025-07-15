import duckdb
import pandas as pd
from typing import Tuple, Optional

def export_df_to_sql(df: pd.DataFrame, table_name: str = "fatura_df") -> str:
    sql = f"CREATE TABLE {table_name} (fatura_tarihi TEXT, toplam_tutar TEXT, fatura_no TEXT, satıcı_adı TEXT, vergi_no TEXT);\n"
    for _, row in df.iterrows():
        values = [str(row[col]).replace("'", "''") for col in df.columns]
        sql += f"INSERT INTO {table_name} VALUES ('{', '.join(values)}');\n"
    return sql

def run_sql_query(query: str, df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    try:
        con = duckdb.connect(database=':memory:', read_only=False)
        con.register('fatura_df', df)
        result = con.execute(query).df()
        con.close()
        return result, None
    except Exception as e:
        return None, str(e) 