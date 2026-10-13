import pandas as pd

from ml_pipeline.eda_and_cleaning import (
    clean_data,
    save_cleaned_data,
    summarize_events,
)


def test_clean_data_removes_duplicates_and_fills_missing_values():
    data = pd.DataFrame(
        {
            "event_type": ["view", "view", "purchase"],
            "event_time": [
                "2019-11-01 10:00:00",
                "2019-11-01 10:00:00",
                "2019-11-01 10:05:00",
            ],
            "brand": [None, None, "Brand A"],
            "category_code": ["electronics", "electronics", None],
        }
    )

    result = clean_data(data)

    assert len(result) == 2
    assert result["brand"].tolist() == ["Unknown", "Brand A"]
    assert result["category_code"].tolist() == ["electronics", "Unknown"]


def test_clean_data_does_not_modify_input():
    data = pd.DataFrame(
        {
            "event_type": ["view"],
            "event_time": ["2019-11-01 10:00:00"],
            "brand": [None],
            "category_code": [None],
        }
    )
    original = data.copy(deep=True)

    clean_data(data)

    pd.testing.assert_frame_equal(data, original)


def test_clean_data_preserves_columns_without_missing_values():
    data = pd.DataFrame(
        {
            "event_type": ["view"],
            "event_time": ["2019-11-01 10:00:00"],
            "brand": ["Brand A"],
            "category_code": ["electronics"],
        }
    )

    result = clean_data(data)

    assert list(result.columns) == list(data.columns)
    assert result.loc[0, "event_type"] == "view"
    assert result.loc[0, "event_time"] == pd.Timestamp("2019-11-01 10:00:00")
    assert result.loc[0, "brand"] == "Brand A"
    assert result.loc[0, "category_code"] == "electronics"


def test_summarize_events_returns_counts_and_percentages():
    data = pd.DataFrame({"event_type": ["view", "view", "cart", "purchase"]})

    result = summarize_events(data)

    assert result.loc["view", "count"] == 2
    assert result.loc["cart", "count"] == 1
    assert result.loc["purchase", "percentage"] == 25.0
    assert result["percentage"].sum() == 100.0


def test_save_cleaned_data_creates_directory_and_file(tmp_path):
    data = pd.DataFrame(
        {
            "event_type": ["view"],
            "event_time": ["2019-11-01 10:00:00"],
            "brand": ["Brand A"],
            "category_code": ["electronics"],
        }
    )
    output_path = tmp_path / "cleaned" / "events.csv"

    result = save_cleaned_data(data, output_path)

    assert result == output_path
    assert output_path.exists()
    pd.testing.assert_frame_equal(pd.read_csv(output_path), data)


def test_clean_data_converts_valid_dates_and_coerces_invalid_dates():
    data = pd.DataFrame(
        {
            "event_type": ["view", "purchase"],
            "event_time": ["2019-11-01 10:00:00", "not-a-date"],
            "brand": ["Brand A", "Brand B"],
            "category_code": ["electronics", "audio"],
        }
    )

    result = clean_data(data)

    assert pd.api.types.is_datetime64_dtype(result["event_time"])
    assert result.loc[0, "event_time"] == pd.Timestamp("2019-11-01 10:00:00")
    assert pd.isna(result.loc[1, "event_time"])


def test_clean_data_drops_rows_with_missing_required_values():
    data = pd.DataFrame(
        {
            "event_type": ["view", "cart", "purchase", "view"],
            "event_time": [
                "2019-11-01 10:00:00",
                "2019-11-01 10:01:00",
                "2019-11-01 10:02:00",
                "2019-11-01 10:03:00",
            ],
            "user_id": [101, None, 103, 104],
            "product_id": [1001, 1002, None, 1004],
            "price": [100.0, 200.0, 300.0, None],
            "brand": ["Brand A", "Brand B", "Brand C", "Brand D"],
            "category_code": ["audio", "audio", "phone", "phone"],
        }
    )

    result = clean_data(data)

    assert len(result) == 1
    assert result.iloc[0]["user_id"] == 101
    assert result.iloc[0]["product_id"] == 1001
    assert result.iloc[0]["price"] == 100.0


def test_clean_data_allows_missing_optional_columns():
    data = pd.DataFrame(
        {
            "event_type": ["view"],
            "brand": [None],
            "category_code": [None],
        }
    )

    result = clean_data(data)

    assert list(result.columns) == ["event_type", "brand", "category_code"]
    assert result.loc[0, "brand"] == "Unknown"
    assert result.loc[0, "category_code"] == "Unknown"


def test_clean_data_does_not_require_event_time_column():
    data = pd.DataFrame(
        {
            "event_type": ["view"],
            "user_id": [101],
            "product_id": [1001],
            "price": [100.0],
        }
    )

    result = clean_data(data)

    pd.testing.assert_frame_equal(result, data)
