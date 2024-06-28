import re

from src.utils import get_json_from_dataframe, read_data_transactions, setup_logger

logger = setup_logger("services")


def simple_searching(search_field: str, file_path: str = "data/operations.xls") -> list[dict]:
    """
    Функция для поиска операций по полю поиска в описании операции или в категории.
    Аргументы:
        `search_field` (str): Поле поиска
        `file_path` (str): Путь до файла
    Возвращает:
        `list[dict]`: Список операций
    """

    search_field = search_field.lower()
    all_op_data = get_json_from_dataframe(read_data_transactions(file_path))

    tmp = []
    for op in all_op_data:
        op_category = op["Категория"] or " "
        op_descr = op["Описание"] or " "

        if search_field in op_category.lower() or search_field in op_descr.lower():
            tmp.append(op)

    logger.info(f"В поиск передано: {search_field}. Найдено совпадений: {len(tmp)}")

    return tmp


def search_by_persons(file_path: str = "data/operations.xls") -> list[dict]:
    """
    Функция возвращает список операций физическим лицам

    Аргументы:
        `file_path` (str): Путь до файла
    Возвращает:
        `list[dict]`: Список операций
    """

    tmp = []
    op_data = get_json_from_dataframe(read_data_transactions(file_path))

    for op in op_data:
        if op["Категория"] != "Переводы":
            continue

        regex_pattern = r"\w* [\w]{1}\."
        result = re.findall(regex_pattern, op["Описание"])
        if result:
            tmp.append(op)

    logger.info(f"Найдено совпадений: {len(tmp)}")

    return tmp


if __name__ == "__main__":
    print(simple_searching("колхоз"))
