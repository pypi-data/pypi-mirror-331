"""Football-specific data processor implementation."""

from typing import Any, Dict

import pandas as pd

from .base import BaseProcessor


class FootballProcessor(BaseProcessor):
    """Football-specific data processing logic."""

    def process_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process football match data.

        Parameters
        ----------
        df : pd.DataFrame
            Raw match data DataFrame

        Returns:
        -------
        pd.DataFrame
            Processed DataFrame with football-specific calculations
        """
        # Apply common processing from base class
        df = super().process_match_data(df)

        if df.empty:
            return df

        # Process additional_data for each match
        if "additional_data" in df.columns:
            # Extract period scores
            df["first_half_difference"] = df["additional_data"].apply(
                lambda x: self._calculate_period_difference(x, "first_half"),
            )
            df["second_half_difference"] = df["additional_data"].apply(
                lambda x: self._calculate_period_difference(x, "second_half"),
            )

            # Calculate period totals
            df["first_half_goals"] = df["additional_data"].apply(
                lambda x: self._calculate_period_total(x, "first_half"),
            )
            df["second_half_goals"] = df["additional_data"].apply(
                lambda x: self._calculate_period_total(x, "second_half"),
            )

            # Extract extra time and penalties if available
            df["extra_time_played"] = df["additional_data"].apply(
                lambda x: self._has_extra_time(x),
            )
            df["penalties_played"] = df["additional_data"].apply(
                lambda x: self._has_penalties(x),
            )

        return df

    def process_additional_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process football-specific JSON data.

        Parameters
        ----------
        data : Dict[str, Any]
            Raw additional data dictionary

        Returns:
        -------
        Dict[str, Any]
            Processed football-specific data
        """
        processed = {}

        # Process regular time periods
        for period in ["first_half", "second_half"]:
            home, away = self._extract_period_scores(data, period)
            processed.update(
                {
                    f"home_score_{period}": home,
                    f"away_score_{period}": away,
                    f"total_goals_{period}": home + away,
                    f"score_difference_{period}": home - away,
                }
            )

        # Process extra time if available
        if self._has_extra_time(data):
            et_home, et_away = self._extract_period_scores(data, "extra_time")
            processed.update(
                {
                    "home_score_extra_time": et_home,
                    "away_score_extra_time": et_away,
                    "total_goals_extra_time": et_home + et_away,
                    "score_difference_extra_time": et_home - et_away,
                }
            )

        # Process penalties if available
        if self._has_penalties(data):
            pen_home, pen_away = self._extract_period_scores(data, "penalties")
            processed.update(
                {
                    "home_score_penalties": pen_home,
                    "away_score_penalties": pen_away,
                    "penalties_difference": pen_home - pen_away,
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
            Period identifier (e.g., "first_half", "second_half")

        Returns:
        -------
        int
            Score difference for the period
        """
        home, away = self._extract_period_scores(data, period)
        return home - away

    def _calculate_period_total(self, data: Dict[str, Any], period: str) -> int:
        """Calculate total goals for a specific period.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        period : str
            Period identifier (e.g., "first_half", "second_half")

        Returns:
        -------
        int
            Total goals for the period
        """
        home, away = self._extract_period_scores(data, period)
        return home + away

    def _has_extra_time(self, data: Dict[str, Any]) -> bool:
        """Check if match went to extra time.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary

        Returns:
        -------
        bool
            True if match had extra time
        """
        return any(
            data.get(f"{team}_score_extra_time", 0) > 0 for team in ["home", "away"]
        )

    def _has_penalties(self, data: Dict[str, Any]) -> bool:
        """Check if match went to penalties.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary

        Returns:
        -------
        bool
            True if match had penalties
        """
        return any(
            data.get(f"{team}_score_penalties", 0) > 0 for team in ["home", "away"]
        )
