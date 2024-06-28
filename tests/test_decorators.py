import os

import pandas as pd

from src.decorators import ReportSaver


def test_deco():

    @ReportSaver.to_excel()
    def some_func():
        return pd.DataFrame({"Test01": [0], "Test02": [1]})

    some_func()
    created_file_path = os.path.join("data/", "result_some_func.xls")
    assert os.path.exists(created_file_path)
    assert pd.read_excel(created_file_path).to_dict("records") == [{"Test01": 0, "Test02": 1}]
    os.remove(created_file_path)
    assert not os.path.exists(created_file_path)