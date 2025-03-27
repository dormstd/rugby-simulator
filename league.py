import itertools
import random
from constants import POINTS_FOR_WIN, POINTS_FOR_DRAW, POINTS_FOR_LOSS


class League:
    """Manages the league table and fixtures."""

    def __init__(self, teams):
        self.teams = teams
        self.fixtures = []  # List of tuples: (home_team, away_team)
        self.results = {}  # Stores results: {(home, away): (home_score, away_score)}
        self.table = {}  # {team_name: {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'PF': 0, 'PA': 0, 'PD': 0, 'Pts': 0}}
        self._initialize_table()
        self.generate_fixtures()

    def _initialize_table(self):
        """Sets up the initial empty league table."""
        for team in self.teams:
            self.table[team.name] = {
                "P": 0,
                "W": 0,
                "D": 0,
                "L": 0,
                "PF": 0,
                "PA": 0,
                "PD": 0,
                "Pts": 0,
            }

    def generate_fixtures(self):
        """Generates a simple round-robin fixture list (each team plays each other once)."""
        self.fixtures = list(itertools.combinations(self.teams, 2))
        random.shuffle(self.fixtures)  # Randomize match order
        # Could expand this later for home/away

    def update_table(self, home_team, away_team, home_score, away_score):
        """Updates the league table based on a match result."""
        self.results[(home_team, away_team)] = (home_score, away_score)

        # Update stats for both teams
        for team, score, opponent_score in [
            (home_team, home_score, away_score),
            (away_team, away_score, home_score),
        ]:
            stats = self.table[team.name]
            stats["P"] += 1
            stats["PF"] += score
            stats["PA"] += opponent_score
            stats["PD"] = stats["PF"] - stats["PA"]

            if score > opponent_score:
                stats["W"] += 1
                stats["Pts"] += POINTS_FOR_WIN
            elif score < opponent_score:
                stats["L"] += 1
                stats["Pts"] += POINTS_FOR_LOSS
            else:
                stats["D"] += 1
                stats["Pts"] += POINTS_FOR_DRAW
            # Add logic for bonus points here if needed later

    def get_sorted_table(self):
        """Returns the table sorted by Points (desc), then Point Difference (desc)."""
        # Convert dict to list of tuples for sorting
        table_list = [(team_name, stats) for team_name, stats in self.table.items()]
        # Sort: Primary key = Points (desc), Secondary key = Point Difference (desc)
        table_list.sort(key=lambda item: (item[1]["Pts"], item[1]["PD"]), reverse=True)
        return table_list
