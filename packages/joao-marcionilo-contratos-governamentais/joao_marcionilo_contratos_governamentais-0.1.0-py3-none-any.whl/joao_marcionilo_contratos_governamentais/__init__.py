"""
Agrupa os datasets para uma análise das contratações dos órgãos e entidades da administração pública direta, autárquica
e fundacional obtidos através do site: https://portaldatransparencia.gov.br/download-de-dados/compras
"""

import zipfile

import pyodbc
import pandas as pd


def _sql(credential, fetch=False):
    def wrapper(query, data=None) -> None | tuple:
        if data is None:
            data = []
        with pyodbc.connect(credential) as conn:
            cursor = conn.cursor()
            if data:
                cursor.execute(query, data)
            else:
                cursor.execute(query)
            if fetch:
                return cursor.fetchall(), cursor.description
            cursor.commit()
    return wrapper


def create_table(credential:str, path:str, date:str):
    """
    Converte um arquivo csv de um arquivo zip para uma tabela Sql Server, mantendo somente as colunas desejadas
    :param credential: String de conexão para PYODBC
    :param path: Caminho do CSV
    :param date: String de uma data no formato AnoMês, ex: "202502"
    """
    sql = _sql(credential)
    table = f"[{date}_Compras]"
    sql(f"""
    IF NOT EXISTS(SELECT * FROM sysobjects WHERE name='{table}' AND xtype='U')
    CREATE TABLE {table}(
        [Nome_Órgão_Superior] varchar(200),
        [Nome_Órgão] varchar(200),
        [Valor_Final_Compra] float
    )
    """)
    unzipped = zipfile.ZipFile(path + date + "_Compras.zip").open(date + "_Compras.csv")
    df = pd.read_csv(unzipped, encoding="unicode_escape", sep=';', usecols=["Nome Órgão Superior", "Nome Órgão", "Valor Final Compra"])
    results = [
        df[key].values.tolist() if key != "Valor Final Compra" else
        [result.replace(",", ".") for result in df[key].values.tolist()]
        for key in ["Nome Órgão Superior", "Nome Órgão", "Valor Final Compra"]
    ]
    query = f"INSERT INTO {table}([Nome_Órgão_Superior], [Nome_Órgão], [Valor_Final_Compra]) VALUES (?, ?, ?)"
    for data in zip(results[0], results[1], results[2]):
        sql(query, data)


def fetch_costs(credential:str, dates:tuple, oe="", superior=True, save_as:str=None) -> list:
    """
    Busca pelos gastos totais de um ou mais Órgãos Públicos durante as datas providas
    :param credential: String de conexão para PYODBC
    :param dates: Datas das comparações a serem feitas, ex: (("2025", "01"), ("2025", "02"))
    :param oe: Filtra qual órgão/entidade deve ser análisado
    :param superior: Define se as buscas serão agrupadas pelos órgãos/entidades responsáveis ou pelo seu superior
    :param save_as: Salva a busca em csv
    :return: Lista com os resultados
    """
    selections = "[Nome_Órgão_Superior]" if superior else "[Nome_Órgão], [Nome_Órgão_Superior]"
    where = "[Nome_Órgão_Superior]" if superior else "[Nome_Órgão]"
    sql = _sql(credential, True)
    query = (
        f"SELECT {selections}, " +
        "SUM([Valor_Final_Compra]) AS [Gastos], CONVERT(date, '{0}-{1}-01') AS [Período] FROM [{0}{1}_Compras] " +
        (f"WHERE {where} = '{oe}'" if oe else "") +
        f" GROUP BY {selections}"
    )
    query = sql(f"""
    SELECT {selections}, [Gastos], [Período] FROM (
        {" UNION ".join(query.format(y, m) for y, m in dates)}
    ) AS subquery
    """)
    if save_as:
        df = pd.DataFrame([list(i) for i in query[0]], columns=[i[0] for i in query[1]])
        df.to_csv(save_as, index=False)
    return query[0]


def delete_table(credential:str, date:str):
    """
    Deleta uma tabela registrada
    :param credential: String de conexão para PYODBC
    :param date: String de uma data no formato AnoMês, ex: "202502"
    """
    sql = _sql(credential)
    sql(f"DROP TABLE [{date}_Compras]")
