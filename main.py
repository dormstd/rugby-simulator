# main.py
import pygame
import sys
from constants import *  # Import all constants
from game_state import Game
from ui import draw_text, draw_league_table, draw_button, draw_fixture, draw_player_list


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rugby Manager MVP")
    clock = pygame.time.Clock()

    game = Game()
    current_view = VIEW_LEAGUE  # Start with the league view
    viewed_team_index = 0  # Index of the team being viewed in player list

    # --- UI Element Rects ---
    # League View Buttons
    next_match_button_rect = pygame.Rect(
        SCREEN_WIDTH - BUTTON_WIDTH - 20,
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    view_squad_button_rect = pygame.Rect(
        SCREEN_WIDTH - (BUTTON_WIDTH * 2) - 30,
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    # Player View Buttons
    back_button_rect = pygame.Rect(
        20,
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,  # Bottom-left
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    next_team_button_rect = pygame.Rect(  # New button
        SCREEN_WIDTH - BUTTON_WIDTH - 20,  # Bottom-right
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    prev_team_button_rect = pygame.Rect(  # New button
        SCREEN_WIDTH - (BUTTON_WIDTH * 2) - 30,  # Left of Next Team
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    running = True
    while running:
        # --- Event Handling ---
        mouse_pos = pygame.mouse.get_pos()  # Get mouse position once per frame
        clicked = False  # Flag to check if a relevant click happened

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    clicked = True  # Register the click

        # --- Handle Clicks based on Current View ---
        if clicked:
            if current_view == VIEW_LEAGUE:
                # Check clicks for League View buttons
                if (
                    next_match_button_rect.collidepoint(mouse_pos)
                    and not game.is_season_over()
                ):
                    game.play_next_match()
                elif view_squad_button_rect.collidepoint(mouse_pos):
                    # --- Initialize viewed team when switching ---
                    try:
                        # Start by viewing the player's own team
                        viewed_team_index = game.teams.index(game.player_team)
                    except (ValueError, AttributeError):
                        viewed_team_index = 0  # Default to first team if error
                    current_view = VIEW_PLAYERS  # Switch view

            elif current_view == VIEW_PLAYERS:
                # Check clicks for Player View buttons
                if back_button_rect.collidepoint(mouse_pos):
                    current_view = VIEW_LEAGUE  # Switch back
                elif next_team_button_rect.collidepoint(mouse_pos):
                    # Cycle to the next team, wrap around using modulo
                    viewed_team_index = (viewed_team_index + 1) % len(game.teams)
                elif prev_team_button_rect.collidepoint(mouse_pos):
                    # Cycle to the previous team, wrap around using modulo
                    # Add len(game.teams) before modulo to handle negative result correctly
                    viewed_team_index = (viewed_team_index - 1 + len(game.teams)) % len(
                        game.teams
                    )

        # --- Drawing ---
        screen.fill(WHITE)

        # --- Draw based on Current View ---
        if current_view == VIEW_LEAGUE:
            # Draw Title
            draw_text(
                screen,
                "Rugby Manager - League",
                (SCREEN_WIDTH // 2, 30),
                FONT_DEFAULT,
                BLACK,
                center=True,
            )
            # Draw League Table
            draw_league_table(screen, game.league, (50, 80))
            # Draw Next Fixture / Last Result
            fixture_y_pos = SCREEN_HEIGHT - 100
            next_fixture = game.get_next_fixture()
            current_result = None
            fixture_to_display = None
            if game.last_match_result and game.current_fixture_index > 0:
                fixture_to_display = game.league.fixtures[
                    game.current_fixture_index - 1
                ]
                current_result = game.last_match_result
            elif next_fixture:
                fixture_to_display = next_fixture
            if fixture_to_display:
                draw_fixture(
                    screen, fixture_to_display, current_result, (50, fixture_y_pos)
                )
            # Draw League View Buttons
            if not game.is_season_over():
                draw_button(screen, next_match_button_rect, "Next Match")
            else:
                draw_text(
                    screen,
                    "Season Over!",
                    next_match_button_rect.center,
                    FONT_DEFAULT,
                    RED,
                    center=True,
                )
            draw_button(screen, view_squad_button_rect, "View Squad")

        elif current_view == VIEW_PLAYERS:
            # --- Get the team to display based on the index ---
            team_to_display = None
            if 0 <= viewed_team_index < len(game.teams):
                team_to_display = game.teams[viewed_team_index]

            # Draw Player List Screen
            # The draw_player_list function already includes the team name title
            draw_player_list(
                screen, team_to_display, (50, 20)
            )  # Pass the selected team

            # Draw Player View Buttons
            draw_button(screen, back_button_rect, "Back to League")
            # Only draw Prev/Next if there's more than one team
            if len(game.teams) > 1:
                draw_button(screen, prev_team_button_rect, "Prev Team")
                draw_button(screen, next_team_button_rect, "Next Team")

        # --- Update Display ---
        pygame.display.flip()

        # --- Frame Rate ---
        clock.tick(60)  # Limit FPS to 60

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
