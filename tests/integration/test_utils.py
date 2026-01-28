def normalize_game(game):
    normalized = {}
    for key, value in game.items():
        if isinstance(value, str):
            normalized[key] = value.strip()
        else:
            normalized[key] = value
    return normalized


def normalize_games(games):
    return {
        date: sorted(
            (normalize_game(game) for game in day_games), key=lambda game: game["boxscore"]
        )
        for date, day_games in games.items()
    }


def normalize_rankings_entries(entries):
    """Strip non-deterministic fields before comparing ranking rows."""
    normalized = []
    for entry in entries:
        copy = {k: v for k, v in entry.items() if k != "date"}
        normalized.append(copy)
    return sorted(normalized, key=lambda row: (row.get("rank"), row.get("name")))


def normalize_rankings_complete(complete):
    return {
        week: normalize_rankings_entries(week_entries) for week, week_entries in complete.items()
    }
