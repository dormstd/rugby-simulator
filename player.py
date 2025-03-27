import random


class Player:
    """Represents a single player with more detailed attributes."""

    def __init__(self, name, position, tackling, passing, kicking, speed, strength):
        self.name = name
        self.position = position  # e.g., "Prop", "Fly-half", "Fullback"

        # Attributes (scale 1-100, simplified)
        self.tackling = max(1, min(100, tackling))
        self.passing = max(1, min(100, passing))
        self.kicking = max(1, min(100, kicking))  # General kicking (goal, tactical)
        self.speed = max(1, min(100, speed))
        self.strength = max(1, min(100, strength))

        # Overall skill derived or separate? Let's keep it separate for now as a general indicator
        self.skill = int(
            (self.tackling + self.passing + self.kicking + self.speed + self.strength)
            / 5
        )

    def __str__(self):
        # Provide a more detailed string representation if needed, e.g., for debugging
        # return f"{self.name} ({self.position}) - T:{self.tackling} P:{self.passing} K:{self.kicking} Sp:{self.speed} St:{self.strength} (Sk:{self.skill})"
        return (
            f"{self.name} ({self.position}) - Skill: {self.skill}"  # Keep simple for UI
        )


# --- Helper function to create placeholder players ---
def generate_player(position):
    """Generates a random player for a given position with detailed attributes."""
    first_names = [
        "Jonny",
        "Richie",
        "Dan",
        "Brian",
        "Serge",
        "Martin",
        "David",
        "Siya",
        "Faf",
        "Cheslin",
    ]
    last_names = [
        "Wilkinson",
        "McCaw",
        "Carter",
        "O'Driscoll",
        "Blanco",
        "Johnson",
        "Campese",
        "Kolisi",
        "De Klerk",
        "Kolbe",
    ]
    name = f"{random.choice(first_names)} {random.choice(last_names)}"

    # Generate random attributes (adjust ranges based on position later if desired)
    tackling = random.randint(40, 85)
    passing = random.randint(30, 90)
    kicking = random.randint(20, 85)
    speed = random.randint(40, 90)
    strength = random.randint(40, 90)

    # Basic positional adjustments (Example - make props stronger/slower, backs faster/better passers)
    if position in ["Prop", "Hooker", "Lock"]:
        strength = random.randint(65, 95)
        speed = random.randint(30, 65)
        passing = random.randint(20, 50)
    elif position in ["Scrum-half", "Fly-half"]:
        passing = random.randint(65, 95)
        kicking = random.randint(60, 95)
        speed = random.randint(60, 85)
    elif position in ["Wing", "Fullback"]:
        speed = random.randint(70, 95)
        kicking = random.randint(50, 90)
    elif position in ["Centre"]:
        speed = random.randint(60, 85)
        strength = random.randint(55, 85)
        passing = random.randint(50, 80)

    # Ensure values stay within bounds after adjustments
    tackling = max(1, min(100, tackling))
    passing = max(1, min(100, passing))
    kicking = max(1, min(100, kicking))
    speed = max(1, min(100, speed))
    strength = max(1, min(100, strength))

    return Player(name, position, tackling, passing, kicking, speed, strength)
