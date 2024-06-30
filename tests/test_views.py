import json
import unittest
from unittest.mock import patch

from src.views import post_events_response


def test_post_events_response():
    # Mock data
    mock_operations = [
        {"Дата операции": "22.05.2020 12:00:00", "Категория": "Продукты", "Статус": "OK", "Сумма платежа": -1000},
        {"Дата операции": "22.05.2020 15:00:00", "Категория": "Премия", "Статус": "OK", "Сумма платежа": 1000},
    ]
    mock_currency_stocks = [{"currency": "USD", "rate": 75.0}, {"currency": "EUR", "rate": 85.0}]

    with patch("src.views.get_operations_by_date_range") as mock_get_operations_by_date_range, patch(
        "src.views.get_expences_income"
    ) as mock_get_expences_income, patch("src.views.get_currency_stocks") as mock_get_currency_stocks, patch(
        "src.views.setup_logger"
    ) as mock_setup_logger:

        # Configure mock return values
        mock_get_operations_by_date_range.return_value = mock_operations
        mock_get_expences_income.return_value = (
            {"total_amount": 1000, "main": [], "transfers_and_cash": []},
            {"total_amount": 1000, "main": []},
        )
        mock_get_currency_stocks.return_value = mock_currency_stocks
        mock_setup_logger.return_value = None  # Mocking setup_logger

        # Calling the function under test
        result = post_events_response("22.05.2020", "W")

        # Asserting the result is a valid JSON string
        assert isinstance(result, str)

        # Converting JSON string back to dictionary for validation
        result_dict = json.loads(result)

        # Asserting the structure and content of the returned JSON
        assert "expences" in result_dict
        assert "income" in result_dict
        assert "currency_rates" in result_dict
        assert "stock_prices" in result_dict

        # Asserting the content of "expences" and "income"
        assert result_dict["expences"]["total_amount"] == 1000
        assert result_dict["income"]["total_amount"] == 1000


if __name__ == "__main__":
    unittest.main()
