# match_view.py
import pygame
import random
import time
import math  # For distance calculations
from constants import *
from team import Team
from player import Player  # Import Player for type hinting and attribute access
from match_engine import calculate_team_ratings
from ui import draw_text, draw_button


class PlayerState:
    """Holds positional and state data for a player within the match view."""

    def __init__(self, player_obj: Player, team_obj: Team, x: float, y: float):
        self.player = player_obj
        self.team = team_obj
        self.x = x
        self.y = y
        self.target_x = x  # Where the player intends to move
        self.target_y = y
        # Add more state if needed (e.g., fatigued, injured)

    def get_speed(self):
        """Calculate player's speed for this step."""
        # Could add fatigue later
        base = PLAYER_DEFAULT_SPEED
        variation = (
            (self.player.speed - 50) / 50.0
        ) * PLAYER_SPEED_VARIATION  # Scale based on speed attribute
        return max(0.5, base + variation)  # Ensure minimum speed

    def move_towards_target(self):
        """Move the player a step towards their target coordinates."""
        speed = self.get_speed()
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.hypot(dx, dy)

        if distance < speed:
            self.x = self.target_x
            self.y = self.target_y
        elif distance > 0:
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed

        # Clamp position to pitch bounds (loosely, allow slightly outside)
        self.x = max(PITCH_RECT.left - 20, min(self.x, PITCH_RECT.right + 20))
        self.y = max(PITCH_RECT.top - 20, min(self.y, PITCH_RECT.bottom + 20))


class MatchView:
    """Manages and displays the graphical match simulation with player movement."""

    def __init__(self, screen, home_team: Team, away_team: Team, finish_callback):
        self.screen = screen
        self.home_team = home_team
        self.away_team = away_team
        self.finish_callback = finish_callback

        self.font = FONT_DEFAULT
        self.font_small = FONT_SMALL

        # --- Simulation State ---
        self.home_score = 0
        self.away_score = 0
        self.match_time = 0
        self.last_step_time = 0
        self.is_finished = False
        self.paused = False
        self.status_message = ""  # To display Try!, Turnover!, etc.
        self.message_timer = 0  # How long to display the message

        # Player positional data
        self.home_players: list[PlayerState] = []
        self.away_players: list[PlayerState] = []
        self._initialize_player_states()

        # Ball state
        self.ball_x = PITCH_RECT.centerx
        self.ball_y = PITCH_RECT.centery
        self.ball_carrier: PlayerState | None = None
        self.possession_team: Team | None = None  # Track team, not just player

        # Ratings (could recalculate if subs happen)
        self.home_ratings = calculate_team_ratings(self.home_team)
        self.away_ratings = calculate_team_ratings(self.away_team)

        # Initial kickoff/possession
        self._kickoff()

        # UI
        self.skip_button_rect = pygame.Rect(
            SCREEN_WIDTH - BUTTON_WIDTH - 20, 10, BUTTON_WIDTH, BUTTON_HEIGHT
        )

        print(f"Starting Dynamic Match: {self.home_team.name} vs {self.away_team.name}")

    def _initialize_player_states(self):
        """Set up initial player positions in a rough formation."""
        self.home_players = []
        self.away_players = []

        # Simple formation: 8 forwards, 7 backs
        # Y positions relative to pitch center/lines
        home_def_y = PITCH_RECT.centery - PITCH_RECT.height * 0.15
        home_att_y = PITCH_RECT.centery - PITCH_RECT.height * 0.35
        away_def_y = PITCH_RECT.centery + PITCH_RECT.height * 0.15
        away_att_y = PITCH_RECT.centery + PITCH_RECT.height * 0.35

        # Forwards X positions (tighter)
        fwd_x_spacing = PITCH_RECT.width / 9
        fwd_xs = [PITCH_RECT.left + fwd_x_spacing * (i + 1) for i in range(8)]

        # Backs X positions (wider)
        back_x_spacing = PITCH_RECT.width / 8
        back_xs = [
            PITCH_RECT.left + back_x_spacing * (i + 0.5) for i in range(7)
        ]  # Offset for centering

        # Create PlayerState objects - HOME
        for i, p in enumerate(self.home_team.players):
            if i < 8:  # Forwards
                x = fwd_xs[i]
                y = home_def_y + random.uniform(-15, 15)
            else:  # Backs
                x = back_xs[i - 8]
                y = home_att_y + random.uniform(-15, 15)
            self.home_players.append(PlayerState(p, self.home_team, x, y))

        # Create PlayerState objects - AWAY
        for i, p in enumerate(self.away_team.players):
            if i < 8:  # Forwards
                x = fwd_xs[i]
                y = away_def_y + random.uniform(-15, 15)
            else:  # Backs
                x = back_xs[i - 8]
                y = away_att_y + random.uniform(-15, 15)
            self.away_players.append(PlayerState(p, self.away_team, x, y))

    def _kickoff(self):
        """Set initial possession and ball position for kickoff."""
        self.ball_x = PITCH_RECT.centerx
        self.ball_y = PITCH_RECT.centery
        self.possession_team = random.choice([self.home_team, self.away_team])
        # Find a player near center to receive (simplified)
        receiving_team_players = (
            self.home_players
            if self.possession_team == self.home_team
            else self.away_players
        )
        receiver = min(
            receiving_team_players,
            key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y),
        )
        self.ball_carrier = receiver
        self.set_status(f"Kick off! {self.possession_team.name} possession.", 2000)

    def set_status(self, message, duration_ms=1500):
        """Display a status message for a duration."""
        self.status_message = message
        self.message_timer = pygame.time.get_ticks() + duration_ms

    def handle_input(self, event):
        """Handles user input specific to the match view."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.skip_button_rect.collidepoint(event.pos):
                print("Skipping match...")
                self._skip_to_end()  # Use the instant simulation for skip

    def update(self):
        """Updates the simulation state step-by-step."""
        if self.is_finished or self.paused:
            return

        current_time_ms = pygame.time.get_ticks()

        # Update message display timer
        if self.message_timer != 0 and current_time_ms > self.message_timer:
            self.status_message = ""
            self.message_timer = 0

        # Process simulation step
        if current_time_ms - self.last_step_time >= SIMULATION_SPEED_MS:
            self.last_step_time = current_time_ms

            if self.match_time < MATCH_DURATION_STEPS:
                self._simulate_step()
                self.match_time += 1
            else:
                # Match finished
                self.is_finished = True
                final_msg = f"Full Time! {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
                print(final_msg)
                self.set_status(final_msg, 5000)  # Show final score longer
                # Use a slight delay before calling back to show final score msg
                pygame.time.set_timer(pygame.USEREVENT + 1, 3000, loops=1)

    def handle_end_match_event(self):
        """Called by timer event after match end."""
        if not self.is_finished:
            return  # Should not happen but safe check
        self.finish_callback(self.home_score, self.away_score)

    def draw(self):
        """Draws the match simulation screen."""
        self.screen.fill(WHITE)

        # Draw Pitch
        pygame.draw.rect(self.screen, GREEN, PITCH_RECT)
        pygame.draw.rect(self.screen, DARK_GREEN, PITCH_RECT, 3)
        home_try_line_y = PITCH_RECT.top + 20
        away_try_line_y = PITCH_RECT.bottom - 20
        halfway_line_y = PITCH_RECT.centery
        pygame.draw.line(
            self.screen,
            WHITE,
            (PITCH_RECT.left, home_try_line_y),
            (PITCH_RECT.right, home_try_line_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            WHITE,
            (PITCH_RECT.left, away_try_line_y),
            (PITCH_RECT.right, away_try_line_y),
            2,
        )
        pygame.draw.line(
            self.screen,
            WHITE,
            (PITCH_RECT.left, halfway_line_y),
            (PITCH_RECT.right, halfway_line_y),
            2,
        )
        # Add 22m lines (optional)
        pygame.draw.line(
            self.screen,
            WHITE,
            (PITCH_RECT.left, PITCH_RECT.top + PITCH_RECT.height * 0.25),
            (PITCH_RECT.right, PITCH_RECT.top + PITCH_RECT.height * 0.25),
            1,
        )
        pygame.draw.line(
            self.screen,
            WHITE,
            (PITCH_RECT.left, PITCH_RECT.bottom - PITCH_RECT.height * 0.25),
            (PITCH_RECT.right, PITCH_RECT.bottom - PITCH_RECT.height * 0.25),
            1,
        )

        # Draw Players
        home_color = RED
        away_color = BLUE
        for p_state in self.home_players:
            color = home_color
            outline = BLACK if p_state == self.ball_carrier else None
            pygame.draw.circle(
                self.screen, color, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS
            )
            if outline:
                pygame.draw.circle(
                    self.screen,
                    outline,
                    (int(p_state.x), int(p_state.y)),
                    PLAYER_RADIUS,
                    2,
                )  # Highlight carrier

        for p_state in self.away_players:
            color = away_color
            outline = BLACK if p_state == self.ball_carrier else None
            pygame.draw.circle(
                self.screen, color, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS
            )
            if outline:
                pygame.draw.circle(
                    self.screen,
                    outline,
                    (int(p_state.x), int(p_state.y)),
                    PLAYER_RADIUS,
                    2,
                )

        # Draw Ball (only if not carried, or draw slightly offset?)
        # Let's just draw it at carrier's position for simplicity
        if self.ball_carrier:
            self.ball_x, self.ball_y = (
                self.ball_carrier.x,
                self.ball_carrier.y + PLAYER_RADIUS,
            )  # Slight offset
        pygame.draw.circle(
            self.screen, YELLOW, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS
        )
        pygame.draw.circle(
            self.screen, BLACK, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS, 1
        )

        # Draw Scoreboard, Time, Possession
        score_text = f"{self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
        time_text = f"Minute: {self.match_time}'"
        possession_name = self.possession_team.name if self.possession_team else "None"
        poss_color = BLACK
        if self.possession_team == self.home_team:
            poss_color = RED
        elif self.possession_team == self.away_team:
            poss_color = BLUE
        possession_text = f"Possession: {possession_name}"

        draw_text(
            self.screen,
            score_text,
            (SCREEN_WIDTH // 2, 30),
            self.font,
            BLACK,
            center=True,
        )
        draw_text(
            self.screen,
            time_text,
            (PITCH_RECT.left, PITCH_RECT.top - 30),
            self.font_small,
            BLACK,
        )
        draw_text(
            self.screen,
            possession_text,
            (PITCH_RECT.left, PITCH_RECT.bottom + 10),
            self.font_small,
            poss_color,
        )

        # Draw Status Message
        if self.status_message:
            draw_text(
                self.screen,
                self.status_message,
                (SCREEN_WIDTH // 2, PITCH_RECT.centery),
                self.font,
                BLACK,
                center=True,
            )
            # Add background?
            # msg_surf = self.font.render(self.status_message, True, BLACK)
            # msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, PITCH_RECT.centery))
            # pygame.draw.rect(self.screen, GRAY, msg_rect.inflate(10, 5))
            # self.screen.blit(msg_surf, msg_rect)

        # Draw Skip Button
        draw_button(
            self.screen,
            self.skip_button_rect,
            "Skip Match",
            GRAY,
            BLACK,
            self.font_small,
        )

    def _simulate_step(self):
        """Simulate one dynamic step (minute) of the match."""

        if not self.ball_carrier or not self.possession_team:
            # Ball is loose, find nearest player to pick it up (simplification)
            all_players = self.home_players + self.away_players
            nearest_player = min(
                all_players,
                key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y),
            )
            self.ball_carrier = nearest_player
            self.possession_team = nearest_player.team
            self.set_status(f"{self.possession_team.name} recover the ball")
            # return # Process next step

        # --- Determine Player Targets ---
        self._update_player_targets()

        # --- Move Players ---
        for p_state in self.home_players + self.away_players:
            p_state.move_towards_target()

        # --- Ball Position Update ---
        if self.ball_carrier:
            self.ball_x = self.ball_carrier.x
            self.ball_y = self.ball_carrier.y

        # --- Check Interactions (Tackles) ---
        tackle_occurred = self._check_tackles()

        # If a tackle resulted in turnover/penalty, the state might change,
        # potentially skip rest of step? For now, continue.

        # --- Check for Random Penalties (Infringements not related to tackles) ---
        if not tackle_occurred and random.random() < BASE_PENALTY_CHANCE:
            # Award to non-possessing team? Or random? Let's give to non-possessing.
            penalty_team = (
                self.away_team
                if self.possession_team == self.home_team
                else self.home_team
            )
            self.handle_penalty(penalty_team, "General infringement")
            return  # End step after penalty resolution

        # --- Check for Scoring ---
        self._check_scoring()

    def _update_player_targets(self):
        """Set the target coordinates for each player based on game state."""
        if not self.ball_carrier or not self.possession_team:
            return  # No carrier, players hold position? Or move towards ball?

        carrier = self.ball_carrier
        attacking_players = (
            self.home_players
            if self.possession_team == self.home_team
            else self.away_players
        )
        defending_players = (
            self.away_players
            if self.possession_team == self.home_team
            else self.home_players
        )

        # Target for Ball Carrier: Move towards opponent try line
        target_y_direction = -1 if self.possession_team == self.home_team else 1
        carrier_target_y = (
            carrier.y + target_y_direction * PITCH_RECT.height
        )  # Aim way past line
        # Add slight random horizontal drift to avoid straight lines
        carrier_target_x = carrier.x + random.uniform(
            -PITCH_RECT.width * 0.1, PITCH_RECT.width * 0.1
        )
        carrier.target_x = carrier_target_x
        carrier.target_y = carrier_target_y

        # Target for Support Players
        # Find players near carrier, move towards carrier but maintain some distance
        support_candidates = sorted(
            attacking_players,
            key=lambda p: math.hypot(p.x - carrier.x, p.y - carrier.y),
        )
        num_support = 3  # How many players actively support
        for i, p_state in enumerate(support_candidates):
            if p_state == carrier:
                continue
            if i < num_support + 1:  # +1 because carrier is in list
                # Aim for a position slightly behind/beside the carrier
                offset_x = (p_state.x - carrier.x) * 0.5 + random.uniform(
                    -SUPPORT_DISTANCE * 0.5, SUPPORT_DISTANCE * 0.5
                )
                offset_y = (
                    p_state.y - carrier.y
                ) * 0.5 - target_y_direction * SUPPORT_DISTANCE * 0.7  # Slightly behind
                dist = math.hypot(offset_x, offset_y)
                target_dist = SUPPORT_DISTANCE

                if dist > 0:
                    # Scale offset to be closer to SUPPORT_DISTANCE
                    final_offset_x = (offset_x / dist) * target_dist
                    final_offset_y = (offset_y / dist) * target_dist
                    p_state.target_x = carrier.x + final_offset_x
                    p_state.target_y = carrier.y + final_offset_y
                else:  # If player is right on top, move them slightly
                    p_state.target_x = carrier.x + random.uniform(-20, 20)
                    p_state.target_y = carrier.y + random.uniform(-20, 20)

            else:
                # Other attackers drift towards general play or hold formation?
                # Simple: move slowly towards center line vertically, hold horizontal
                p_state.target_y += (PITCH_RECT.centery - p_state.y) * 0.05
                # p_state.target_x = p_state.x # Hold horizontal

        # Target for Defending Players
        # Find defenders near carrier and move towards them
        defense_candidates = sorted(
            defending_players,
            key=lambda p: math.hypot(p.x - carrier.x, p.y - carrier.y),
        )
        num_defend = 4  # How many actively defend
        for i, p_state in enumerate(defense_candidates):
            dist_to_carrier = math.hypot(p_state.x - carrier.x, p_state.y - carrier.y)
            if dist_to_carrier < DEFENSE_AGGRESSION_RADIUS or i < num_defend:
                # Target the ball carrier directly
                p_state.target_x = carrier.x
                p_state.target_y = carrier.y
            else:
                # Other defenders hold position or fall back?
                # Simple: move slowly towards own try line
                def_target_y_dir = 1 if p_state.team == self.home_team else -1
                p_state.target_y += def_target_y_dir * 5  # Fall back slowly
                # p_state.target_x = p_state.x # Hold horizontal

    def _check_tackles(self) -> bool:
        """Check for defenders near the carrier and attempt tackles."""
        if not self.ball_carrier:
            return False

        carrier = self.ball_carrier
        defending_players = (
            self.away_players
            if self.possession_team == self.home_team
            else self.home_players
        )
        tackle_attempted = False

        for defender in defending_players:
            distance = math.hypot(defender.x - carrier.x, defender.y - carrier.y)

            if distance < TACKLE_RADIUS:
                tackle_attempted = True
                # Calculate tackle success chance
                str_diff = carrier.player.strength - defender.player.strength
                tck_diff = defender.player.tackling - 50  # Defender tackling ability
                spd_diff = (
                    defender.player.speed - carrier.player.speed
                )  # Defender speed helps

                success_chance = TACKLE_SUCCESS_BASE
                success_chance -= (
                    str_diff * TACKLE_STRENGTH_INFLUENCE
                )  # Higher carrier str reduces chance
                success_chance += (
                    tck_diff * TACKLE_STRENGTH_INFLUENCE
                )  # Higher defender tck increases chance
                success_chance += (
                    spd_diff * TACKLE_SPEED_INFLUENCE
                )  # Higher defender spd increases chance
                success_chance = max(0.05, min(0.95, success_chance))  # Clamp

                if random.random() < success_chance:
                    # --- Successful Tackle ---
                    self.set_status(
                        f"Tackle! {defender.player.name} stops {carrier.player.name}!"
                    )
                    # Turnover
                    self.possession_team = defender.team
                    self.ball_carrier = None  # Ball is loose briefly
                    self.ball_x = carrier.x  # Drop ball at tackle spot
                    self.ball_y = carrier.y
                    # In next step, nearest player from new possession_team will likely pick up

                    # Chance of penalty during tackle
                    if (
                        random.random() < BASE_PENALTY_CHANCE * 2
                    ):  # Higher chance on tackle
                        penalty_offender = carrier.team
                        penalty_winner = defender.team
                        self.handle_penalty(
                            penalty_winner,
                            f"Infringement by {penalty_offender.name} at tackle",
                        )

                    return True  # Stop checking other defenders for this step

                else:
                    # --- Broken Tackle ---
                    self.set_status(f"{carrier.player.name} breaks the tackle!")
                    # Carrier might be slowed briefly? (Add later if needed)
                    # Defender might be knocked back?
                    defender.x += (defender.x - carrier.x) * 0.2  # Simple knockback
                    defender.y += (defender.y - carrier.y) * 0.2

                    # Don't return true, another defender might try

        return tackle_attempted  # Return if any tackle was attempted

    def handle_penalty(self, winning_team: Team, reason: str):
        """Process a penalty decision."""
        self.set_status(f"Penalty! {winning_team.name}. ({reason})")
        self.possession_team = winning_team
        self.ball_carrier = None  # Stop current play

        # Find kicker (player with best kicking?)
        kicker = max(
            self.home_players if winning_team == self.home_team else self.away_players,
            key=lambda p: p.player.kicking,
        )
        self.ball_x = kicker.x  # Move ball to kicker approx loc
        self.ball_y = kicker.y

        # Decision: Kick for goal or touch?
        is_home_kicking = winning_team == self.home_team
        opponent_try_line = PITCH_RECT.bottom if is_home_kicking else PITCH_RECT.top
        dist_to_posts = abs(self.ball_y - opponent_try_line)
        kick_range = PITCH_RECT.height * 0.40  # 40% range

        time.sleep(0.5)  # Pause briefly for penalty message

        if dist_to_posts < kick_range:
            # Attempt penalty goal
            kick_success_chance = (
                PENALTY_SUCCESS_RATE + (kicker.player.kicking - 60) / 150
            )  # Kicking skill influence
            if random.random() < kick_success_chance:
                self.set_status("Penalty goal successful!")
                if is_home_kicking:
                    self.home_score += PENALTY_POINTS
                else:
                    self.away_score += PENALTY_POINTS
                    # Reset for restart
                self._reset_to_midfield(
                    self.home_team if not is_home_kicking else self.away_team
                )  # Other team restarts
            else:
                self.set_status("Penalty kick missed.")
                # Reset for 22 dropout (simplified: restart from defending 22)
                restart_team = self.home_team if not is_home_kicking else self.away_team
                self.ball_y = (
                    PITCH_RECT.top + PITCH_RECT.height * 0.25
                    if restart_team == self.home_team
                    else PITCH_RECT.bottom - PITCH_RECT.height * 0.25
                )
                self._reset_player_possession(restart_team)

        else:
            # Kick for touch (gain territory)
            self.set_status("Penalty kicked for touch.")
            move_direction = -1 if is_home_kicking else 1
            self.ball_y += move_direction * PITCH_RECT.height * 0.3  # Significant gain
            self.ball_y = max(
                PITCH_RECT.top + 10, min(self.ball_y, PITCH_RECT.bottom - 10)
            )
            # Keep possession (lineout simulation would be next, simplified: just restart play)
            self._reset_player_possession(
                winning_team
            )  # Restart play near touchline? Just restart possession.

    def _check_scoring(self):
        """Check if the ball carrier has crossed the try line."""
        if not self.ball_carrier:
            return

        carrier = self.ball_carrier
        home_try_line_y = PITCH_RECT.top + 5
        away_try_line_y = PITCH_RECT.bottom - 5

        scored = False
        if self.possession_team == self.home_team and carrier.y <= home_try_line_y:
            self.set_status(f"TRY! {self.home_team.name}!")
            self.home_score += TRY_POINTS
            scored = True
        elif self.possession_team == self.away_team and carrier.y >= away_try_line_y:
            self.set_status(f"TRY! {self.away_team.name}!")
            self.away_score += TRY_POINTS
            scored = True

        if scored:
            # Attempt conversion
            kicker = max(
                self.home_players
                if self.possession_team == self.home_team
                else self.away_players,
                key=lambda p: p.player.kicking,
            )
            conversion_chance = (
                CONVERSION_SUCCESS_RATE + (kicker.player.kicking - 60) / 150
            )
            time.sleep(0.5)  # Pause for try message
            if random.random() < conversion_chance:
                self.set_status("Conversion successful!")
                if self.possession_team == self.home_team:
                    self.home_score += CONVERSION_POINTS
                else:
                    self.away_score += CONVERSION_POINTS
            else:
                self.set_status("Conversion missed.")

            # Reset for restart kick by non-scoring team
            time.sleep(0.5)  # Pause for conversion message
            restart_team = (
                self.away_team
                if self.possession_team == self.home_team
                else self.home_team
            )
            self._reset_to_midfield(restart_team)

    def _reset_to_midfield(self, possession_team: Team):
        """Reset ball and players for a midfield restart."""
        print(f"Resetting to midfield, possession: {possession_team.name}")
        self.ball_x = PITCH_RECT.centerx
        self.ball_y = PITCH_RECT.centery
        # Reposition players roughly? Or let them converge? Let them converge for now.
        self._reset_player_possession(possession_team)

    def _reset_player_possession(self, possession_team: Team):
        """Assign ball carrier after a reset, based on new possession team."""
        self.possession_team = possession_team
        self.ball_carrier = None  # Ensure ball is loose first
        # Find a player near the ball to receive
        receiving_team_players = (
            self.home_players
            if possession_team == self.home_team
            else self.away_players
        )
        if not receiving_team_players:
            return  # Should not happen
        # Find player closest to current ball position
        receiver = min(
            receiving_team_players,
            key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y),
        )
        self.ball_carrier = receiver
        self.set_status(f"{possession_team.name} possession.")

    def _skip_to_end(self):
        """Instantly simulates the rest of the match using simplified engine (placeholder)."""
        # For a true skip, we'd ideally run the original non-graphical match_engine
        # But for now, just fast-forward the graphical one crudely
        # OR: just calculate result instantly (better)
        print("Calculating skip result...")
        temp_home_score, temp_away_score = simulate_match(
            self.home_team, self.away_team
        )  # Use the instant engine
        self.home_score = temp_home_score
        self.away_score = temp_away_score
        self.match_time = MATCH_DURATION_STEPS  # Set time to end

        # Trigger the end sequence immediately
        self.is_finished = True
        final_msg = f"(Skipped) Final Score: {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
        print(final_msg)
        self.set_status(final_msg, 5000)
        pygame.time.set_timer(
            pygame.USEREVENT + 1, 100, loops=1
        )  # Call callback almost immediately
