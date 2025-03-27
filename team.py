from player import generate_player
import random


class Team:
    """Represents a rugby team."""

    def __init__(self, name, player_controlled=False):
        self.name = name
        self.players = []
        self.player_controlled = player_controlled
        self._generate_initial_squad()  # Populate with players

    def _generate_initial_squad(self):
        """Generates a basic squad of 15 players for MVP."""
        # Simplified positions for MVP
        positions = (
            ["Prop"] * 2
            + ["Hooker"]
            + ["Lock"] * 2
            + ["Flanker"] * 2
            + ["Number 8"]
            + ["Scrum-half"]
            + ["Fly-half"]
            + ["Centre"] * 2
            + ["Wing"] * 2
            + ["Fullback"]
        )

        self.players = [generate_player(pos) for pos in positions]

    def get_average_skill(self):
        """Calculates the average overall skill level of the team (derived from attributes)."""
        if not self.players:
            return 0
        # Use the derived 'skill' attribute from Player class
        total_skill = sum(player.skill for player in self.players)
        return total_skill / len(self.players)

    def get_average_attribute(self, attribute_name):
        """Calculates the average of a specific attribute for the team."""
        if not self.players:
            return 0
        try:
            total_attribute = sum(
                getattr(player, attribute_name) for player in self.players
            )
            return total_attribute / len(self.players)
        except AttributeError:
            print(f"Warning: Attribute '{attribute_name}' not found on Player.")
            return 0

    def __str__(self):
        return self.name


# --- Helper function to create placeholder teams ---
def create_initial_teams(num_teams=4):
    """Creates a list of initial teams for the league."""
    team_names = [
        "Harlequins",
        "Saracens",
        "Leicester Tigers",
        "Exeter Chiefs",
        "Northampton Saints",
        "Sale Sharks",
        "Bath Rugby",
        "Bristol Bears",
    ]
    random.shuffle(team_names)  # Use different teams each time

    if num_teams > len(team_names):
        num_teams = len(team_names)

    teams = [Team(team_names[0], player_controlled=True)]  # First team is player's
    teams.extend([Team(team_names[i]) for i in range(1, num_teams)])
    return teams
