"""Volleyball-specific data processor implementation."""

from typing import Any, Dict, List, Tuple

import pandas as pd

from .base import BaseProcessor


class VolleyballProcessor(BaseProcessor):
    """Volleyball-specific data processing logic."""

    MAX_SETS = 5

    def process_match_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process volleyball match data.

        Parameters
        ----------
        df : pd.DataFrame
            Raw match data DataFrame

        Returns:
        -------
        pd.DataFrame
            Processed DataFrame with volleyball-specific calculations
        """
        # Apply common processing from base class
        df = super().process_match_data(df)

        if df.empty:
            return df

        # Process additional_data for each match
        if "additional_data" in df.columns:
            # Calculate set-specific metrics
            for set_num in range(1, self.MAX_SETS + 1):
                set_key = f"set_{set_num}"

                # Set differences
                df[f"{set_key}_difference"] = df["additional_data"].apply(
                    lambda x: self._calculate_set_difference(x, set_num),
                )

                # Set totals
                df[f"{set_key}_total"] = df["additional_data"].apply(
                    lambda x: self._calculate_set_total(x, set_num),
                )

            # Calculate match statistics
            df["sets_played"] = df["additional_data"].apply(
                self._count_sets_played,
            )
            df["avg_points_per_set"] = df["additional_data"].apply(
                self._calculate_avg_points_per_set,
            )
            df["decisive_set_played"] = df["sets_played"] == self.MAX_SETS

        return df

    def process_additional_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process volleyball-specific JSON data.

        Parameters
        ----------
        data : Dict[str, Any]
            Raw additional data dictionary

        Returns:
        -------
        Dict[str, Any]
            Processed volleyball-specific data
        """
        processed = {}
        set_scores: List[Tuple[int, int]] = []

        # Process each set
        for set_num in range(1, self.MAX_SETS + 1):
            home, away = self._extract_period_scores(data, f"set_{set_num}")
            if home > 0 or away > 0:  # Set was played
                set_scores.append((home, away))
                processed.update(
                    {
                        f"home_score_set_{set_num}": home,
                        f"away_score_set_{set_num}": away,
                        f"total_points_set_{set_num}": home + away,
                        f"point_difference_set_{set_num}": home - away,
                    }
                )

        # Calculate match statistics
        if set_scores:
            total_sets = len(set_scores)
            total_points = sum(home + away for home, away in set_scores)

            processed.update(
                {
                    "sets_played": total_sets,
                    "avg_points_per_set": round(total_points / total_sets, 2),
                    "total_points": total_points,
                    "decisive_set_played": total_sets == self.MAX_SETS,
                    "min_points_in_set": min(home + away for home, away in set_scores),
                    "max_points_in_set": max(home + away for home, away in set_scores),
                }
            )

            # Calculate set win statistics
            home_sets = sum(1 for home, away in set_scores if home > away)
            away_sets = total_sets - home_sets
            processed.update(
                {
                    "home_sets_won": home_sets,
                    "away_sets_won": away_sets,
                    "set_win_ratio": round(home_sets / total_sets, 3),
                }
            )

        return processed

    def _calculate_set_difference(self, data: Dict[str, Any], set_num: int) -> int:
        """Calculate point difference for a specific set.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        set_num : int
            Set number (1-5)

        Returns:
        -------
        int
            Point difference for the set
        """
        home, away = self._extract_period_scores(data, f"set_{set_num}")
        return home - away

    def _calculate_set_total(self, data: Dict[str, Any], set_num: int) -> int:
        """Calculate total points for a specific set.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary
        set_num : int
            Set number (1-5)

        Returns:
        -------
        int
            Total points for the set
        """
        home, away = self._extract_period_scores(data, f"set_{set_num}")
        return home + away

    def _count_sets_played(self, data: Dict[str, Any]) -> int:
        """Count number of sets played in the match.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary

        Returns:
        -------
        int
            Number of sets played
        """
        return sum(
            1
            for set_num in range(1, self.MAX_SETS + 1)
            if any(self._extract_period_scores(data, f"set_{set_num}"))
        )

    def _calculate_avg_points_per_set(self, data: Dict[str, Any]) -> float:
        """Calculate average points per set.

        Parameters
        ----------
        data : Dict[str, Any]
            Additional data dictionary

        Returns:
        -------
        float
            Average points per set
        """
        set_totals = [
            sum(self._extract_period_scores(data, f"set_{set_num}"))
            for set_num in range(1, self.MAX_SETS + 1)
            if any(self._extract_period_scores(data, f"set_{set_num}"))
        ]

        return round(sum(set_totals) / len(set_totals), 2) if set_totals else 0.0
