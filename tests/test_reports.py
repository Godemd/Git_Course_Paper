from pandas import Timestamp

from src.reports import spending_by_category


def test_spending_by_category(dataframe_dat_cat):
    assert spending_by_category(dataframe_dat_cat, "Топливо", "1.02.2000").to_dict("records") == [
        {"Дата операции": Timestamp("2000-01-01 00:00:00"), "Категория": "Топливо"},
        {"Дата операции": Timestamp("2000-01-04 00:00:00"), "Категория": "Топливо"},
    ]
    assert spending_by_category(dataframe_dat_cat, "Топливо").to_dict("records") == []
