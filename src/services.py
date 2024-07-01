import json
import re

from src.utils import setup_logger

logger = setup_logger("services")


def simple_searching(search_field: str, transactions: list[dict]) -> str:
    """
    Функция для поиска операций по полю поиска в описании операции или в категории.
    Аргументы:
        `search_field` (str): Поле поиска
        `transactions` (list[dict]): Список операций
    Возвращает:
        `str`: JSON-строка с результатами поиска
    """

    search_field = search_field.lower()

    tmp = []
    for op in transactions:
        op_category = op.get("Категория", " ")
        op_descr = op.get("Описание", " ")

        if (op_category and search_field in op_category.lower()) or (op_descr and search_field in op_descr.lower()):
            tmp.append(op)

    logger.info(f"В поиск передано: {search_field}. Найдено совпадений: {len(tmp)}")

    return json.dumps(tmp, ensure_ascii=False, indent=4)


def search_by_persons(transactions: list[dict]) -> str:
    """
    Функция возвращает список операций физическим лицам
    Аргументы:
        `transactions` (list[dict]): Список операций
    Возвращает:
        `str`: JSON-строка с результатами поиска
    """

    tmp = []

    for op in transactions:
        if op.get("Категория") != "Переводы":
            continue

        regex_pattern = r"\w* [\w]{1}\."
        result = re.findall(regex_pattern, op.get("Описание", ""))
        if result:
            tmp.append(op)

    logger.info(f"Найдено совпадений: {len(tmp)}")

    return json.dumps(tmp, ensure_ascii=False, indent=4)
