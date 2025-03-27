from team import create_initial_teams
from league import League
from match_engine import simulate_match


class Game:
    """Holds the overall game state and logic."""

    def __init__(self):
        self.teams = create_initial_teams(num_teams=6)  # Create 6 teams
        self.player_team = next(team for team in self.teams if team.player_controlled)
        self.league = League(self.teams)
        self.current_fixture_index = 0
        self.last_match_result = None  # Store the result of the last played match

    def get_next_fixture(self):
        """Returns the next fixture tuple (home_team, away_team) or None if finished."""
        if self.current_fixture_index < len(self.league.fixtures):
            return self.league.fixtures[self.current_fixture_index]
        return None

    def play_next_match(self):
        """Simulates the next match, updates table, and advances index."""
        fixture = self.get_next_fixture()
        if fixture:
            home_team, away_team = fixture
            home_score, away_score = simulate_match(home_team, away_team)
            self.league.update_table(home_team, away_team, home_score, away_score)
            self.last_match_result = (home_score, away_score)
            self.current_fixture_index += 1
            print(
                f"Played: {home_team.name} {home_score} - {away_score} {away_team.name}"
            )  # Console output
            return True  # Match was played
        else:
            print("End of season.")
            self.last_match_result = None  # Clear last result
            return False  # No more matches

    def is_season_over(self):
        """Checks if all fixtures have been played."""
        return self.current_fixture_index >= len(self.league.fixtures)
