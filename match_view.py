# match_view.py
import pygame
import random
import time
import math
from constants import *
from team import Team
from player import Player
from match_engine import calculate_team_ratings, simulate_match
from ui import draw_text, draw_button

class PlayerState:
    """Holds positional and state data for a player within the match view."""
    def __init__(self, player_obj: Player, team_obj: Team, x: float, y: float):
        self.player = player_obj
        self.team = team_obj
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y

    def get_speed(self):
        """Calculate player's speed for this step."""
        base = PLAYER_DEFAULT_SPEED
        variation = ((self.player.speed - 50) / 50.0) * PLAYER_SPEED_VARIATION
        return max(0.5, base + variation)

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
            # Apply a small inertia/smoothing factor? (Optional)
            # factor = 0.8
            # self.x = self.x * (1-factor) + (self.x + (dx / distance) * speed) * factor
            # self.y = self.y * (1-factor) + (self.y + (dy / distance) * speed) * factor
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

        # Simulation State
        self.home_score = 0
        self.away_score = 0
        self.current_step = 0
        self.displayed_minute = 0
        self.last_step_time = 0
        self.is_finished = False
        self.paused = False
        self.status_message = ""
        self.message_timer = 0

        # Player positional data
        self.home_players: list[PlayerState] = []
        self.away_players: list[PlayerState] = []
        self._initialize_player_states()

        # Ball state
        self.ball_x = PITCH_RECT.centerx
        self.ball_y = PITCH_RECT.centery
        self.ball_carrier: PlayerState | None = None
        self.possession_team: Team | None = None

        # Ratings
        self.home_ratings = calculate_team_ratings(self.home_team)
        self.away_ratings = calculate_team_ratings(self.away_team)

        # Initial kickoff
        self._kickoff()

        # UI
        self.skip_button_rect = pygame.Rect(SCREEN_WIDTH - BUTTON_WIDTH - 20, 10, BUTTON_WIDTH, BUTTON_HEIGHT)

        print(f"Starting Dynamic Match: {self.home_team.name} vs {self.away_team.name}")
        print(f"Simulation Steps: {MATCH_DURATION_STEPS}, Game Minutes: {GAME_DURATION_MINUTES}")

    def _initialize_player_states(self):
        """Set up initial player positions in a rough formation."""
        self.home_players = []
        self.away_players = []
        home_def_y = PITCH_RECT.centery - PITCH_RECT.height * 0.15
        home_att_y = PITCH_RECT.centery - PITCH_RECT.height * 0.35
        away_def_y = PITCH_RECT.centery + PITCH_RECT.height * 0.15
        away_att_y = PITCH_RECT.centery + PITCH_RECT.height * 0.35
        fwd_x_spacing = PITCH_RECT.width / 9
        fwd_xs = [PITCH_RECT.left + fwd_x_spacing * (i + 1) for i in range(8)]
        back_x_spacing = PITCH_RECT.width / 8
        back_xs = [PITCH_RECT.left + back_x_spacing * (i + 0.5) for i in range(7)]

        for i, p in enumerate(self.home_team.players):
            if i < 8: x, y = fwd_xs[i], home_def_y + random.uniform(-15, 15)
            else: x, y = back_xs[i - 8], home_att_y + random.uniform(-15, 15)
            self.home_players.append(PlayerState(p, self.home_team, x, y))

        for i, p in enumerate(self.away_team.players):
            if i < 8: x, y = fwd_xs[i], away_def_y + random.uniform(-15, 15)
            else: x, y = back_xs[i - 8], away_att_y + random.uniform(-15, 15)
            self.away_players.append(PlayerState(p, self.away_team, x, y))

    def _kickoff(self):
        """Set initial possession and ball position for kickoff."""
        self.ball_x = PITCH_RECT.centerx; self.ball_y = PITCH_RECT.centery
        self.possession_team = random.choice([self.home_team, self.away_team])
        receiving_team_players = self.home_players if self.possession_team == self.home_team else self.away_players
        if not receiving_team_players: return
        receiver = min(receiving_team_players, key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y))
        self.ball_carrier = receiver
        self.set_status(f"Kick off! {self.possession_team.name} possession.", 2000)

    def set_status(self, message, duration_ms=1500):
        self.status_message = message
        self.message_timer = pygame.time.get_ticks() + duration_ms

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.skip_button_rect.collidepoint(event.pos):
                print("Skipping match...")
                self._skip_to_end()

    def update(self):
        if self.is_finished or self.paused: return
        current_time_ms = pygame.time.get_ticks()
        if self.message_timer != 0 and current_time_ms > self.message_timer:
             self.status_message = ""; self.message_timer = 0

        if current_time_ms - self.last_step_time >= SIMULATION_SPEED_MS:
            self.last_step_time = current_time_ms
            if self.current_step < MATCH_DURATION_STEPS:
                self.displayed_minute = int((self.current_step / MATCH_DURATION_STEPS) * GAME_DURATION_MINUTES)
                self._simulate_step()
                self.current_step += 1
            else:
                if not self.is_finished:
                    self.is_finished = True; self.displayed_minute = GAME_DURATION_MINUTES
                    final_msg = f"Full Time! {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
                    print(final_msg); self.set_status(final_msg, 5000)
                    pygame.time.set_timer(pygame.USEREVENT + 1, 3000, loops=1)

    def handle_end_match_event(self):
         if not self.is_finished: return
         if hasattr(self, '_callback_called') and self._callback_called: return
         self._callback_called = True
         self.finish_callback(self.home_score, self.away_score)

    def draw(self):
        # (Draw function remains unchanged - only difference was time display which was already fixed)
        self.screen.fill(WHITE)
        pygame.draw.rect(self.screen, GREEN, PITCH_RECT)
        pygame.draw.rect(self.screen, DARK_GREEN, PITCH_RECT, 3)
        home_try_line_y = PITCH_RECT.top + 20
        away_try_line_y = PITCH_RECT.bottom - 20
        halfway_line_y = PITCH_RECT.centery
        pygame.draw.line(self.screen, WHITE, (PITCH_RECT.left, home_try_line_y), (PITCH_RECT.right, home_try_line_y), 2)
        pygame.draw.line(self.screen, WHITE, (PITCH_RECT.left, away_try_line_y), (PITCH_RECT.right, away_try_line_y), 2)
        pygame.draw.line(self.screen, WHITE, (PITCH_RECT.left, halfway_line_y), (PITCH_RECT.right, halfway_line_y), 2)
        twenty_two_top_y = PITCH_RECT.top + PITCH_RECT.height * 0.25
        twenty_two_bottom_y = PITCH_RECT.bottom - PITCH_RECT.height * 0.25
        pygame.draw.line(self.screen, WHITE, (PITCH_RECT.left, twenty_two_top_y), (PITCH_RECT.right, twenty_two_top_y), 1, )
        pygame.draw.line(self.screen, WHITE, (PITCH_RECT.left, twenty_two_bottom_y), (PITCH_RECT.right, twenty_two_bottom_y), 1, )

        home_color, away_color = RED, BLUE
        for p_state in self.home_players:
            outline = BLACK if p_state == self.ball_carrier else None
            pygame.draw.circle(self.screen, home_color, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS)
            if outline: pygame.draw.circle(self.screen, outline, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS, 2)
        for p_state in self.away_players:
            outline = BLACK if p_state == self.ball_carrier else None
            pygame.draw.circle(self.screen, away_color, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS)
            if outline: pygame.draw.circle(self.screen, outline, (int(p_state.x), int(p_state.y)), PLAYER_RADIUS, 2)

        if self.ball_carrier:
             self.ball_x, self.ball_y = self.ball_carrier.x + PLAYER_RADIUS * 0.5, self.ball_carrier.y + PLAYER_RADIUS * 0.5
        if self.ball_x is not None and self.ball_y is not None:
            pygame.draw.circle(self.screen, YELLOW, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS)
            pygame.draw.circle(self.screen, BLACK, (int(self.ball_x), int(self.ball_y)), BALL_RADIUS, 1)

        score_text = f"{self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
        time_text = f"Minute: {self.displayed_minute}'" # Uses displayed_minute
        possession_name = self.possession_team.name if self.possession_team else "None"
        poss_color = BLACK
        if self.possession_team == self.home_team: poss_color = RED
        elif self.possession_team == self.away_team: poss_color = BLUE
        possession_text = f"Possession: {possession_name}"
        draw_text(self.screen, score_text, (SCREEN_WIDTH // 2, 30), self.font, BLACK, center=True)
        draw_text(self.screen, time_text, (PITCH_RECT.left, PITCH_RECT.top - 30), self.font_small, BLACK)
        draw_text(self.screen, possession_text, (PITCH_RECT.left, PITCH_RECT.bottom + 10), self.font_small, poss_color)
        if self.status_message:
            draw_text(self.screen, self.status_message, (SCREEN_WIDTH // 2, PITCH_RECT.centery), self.font, BLACK, center=True)
        draw_button(self.screen, self.skip_button_rect, "Skip Match", GRAY, BLACK, self.font_small)

    # --- SIMULATION LOGIC ---

    def _simulate_step(self):
        """Simulate one dynamic step of the match."""
        if not self.ball_carrier or not self.possession_team: # Handle loose ball pickup
            all_players = self.home_players + self.away_players
            if not all_players: return
            nearest_player = min(all_players, key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y))
            if nearest_player:
                self.ball_carrier = nearest_player; self.possession_team = nearest_player.team
            else: return

        self._update_player_targets() # Determine where everyone wants to go
        for p_state in self.home_players + self.away_players: # Move everyone
            p_state.move_towards_target()
        if self.ball_carrier: # Update ball position
            self.ball_x, self.ball_y = self.ball_carrier.x, self.ball_carrier.y

        # Check events in order of precedence
        pass_event_occurred = self._check_passing_attempt()
        if pass_event_occurred: return
        tackle_resolved = self._check_tackles()
        if tackle_resolved: return
        if random.random() < BASE_PENALTY_CHANCE:
             penalty_team = self.away_team if self.possession_team == self.home_team else self.home_team
             self.handle_penalty(penalty_team, "General infringement"); return
        self._check_scoring()


    # --- UPDATED TARGETING LOGIC ---
    def _update_player_targets(self):
        """Set the target coordinates for each player based on game state (attack/defense formations)."""
        if not self.ball_carrier or not self.possession_team: return

        carrier = self.ball_carrier
        attacking_players = self.home_players if self.possession_team == self.home_team else self.away_players
        defending_players = self.away_players if self.possession_team == self.home_team else self.home_players
        is_home_attacking = self.possession_team == self.home_team
        target_y_direction = 1 if is_home_attacking else -1 # Home attacks down (+Y)

        # --- Attacking Team Targets ---
        # Carrier: Move towards opponent try line
        carrier_target_y = carrier.y + target_y_direction * PITCH_RECT.height
        carrier_target_x = carrier.x + random.uniform(-PITCH_RECT.width * 0.05, PITCH_RECT.width * 0.05) # Less horizontal drift?
        carrier.target_x, carrier.target_y = carrier_target_x, carrier_target_y

        # Support Players: Form up behind carrier
        support_candidates = sorted([p for p in attacking_players if p != carrier],
                                    key=lambda p: math.hypot(p.x - carrier.x, p.y - carrier.y))
        num_immediate_support = 4 # How many players form the immediate support line

        for i, p_state in enumerate(support_candidates):
            # Target Y: Behind the carrier
            target_y = carrier.y - target_y_direction * SUPPORT_DISTANCE + random.uniform(-5, 5)

            # Target X: Spread out horizontally
            # Assign slots left/right of carrier based on index
            slot_index = i // 2 + 1 # 1, 1, 2, 2, 3, 3...
            side_mult = 1 if i % 2 == 0 else -1 # Alternate sides: +1, -1, +1, -1...
            target_x = carrier.x + side_mult * slot_index * ATTACKING_SUPPORT_WIDTH + random.uniform(-10, 10)

            # Immediate support players get higher priority to reach these spots
            if i < num_immediate_support:
                p_state.target_x, p_state.target_y = target_x, target_y
            else:
                # Players further away move generally towards play but maybe slower or hold width
                # Simple approach: Target the same support line but move slower?
                # Or just move towards carrier's Y level but stay wide?
                general_target_x = p_state.x # Hold width initially
                general_target_y = carrier.y - target_y_direction * (SUPPORT_DISTANCE + 30) # Further back
                # Blend target with current position for slower reaction
                p_state.target_x = p_state.x * 0.8 + general_target_x * 0.2
                p_state.target_y = p_state.y * 0.8 + general_target_y * 0.2


        # --- Defending Team Targets ---
        # Determine the desired Y-position of the defensive line
        # Slightly ahead of the carrier, but not grossly offside (behind carrier towards defender's goal)
        defensive_line_y = carrier.y - target_y_direction * DEFENSIVE_LINE_Y_OFFSET

        # Offside check: Ensure line_y is not ahead of carrier relative to *defender's* try line
        # Home (Red) defends TOP, Away (Blue) defends BOTTOM
        home_try_line_y = PITCH_RECT.top
        away_try_line_y = PITCH_RECT.bottom
        if is_home_attacking: # Away team (Blue) is defending
            defensive_line_y = max(defensive_line_y, carrier.y + PASS_Y_TOLERANCE) # Must be >= carrier.y (approx)
            defensive_line_y = min(defensive_line_y, away_try_line_y - 10) # Don't sit on own line
        else: # Home team (Red) is defending
            defensive_line_y = min(defensive_line_y, carrier.y - PASS_Y_TOLERANCE) # Must be <= carrier.y (approx)
            defensive_line_y = max(defensive_line_y, home_try_line_y + 10) # Don't sit on own line

        # Sort defenders by their current X position to assign line spots
        defenders_sorted_x = sorted(defending_players, key=lambda p: p.x)
        num_defenders = len(defenders_sorted_x)
        line_center_x = carrier.x # Line shifts horizontally with the carrier

        # Assign targets for the main defensive line (exclude sweeper for now)
        num_in_line = num_defenders - 1 if num_defenders > 5 else num_defenders # Keep one back as sweeper if enough players
        sweeper = None

        for i, p_state in enumerate(defenders_sorted_x):
            if i == num_in_line and num_defenders > 5 : # Designate last player (often widest?) as sweeper
                sweeper = p_state
                continue

            # Calculate target X based on position in the sorted list
            # Centered around the carrier's X, with spacing
            target_x = line_center_x + (i - num_in_line // 2) * DEFENSIVE_LINE_SPACING
            p_state.target_x = target_x
            p_state.target_y = defensive_line_y + random.uniform(-3, 3) # Slight Y variation

        # Position the sweeper (if designated)
        if sweeper:
            sweeper_y = defensive_line_y + target_y_direction * SWEEPER_DEPTH_OFFSET # Behind the line
            # Sweeper covers centrally or shifts slightly with ball? Central for now.
            sweeper_target_x = line_center_x # PITCH_RECT.centerx
            sweeper.target_x = sweeper_target_x
            sweeper.target_y = sweeper_y

    # --- Event Handling Logic (Pass, Tackle, Penalty, Scoring) ---
    # (These functions remain unchanged from the previous version with passing)

    def _check_passing_attempt(self) -> bool:
        if not self.ball_carrier: return False
        carrier = self.ball_carrier
        defending_players = self.away_players if self.possession_team == self.home_team else self.home_players
        attacking_players = self.home_players if self.possession_team == self.home_team else self.away_players
        under_pressure = any(math.hypot(d.x - carrier.x, d.y - carrier.y) < PASS_PRESSURE_RADIUS for d in defending_players)
        pass_chance = BASE_PASS_CHANCE + (PASS_PRESSURE_BONUS if under_pressure else 0)
        if random.random() < pass_chance:
            target = self._find_pass_target(carrier, attacking_players)
            if target: return self._execute_pass(carrier, target, defending_players)
        return False

    def _find_pass_target(self, carrier: PlayerState, teammates: list[PlayerState]) -> PlayerState | None:
        valid_targets = []
        is_home_team = carrier.team == self.home_team
        required_y_comparison = (lambda r_y, c_y: r_y >= c_y - PASS_Y_TOLERANCE) if is_home_team else \
                                (lambda r_y, c_y: r_y <= c_y + PASS_Y_TOLERANCE)
        for p_state in teammates:
            if p_state == carrier: continue
            distance = math.hypot(p_state.x - carrier.x, p_state.y - carrier.y)
            if required_y_comparison(p_state.y, carrier.y) and distance < PASS_MAX_DISTANCE:
                valid_targets.append((p_state, distance))
        if not valid_targets: return None
        valid_targets.sort(key=lambda item: item[1])
        return valid_targets[0][0]

    def _execute_pass(self, carrier: PlayerState, target: PlayerState, defenders: list[PlayerState]) -> bool:
        distance = math.hypot(target.x - carrier.x, target.y - carrier.y)
        success_chance = PASS_SUCCESS_BASE + (carrier.player.passing - 60) * PASS_ACCURACY_INFLUENCE - distance * PASS_DISTANCE_PENALTY
        success_chance = max(0.1, min(0.98, success_chance))
        if random.random() < success_chance: # Successful Pass
            self.ball_carrier = target; self.set_status(f"Pass to {target.player.name}")
            return True
        else: # Failed Pass
            for defender in defenders: # Check Interception
                if math.hypot(defender.x - target.x, defender.y - target.y) < PASS_INTERCEPTION_RADIUS:
                    intercept_chance = PASS_INTERCEPTION_BASE_CHANCE
                    if random.random() < intercept_chance:
                        self.ball_carrier = defender; self.possession_team = defender.team
                        self.set_status(f"INTERCEPTED by {defender.player.name}!"); return True
            # Dropped Pass
            self.ball_carrier = None; self.ball_x, self.ball_y = target.x + random.uniform(-5, 5), target.y + random.uniform(-5, 5)
            self.set_status("Dropped pass!"); return True

    def _check_tackles(self) -> bool:
        if not self.ball_carrier: return False
        carrier = self.ball_carrier
        defending_players = self.away_players if self.possession_team == self.home_team else self.home_players
        tackle_resolved = False
        potential_tacklers = [d for d in defending_players if math.hypot(d.x - carrier.x, d.y - carrier.y) < TACKLE_RADIUS]
        if not potential_tacklers: return False
        defender = min(potential_tacklers, key=lambda d: math.hypot(d.x - carrier.x, d.y - carrier.y))
        str_diff = carrier.player.strength - defender.player.strength; tck_diff = defender.player.tackling - 50; spd_diff = defender.player.speed - carrier.player.speed
        success_chance = TACKLE_SUCCESS_BASE - str_diff * TACKLE_STRENGTH_INFLUENCE + tck_diff * TACKLE_STRENGTH_INFLUENCE + spd_diff * TACKLE_SPEED_INFLUENCE
        success_chance = max(0.05, min(0.95, success_chance))
        if random.random() < success_chance: # Successful Tackle
            self.set_status(f"Tackle! {defender.player.name} stops {carrier.player.name}!")
            penalty_chance_on_tackle = BASE_PENALTY_CHANCE * 2.5
            if random.random() < penalty_chance_on_tackle: # Check Penalty
                penalty_offender = carrier.team; penalty_winner = defender.team
                self.handle_penalty(penalty_winner, f"Infringement by {penalty_offender.name} at tackle"); tackle_resolved = True
            else: # Process Turnover
                self.possession_team = defender.team; self.ball_carrier = None; self.ball_x, self.ball_y = carrier.x, carrier.y; tackle_resolved = True
        else: # Broken Tackle
            self.set_status(f"{carrier.player.name} breaks the tackle from {defender.player.name}!")
            knockback_factor = 0.3; defender.x += (defender.x - carrier.x) * knockback_factor; defender.y += (defender.y - carrier.y) * knockback_factor
        return tackle_resolved

    def handle_penalty(self, winning_team: Team, reason: str):
        self.set_status(f"Penalty! {winning_team.name}. ({reason})", 2000); self.possession_team = winning_team; self.ball_carrier = None
        kicker_candidates = self.home_players if winning_team == self.home_team else self.away_players
        if not kicker_candidates: return
        kicker = max(kicker_candidates, key=lambda p: p.player.kicking); self.ball_x, self.ball_y = kicker.x, kicker.y
        is_home_kicking = winning_team == self.home_team; target_try_line_y = PITCH_RECT.bottom if is_home_kicking else PITCH_RECT.top
        dist_to_posts = abs(self.ball_y - target_try_line_y); kick_range = PITCH_RECT.height * 0.45; time.sleep(0.5)
        if dist_to_posts < kick_range: # Attempt goal
            kick_success_chance = PENALTY_SUCCESS_RATE + (kicker.player.kicking - 60) / 150
            if random.random() < kick_success_chance:
                self.set_status("Penalty goal successful!", 2000)
                if is_home_kicking: self.home_score += PENALTY_POINTS
                else: self.away_score += PENALTY_POINTS
                time.sleep(0.5); self._reset_to_midfield(self.away_team if is_home_kicking else self.home_team)
            else:
                self.set_status("Penalty kick missed.", 2000); time.sleep(0.5)
                defending_team = self.away_team if is_home_kicking else self.home_team
                dropout_y = PITCH_RECT.top + PITCH_RECT.height * 0.25 if defending_team == self.home_team else PITCH_RECT.bottom - PITCH_RECT.height * 0.25
                self.ball_y, self.ball_x = dropout_y, PITCH_RECT.centerx; self._reset_player_possession(defending_team)
        else: # Kick for touch
            self.set_status("Penalty kicked for touch.", 2000); time.sleep(0.5)
            move_direction = 1 if is_home_kicking else -1; self.ball_y += move_direction * PITCH_RECT.height * 0.3
            self.ball_y = max(PITCH_RECT.top + 10, min(self.ball_y, PITCH_RECT.bottom - 10)); self._reset_player_possession(winning_team)

    def _check_scoring(self):
        if not self.ball_carrier: return
        carrier = self.ball_carrier; home_target_try_line_y = PITCH_RECT.bottom - 5; away_target_try_line_y = PITCH_RECT.top + 5
        scored, scoring_team = False, None
        if self.possession_team == self.home_team and carrier.y >= home_target_try_line_y:
            self.set_status(f"TRY! {self.home_team.name}!", 2000); scored, scoring_team = True, self.home_team; self.home_score += TRY_POINTS
        elif self.possession_team == self.away_team and carrier.y <= away_target_try_line_y:
            self.set_status(f"TRY! {self.away_team.name}!", 2000); scored, scoring_team = True, self.away_team; self.away_score += TRY_POINTS
        if scored and scoring_team:
            self.ball_carrier = None; self.ball_x, self.ball_y = None, None
            kicker_candidates = self.home_players if scoring_team == self.home_team else self.away_players
            if not kicker_candidates: return
            kicker = max(kicker_candidates, key=lambda p: p.player.kicking)
            conversion_chance = CONVERSION_SUCCESS_RATE + (kicker.player.kicking - 60) / 150; time.sleep(1.0)
            if random.random() < conversion_chance:
                self.set_status("Conversion successful!", 2000)
                if scoring_team == self.home_team: self.home_score += CONVERSION_POINTS
                else: self.away_score += CONVERSION_POINTS
            else: self.set_status("Conversion missed.", 2000)
            time.sleep(1.0)
            restart_team = self.away_team if scoring_team == self.home_team else self.home_team
            self._reset_to_midfield(restart_team)

    def _reset_to_midfield(self, possession_team: Team):
         print(f"Resetting to midfield, possession: {possession_team.name}"); self.ball_x, self.ball_y = PITCH_RECT.centerx, PITCH_RECT.centery
         self._reset_player_possession(possession_team)

    def _reset_player_possession(self, possession_team: Team):
        self.possession_team = possession_team; self.ball_carrier = None
        receiving_team_players = self.home_players if possession_team == self.home_team else self.away_players
        if not receiving_team_players: return
        receiver = min(receiving_team_players, key=lambda p: math.hypot(p.x - self.ball_x, p.y - self.ball_y))
        self.ball_carrier = receiver
        if self.message_timer == 0 or pygame.time.get_ticks() > self.message_timer : self.set_status(f"{possession_team.name} possession.")

    def _skip_to_end(self):
         if self.is_finished: return
         if hasattr(self, '_skip_processing') and self._skip_processing: return
         self._skip_processing = True; print("Calculating skip result using instant engine...")
         temp_home_score, temp_away_score = simulate_match(self.home_team, self.away_team)
         self.home_score, self.away_score = temp_home_score, temp_away_score
         self.current_step = MATCH_DURATION_STEPS; self.displayed_minute = GAME_DURATION_MINUTES; self.is_finished = True
         final_msg = f"(Skipped) Final Score: {self.home_team.name} {self.home_score} - {self.away_score} {self.away_team.name}"
         print(final_msg); self.set_status(final_msg, 5000)
         pygame.time.set_timer(pygame.USEREVENT + 1, 100, loops=1) # Callback almost immediately