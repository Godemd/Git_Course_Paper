import json
from typing import Literal

from src.utils import get_currency_stocks, get_expences_income, get_operations_by_date_range, setup_logger

logger = setup_logger("views")


def post_events_response(date: str, optional_flag: Literal["M", "W", "Y", "ALL"] = "M") -> str:
    """
    Главная функция.
    Собирает данные(траты, поступления, стоимости валют и акций) из других функций
    и возвращает готовый JSON ответ

    Аргументы:
        `date` (str): Дата в формате DD.MM.YYYY
        `optional_flag` (str) = "M": Отображение операций за месяц/неделю/год/всё время(до введенной даты)

    Возвращает:
        `str`: JSON ответ с данными
    """

    f_by_date_operations = get_operations_by_date_range(date, optional_flag)
    expences, income = get_expences_income(f_by_date_operations)

    currency_rates, stocks_prices = get_currency_stocks("user_settings.json")
    result = {"expences": expences, "income": income, "currency_rates": currency_rates, "stock_prices": stocks_prices}

    logger.info("Возвращенные данные указаны ниже")
    logger.info(result)

    return json.dumps(result, ensure_ascii=False, indent=4)
