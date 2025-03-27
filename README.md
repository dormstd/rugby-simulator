# Rugby Manager MVP (Pygame)

A Minimal Viable Product (MVP) for a rugby union management simulation game, built using Python and the Pygame library. This project utilizes `uv` for fast environment and dependency management.

It serves as a basic foundation demonstrating core concepts like league simulation, team/player data management, and a simple UI.

## Features

*   **Basic League Structure:** Simulates a simple round-robin league where each team plays every other team once.
*   **Generated Teams & Players:** Creates a predefined number of teams with randomly generated players at the start.
*   **Player Attributes:** Players have basic attributes (Tackling, Passing, Kicking, Speed, Strength) influencing team performance.
*   **Match Simulation:** A simple match engine calculates results based on aggregated team ratings (derived from player attributes) plus a degree of randomness. Scores include tries, conversions, and penalties.
*   **League Table:** Displays the current league standings, sorted by points and then point difference.
*   **Game Progression:** Allows the user to advance through the season one match day at a time.
*   **Team Roster Viewing:** Includes a separate screen to view the player list and attributes for *any* team in the league, with buttons to cycle through teams.
*   **Basic UI:** Simple Pygame interface with clickable buttons to navigate between the League view and the Player Roster view, and to advance the simulation.

## Screenshots

*(Add screenshots of your application here)*

*Replace this text with a screenshot of the League View:*
`[Screenshot of League View]`

*Replace this text with a screenshot of the Player List View:*
`[Screenshot of Player List View]`

## Requirements

*   Python 3.8+
*   [uv](https://github.com/astral-sh/uv) (for installation and environment management)
*   Pygame library (will be installed via `uv`)

## Installation

1.  **Install `uv`:**
    If you don't have `uv` installed, follow the official installation instructions: [https://github.com/astral-sh/uv#installation](https://github.com/astral-sh/uv#installation)

2.  **Clone the repository (or download the source code):**
    ```bash
    git clone https://github.com/dormstd/rugby-simulator.git # Or download ZIP and extract
    cd rugby-simulator
    ```

3.  **Install Dependencies using `uv`:**

    Make `uv`sync download and sync the required dependencies for the project
        ```bash
        uv sync
        ```

## How to Run

Run the project using uv:

```bash
uv run main.py
```