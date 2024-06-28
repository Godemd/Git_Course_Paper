from src.reports import spending_by_category
from src.services import search_by_persons, simple_searching
from src.views import post_events_response
from src.utils import read_data_transactions

if __name__ == "__main__":
    # Пример работы функции на запрос json для "Веб-страницы" - "Страница События"
    print(
        'Пример работы функции для "Веб-страницы" - "Страница События',
    )

    print(post_events_response("1.10.2020", "ALL"))

    print("Конец работы функции")

    # Пример работы функции для "Сервисы" - "Простой поиск"

    print('ример работы функции для "Сервисы" - "Простой поиск"')

    print(simple_searching("Топливо", "data/operations.xls"))

    print("Конец работы функции")

    # Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам"

    print(
        'Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам"',
    )

    print(search_by_persons("data/operations.xls"))

    print("Конец работы функции")

    # Пример работы функций для "Отчеты" - "Траты по категории"

    print(
        'Пример работы функций для "Отчеты" - "Траты по категории"',
    )

    df = read_data_transactions("data/operations.xls")
    print(spending_by_category(df, "Топливо", "15.02.2018"))
