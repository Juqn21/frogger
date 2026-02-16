import pygame
import sys
import random
import os
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT
from constants import MARGIN_X, OFFSET_Y, TILE_SIZE, MAP_PATH, GOAL_PATH, MAX_TIME
from entities.frog import Frog
from entities.obstacles import Car, Log, Turtle, Snake, Crocodile

class Game(GameBase):
    def __init__(self, metadata: GameMeta) -> None:
        super().__init__(metadata)
        pygame.font.init()
        self.font_small = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 50, bold=True)
        
        self.state = "START"
        self.lives = 5
        self.level = 1
        self.score = 0
        self.time_left = MAX_TIME # Inicialización
        self.difficulty_multiplier = 1.0
        
        self.background = None
        self.goal_image = None
        self.slots_rangos = [(MARGIN_X + 59 + (i*120), MARGIN_X + 99 + (i*120)) for i in range(5)]
        self.slots_ocupados = [False] * 5
        self.start_x = MARGIN_X + 300
        self.start_y = OFFSET_Y + (14 * TILE_SIZE)
        
        self.cars, self.logs, self.turtles, self.snakes, self.crocodiles = [pygame.sprite.Group() for _ in range(5)]
        self.trunk_snake = None 
        self.target_log = None  
        
        self.reset_game_logic()

    def reset_game_logic(self):
        self.lives = 5
        self.level = 1
        self.score = 0
        self.difficulty_multiplier = 1.0
        self.slots_ocupados = [False] * 5
        self.reset_level_entities()

    def reset_level_entities(self):
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles]:
            group.empty()
        self.trunk_snake = None
        self.target_log = None
        self._setup_entities()
        self.spawn_frog()

    def _setup_entities(self):
        m = self.difficulty_multiplier
        traffic = [(7, -2.2*m, 0, 45, [100, 350, 550]), (8, 1.6*m, 1, 40, [50, 400]), (9, -1.8*m, 2, 40, [150, 210, 270]), (10, 1.3*m, 3, 55, [0, 350]), (11, -1.5*m, 1, 40, [0, 160, 320, 480]), (12, 1.9*m, 2, 40, [20, 280, 520])]
        for r, s, idx, w, pos in traffic:
            y = OFFSET_Y + (r * TILE_SIZE)
            for px in pos: self.cars.add(Car(MARGIN_X + px, y, s, idx, MARGIN_X, 640, w))
        
        y_r = [OFFSET_Y + (i * TILE_SIZE) for i in range(5, 0, -1)]
        for i in range(4): self.logs.add(Log(MARGIN_X + (i*160), y_r[0], -1.2*m, MARGIN_X, 640, 95, 2))
        for g in range(3): 
            for i in range(2): self.turtles.add(Turtle(MARGIN_X + (g*220) + (i*46), y_r[1], 2.0*m, MARGIN_X, 640, group_offset=g*6.0))
        
        pos_f3 = [0, 220, 440]
        c_idx = random.randint(0, 2) if self.level >= 2 else -1
        for i, px in enumerate(pos_f3):
            if i == c_idx: self.crocodiles.add(Crocodile(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, 640))
            else: self.logs.add(Log(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, 640, 180, 3))

        for g in range(3): 
            for i in range(3): self.turtles.add(Turtle(MARGIN_X + (g*210) + (i*46), y_r[3], 1.5*m, MARGIN_X, 640, group_offset=g*5.0))
        for i in range(3): self.logs.add(Log(MARGIN_X + (i*250), y_r[4], -2.2*m, MARGIN_X, 640, 120, 1))

    def spawn_frog(self):
       
        self.frog = Frog(self.start_x, self.start_y, MARGIN_X)
        self.all_sprites = pygame.sprite.Group(self.frog)
        self.max_y_reached = 14
        self.time_left = MAX_TIME 

    def update(self, dt):
        if self.state != "PLAYING": return
        
    
        if self.frog.state == "ALIVE":
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.handle_death()
                return

       
        if self.frog.is_finished:
            self.spawn_frog()

        self.all_sprites.update()
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles]:
            group.update()

        if self.trunk_snake and self.target_log:
            self.trunk_snake.rect.x = self.target_log.rect.x + (self.target_log.rect.width // 2 - 20)

        if self.frog.state == "ALIVE":
            for enemy in list(self.cars) + list(self.snakes):
                if self.frog.hitbox.colliderect(enemy.hitbox): 
                    self.handle_death(); return
            
            f_row = (self.frog.rect.y - OFFSET_Y) // TILE_SIZE
            if 1 <= f_row <= 5:
                on = False
                for l in self.logs:
                    if self.frog.hitbox.colliderect(l.hitbox): self.frog.rect.x += l.speed; on = True; break
                if not on:
                    for c in self.crocodiles:
                        if self.frog.hitbox.colliderect(c.hitbox):
                            head_x = c.rect.x if c.speed < 0 else c.rect.right - 40
                            head = pygame.Rect(head_x, c.rect.y, 40, 40)
                            if c.state == "OPEN" and self.frog.hitbox.colliderect(head): self.handle_death(); return
                            self.frog.rect.x += c.speed; on = True; break
                if not on:
                    for t in self.turtles:
                        if self.frog.hitbox.colliderect(t.hitbox):
                            if t.is_submerged: self.handle_death(); return
                            else: self.frog.rect.x += t.speed; on = True; break
                if not on: self.handle_death()

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if self.state == "START":
                if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN:
                    self.state = "PLAYING"
            
            elif self.state == "GAME_OVER":
                if e.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if BASE_WIDTH//2 - 100 < mx < BASE_WIDTH//2 + 100 and 350 < my < 400:
                        self.reset_game_logic()
                        self.state = "PLAYING"
                    if BASE_WIDTH//2 - 100 < mx < BASE_WIDTH//2 + 100 and 420 < my < 470:
                        pygame.quit(); sys.exit()

            elif self.state == "PLAYING":
                if e.type == pygame.KEYDOWN:
                    res = None
                    if e.key == pygame.K_UP: res = self.frog.move("UP", self.slots_rangos)
                    elif e.key == pygame.K_DOWN: res = self.frog.move("DOWN")
                    elif e.key == pygame.K_LEFT: res = self.frog.move("LEFT")
                    elif e.key == pygame.K_RIGHT: res = self.frog.move("RIGHT")
                    
                    if res is not None:
                        if not self.slots_ocupados[res]:
                            self.slots_ocupados[res] = True
                            self.score += 50 
                            if all(self.slots_ocupados): 
                                self.score += 1000; self.level += 1; self.lives = 5
                                self.slots_ocupados = [False]*5; self.reset_level_entities()
                            else: 
                                self.spawn_frog() 
                        else: self.frog.rect.y += TILE_SIZE 

    def handle_death(self):
        if self.frog.state == "ALIVE":
            self.lives -= 1
            if self.lives <= 0: self.state = "GAME_OVER"
            else: self.frog.die()

    def render(self, surface=None):
        if surface is None: surface = self.surface
        
        if self.state == "START":
            surface.fill((0, 0, 0))
            title = self.font_big.render("FROGGER", True, (0, 255, 0))
            instr = self.font_small.render("PULSA PARA ENTRAR", True, (255, 255, 255))
            surface.blit(title, (BASE_WIDTH//2 - title.get_width()//2, 200))
            surface.blit(instr, (BASE_WIDTH//2 - instr.get_width()//2, 350))
            
        elif self.state == "PLAYING":
            if self.background is None and os.path.exists(MAP_PATH): 
                self.background = pygame.image.load(MAP_PATH).convert()
            surface.blit(self.background or pygame.Surface((BASE_WIDTH, BASE_HEIGHT)), (0, 0))
            
            for group in [self.turtles, self.logs, self.crocodiles, self.snakes, self.cars, self.all_sprites]:
                group.draw(surface)
            
          
            pygame.draw.rect(surface, (255, 255, 255), (0, 0, MARGIN_X, BASE_HEIGHT))
            pygame.draw.rect(surface, (255, 255, 255), (MARGIN_X + 640, 0, MARGIN_X, BASE_HEIGHT))
            
           
            bar_x, bar_y = 10, 140
            pct = max(0, self.time_left / MAX_TIME)
            bar_color = (0, 200, 0) if pct > 0.3 else (220, 0, 0)
            
            surface.blit(self.font_small.render("TIEMPO:", True, (0, 0, 0)), (bar_x, bar_y - 25))
            pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, 120, 15)) 
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(120 * pct), 15)) 
            
            surface.blit(self.font_small.render(f"SCORE: {self.score}", True, (0, 0, 0)), (10, 20))
            surface.blit(self.font_small.render(f"LEVEL: {self.level}", True, (0, 0, 0)), (10, 50))
            surface.blit(self.font_small.render(f"LIVES: {self.lives}", True, (200, 0, 0)), (10, 80))

        elif self.state == "GAME_OVER":
            surface.fill((0, 0, 0))
            txt = self.font_big.render("GAME OVER", True, (255, 0, 0))
            surface.blit(txt, (BASE_WIDTH//2 - txt.get_width()//2, 150))