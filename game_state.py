# game_state.py
from team import create_initial_teams
from league import League

# Keep simulate_match import if you want play_next_match for other purposes later
from match_engine import simulate_match


class Game:
    """Holds the overall game state and logic."""

    def __init__(self):
        self.teams = create_initial_teams(num_teams=6)  # Create 6 teams
        self.player_team = next(
            (team for team in self.teams if team.player_controlled), None
        )  # Safer find
        if (
            not self.player_team and self.teams
        ):  # Assign first team if player_controlled fails
            self.player_team = self.teams[0]
            self.player_team.player_controlled = True

        self.league = League(self.teams)
        self.current_fixture_index = 0
        self.last_match_result = None

    def get_next_fixture(self):
        """Returns the next fixture tuple (home_team, away_team) or None if finished."""
        if self.current_fixture_index < len(self.league.fixtures):
            return self.league.fixtures[self.current_fixture_index]
        return None

    # This function is NO LONGER CALLED by the main "Next Match" button click
    # It instantly simulates a match without graphics. Keep for potential future use.
    def play_next_match_instant(self):
        """Simulates the next match instantly, updates table, and advances index."""
        fixture = self.get_next_fixture()
        if fixture:
            home_team, away_team = fixture
            home_score, away_score = simulate_match(
                home_team, away_team
            )  # Uses the original engine
            self.league.update_table(home_team, away_team, home_score, away_score)
            self.last_match_result = (home_score, away_score)
            self.current_fixture_index += 1
            print(
                f"Instant Sim: {home_team.name} {home_score} - {away_score} {away_team.name}"
            )
            return True  # Match was played
        else:
            print("End of season.")
            self.last_match_result = None
            return False  # No more matches

    def is_season_over(self):
        """Checks if all fixtures have been played."""
        return self.current_fixture_index >= len(self.league.fixtures)
