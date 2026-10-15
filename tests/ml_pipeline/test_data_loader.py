import pandas as pd
import pytest

from ml_pipeline.data_loader import (
    REQUIRED_COLUMNS,
    load_data,
)


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


def test_load_data_rejects_missing_file(tmp_path):
    missing_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="missing.csv"):
        load_data(missing_path)


def test_load_data_uses_cleaned_default_data_when_available(tmp_path):
    raw_path = tmp_path / "raw.csv"
    cleaned_path = tmp_path / "cleaned.csv"

    create_csv(
        raw_path,
        {
            "event_type": ["view"],
            "user_id": [101],
            "event_time": ["raw"],
            "product_id": [1001],
            "category_code": ["electronics"],
            "brand": ["Brand A"],
            "price": [100.0],
        },
    )
    create_csv(
        cleaned_path,
        {
            "event_type": ["purchase"],
            "user_id": [202],
            "event_time": ["cleaned"],
            "product_id": [2002],
            "category_code": ["audio"],
            "brand": ["Brand B"],
            "price": [200.0],
        },
    )

    result = load_data(path=None, cleaned_path=cleaned_path)

    assert result["event_type"].tolist() == ["purchase"]


def test_load_data_uses_explicit_path_instead_of_cleaned_cache(tmp_path):
    raw_path = tmp_path / "raw.csv"
    cleaned_path = tmp_path / "cleaned.csv"
    create_csv(
        raw_path,
        {
            "event_type": ["view"],
            "user_id": [101],
            "event_time": ["raw"],
            "product_id": [1001],
            "category_code": ["electronics"],
            "brand": ["Brand A"],
            "price": [100.0],
        },
    )
    create_csv(
        cleaned_path,
        {
            "event_type": ["purchase"],
            "user_id": [202],
            "event_time": ["cleaned"],
            "product_id": [2002],
            "category_code": ["audio"],
            "brand": ["Brand B"],
            "price": [200.0],
        },
    )

    result = load_data(raw_path, cleaned_path=cleaned_path)

    assert result["event_type"].tolist() == ["view"]
