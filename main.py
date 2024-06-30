from src.reports import spending_by_category
from src.services import search_by_persons, simple_searching
from src.utils import read_data_transactions
from src.views import post_events_response

if __name__ == "__main__":
    # Пример работы функции на запрос json для "Веб-страницы" - "Страница События"
    print('Пример работы функции для "Веб-страницы" - "Страница События"')
    print(post_events_response("1.10.2020", "ALL"))
    print("Конец работы функции")

    # Пример работы функции для "Сервисы" - "Простой поиск"
    print('Пример работы функции для "Сервисы" - "Простой поиск"')
    transactions = read_data_transactions("data/operations.xls")
    transactions_list = transactions.to_dict(orient="records")
    print(simple_searching("Топливо", transactions_list))
    print("Конец работы функции")

    # # Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам"
    print('Пример работы функций для "Сервисы" - "Поиск переводов физическим лицам"')
    print(search_by_persons(transactions_list))
    print("Конец работы функции")

    # # Пример работы функций для "Отчеты" - "Траты по категории"
    print('Пример работы функций для "Отчеты" - "Траты по категории"')
    df = read_data_transactions("data/operations.xls")
    spending_df = spending_by_category(df, "Топливо", "15.02.2018")
    print(spending_df.to_json(orient="records", force_ascii=False, indent=4))
    print("Конец работы функции")
