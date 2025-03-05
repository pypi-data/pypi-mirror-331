# Flashscore Scraper

A Python package for scraping handball match data from Flashscore. This package provides tools to collect match IDs, detailed match information, and betting odds data.

## Features

- Match ID scraping from league results pages
- Detailed match data collection (scores, teams, dates)
- Betting odds data collection from multiple bookmakers
- Configurable league and season selection
- SQLite database storage
- Headless browser support

## Installation

```bash
pip install flashscore-scraper
```

## Quick Start

```python
from flashscore_scraper.scrapers import MatchIDScraper, MatchDataScraper, OddsDataScraper

# Initialize scrapers
match_id_scraper = MatchIDScraper()
match_data_scraper = MatchDataScraper()
odds_data_scraper = OddsDataScraper()

# Scrape match IDs
match_id_scraper.scrape()

# Scrape match details
match_data_scraper.scrape()

# Scrape odds data
odds_data_scraper.scrape()
```

## Configuration

Create a `config/flashscore_urls.yaml` file with your league configurations:

```yaml
- league: https://www.flashscore.com/handball/denmark/handboldligaen
  seasons:
    - 2024
    - 2023
    - 2022

- league: https://www.flashscore.com/handball/germany/bundesliga
  seasons:
    - 2024
    - 2023
    - 2022
```

## Database Schema

The package uses SQLite for data storage with the following tables:

- `handball_match_id`: Stores unique match identifiers
- `handball_match_data`: Stores detailed match information
- `handball_odds_data`: Stores betting odds from various bookmakers

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
