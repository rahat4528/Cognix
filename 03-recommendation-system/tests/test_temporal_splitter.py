import pandas as pd
from data_processing.temporal_splitter import TemporalDataSplitter


def test_temporal_splitter_no_leakage():
    # Construct sequence with clear temporal ordering
    timestamps = list(range(100, 200))
    df = pd.DataFrame({
        "user_id": [f"u{i%5}" for i in range(100)],
        "item_id": [f"item{i%10}" for i in range(100)],
        "timestamp": timestamps
    })

    splitter = TemporalDataSplitter(train_ratio=0.60, val_ratio=0.20)
    train_df, val_df, test_df = splitter.split(df, timestamp_col="timestamp")

    assert len(train_df) == 60
    assert len(val_df) == 20
    assert len(test_df) == 20

    # Strict temporal boundary check
    assert train_df['timestamp'].max() <= val_df['timestamp'].min()
    assert val_df['timestamp'].max() <= test_df['timestamp'].min()
