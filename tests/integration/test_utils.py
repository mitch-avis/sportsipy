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
