# main.py
import pygame
import sys
from constants import *  # Import all constants
from game_state import Game
from ui import draw_text, draw_league_table, draw_button, draw_fixture, draw_player_list
from match_view import MatchView  # Import the new dynamic match view class

# Ensure simulate_match is imported if used by skip logic or other parts
from match_engine import simulate_match


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rugby Manager MVP")
    clock = pygame.time.Clock()

    game = Game()
    current_view = VIEW_LEAGUE  # Start with the league view
    viewed_team_index = 0  # Index of the team being viewed in player list
    active_match_view = None  # Variable to hold the current MatchView instance

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
    next_team_button_rect = pygame.Rect(  # Button for player view team cycling
        SCREEN_WIDTH - BUTTON_WIDTH - 20,  # Bottom-right in player view
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    prev_team_button_rect = pygame.Rect(  # Button for player view team cycling
        SCREEN_WIDTH - (BUTTON_WIDTH * 2) - 30,  # Left of Next Team in player view
        SCREEN_HEIGHT - BUTTON_HEIGHT - 20,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    # Note: Skip button rect is managed within MatchView itself now

    # --- Callback function for when a match finishes ---
    def handle_match_finished(home_score, away_score):
        """
        This function is called by MatchView when the simulation ends.
        It updates the game state (league table, fixture index) and switches back to League View.
        """
        nonlocal current_view, active_match_view  # Allow modification of outer scope variables
        print("Match finished callback received.")
        if game.current_fixture_index < len(game.league.fixtures):
            # Get the fixture that just finished
            home_team, away_team = game.league.fixtures[game.current_fixture_index]
            # Update the league table with the result
            game.league.update_table(home_team, away_team, home_score, away_score)
            game.last_match_result = (
                home_score,
                away_score,
            )  # Store result for display
            game.current_fixture_index += 1  # Advance to the next fixture index
            print(
                f"Table updated for {home_team.name} vs {away_team.name}. Next fixture index: {game.current_fixture_index}"
            )
        else:
            # This case should ideally not happen if logic is correct
            print(
                "Error: Match finished but no more fixtures were expected based on current_fixture_index."
            )

        active_match_view = None  # Clear the finished match view instance
        current_view = VIEW_LEAGUE  # Return to league view
        print("Switched back to League View.")

    # --- Main Game Loop ---
    running = True
    while running:
        # --- Event Handling ---
        mouse_pos = pygame.mouse.get_pos()  # Get mouse position once per frame
        clicked = False  # Flag to check if a relevant click happened this frame
        events = pygame.event.get()  # Get all events for this frame

        for event in events:
            if event.type == pygame.QUIT:
                running = False  # Exit the main loop

            if (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):  # Left mouse click
                clicked = True  # Register the click for processing below

            # --- Handle custom timer event for match end callback ---
            # This event is triggered by MatchView after the simulation finishes
            # to allow the final score message to display briefly.
            if event.type == pygame.USEREVENT + 1:
                if current_view == VIEW_MATCH and active_match_view:
                    print("Received USEREVENT+1 for match end.")
                    active_match_view.handle_end_match_event()  # Trigger the callback via MatchView
                pygame.time.set_timer(
                    pygame.USEREVENT + 1, 0
                )  # Important: Disable the timer after it fires once

            # --- Pass input events to the active match view if it exists ---
            if current_view == VIEW_MATCH and active_match_view:
                # MatchView might handle specific inputs like skipping
                active_match_view.handle_input(event)

        # --- Handle Clicks & State Updates (based on view and clicks detected above) ---
        if clicked:
            # --- Clicks in League View ---
            if current_view == VIEW_LEAGUE:
                # Check "Next Match" button click
                if (
                    next_match_button_rect.collidepoint(mouse_pos)
                    and not game.is_season_over()
                ):
                    # --- Start the graphical match simulation ---
                    next_fixture_teams = game.get_next_fixture()
                    if next_fixture_teams:
                        home_team, away_team = next_fixture_teams
                        # Create a new MatchView instance for this fixture
                        # Pass the screen, teams, and the callback function
                        active_match_view = MatchView(
                            screen, home_team, away_team, handle_match_finished
                        )
                        current_view = (
                            VIEW_MATCH  # Switch the game state to the match view
                        )
                        print(
                            f"Switching to Match View: {home_team.name} vs {away_team.name}"
                        )
                    # Note: game.play_next_match() is NOT called here; simulation is handled by MatchView

                # Check "View Squad" button click
                elif view_squad_button_rect.collidepoint(mouse_pos):
                    try:  # Set the initial team to view to the player's team
                        viewed_team_index = game.teams.index(game.player_team)
                    except (
                        ValueError,
                        AttributeError,
                    ):  # Fallback if player team not found
                        viewed_team_index = 0
                    current_view = VIEW_PLAYERS  # Switch to player list view

            # --- Clicks in Player List View ---
            elif current_view == VIEW_PLAYERS:
                # Check "Back to League" button click
                if back_button_rect.collidepoint(mouse_pos):
                    current_view = VIEW_LEAGUE  # Switch back to league view
                # Check "Next Team" button click
                elif (
                    next_team_button_rect.collidepoint(mouse_pos)
                    and len(game.teams) > 1
                ):
                    # Cycle to the next team index, wrap around if necessary
                    viewed_team_index = (viewed_team_index + 1) % len(game.teams)
                # Check "Prev Team" button click
                elif (
                    prev_team_button_rect.collidepoint(mouse_pos)
                    and len(game.teams) > 1
                ):
                    # Cycle to the previous team index, wrap around if necessary
                    viewed_team_index = (viewed_team_index - 1 + len(game.teams)) % len(
                        game.teams
                    )

            # Note: Click handling specific to the Match View (like Skip)
            # is done within MatchView's handle_input method, called in the event loop above.

        # --- Game State Update ---
        # Update the active match simulation if we are in the match view
        if current_view == VIEW_MATCH and active_match_view:
            active_match_view.update()  # This runs the simulation step

        # --- Drawing ---
        screen.fill(WHITE)  # Clear the screen at the start of each frame

        # --- Draw based on the Current View ---
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
            draw_league_table(screen, game.league, (50, 80))  # Position table
            # Draw Next Fixture / Last Result section
            fixture_y_pos = SCREEN_HEIGHT - 100  # Position above buttons
            next_fixture = game.get_next_fixture()
            current_result = None
            fixture_to_display = None
            # Display result of the last completed match
            if game.last_match_result and game.current_fixture_index > 0:
                # Get the fixture corresponding to the last result
                fixture_to_display = game.league.fixtures[
                    game.current_fixture_index - 1
                ]
                current_result = game.last_match_result
            # Or display the upcoming fixture if no result to show / before first match
            elif next_fixture:
                fixture_to_display = next_fixture
            # Draw the fixture/result text if available
            if fixture_to_display:
                draw_fixture(
                    screen, fixture_to_display, current_result, (50, fixture_y_pos)
                )
            # Draw League View Buttons
            if not game.is_season_over():
                draw_button(screen, next_match_button_rect, "Next Match")
            else:  # Season finished
                draw_text(
                    screen,
                    "Season Over!",
                    next_match_button_rect.center,
                    FONT_DEFAULT,
                    RED,
                    center=True,
                )
            # Always draw the view squad button on the league screen
            draw_button(screen, view_squad_button_rect, "View Squad")

        elif current_view == VIEW_PLAYERS:
            # Draw Player List View
            team_to_display = None
            if 0 <= viewed_team_index < len(game.teams):
                team_to_display = game.teams[viewed_team_index]  # Get the selected team
            # Call the drawing function from ui.py
            draw_player_list(screen, team_to_display, (50, 20))  # Start list near top
            # Draw Player View Buttons
            draw_button(screen, back_button_rect, "Back to League")
            if len(game.teams) > 1:  # Only show cycling buttons if multiple teams
                draw_button(screen, prev_team_button_rect, "Prev Team")
                draw_button(screen, next_team_button_rect, "Next Team")

        elif current_view == VIEW_MATCH and active_match_view:
            # --- Draw the active match simulation ---
            active_match_view.draw()

        # --- Update Display ---
        pygame.display.flip()  # Show the drawn frame on the screen

        # --- Frame Rate ---
        clock.tick(60)  # Limit the game loop to 60 frames per second

    # --- Cleanup ---
    pygame.quit()  # Uninitialize Pygame modules
    sys.exit()  # Exit the Python script


# --- Entry Point ---
if __name__ == "__main__":
    main()  # Run the main function when the script is executed
