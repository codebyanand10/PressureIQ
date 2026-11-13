"""Pressure feature and score normalization module.

Provides percentile and empirical CDF scaling across competitions with
group-size validation and transparent fallback to global distributions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Dict, Optional, Union
from src.pressure.pressure_config import PressureConfig


class PressureNormalizer:
    """Normalizes raw pressure values using empirical percentile scaling."""

    def __init__(self, config: Optional[PressureConfig] = None) -> None:
        """Initialize normalizer with settings."""
        self.config = config or PressureConfig()
        self.method: str = self.config.normalization_method
        self.min_group_size: int = self.config.minimum_group_size
        self.fallback_to_global: bool = self.config.fallback_to_global

        self.global_quantiles: Optional[np.ndarray] = None
        self.group_quantiles: Dict[str, np.ndarray] = {}

    def fit(self, values: pd.Series, groups: Optional[pd.Series] = None) -> "PressureNormalizer":
        """Compute quantile breakpoints for normalization."""
        clean_vals = values.dropna().values
        if len(clean_vals) == 0:
            self.global_quantiles = np.linspace(0.0, 100.0, 101)
            return self

        # Global percentiles (0 to 100)
        self.global_quantiles = np.percentile(clean_vals, np.linspace(0, 100, 101))

        if groups is not None:
            df = pd.DataFrame({"val": values, "grp": groups}).dropna()
            for grp_name, grp_data in df.groupby("grp"):
                grp_vals = grp_data["val"].values
                if len(grp_vals) >= self.min_group_size:
                    self.group_quantiles[str(grp_name)] = np.percentile(grp_vals, np.linspace(0, 100, 101))

        return self

    def transform(
        self,
        values: Union[pd.Series, np.ndarray],
        groups: Optional[Union[pd.Series, np.ndarray]] = None,
    ) -> np.ndarray:
        """Transform values to [0.0, 100.0] percentile scale."""
        vals = np.asarray(values, dtype=float)
        if self.global_quantiles is None:
            raise RuntimeError("PressureNormalizer must be fit before calling transform().")

        if groups is None:
            # Global transform
            # np.searchsorted gives rank between 0 and 100
            ranks = np.searchsorted(self.global_quantiles, vals, side="right")
            ranks = np.clip(ranks, 0, 100).astype(float)
            return ranks

        grps = np.asarray(groups, dtype=str)
        transformed = np.zeros_like(vals, dtype=float)

        for i, (v, g) in enumerate(zip(vals, grps)):
            if np.isnan(v):
                transformed[i] = np.nan
                continue

            ref_quantiles = self.group_quantiles.get(g, None)
            if ref_quantiles is None or not self.fallback_to_global and g not in self.group_quantiles:
                ref_quantiles = self.global_quantiles

            rank = float(np.searchsorted(ref_quantiles, v, side="right"))
            transformed[i] = np.clip(rank, 0.0, 100.0)

        return transformed

    def fit_transform(
        self,
        values: pd.Series,
        groups: Optional[pd.Series] = None,
    ) -> pd.Series:
        """Fit and transform in a single step, preserving pandas Series structure."""
        self.fit(values, groups)
        transformed = self.transform(values, groups)
        return pd.Series(transformed, index=values.index, name=values.name)

