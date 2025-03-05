"""Base processor interface for sport-specific data processing."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

import pandas as pd


class BaseProcessor(ABC):
    """Base interface for sport-specific data processing."""

    @abstractmethod
    def process_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process match data with sport-specific logic.

        Parameters
        ----------
        df : pd.DataFrame
            Raw match data DataFrame

        Returns:
        -------
        pd.DataFrame
            Processed DataFrame with sport-specific calculations
        """
        # Add common processing that applies to all sports
        if not df.empty:
            df = df.assign(
                goal_difference=lambda x: x["home_score"] - x["away_score"],
                total_score=lambda x: x["home_score"] + x["away_score"],
            )
        return df

    @abstractmethod
    def process_additional_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process sport-specific JSON data.

        Parameters
        ----------
        data : Dict[str, Any]
            Raw additional data dictionary

        Returns:
        -------
        Dict[str, Any]
            Processed sport-specific data
        """
        pass

    def _safe_int(self, value: Any, default: int = 0) -> int:
        """Safely convert value to integer.

        Parameters
        ----------
        value : Any
            Value to convert
        default : int, optional
            Default value if conversion fails, by default 0

        Returns:
        -------
        int
            Converted integer value
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        """Safely convert value to float.

        Parameters
        ----------
        value : Any
            Value to convert
        default : float, optional
            Default value if conversion fails, by default 0.0

        Returns:
        -------
        float
            Converted float value
        """
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _extract_period_scores(
        self, data: Dict[str, Any], period_key: str
    ) -> Tuple[int, int]:
        """Extract home and away scores for a specific period.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        period_key : str
            Key for the period scores

        Returns:
        -------
        Tuple[int, int]
            Tuple of (home_score, away_score)
        """
        home_key = f"home_score_{period_key}"
        away_key = f"away_score_{period_key}"
        return (self._safe_int(data.get(home_key)), self._safe_int(data.get(away_key)))
