# Contratos Governamentais

Agrupa os datasets para uma análise das contratações dos órgãos e entidades da administração pública direta, autárquica
e fundacional obtidos através do site: https://portaldatransparencia.gov.br/download-de-dados/compras

## Instalação

Pode ser instalado usando pip:

```
py -m pip install joao_marcionilo_contratos_governamentais
```

## Criar Tabela

**Function:** `create_table(credential:str, path:str, date:str)`

Converte um arquivo csv de um arquivo zip para uma tabela Sql Server, mantendo somente as colunas desejadas

### Example

```
import joao_marcionilo_contratos_governamentais as cg
    
conn_data = ""

cg.create_table(conn_data, path_to_zip, "202502")
```

### Parameters

| Parameter    | Type  | Description                                          |
|--------------|-------|------------------------------------------------------|
| `credential` | `str` | String de conexão para PYODBC                        |
| `path`       | `str` | Caminho do CSV                                       |
| `date`       | `str` | String de uma data no formato AnoMês, ex: `"202502"` |

## Buscar Resultados

**Function:** `fetch_costs(credential:str, dates:tuple, oe="", superior=True, save_as:str=None)`

Busca pelos gastos totais de um ou mais Órgãos Públicos durante as datas providas

### Example

```
import joao_marcionilo_contratos_governamentais as cg
    
conn_data = ""

print(cg.fetch_costs(conn_data, (("2025", "01"), ("2025", "02")), "202502"))
```

### Parameters

| Parameter    | Type    | Description                                                                                  |
|--------------|---------|----------------------------------------------------------------------------------------------|
| `credential` | `str`   | String de conexão para PYODBC                                                                |
| `dates`      | `tuple` | Datas das comparações a serem feitas, ex: `(("2025", "01"), ("2025", "02"))`                 |
| `oe`         | `str`   | Filtra qual órgão/entidade deve ser análisado                                                |
| `superior`   | `bool`  | Define se as buscas serão agrupadas pelos órgãos/entidades responsáveis ou pelo seu superior |
| `save_as`    | `str`   | Salva a busca em csv                                                                         |

### Return type: `list`

## Deletar Tabela

**Function:** `delete_table(credential:str, date:str)`

Deleta uma tabela registrada

### Example

```
import joao_marcionilo_contratos_governamentais as cg
    
conn_data = ""

print(cg.delete_table(conn_data, "202502")
```

### Parameters

| Parameter    | Type  | Description                                          |
|--------------|-------|------------------------------------------------------|
| `credential` | `str` | String de conexão para PYODBC                        |
| `date`       | `str` | String de uma data no formato AnoMês, ex: `"202502"` |