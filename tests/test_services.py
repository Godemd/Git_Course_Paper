import json
from unittest.mock import patch

import pytest

from src.services import search_by_persons


@pytest.fixture
def mock_transactions():
    return [
        {"Категория": "Переводы", "Описание": "Перевод на И.И."},
        {"Категория": "Продукты", "Описание": "Покупка продуктов"},
        {"Категория": "Переводы", "Описание": "Перевод на П.П."},
        {"Категория": "Транспорт", "Описание": "Такси до работы"},
    ]


def test_search_by_persons_with_matches(mock_transactions):
    expected_result = [
        {"Категория": "Переводы", "Описание": "Перевод на И.И."},
        {"Категория": "Переводы", "Описание": "Перевод на П.П."},
    ]

    with patch("src.services.setup_logger"), patch("src.services.re.findall", return_value=["И.И.", "П.П."]), patch(
        "src.services.json.dumps", side_effect=json.dumps
    ), patch(
        "src.services.json.loads", side_effect=json.loads
    ):  # использование реальной функции loads
        result = search_by_persons(mock_transactions)
        result_dict = json.loads(result)
        assert result_dict == expected_result


def test_search_by_persons_no_matches(mock_transactions):
    expected_result = []

    with patch("src.services.setup_logger"), patch("src.services.re.findall", return_value=[]), patch(
        "src.services.json.dumps", side_effect=json.dumps
    ), patch("src.services.json.loads", side_effect=json.loads):
        result = search_by_persons(mock_transactions)
        result_dict = json.loads(result)
        assert result_dict == expected_result
