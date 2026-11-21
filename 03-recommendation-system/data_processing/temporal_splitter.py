from typing import Tuple
import pandas as pd


class TemporalDataSplitter:
    """
    Chronological temporal dataset splitter.
    Guarantees zero future-to-past information leakage by partitioning
    strictly on timestamp cutoffs.
    """
    def __init__(self, train_ratio: float = 0.60, val_ratio: float = 0.20):
        if train_ratio + val_ratio >= 1.0:
            raise ValueError("train_ratio + val_ratio must be strictly less than 1.0")
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio

    def split(
        self,
        df: pd.DataFrame,
        timestamp_col: str = "timestamp"
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Partitions dataframe into (train_df, val_df, test_df).
        """
        if df.empty:
            return df.copy(), df.copy(), df.copy()

        sorted_df = df.sort_values(timestamp_col).reset_index(drop=True)

        t_cutoff_1 = sorted_df[timestamp_col].quantile(self.train_ratio)
        t_cutoff_2 = sorted_df[timestamp_col].quantile(self.train_ratio + self.val_ratio)

        train_df = sorted_df[sorted_df[timestamp_col] <= t_cutoff_1].copy()
        val_df = sorted_df[
            (sorted_df[timestamp_col] > t_cutoff_1) & 
            (sorted_df[timestamp_col] <= t_cutoff_2)
        ].copy()
        test_df = sorted_df[sorted_df[timestamp_col] > t_cutoff_2].copy()

        # Sanity assertion against leakage
        if not train_df.empty and not val_df.empty:
            assert train_df[timestamp_col].max() <= val_df[timestamp_col].min(), "Data leakage: train overlap with validation!"
        if not val_df.empty and not test_df.empty:
            assert val_df[timestamp_col].max() <= test_df[timestamp_col].min(), "Data leakage: validation overlap with test!"

        return train_df, val_df, test_df
