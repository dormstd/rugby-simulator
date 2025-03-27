# ui.py
import pygame
from constants import *  # Import all constants


# --- CORE DRAWING FUNCTION ---
def draw_text(surface, text, pos, font=FONT_DEFAULT, color=BLACK, center=False):
    """Helper function to draw text onto a surface."""
    # Ensure font is initialized (redundant if constants.py does it, but safe)
    if not pygame.font.get_init():
        pygame.font.init()

    try:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = pos
        else:
            text_rect.topleft = pos
        surface.blit(text_surface, text_rect)
        return text_rect  # Return rect for potential interaction
    except Exception as e:
        print(f"Error rendering text '{text}': {e}")
        # Draw an error message on screen maybe?
        error_font = pygame.font.Font(None, FONT_TINY_SIZE)
        error_surf = error_font.render(f"ERR: {e}", True, RED)
        error_rect = error_surf.get_rect(topleft=pos)
        surface.blit(error_surf, error_rect)
        return error_rect


# --- UI ELEMENT DRAWING FUNCTIONS ---


def draw_league_table(surface, league, start_pos):
    """Draws the league table."""
    x, y = start_pos
    col_widths = [150, 30, 30, 30, 30, 40, 40, 40, 40]  # Adjust as needed
    headers = ["Team", "P", "W", "D", "L", "PF", "PA", "PD", "Pts"]
    line_height = FONT_SMALL_SIZE + 5

    # Draw headers
    current_x = x
    for i, header in enumerate(headers):
        draw_text(surface, header, (current_x, y), FONT_SMALL, BLUE)
        current_x += col_widths[i]
    y += line_height  # Spacing

    # Draw table rows
    try:
        sorted_table = league.get_sorted_table()
        for team_name, stats in sorted_table:
            row_data = [
                team_name,
                str(stats["P"]),
                str(stats["W"]),
                str(stats["D"]),
                str(stats["L"]),
                str(stats["PF"]),
                str(stats["PA"]),
                str(stats["PD"]),
                str(stats["Pts"]),
            ]
            current_x = x
            for i, data in enumerate(row_data):
                # Highlight player team (optional)
                player_team_obj = getattr(league, "player_team", None)  # Safer check
                color = (
                    RED
                    if player_team_obj and team_name == player_team_obj.name
                    else BLACK
                )
                # Check if team object exists before accessing player_controlled
                # color = RED if any(t.name == team_name and getattr(t, 'player_controlled', False) for t in league.teams) else BLACK

                draw_text(surface, data, (current_x, y), FONT_SMALL, color)
                current_x += col_widths[i]
            y += line_height  # Spacing
    except Exception as e:
        print(f"Error drawing league table row: {e}")
        draw_text(surface, f"Error: {e}", (x, y), FONT_SMALL, RED)
        y += line_height


def draw_button(
    surface, rect, text, button_color=GRAY, text_color=BLACK, font=FONT_DEFAULT
):
    """Draws a simple rectangle button."""
    pygame.draw.rect(surface, button_color, rect, border_radius=5)
    draw_text(surface, text, rect.center, font, text_color, center=True)


def draw_fixture(surface, fixture, result, pos):
    """Draws the next fixture and its result (if available)."""
    if not fixture:
        return  # Skip if no fixture provided
    home_team, away_team = fixture
    home_name = getattr(home_team, "name", "Unknown")  # Safer access
    away_name = getattr(away_team, "name", "Unknown")

    if result:
        home_score, away_score = result
        text = f"Result: {home_name} {home_score} - {away_score} {away_name}"
    else:
        text = f"Next Match: {home_name} vs {away_name}"
    draw_text(surface, text, pos, FONT_DEFAULT, BLUE)


def draw_player_list(surface, team, start_pos):
    """Draws the list of players and their attributes for a team."""
    if not team:
        draw_text(surface, "No team selected.", start_pos, FONT_DEFAULT, RED)
        return

    x, y = start_pos
    # Define column headers and widths (adjust these for layout)
    headers = ["Name", "Pos", "Tck", "Pas", "Kck", "Spd", "Str", "Skill"]
    col_widths = [180, 60, 40, 40, 40, 40, 40, 45]  # Adjusted widths
    line_height = FONT_SMALL_SIZE + 4

    # Draw Title
    team_name = getattr(team, "name", "Unknown Team")
    draw_text(
        surface,
        f"{team_name} Squad",
        (SCREEN_WIDTH // 2, y),
        FONT_DEFAULT,
        BLUE,
        center=True,
    )
    y += FONT_DEFAULT_SIZE + 15

    # Draw Headers
    current_x = x
    for i, header in enumerate(headers):
        draw_text(surface, header, (current_x, y), FONT_SMALL, DARK_GRAY)
        current_x += col_widths[i]
    y += line_height
    # Draw separator line using the calculated end position
    separator_end_x = x + sum(col_widths) - 5  # Adjust end position slightly
    pygame.draw.line(
        surface,
        DARK_GRAY,
        (x, y - (line_height / 2)),
        (separator_end_x, y - (line_height / 2)),
        1,
    )

    # Draw Player Rows
    if not team.players:
        draw_text(surface, "No players found.", (x, y), FONT_SMALL, RED)
        return

    # Sort players maybe? Optional. By position?
    # sorted_players = sorted(team.players, key=lambda p: p.position) # Example sort
    sorted_players = team.players  # Keep original order for now

    for player in sorted_players:
        # Use getattr for safety in case attributes are missing somehow
        player_data = [
            getattr(player, "name", "N/A"),
            getattr(player, "position", "N/A"),
            str(getattr(player, "tackling", "?")),
            str(getattr(player, "passing", "?")),
            str(getattr(player, "kicking", "?")),
            str(getattr(player, "speed", "?")),
            str(getattr(player, "strength", "?")),
            str(getattr(player, "skill", "?")),  # Display the calculated overall skill
        ]

        current_x = x
        for i, data in enumerate(player_data):
            # Shorten long names if needed
            display_data = data
            # Estimate text width (very rough) based on font size
            estimated_char_width = FONT_SMALL_SIZE * 0.6
            if i == 0 and len(data) * estimated_char_width > col_widths[i] - 10:
                max_chars = int((col_widths[i] - 15) / estimated_char_width)
                display_data = data[: max(1, max_chars)] + "..."  # Truncate safely

            draw_text(
                surface, display_data, (current_x + 2, y), FONT_SMALL, BLACK
            )  # Add small padding
            current_x += col_widths[i]
        y += line_height

        # Stop drawing if we go off screen (simple pagination placeholder)
        if y > SCREEN_HEIGHT - BUTTON_HEIGHT - 30:  # Adjusted limit
            draw_text(surface, "...", (x, y), FONT_SMALL, BLACK)
            break
