import pandas as pd

from ml_pipeline.data_loader import load_data
from ml_pipeline.prepare_data import prepare_data


def test_prepare_data_creates_cleaned_csv(tmp_path):
    source_path = tmp_path / "raw" / "events.csv"
    output_path = tmp_path / "cleaned" / "events.csv"
    source_path.parent.mkdir()

    pd.DataFrame(
        {
            "event_type": ["view", "view", "purchase"],
            "user_id": [101, 101, 102],
            "event_time": [
                "2019-11-01 10:00:00",
                "2019-11-01 10:00:00",
                "2019-11-01 10:05:00",
            ],
            "product_id": [1001, 1001, 1002],
            "category_code": ["electronics", "electronics", "audio"],
            "brand": ["Brand A", "Brand A", "Brand B"],
            "price": [100.0, 100.0, 200.0],
        }
    ).to_csv(source_path, index=False)

    result_path = prepare_data(source_path, output_path)
    result = load_data(result_path)

    assert result_path == output_path
    assert len(result) == 2
    assert result["category_code"].tolist() == ["electronics", "audio"]
    assert pd.to_datetime(result["event_time"]).notna().all()
