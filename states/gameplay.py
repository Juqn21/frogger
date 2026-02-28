import pygame
import random
from states.base import State
from constants import MARGIN_X, OFFSET_Y, TILE_SIZE, MAP_PATH, GOAL_PATH, MAX_TIME, GAME_WIDTH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT
from entities.frog import Frog
from entities.obstacles import Car, Log, Turtle, Snake, Crocodile

class GameplayState(State):
    def __init__(self, game):
        super().__init__(game)
        self.background = None
        self.goal_image = None
        
        self.slots_rangos = [(MARGIN_X + 59 + (i*120), MARGIN_X + 99 + (i*120)) for i in range(5)]
        self.start_x = MARGIN_X + 300
        self.start_y = OFFSET_Y + (14 * TILE_SIZE)
        
        self.cars, self.logs, self.turtles, self.snakes, self.crocodiles = [pygame.sprite.Group() for _ in range(5)]
        self.trunk_snake = None
        self.target_log = None

    def on_enter(self):
        if not self.background:
            self.background = pygame.image.load(MAP_PATH).convert()
        if not self.goal_image:
            self.goal_image = pygame.transform.scale(pygame.image.load(GOAL_PATH).convert_alpha(), (34, 34))
        self.reset_level_entities()

    def reset_level_entities(self):
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles]:
            group.empty()
        self.trunk_snake = None
        self.target_log = None
        self._setup_entities()
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
        self.max_row_reached = 14 

    def update(self, dt):
        if self.frog.state == "ALIVE":
            if not self.game.god_mode:
                self.game.time_left -= dt
                if self.game.time_left <= 0: self.handle_death(); return
            
            if not self.game.god_mode:
                enemies = list(self.cars) + list(self.snakes)
                for e in enemies:
                    if self.frog.hitbox.colliderect(e.hitbox):
                        self.handle_death(); return

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

        # --- AQUÍ ESTÁ EL DELAY CON EL RETURN ---
        if self.frog.is_finished:
            if self.game.lives <= 0:
                self.game.change_state("GAME_OVER")
            else:
                self.spawn_frog()
            return # Detiene la ejecución para no actualizar una rana que ya terminó de morir

        self.all_sprites.update()
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles]: group.update()

        for s in self.snakes:
            if s == self.trunk_snake and self.target_log: s.rect.x = self.target_log.rect.x + 10 
            else:
                if s.rect.left <= MARGIN_X: s.speed = abs(s.speed)
                elif s.rect.right >= MARGIN_X + GAME_WIDTH: s.speed = -abs(s.speed)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_g: self.game.god_mode = not self.game.god_mode
                
                if self.frog.state == "ALIVE":
                    old_y = self.frog.rect.y
                    res = self.frog.move("UP", self.slots_rangos) if e.key == pygame.K_UP else \
                          self.frog.move("DOWN") if e.key == pygame.K_DOWN else \
                          self.frog.move("LEFT") if e.key == pygame.K_LEFT else \
                          self.frog.move("RIGHT") if e.key == pygame.K_RIGHT else None
                    
                    if e.key == pygame.K_UP and self.frog.rect.y < old_y:
                        current_row = (self.frog.rect.y - OFFSET_Y) // TILE_SIZE
                        if current_row < self.max_row_reached:
                            self.game._add_score(10)
                            self.max_row_reached = current_row

                    if res is not None:
                        if not self.game.slots_ocupados[res]:
                            self.game.slots_ocupados[res] = True
                            self.game._add_score(100)
                            if all(self.game.slots_ocupados): 
                                self.game._add_score(1000)
                                self.game.level += 1
                                self.game.lives = min(self.game.lives + 1, 9)
                                self.game.difficulty_multiplier += 0.15 
                                self.game.slots_ocupados = [False]*5
                                self.reset_level_entities()
                            else: self.spawn_frog()
                        else: self.frog.rect.y += TILE_SIZE 

    def handle_death(self):
        if self.frog.state == "ALIVE":
            self.game.lives -= 1
            # Iniciamos la animación de la muerte
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
        
        for gp in [self.turtles, self.logs, self.crocodiles, self.snakes, self.cars, self.all_sprites]:
            gp.draw(surface)
        surface.set_clip(None)
        
        t_max_w, t_h = 200, 15
        t_x, t_y = BASE_WIDTH - 220, 750 
        pct = max(0, self.game.time_left / MAX_TIME)
        
        if pct > 0.5: t_color = (0, 255, 0)
        elif pct > 0.25: t_color = (255, 255, 0)
        else: t_color = (255, 0, 0) if pygame.time.get_ticks() % 500 < 250 else (150, 0, 0)

        pygame.draw.rect(surface, (40, 40, 40), (t_x - 2, t_y - 2, t_max_w + 4, t_h + 4))
        pygame.draw.rect(surface, t_color, (t_x, t_y, t_max_w * pct, t_h))
        self.game._draw_text_with_shadow(surface, "TIME", (t_x - 70, t_y - 5))

        self.game._draw_text_with_shadow(surface, f"SCORE: {self.game.score:05d}", (16, 119))
        self.game._draw_text_with_shadow(surface, f"LEVEL: {self.game.level}", (17, 63))
        self.game._draw_text_with_shadow(surface, f"LIVES: {self.game.lives}", (17, 175), (255, 50, 50))
        if self.game.god_mode:
            self.game._draw_text_with_shadow(surface, "GOD MODE", (10, 250), (255, 140, 0))