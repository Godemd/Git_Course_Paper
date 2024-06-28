import json
import logging
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.utils import get_json_from_dataframe, read_data_transactions, setup_logger


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
    """Проверяет, что функция read_data_transactions генерирует NotImplementedError, если формат файла не поддерживается."""
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