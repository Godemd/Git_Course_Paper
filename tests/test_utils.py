import json
import logging
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (get_currency_stocks, get_expences_categories, get_expences_income, get_income_categories,
                       get_json_from_dataframe, get_operations_by_date_range, read_data_transactions, setup_logger)


def test_setup_logger():
    """Проверяет, что функция setup_logger создает логгер с правильными настройками."""
    logger = setup_logger("test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)
    assert logger.handlers[0].formatter._fmt == "%(asctime)s %(levelname)-7s %(name)s:%(lineno)d -> %(message)s"


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data='[{"key": "value"}]')
@patch("json.load", return_value=[{"key": "value"}])
@patch("src.utils.logger")
def test_read_json_success(mock_logger, mock_json_load, mock_open, mock_exists):
    """Проверяет, что функция read_data_transactions успешно читает JSON-файл."""
    result = read_data_transactions("test.json")
    expected_df = pd.DataFrame([{"key": "value"}])
    assert result.equals(expected_df)  # Use DataFrame.equals for comparison
    mock_logger.warning.assert_not_called()


@patch("os.path.exists", return_value=False)
@patch("src.utils.logger")
def test_file_not_found(mock_logger, mock_exists):
    """Проверяет, что функция read_data_transactions генерирует FileNotFoundError, если файл не найден."""
    with pytest.raises(FileNotFoundError):
        read_data_transactions("missing.json")
    mock_logger.warning.assert_called_once_with("Файл missing.json не найден")


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="invalid json")
@patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "invalid json", 0))
@patch("src.utils.logger")
def test_json_decode_error(mock_logger, mock_json_load, mock_open, mock_exists):
    """Проверяет, что функция read_data_transactions генерирует ValueError, если JSON-файл некорректен."""
    with pytest.raises(ValueError):  # Expect ValueError instead of JSONDecodeError
        read_data_transactions("test.json")
    mock_logger.warning.assert_not_called()


@patch("os.path.exists", return_value=True)
@patch("builtins.open", new_callable=mock_open, read_data="invalid json")
@patch("json.load", return_value={})
@patch("src.utils.logger")
def test_json_list_error(mock_logger, mock_json_load, mock_open, mock_exists):
    """Проверяет, что функция read_data_transactions генерирует ValueError, если JSON-файл не содержит список."""
    with pytest.raises(ValueError):
        read_data_transactions("test.json")
    mock_logger.warning.assert_not_called()


@patch("pandas.read_csv")
@patch("os.path.exists", return_value=True)
@patch("src.utils.logger")
def test_read_csv_success(mock_logger, mock_exists, mock_read_csv):
    """Проверяет, что функция read_data_transactions успешно читает CSV-файл."""
    mock_read_csv.return_value = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    result = read_data_transactions("test.csv")
    assert result.equals(pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))
    mock_logger.warning.assert_not_called()


@patch("pandas.read_excel")
@patch("os.path.exists", return_value=True)
@patch("src.utils.logger")
def test_read_xlsx_success(mock_logger, mock_exists, mock_read_excel):
    """Проверяет, что функция read_data_transactions успешно читает XLSX-файл."""
    mock_read_excel.return_value = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    result = read_data_transactions("test.xlsx")
    assert result.equals(pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))
    mock_logger.warning.assert_not_called()


@patch("pandas.read_excel")
@patch("os.path.exists", return_value=True)
@patch("src.utils.logger")
def test_read_xls_success(mock_logger, mock_exists, mock_read_excel):
    """Проверяет, что функция read_data_transactions успешно читает XLS-файл."""
    mock_read_excel.return_value = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    result = read_data_transactions("test.xls")
    assert result.equals(pd.DataFrame({"col1": [1, 2], "col2": [3, 4]}))
    mock_logger.warning.assert_not_called()


@patch("os.path.exists", return_value=True)
@patch("src.utils.logger")
def test_read_transactions_file_unsupported_format(mock_logger, mock_exists):
    """Проверяет, что функция read_data_transactions генерирует NotImplementedError,
    если формат файла не поддерживается."""
    with pytest.raises(NotImplementedError):
        read_data_transactions("test.txt")
    mock_logger.warning.assert_called_once_with("Файл test.txt не поддерживается")


def test_get_json_from_dataframe():
    """Проверяет, что функция get_json_from_dataframe преобразует DataFrame в список словарей."""
    df = pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})
    result = get_json_from_dataframe(df)
    assert result == [{"col1": 1, "col2": 3}, {"col1": 2, "col2": 4}]


def mock_open(read_data):
    class MockFile:
        def __init__(self, read_data):
            self.read_data = read_data

        def read(self):
            return self.read_data

    return MagicMock(return_value=MockFile(read_data))


@patch("src.utils.read_data_transactions")
@patch("src.utils.get_json_from_dataframe")
def test_get_operations_by_date_range(mock_get_json_from_dataframe, mock_read_data_transactions):
    # Mock data
    mock_operations = [
        {"Дата операции": "22.05.2020 12:00:00", "Категория": "Продукты", "Статус": "OK", "Сумма платежа": -1000},
        {"Дата операции": "22.05.2020 15:00:00", "Категория": "Премия", "Статус": "OK", "Сумма платежа": 1000},
    ]
    mock_get_json_from_dataframe.return_value = mock_operations
    mock_read_data_transactions.return_value = "mock_dataframe"

    # Test case 1: Monthly operations
    result_monthly = get_operations_by_date_range("22.05.2020", "M")
    assert len(result_monthly) == 2

    # Test case 2: Weekly operations
    result_weekly = get_operations_by_date_range("22.05.2020", "W")
    assert len(result_weekly) == 2

    # Test case 3: Yearly operations
    result_yearly = get_operations_by_date_range("22.05.2020", "Y")
    assert len(result_yearly) == 2

    # Test case 4: All time operations
    result_all = get_operations_by_date_range("22.05.2020", "ALL")
    assert len(result_all) == 2


def test_get_expences_categories():
    # Mock data
    mock_expences_categories = {"Продукты": 1000, "Премия": 500}

    result = get_expences_categories(mock_expences_categories)
    assert result["total_amount"] == 1500
    assert len(result["main"]) == 2
    assert len(result["transfers_and_cash"]) == 0


def test_get_income_categories():
    # Mock data
    mock_income_categories = {"Зарплата": 3000, "Дивиденды": 1000}

    result = get_income_categories(mock_income_categories)
    assert result["total_amount"] == 4000
    assert len(result["main"]) == 2


def test_get_expences_income():
    # Mock data
    mock_operations = [
        {"Дата операции": "22.05.2020 12:00:00", "Категория": "Продукты", "Статус": "OK", "Сумма платежа": -1000},
        {"Дата операции": "22.05.2020 15:00:00", "Категория": "Премия", "Статус": "OK", "Сумма платежа": 1000},
    ]

    result_expences, result_income = get_expences_income(mock_operations)
    assert result_expences["total_amount"] == 1000
    assert result_income["total_amount"] == 1000


@patch("src.utils.read_user_settings")
@patch("src.utils.get_currency_price")
@patch("src.utils.get_stock_price")
def test_get_currency_stocks(mock_get_stock_price, mock_get_currency_price, mock_read_user_settings):
    # Mock data
    mock_read_user_settings.return_value = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "GOOGL"]}
    mock_get_currency_price.side_effect = lambda x: 75.0 if x == "USD" else 85.0
    mock_get_stock_price.side_effect = lambda x: 300.0 if x == "AAPL" else 1500.0

    result_currency, result_stocks = get_currency_stocks("mock_file_path")
    assert len(result_currency) == 2
    assert len(result_stocks) == 2

    # Check currency rates
    assert result_currency[0]["currency"] == "USD"
    assert result_currency[0]["rate"] == 75.0
    assert result_currency[1]["currency"] == "EUR"
    assert result_currency[1]["rate"] == 85.0

    # Check stock prices
    assert result_stocks[0]["stock"] == "AAPL"
    assert result_stocks[0]["price"] == 300.0
    assert result_stocks[1]["stock"] == "GOOGL"
    assert result_stocks[1]["price"] == 1500.0
