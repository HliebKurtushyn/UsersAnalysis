import pandas as pd
import pytest

from ml_pipeline.data_loader import REQUIRED_COLUMNS, load_data


def create_csv(path, data):
    pd.DataFrame(data).to_csv(path, index=False)


def test_load_data_reads_csv(tmp_path):
    csv_path = tmp_path / "events.csv"
    create_csv(
        csv_path,
        {
            "event_type": ["view", "purchase"],
            "user_id": [101, 102],
            "event_time": ["2019-11-01 10:00:00", "2019-11-01 10:05:00"],
            "product_id": [1001, 1002],
            "category_code": ["electronics", "audio"],
            "brand": ["Brand A", "Brand B"],
            "price": [100.0, 200.0],
        },
    )

    result = load_data(csv_path)

    assert REQUIRED_COLUMNS.issubset(result.columns)
    assert len(result) == 2
    assert result["event_type"].tolist() == ["view", "purchase"]


def test_load_data_limits_number_of_rows(tmp_path):
    csv_path = tmp_path / "events.csv"
    create_csv(
        csv_path,
        {
            "event_type": ["view", "cart", "purchase"],
            "user_id": [101, 102, 103],
            "event_time": ["t1", "t2", "t3"],
            "product_id": [1001, 1002, 1003],
            "category_code": ["electronics", "audio", "electronics"],
            "brand": ["Brand A", "Brand B", "Brand A"],
            "price": [100.0, 200.0, 300.0],
        },
    )

    result = load_data(csv_path, rows=2)

    assert len(result) == 2
    assert result["user_id"].tolist() == [101, 102]


def test_load_data_rejects_csv_without_required_columns(tmp_path):
    csv_path = tmp_path / "invalid.csv"
    create_csv(
        csv_path,
        {
            "event_type": ["view"],
            "user_id": [101],
        },
    )

    with pytest.raises(ValueError, match="event_time"):
        load_data(csv_path)
