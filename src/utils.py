import logging
import os
from typing import Any

import numpy as np
import pandas as pd


def setup_logger(name: str) -> logging.Logger:
    """
    ## Настройка логгера
    Аргументы:
        `name (str)`: Имя логгера
    Возвращает:
        `logging.Logger`: Объект логгера
    """
    file_path = os.path.join("logs", f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s:%(lineno)d -> %(message)s")

    logger_file_handler = logging.FileHandler(file_path, encoding="utf-8", mode="w")
    logger_file_handler.setFormatter(formatter)

    logger.addHandler(logger_file_handler)

    return logger


logger = setup_logger("utils")


def read_data_transactions(file_path: str) -> pd.DataFrame:
    """
    ## Возвращает список словарей из JSON/CSV/XLSX
    Аргументы:
        `file_path (str)`: Путь к JSON/CSV/XLSX-файлу
    Возвращает:
        `DataFrame`: С колонками и рядами
    """
    print(file_path)
    if not os.path.exists(file_path):
        logger.warning(f"Файл {file_path} не найден")
        raise FileNotFoundError(f"Файл {file_path} не найден")

    if file_path.endswith(".json"):
        return pd.read_json(file_path)

    elif file_path.endswith(".csv"):
        return pd.read_csv(file_path, delimiter=";").replace({np.nan: None})

    elif file_path.endswith(".xls") or file_path.endswith(".xlsx"):
        return pd.read_excel(file_path).replace({np.nan: None})

    else:
        logger.warning(f"Файл {file_path} не поддерживается")
        raise NotImplementedError(f"Файл {file_path} не поддерживается")


def get_json_from_dataframe(df: pd.DataFrame) -> list[dict[Any, Any]]:
    """
    ## Возвращает список словарей из JSON-файла
    Аргументы:
        `file_path (str)`: Путь к JSON-файлу
    Возвращает:
        `list[dict[Any, Any]]`: Список словарей
    """
    # return read_data_transactions(file_path).replace({np.nan: None}).to_dict('records')
    return df.to_dict("records")
