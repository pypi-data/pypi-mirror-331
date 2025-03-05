"""Base data loader implementation."""

import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from ..core.database import DatabaseManager


class DataLoader:
    """Generic data loader supporting multiple sports with JSON additional data."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        sport: str,
        date_format: str = "%d.%m.%Y %H:%M",
    ):
        """Initialize data loader with configuration options.

        Parameters
        ----------
        db_manager : DatabaseManager
            Database manager instance for data access
        sport : str
            Sport type (e.g., 'handball', 'football', 'volleyball')
        date_format : str, optional
            Date format for parsing dates, by default "%d.%m.%Y %H:%M"
        """
        self.db_manager = db_manager
        self.sport = sport.lower()
        self.date_format = date_format
        self.sport_id = self._get_sport_id()

    def _get_sport_id(self) -> int:
        """Get or register sport ID.

        Returns:
        -------
        int
            Sport ID from database
        """
        return self.db_manager.register_sport(self.sport)

    def _get_current_teams(
        self,
        league: Optional[str] = None,
        seasons: Optional[List[str]] = None,
        filters: Optional[Dict[str, str]] = None,
    ) -> pd.Series:
        """Retrieve current teams with optional filters.

        Parameters
        ----------
        league : Optional[str], optional
            League name, by default None
        seasons : Optional[List[str]], optional
            List of season identifiers, by default None
        filters : Optional[Dict[str, str]], optional
            Additional filter criteria, by default None

        Returns:
        -------
        pd.Series
            Series of team names

        Raises:
        ------
        ValueError
            If no teams are found for the specified criteria
        """
        base_query = """
            SELECT DISTINCT home_team as team_name
            FROM match_data
            WHERE sport_id = :sport_id
            UNION
            SELECT DISTINCT away_team as team_name
            FROM match_data
            WHERE sport_id = :sport_id
        """
        params: Dict[str, Union[int, str]] = {"sport_id": self.sport_id}

        if league:
            base_query = base_query.replace(
                "WHERE sport_id = :sport_id",
                "WHERE sport_id = :sport_id AND league = :league",
            )
            params["league"] = league

        if seasons:
            season_clause = " OR ".join(
                [f"season = :season_{i}" for i in range(len(seasons))]
            )
            base_query = base_query.replace(
                "WHERE sport_id = :sport_id",
                f"WHERE sport_id = :sport_id AND ({season_clause})",
            )
            for i, season in enumerate(seasons):
                params[f"season_{i}"] = season

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(base_query, params)
            teams = pd.Series([row[0] for row in cursor.fetchall()])

        if teams.empty:
            raise ValueError(f"No teams found for {self.sport} {league} {seasons}")

        return teams

    def load_matches(
        self,
        league: Optional[str] = None,
        seasons: Optional[List[str]] = None,
        date_range: Optional[Tuple[str, str]] = None,
        team_filters: Optional[Dict[str, str]] = None,
    ) -> pd.DataFrame:
        """Load match data with flexible filtering options.

        Parameters
        ----------
        league : Optional[str], optional
            League name, by default None
        seasons : Optional[List[str]], optional
            List of season identifiers, by default None
        date_range : Optional[Tuple[str, str]], optional
            Tuple of (start_date, end_date), by default None
        team_filters : Optional[Dict[str, str]], optional
            Additional filters for teams, by default None

        Returns:
        -------
        pd.DataFrame
            Processed DataFrame of match data
        """
        base_query = """
            SELECT
                m.*,
                json_extract(m.additional_data, '$') as additional_data_json
            FROM match_data m
            WHERE m.sport_id = :sport_id
        """
        params: Dict[str, Union[int, str]] = {"sport_id": self.sport_id}

        if league:
            base_query += " AND m.league = :league"
            params["league"] = league

        if seasons:
            season_clause = " OR ".join(
                [f"m.season = :season_{i}" for i in range(len(seasons))]
            )
            base_query += f" AND ({season_clause})"
            for i, season in enumerate(seasons):
                params[f"season_{i}"] = season

        if date_range:
            base_query += " AND m.datetime BETWEEN :start_date AND :end_date"
            params["start_date"] = date_range[0]
            params["end_date"] = date_range[1]

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(base_query, params)
            data = cursor.fetchall()

        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Parse dates
        df["datetime"] = pd.to_datetime(df["datetime"], format=self.date_format)

        # Parse JSON additional data
        if "additional_data_json" in df.columns:
            df["additional_data"] = df["additional_data_json"].apply(
                lambda x: {} if pd.isna(x) else json.loads(x)
            )
            df = df.drop("additional_data_json", axis=1)

        return df.sort_values("datetime")

    def load_odds(self, match_ids: List[str]) -> pd.DataFrame:
        """Load odds data for given match IDs.

        Parameters
        ----------
        match_ids : List[str]
            List of match IDs to load odds for

        Returns:
        -------
        pd.DataFrame
            DataFrame containing odds data
        """
        if not match_ids:
            return pd.DataFrame()

        base_query = """
            SELECT
                flashscore_id,
                bookmaker,
                home_odds,
                draw_odds,
                away_odds
            FROM odds_data
            WHERE sport_id = :sport_id
            AND flashscore_id IN ({})
        """.format(",".join(f":id_{i}" for i in range(len(match_ids))))

        params: Dict[str, Union[int, str]] = {"sport_id": self.sport_id}
        for i, match_id in enumerate(match_ids):
            params[f"id_{i}"] = match_id

        with self.db_manager.get_cursor() as cursor:
            cursor.execute(base_query, params)
            data = cursor.fetchall()

        return pd.DataFrame(data)

    def close(self) -> None:
        """Close database connection."""
        self.db_manager.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        self.close()
