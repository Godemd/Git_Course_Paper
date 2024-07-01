import os
from functools import wraps
from typing import Callable

import pandas as pd


class ReportSaver:

    @staticmethod
    def to_excel(file_name: str = "result_{func}.xls") -> Callable:
        """
        Декоратор для сохранения результатов в файл.

        Аргументы:
        `file_name` (str): Имя файла, в который сохраняются результаты.

        Возвращает:
        Callable: Декоратор для сохранения результатов в файл.
        """

        def wrapper(func: Callable) -> Callable:
            @wraps(func)
            def inner(*args: tuple, **kwargs: dict) -> pd.DataFrame:

                result: pd.DataFrame = func(*args, **kwargs)

                result.to_excel(
                    f"{os.path.join("data/", file_name.format(func=func.__name__))}", index=False, engine="openpyxl"
                )

                return result

            return inner

        return wrapper
