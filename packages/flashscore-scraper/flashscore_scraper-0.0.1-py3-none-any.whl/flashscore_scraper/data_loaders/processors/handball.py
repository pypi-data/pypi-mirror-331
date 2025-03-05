"""Handball-specific data processor implementation."""

from typing import Any, Dict

import pandas as pd

from .base import BaseProcessor


class HandballProcessor(BaseProcessor):
    """Handball-specific data processing logic."""

    def process_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process handball match data.

        Parameters
        ----------
        df : pd.DataFrame
            Raw match data DataFrame

        Returns:
        -------
        pd.DataFrame
            Processed DataFrame with handball-specific calculations
        """
        # Apply common processing from base class
        df = super().process_match_data(df)

        if df.empty:
            return df

        # Process additional_data for each match
        if "additional_data" in df.columns:
            # Extract period scores
            df["first_half_difference"] = df["additional_data"].apply(
                lambda x: self._calculate_period_difference(x, "h1"),
            )
            df["second_half_difference"] = df["additional_data"].apply(
                lambda x: self._calculate_period_difference(x, "h2"),
            )

            # Calculate period efficiencies
            df["first_half_efficiency"] = df.apply(
                lambda x: self._calculate_period_efficiency(x["additional_data"], "h1"),
                axis=1,
            )
            df["second_half_efficiency"] = df.apply(
                lambda x: self._calculate_period_efficiency(x["additional_data"], "h2"),
                axis=1,
            )

        return df

    def process_additional_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process handball-specific JSON data.

        Parameters
        ----------
        data : Dict[str, Any]
            Raw additional data dictionary

        Returns:
        -------
        Dict[str, Any]
            Processed handball-specific data
        """
        processed = {}

        # Process first half
        h1_home, h1_away = self._extract_period_scores(data, "h1")
        processed.update(
            {
                "home_score_h1": h1_home,
                "away_score_h1": h1_away,
                "total_score_h1": h1_home + h1_away,
                "score_difference_h1": h1_home - h1_away,
            }
        )

        # Process second half
        h2_home, h2_away = self._extract_period_scores(data, "h2")
        processed.update(
            {
                "home_score_h2": h2_home,
                "away_score_h2": h2_away,
                "total_score_h2": h2_home + h2_away,
                "score_difference_h2": h2_home - h2_away,
            }
        )

        # Calculate half-by-half metrics
        processed.update(
            {
                "home_efficiency_h1": self._safe_float(
                    h1_home / 30 if h1_home > 0 else 0
                ),
                "away_efficiency_h1": self._safe_float(
                    h1_away / 30 if h1_away > 0 else 0
                ),
                "home_efficiency_h2": self._safe_float(
                    h2_home / 30 if h2_home > 0 else 0
                ),
                "away_efficiency_h2": self._safe_float(
                    h2_away / 30 if h2_away > 0 else 0
                ),
            }
        )

        return processed

    def _calculate_period_difference(self, data: Dict[str, Any], period: str) -> int:
        """Calculate score difference for a specific period.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        period : str
            Period identifier (e.g., "h1", "h2")

        Returns:
        -------
        int
            Score difference for the period
        """
        home, away = self._extract_period_scores(data, period)
        return home - away

    def _calculate_period_efficiency(self, data: Dict[str, Any], period: str) -> float:
        """Calculate scoring efficiency for a specific period.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        period : str
            Period identifier (e.g., "h1", "h2")

        Returns:
        -------
        float
            Scoring efficiency for the period (goals per minute)
        """
        home, away = self._extract_period_scores(data, period)
        total_goals = home + away
        return self._safe_float(total_goals / 30 if total_goals > 0 else 0)


if __name__ == "__main__":
db_manager = DatabaseManager("database/database.db")

# For handball data
handball_loader = DataLoader(
    db_manager=db_manager,
    sport="handball",
    processor=HandballProcessor(),
)
