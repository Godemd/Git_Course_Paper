import datetime
import json
import logging
import os
from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd
import requests


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


def get_operations_by_date_range(date: str, optional_flag: str = "M") -> list[dict]:
    """
    Функция для фильтрации данных об операциях по дате.

    Аргументы:
        `date` (str): Дата в формате DD.MM.YYYY
        `optional_flag` (str):

    Возвращает:
        `list[dict]`: Список словарей с операциями
    """

    last_date = datetime.datetime.strptime(date, "%d.%m.%Y")
    start_date = last_date.replace(day=1)

    if optional_flag == "W":
        days_between = last_date.day - last_date.weekday()
        start_date = last_date.replace(day=days_between)
    elif optional_flag == "Y":
        start_date = last_date.replace(day=1, month=1)
    elif optional_flag == "ALL":
        start_date = last_date.replace(day=1, month=1, year=1)

    df = read_data_transactions("data/operations.xls")
    op_data = get_json_from_dataframe(df)
    tmp = []

    for op in op_data:
        if op["Статус"] != "OK":
            continue

        op_date = datetime.datetime.strptime(op["Дата операции"], "%d.%m.%Y %H:%M:%S")

        if start_date < op_date < last_date.replace(day=last_date.day + 1):
            tmp.append(op)

    return tmp


def get_expences_categories(expences_categories: dict) -> dict:
    total_amount = 0
    transfers_and_cash = []
    expences_main = []

    for op in dict(expences_categories).items():
        logger.info(op)
        op_category, op_amount = op
        total_amount += op_amount

        if op_category in ["Переводы", "Наличные"]:
            transfers_and_cash.append({"category": op_category, "amount": round(op_amount)})
        else:
            expences_main.append({"category": op_category, "amount": round(op_amount)})

    expences_main.sort(key=lambda x: x["amount"], reverse=True)
    transfers_and_cash.sort(key=lambda x: x["amount"], reverse=True)

    if len(expences_main) > 7:
        other_cat_value = 0
        while len(expences_main) > 7:
            popped_dict: dict = expences_main.pop()
            other_cat_value += popped_dict["amount"]
        expences_main.append({"category": "Остальное", "amount": other_cat_value})

    return {"total_amount": round(total_amount), "main": expences_main, "transfers_and_cash": transfers_and_cash}


def get_income_categories(income_categories: dict) -> dict:
    total_amount = 0
    income_main = []

    for op in dict(income_categories).items():
        logger.debug(op)
        op_category, op_amount = op
        total_amount += op_amount

        income_main.append({"category": op_category, "amount": round(op_amount)})

    income_main.sort(key=lambda x: x["amount"], reverse=True)

    return {"total_amount": round(total_amount), "main": income_main}


def get_expences_income(operations: list[dict]) -> tuple[dict, dict]:
    income_categories: defaultdict = defaultdict(int)
    expences_categories: defaultdict = defaultdict(int)

    for op in operations:
        op_sum = op["Сумма платежа"]
        op_category = op["Категория"]

        if op_sum < 0:
            expences_categories[op_category] += abs(op_sum)
        else:
            income_categories[op_category] += abs(op_sum)

    expences = get_expences_categories(expences_categories)
    incomes = get_income_categories(income_categories)

    return expences, incomes


def get_currency_stocks(file_path: str = "user_settings.json") -> tuple[list, list]:
    user_settings = read_user_settings(file_path)
    user_currencies = user_settings["user_currencies"]
    user_stocks = user_settings["user_stocks"]

    currency_list = []
    stocks_list = []

    for cur in user_currencies:
        cur_price = get_currency_price(cur)
        currency_list.append({"currency": cur, "rate": cur_price})

    for stock in user_stocks:
        stock_price = get_stock_price(stock)
        stocks_list.append({"stock": stock, "price": stock_price})

    return currency_list, stocks_list


def get_currency_price(currency: str) -> None | float:
    response = requests.get(f"https://api.exchangerate-api.com/v4/latest/{currency}")
    if response.status_code != 200:
        return None

    result: float | None = response.json()["rates"].get("RUB", None)
    return result


def get_stock_price(stock: str) -> None | float:
    API_KEY = os.getenv("FMP_API_KEY")

    response = requests.get(f"https://financialmodelingprep.com/api/v3/quote/{stock}?apikey={API_KEY}")

    if response.status_code != 200:
        return None

    result: float | None = response.json()[0]["price"]

    return result


def read_user_settings(filepath: str) -> Any:
    with open(filepath, "r") as f:
        user_settings = json.load(f)
    return user_settings
