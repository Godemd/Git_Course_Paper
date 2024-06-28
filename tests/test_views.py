from unittest.mock import patch

import pytest

from src.views import (
    get_currency_price,
    get_currency_stocks,
    get_expences_categories,
    get_expences_income,
    get_income_categories,
    get_operations_by_date_range,
    get_stock_price,
    post_events_response,
)


@pytest.fixture
def mock_operations():
    return [
        {"Сумма платежа": -1000, "Категория": "Продукты", "Статус": "OK", "Дата операции": "22.05.2020 12:00:00"},
        {"Сумма платежа": 5000, "Категория": "Зарплата", "Статус": "OK", "Дата операции": "22.05.2020 13:00:00"},
        {"Сумма платежа": -500, "Категория": "Транспорт", "Статус": "OK", "Дата операции": "22.05.2020 14:00:00"},
        {"Сумма платежа": 1000, "Категория": "Премия", "Статус": "OK", "Дата операции": "22.05.2020 15:00:00"},
    ]


@pytest.fixture
def mock_user_settings():
    return "user_settings.json"


def test_post_events_response(mock_operations, mock_user_settings):
    with patch("src.views.get_operations_by_date_range") as mock_get_operations_by_date_range, patch(
        "src.views.get_expences_income"
    ) as mock_get_expences_income, patch("src.views.get_currency_stocks") as mock_get_currency_stocks:
        mock_get_operations_by_date_range.return_value = mock_operations
        mock_get_expences_income.return_value = (
            {"total_amount": 1500, "main": [], "transfers_and_cash": []},
            {"total_amount": 6000, "main": []},
        )
        mock_get_currency_stocks.return_value = (
            [{"currency": "USD", "rate": 75.0}],
            [{"stock": "AAPL", "price": 150.0}],
        )
        result = post_events_response("22.05.2020", "W")
        assert result == {
            "expences": {"total_amount": 1500, "main": [], "transfers_and_cash": []},
            "income": {"total_amount": 6000, "main": []},
            "currency_rates": [{"currency": "USD", "rate": 75.0}],
            "stock_prices": [{"stock": "AAPL", "price": 150.0}],
        }


def test_get_operations_by_date_range_month(mock_operations):
    with patch("src.views.read_data_transactions") as mock_read_data_transactions, patch(
        "src.views.get_json_from_dataframe"
    ) as mock_get_json_from_dataframe:
        mock_read_data_transactions.return_value = None
        mock_get_json_from_dataframe.return_value = mock_operations
        result = get_operations_by_date_range("22.05.2020", "M")
        assert result == mock_operations


def test_get_operations_by_date_range_week(mock_operations):
    with patch("src.views.read_data_transactions") as mock_read_data_transactions, patch(
        "src.views.get_json_from_dataframe"
    ) as mock_get_json_from_dataframe:
        mock_read_data_transactions.return_value = None
        mock_get_json_from_dataframe.return_value = mock_operations
        result = get_operations_by_date_range("22.05.2020", "W")
        assert result == mock_operations


def test_get_operations_by_date_range_year(mock_operations):
    with patch("src.views.read_data_transactions") as mock_read_data_transactions, patch(
        "src.views.get_json_from_dataframe"
    ) as mock_get_json_from_dataframe:
        mock_read_data_transactions.return_value = None
        mock_get_json_from_dataframe.return_value = mock_operations
        result = get_operations_by_date_range("22.05.2020", "Y")
        assert result == mock_operations


def test_get_operations_by_date_range_all(mock_operations):
    with patch("src.views.read_data_transactions") as mock_read_data_transactions, patch(
        "src.views.get_json_from_dataframe"
    ) as mock_get_json_from_dataframe:
        mock_read_data_transactions.return_value = None
        mock_get_json_from_dataframe.return_value = mock_operations
        result = get_operations_by_date_range("22.05.2020", "ALL")
        assert result == mock_operations


def test_get_expences_categories():
    expences_categories = {"Продукты": 1000, "Транспорт": 500, "Развлечения": 200, "Одежда": 150, "Кафе": 100}
    result = get_expences_categories(expences_categories)
    assert result["total_amount"] == 1950
    assert len(result["main"]) == 5
    assert len(result["transfers_and_cash"]) == 0


def test_get_income_categories():
    income_categories = {"Зарплата": 50000, "Премия": 10000, "Процентный доход": 500}
    result = get_income_categories(income_categories)
    assert result["total_amount"] == 60500
    assert len(result["main"]) == 3


def test_get_expences_income(mock_operations):
    expences, incomes = get_expences_income(mock_operations)
    assert expences["total_amount"] == 1500
    assert incomes["total_amount"] == 6000


def test_get_currency_stocks_empty_settings():
    with patch("src.views.read_user_settings") as mock_read_user_settings:
        mock_read_user_settings.return_value = {"user_currencies": [], "user_stocks": []}
        currency_list, stocks_list = get_currency_stocks("user_settings.json")
        assert currency_list == []
        assert stocks_list == []


def test_get_currency_stocks_invalid_file_path():
    with patch("src.views.read_user_settings") as mock_read_user_settings:
        mock_read_user_settings.side_effect = FileNotFoundError
        with pytest.raises(FileNotFoundError):
            get_currency_stocks("invalid_file_path.json")


@patch("requests.get")
def test_get_currency_price(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"rates": {"RUB": 75.0}}
    result = get_currency_price("USD")
    assert result == 75.0


@patch("requests.get")
def test_get_stock_price(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"price": 150.0}]
    result = get_stock_price("AAPL")
    assert result == 150.0