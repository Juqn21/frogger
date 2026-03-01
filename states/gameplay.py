import pygame
import random
import os
import math 
from states.base import State
from constants import MARGIN_X, OFFSET_Y, TILE_SIZE, MAP_PATH, GOAL_PATH, MAX_TIME, GAME_WIDTH, GAME_MUSIC_PATH, COIN_SOUND_PATH, JUMP_SOUND_PATH, SQUASH_SOUND_PATH, TIME_SOUND_PATH, EXTRALIFE_SOUND_PATH, SELECT_SOUND_PATH, SLOT_SOUND_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT
from entities.frog import Frog
from entities.obstacles import Car, Log, Turtle, Snake, Crocodile, Coin

class GameplayState(State):
    def __init__(self, game):
        super().__init__(game)
        self.background = None
        self.goal_image = None
        
        self.slots_rangos = [(MARGIN_X + 59 + (i*120), MARGIN_X + 99 + (i*120)) for i in range(5)]
        self.start_x = MARGIN_X + 300
        self.start_y = OFFSET_Y + (14 * TILE_SIZE)
        
        self.cars, self.logs, self.turtles, self.snakes, self.crocodiles, self.coins = [pygame.sprite.Group() for _ in range(6)]
        self.trunk_snake = None
        self.target_log = None
        
        self.next_coin_spawn_time = 0 
        self.coin_sound = None 
        self.jump_sound = None 
        self.squash_sound = None
        self.time_sound = None 
        self.extralife_sound = None 
        self.select_sound = None 
        self.slot_sound = None
        self.time_warning_played = False 
        
        self.pause_state = None 
        self.pause_timer = 0.0
        
        self.is_paused = False
        self.pause_options = ["RESUME", "RESTART", "MENU"]
        self.pause_selected_index = 0
        
        self.display_score = 0.0      
        self.floating_texts = []      

    def on_enter(self):
        self.is_paused = False 
        self.pause_selected_index = 0
        self.display_score = self.game.score 
        self.floating_texts.clear()
        
        if not self.background:
            self.background = pygame.image.load(MAP_PATH).convert()
        if not self.goal_image:
            self.goal_image = pygame.transform.scale(pygame.image.load(GOAL_PATH).convert_alpha(), (34, 34))
            
        if self.coin_sound is None:
            if os.path.exists(COIN_SOUND_PATH): self.coin_sound = pygame.mixer.Sound(COIN_SOUND_PATH)
        if self.jump_sound is None:
            if os.path.exists(JUMP_SOUND_PATH): self.jump_sound = pygame.mixer.Sound(JUMP_SOUND_PATH)
        if self.squash_sound is None:
            if os.path.exists(SQUASH_SOUND_PATH): self.squash_sound = pygame.mixer.Sound(SQUASH_SOUND_PATH)
        if self.time_sound is None:
            if os.path.exists(TIME_SOUND_PATH): self.time_sound = pygame.mixer.Sound(TIME_SOUND_PATH)
        if self.extralife_sound is None:
            if os.path.exists(EXTRALIFE_SOUND_PATH): self.extralife_sound = pygame.mixer.Sound(EXTRALIFE_SOUND_PATH)
        if self.select_sound is None:
            if os.path.exists(SELECT_SOUND_PATH): self.select_sound = pygame.mixer.Sound(SELECT_SOUND_PATH)
        if self.slot_sound is None:
            if os.path.exists(SLOT_SOUND_PATH): self.slot_sound = pygame.mixer.Sound(SLOT_SOUND_PATH)

        if os.path.exists(GAME_MUSIC_PATH):
            pygame.mixer.music.load(GAME_MUSIC_PATH)
            pygame.mixer.music.set_volume(self.game.volume * 0.2) 
            pygame.mixer.music.play(-1) 
            
        self.reset_level_entities()

    def reset_level_entities(self):
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles, self.coins]: group.empty()
        self.trunk_snake = None
        self.target_log = None
        self._setup_entities()
        self.next_coin_spawn_time = pygame.time.get_ticks() + random.randint(8000, 15000)
        self.spawn_frog()

    def _setup_entities(self):
        m = self.game.difficulty_multiplier
        traffic = [(7, -2.2*m, 0, 45, [100, 350, 550]), (8, 1.6*m, 1, 40, [50, 400]), 
                   (9, -1.8*m, 2, 40, [150, 210, 270]), (10, 1.3*m, 3, 55, [0, 350]), 
                   (11, -1.5*m, 1, 40, [0, 160, 320, 480]), (12, 1.9*m, 2, 40, [20, 280, 520])]
        for r, s, idx, w, pos in traffic:
            y = OFFSET_Y + (r * TILE_SIZE)
            for px in pos: self.cars.add(Car(MARGIN_X + px, y, s, idx, MARGIN_X, GAME_WIDTH, w))
        
        y_r = [OFFSET_Y + (i * TILE_SIZE) for i in range(5, 0, -1)]
        row1_logs = []
        for i in range(4): 
            l = Log(MARGIN_X + (i*160), y_r[0], -1.2*m, MARGIN_X, GAME_WIDTH, 95, 2)
            self.logs.add(l)
            row1_logs.append(l)
            
        for g in range(3): 
            for i in range(2): self.turtles.add(Turtle(MARGIN_X + (g*220) + (i*46), y_r[1], 2.0*m, MARGIN_X, GAME_WIDTH, group_offset=g*6.0))
        
        pos_f3 = [0, 220, 440]
        c_idx = random.randint(0, 2) if self.game.level >= 2 else -1
        for i, px in enumerate(pos_f3):
            if i == c_idx: self.crocodiles.add(Crocodile(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, GAME_WIDTH))
            else: self.logs.add(Log(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, GAME_WIDTH, 180, 3))

        for g in range(3): 
            for i in range(3): self.turtles.add(Turtle(MARGIN_X + (g*210) + (i*46), y_r[3], 1.5*m, MARGIN_X, GAME_WIDTH, group_offset=g*5.0))
        for i in range(3): self.logs.add(Log(MARGIN_X + (i*250), y_r[4], -2.2*m, MARGIN_X, GAME_WIDTH, 120, 1))

        if self.game.level >= 2: self.snakes.add(Snake(MARGIN_X + 100, OFFSET_Y + (6 * TILE_SIZE), 2.0*m, MARGIN_X, GAME_WIDTH))
        if self.game.level >= 3: self.snakes.add(Snake(MARGIN_X + 400, OFFSET_Y + (13 * TILE_SIZE), 2.0*m, MARGIN_X, GAME_WIDTH))
        if self.game.level >= 4 and row1_logs:
            self.target_log = random.choice(row1_logs)
            self.trunk_snake = Snake(self.target_log.rect.x, y_r[0], self.target_log.speed, MARGIN_X, GAME_WIDTH)
            self.snakes.add(self.trunk_snake)

    def spawn_frog(self):
        self.frog = Frog(self.start_x, self.start_y, MARGIN_X)
        self.all_sprites = pygame.sprite.Group(self.frog)
        self.game.time_left = MAX_TIME
        self.time_warning_played = False 
        self.max_row_reached = 14 

    def spawn_floating_text(self, text, x, y, color=(255, 255, 255)):
        self.floating_texts.append({
            'text': text,
            'x': x,
            'y': y,
            'timer': 1.0, 
            'color': color
        })

    def update(self, dt):
        if self.is_paused:
            return

        current_time = pygame.time.get_ticks()
        old_lives = self.game.lives 
        
        if self.display_score < self.game.score:
            self.display_score += (self.game.score - self.display_score) * 10 * dt
            if self.game.score - self.display_score < 0.5:
                self.display_score = self.game.score
                
        for ft in self.floating_texts:
            ft['y'] -= 40 * dt  
            ft['timer'] -= dt
        self.floating_texts = [ft for ft in self.floating_texts if ft['timer'] > 0]
        
        if self.pause_state is not None:
            self.pause_timer -= dt
            for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles, self.coins]: group.update()
            if self.pause_timer <= 0:
                if self.pause_state == "LEVEL_TRANSITION":
                    self.game.level += 1
                    self.game.lives = min(self.game.lives + 1, 9)
                    if self.extralife_sound:
                        self.extralife_sound.set_volume(self.game.sfx_volume)
                        self.extralife_sound.play()
                    self.game.difficulty_multiplier += 0.15 
                    self.game.slots_ocupados = [False]*5
                    self.reset_level_entities()
                elif self.pause_state == "GOAL_TRANSITION":
                    self.spawn_frog()
                elif self.pause_state == "GAME_OVER_TRANSITION":
                    self.game.change_state("GAME_OVER")
                self.pause_state = None
            return 
        
        if current_time >= self.next_coin_spawn_time:
            platforms = list(self.logs) + list(self.crocodiles)
            new_coin = Coin(platforms)
            self.coins.add(new_coin)
            self.next_coin_spawn_time = current_time + random.randint(8000, 15000)

        if self.frog.state == "ALIVE":
            if not self.game.god_mode:
                self.game.time_left -= dt
                if self.game.time_left <= 5 and not self.time_warning_played:
                    self.time_warning_played = True
                    if self.time_sound:
                        self.time_sound.set_volume(self.game.sfx_volume)
                        self.time_sound.play(-1) 
                if self.game.time_left <= 0: self.handle_death(); return
            
            if not self.game.god_mode:
                enemies = list(self.cars) + list(self.snakes)
                for e in enemies:
                    if self.frog.hitbox.colliderect(e.hitbox):
                        self.handle_death(); return

            for c in self.coins:
                if self.frog.rect.colliderect(c.hitbox):
                    self.game._add_score(100) 
                    self.spawn_floating_text("+100", c.rect.x, c.rect.y, (255, 215, 0))
                    c.kill() 
                    if self.coin_sound:
                        self.coin_sound.set_volume(self.game.sfx_volume * 0.15) 
                        self.coin_sound.play()
                    
            frog_center_y = self.frog.hitbox.centery
            river_top, river_bottom = OFFSET_Y + TILE_SIZE, OFFSET_Y + 6 * TILE_SIZE
            
            if river_top <= frog_center_y < river_bottom:
                on_safe_ground, platform_speed = False, 0
                for l in self.logs:
                    if self.frog.hitbox.colliderect(l.hitbox):
                        on_safe_ground, platform_speed = True, l.speed
                        break
                if not on_safe_ground:
                    for t in self.turtles:
                        if self.frog.hitbox.colliderect(t.hitbox):
                            if not t.is_submerged: on_safe_ground, platform_speed = True, t.speed
                            break
                if not on_safe_ground:
                    for c in self.crocodiles:
                        if self.frog.hitbox.colliderect(c.hitbox):
                            h_x = c.rect.x if c.speed < 0 else c.rect.right - 40
                            head = pygame.Rect(h_x, c.rect.y, 40, 40)
                            if c.state == "OPEN" and self.frog.hitbox.colliderect(head): on_safe_ground = False 
                            else: on_safe_ground, platform_speed = True, c.speed
                            break
                if on_safe_ground: self.frog.rect.x += platform_speed
                elif not self.game.god_mode: self.handle_death(); return

            if self.game.lives > old_lives and self.extralife_sound:
                self.extralife_sound.set_volume(self.game.sfx_volume)
                self.extralife_sound.play()

        if self.frog.is_finished:
            if self.game.lives <= 0:
                if self.pause_state != "GAME_OVER_TRANSITION":
                    pygame.mixer.music.stop() 
                    self.pause_state = "GAME_OVER_TRANSITION"
                    self.pause_timer = 1.5
            else:
                self.spawn_frog()
            return 

        self.all_sprites.update()
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles, self.coins]: group.update()

        for s in self.snakes:
            if s == self.trunk_snake and self.target_log: s.rect.x = self.target_log.rect.x + 10 
            else:
                if s.rect.left <= MARGIN_X: s.speed = abs(s.speed)
                elif s.rect.right >= MARGIN_X + GAME_WIDTH: s.speed = -abs(s.speed)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                
                if e.key in [pygame.K_p, pygame.K_ESCAPE]:
                    if self.pause_state is None:
                        self.is_paused = not self.is_paused
                        self.pause_selected_index = 0
                        if self.is_paused: pygame.mixer.music.pause()
                        else: pygame.mixer.music.unpause()
                
                if self.is_paused:
                    if e.key == self.game.controls["UP"]:
                        self.pause_selected_index -= 1
                        if self.pause_selected_index < 0: self.pause_selected_index = len(self.pause_options) - 1
                        if self.select_sound:
                            self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                            self.select_sound.play()
                    elif e.key == self.game.controls["DOWN"]:
                        self.pause_selected_index += 1
                        if self.pause_selected_index >= len(self.pause_options): self.pause_selected_index = 0
                        if self.select_sound:
                            self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                            self.select_sound.play()
                    elif e.key == pygame.K_RETURN:
                        if self.select_sound:
                            self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                            self.select_sound.play()
                        selected = self.pause_options[self.pause_selected_index]
                        if selected == "RESUME":
                            self.is_paused = False
                            pygame.mixer.music.unpause()
                        elif selected == "RESTART":
                            self.game.lives = 5
                            self.game.level = 1
                            self.game.score = 0
                            self.game.difficulty_multiplier = 1.0
                            self.game.slots_ocupados = [False] * 5
                            pygame.mixer.music.stop()
                            self.game.change_state("PLAYING")
                        elif selected == "MENU":
                            pygame.mixer.music.stop()
                            self.game.change_state("START")
                    continue 
                
                if self.pause_state is not None:
                    return 
                    
                old_lives = self.game.lives 
                
                if e.key == pygame.K_g: self.game.god_mode = not self.game.god_mode
                if e.key == pygame.K_l: self.game.lives = min(self.game.lives + 1, 9) 
                
                if self.frog.state == "ALIVE":
                    old_y = self.frog.rect.y
                    res = None
                    is_movement_key = False 
                    
                    if e.key == self.game.controls["UP"]: 
                        res = self.frog.move("UP", self.slots_rangos)
                        is_movement_key = True
                    elif e.key == self.game.controls["DOWN"]: 
                        res = self.frog.move("DOWN")
                        is_movement_key = True
                    elif e.key == self.game.controls["LEFT"]: 
                        res = self.frog.move("LEFT")
                        is_movement_key = True
                    elif e.key == self.game.controls["RIGHT"]: 
                        res = self.frog.move("RIGHT")
                        is_movement_key = True
                    
                    if is_movement_key and self.jump_sound:
                        self.jump_sound.set_volume(self.game.sfx_volume) 
                        self.jump_sound.play()

                    if e.key == self.game.controls["UP"] and self.frog.rect.y < old_y:
                        current_row = (self.frog.rect.y - OFFSET_Y) // TILE_SIZE
                        if current_row < self.max_row_reached:
                            self.game._add_score(10)
                            self.max_row_reached = current_row

                    if res is not None:
                        if not self.game.slots_ocupados[res]:
                            self.game.slots_ocupados[res] = True
                            self.game._add_score(100)
                            
                            slot_x = (self.slots_rangos[res][0] + self.slots_rangos[res][1]) // 2 - 17
                            self.spawn_floating_text("+100", slot_x, OFFSET_Y + 10, (0, 255, 255))
                            
                            if self.time_sound: self.time_sound.stop()
                                
                            self.frog.state = "SAFE" 
                            self.frog.rect.x = -1000
                            self.frog.rect.y = -1000
                            
                            if self.slot_sound:
                                self.slot_sound.set_volume(self.game.sfx_volume)
                                self.slot_sound.play()
                                
                            if all(self.game.slots_ocupados): 
                                self.game._add_score(1000)
                                self.pause_state = "LEVEL_TRANSITION"
                                self.pause_timer = 2.0 
                            else: 
                                self.pause_state = "GOAL_TRANSITION"
                                self.pause_timer = 0.5 
                        else: self.frog.rect.y += TILE_SIZE 
                        
                    if self.game.lives > old_lives and self.extralife_sound:
                        self.extralife_sound.set_volume(self.game.sfx_volume)
                        self.extralife_sound.play()

    def handle_death(self):
        if self.frog.state == "ALIVE":
            self.game.lives -= 1
            if self.time_sound: self.time_sound.stop()
            if self.squash_sound:
                self.squash_sound.set_volume(self.game.sfx_volume)
                self.squash_sound.play()
            self.frog.die()

    def render(self, surface):
        surface.blit(self.background, (0, 0))
        
        clip_rect = pygame.Rect(MARGIN_X, 0, GAME_WIDTH, BASE_HEIGHT)
        surface.set_clip(clip_rect)
        if self.goal_image:
            for i, oc in enumerate(self.game.slots_ocupados):
                if oc:
                    x_p = (self.slots_rangos[i][0] + self.slots_rangos[i][1]) // 2 - 17
                    surface.blit(self.goal_image, (x_p, OFFSET_Y + 3))
        
        for gp in [self.turtles, self.logs, self.crocodiles, self.coins, self.snakes, self.cars, self.all_sprites]:
            gp.draw(surface)
            
        surface.set_clip(None)
        
        # --- AQUÍ ESTÁ EL ARREGLO: FONT_UI EN VEZ DE FONT_MENU ---
        for ft in self.floating_texts:
            alpha = max(0, min(255, int(ft['timer'] * 255)))
            txt_surf = self.game.font_ui.render(ft['text'], False, ft['color'])
            txt_border = self.game.font_ui.render(ft['text'], False, (0, 0, 0))
            txt_surf.set_alpha(alpha)
            txt_border.set_alpha(alpha)
            surface.blit(txt_border, (int(ft['x']) + 2, int(ft['y']) + 2))
            surface.blit(txt_surf, (int(ft['x']), int(ft['y'])))
            
        self.game._draw_text_with_shadow(surface, f"LEVEL: {self.game.level}", (17, 63))
        self.game._draw_text_with_shadow(surface, f"SCORE: {int(self.display_score):05d}", (16, 119))
        self.game._draw_text_with_shadow(surface, f"LIVES: {self.game.lives}", (17, 175), (255, 50, 50))
        
        pct = max(0, self.game.time_left / MAX_TIME)
        
        time_color = (255, 255, 255)
        if pct <= 0.25:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.01))
            time_color = (255, int(255 * pulse), int(255 * pulse))
            
        self.game._draw_text_with_shadow(surface, "TIME", (17, 231), time_color)
        t_max_w, t_h = 120, 15  
        t_x, t_y = 17, 258     
        
        if pct > 0.5: t_color = (0, 255, 0)
        elif pct > 0.25: t_color = (255, 255, 0)
        else: t_color = (255, 0, 0) if pygame.time.get_ticks() % 500 < 250 else (150, 0, 0)

        pygame.draw.rect(surface, (40, 40, 40), (t_x - 2, t_y - 2, t_max_w + 4, t_h + 4))
        pygame.draw.rect(surface, t_color, (t_x, t_y, t_max_w * pct, t_h))

        if self.game.god_mode:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            gm_color = (255, int(140 * pulse), 0)
            self.game._draw_text_with_shadow(surface, "GOD MODE", (10, 300), gm_color)
            
        if self.pause_state == "LEVEL_TRANSITION":
            txt = f"LEVEL {self.game.level} CLEARED!"
            txt_w, txt_h = self.game.font_menu.size(txt)
            x_pos = (BASE_WIDTH // 2) - (txt_w // 2)
            y_pos = (BASE_HEIGHT // 2) - (txt_h // 2)
            
            overlay = pygame.Surface((BASE_WIDTH, txt_h + 20), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, y_pos - 10))
            
            txt_borde = self.game.font_menu.render(txt, False, (0, 0, 0))
            txt_color = self.game.font_menu.render(txt, False, (50, 255, 50))
            surface.blit(txt_borde, (x_pos + 3, y_pos + 3))
            surface.blit(txt_color, (x_pos, y_pos))

        if self.is_paused:
            overlay = pygame.Surface((BASE_WIDTH, BASE_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            surface.blit(overlay, (0, 0))
            
            txt_paused_borde = self.game.font_big.render("PAUSED", False, (0, 0, 0))
            txt_paused_color = self.game.font_big.render("PAUSED", False, (255, 255, 0))
            x_title = (BASE_WIDTH // 2) - (txt_paused_color.get_width() // 2)
            y_title = (BASE_HEIGHT // 2) - 100
            surface.blit(txt_paused_borde, (x_title + 3, y_title + 3))
            surface.blit(txt_paused_color, (x_title, y_title))
            
            start_y = (BASE_HEIGHT // 2) - 10
            spacing = 50
            
            for i, opt in enumerate(self.pause_options):
                if i == self.pause_selected_index:
                    text_str = f">{opt}<"
                    color = (125, 33, 129)
                else:
                    text_str = opt
                    color = (255, 255, 255)
                    
                txt_borde = self.game.font_menu.render(text_str, False, (0, 0, 0))
                txt_color = self.game.font_menu.render(text_str, False, color)
                x_pos = (BASE_WIDTH // 2) - (txt_color.get_width() // 2)
                y_pos = start_y + (i * spacing)
                
                surface.blit(txt_borde, (x_pos + 3, y_pos + 3))
                surface.blit(txt_color, (x_pos, y_pos))