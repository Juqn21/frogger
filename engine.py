import pygame
import sys
import random
import os
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT
from constants import MARGIN_X, OFFSET_Y, TILE_SIZE, MAP_PATH, GOAL_PATH, MAX_TIME, BASE_PATH
from entities.frog import Frog
from entities.obstacles import Car, Log, Turtle, Snake, Crocodile

class Game(GameBase):
    def __init__(self, metadata: GameMeta) -> None:
        super().__init__(metadata)
        pygame.font.init()
        
        # --- CARGA DE FUENTE RETRO ---
        # Asumiendo la ruta assest/fonts/retropix.ttf según me indicaste
        font_path = os.path.join(BASE_PATH, "assest", "fonts", "retropix.ttf")
        if os.path.exists(font_path):
            self.font_ui = pygame.font.Font(font_path, 22)
            self.font_big = pygame.font.Font(font_path, 50)
        else:
            # Fallback en caso de que la ruta no coincida
            self.font_ui = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_big = pygame.font.SysFont("Arial", 50, bold=True)
        
        self.state = "START"
        self.lives = 5
        self.level = 1
        self.score = 0
        self.time_left = MAX_TIME
        self.difficulty_multiplier = 1.0
        self.god_mode = False 
        
        self.background = None
        self.goal_image = None
        
        # Configuración de slots y posición inicial
        self.slots_rangos = [(MARGIN_X + 59 + (i*120), MARGIN_X + 99 + (i*120)) for i in range(5)]
        self.slots_ocupados = [False] * 5
        self.start_x = MARGIN_X + 300
        self.start_y = OFFSET_Y + (14 * TILE_SIZE)
        
        # Grupos de sprites
        self.cars, self.logs, self.turtles, self.snakes, self.crocodiles = [pygame.sprite.Group() for _ in range(5)]
        
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
        self._setup_entities()
        self.spawn_frog()

    def _setup_entities(self):
        m = self.difficulty_multiplier
        # Tráfico
        traffic = [(7, -2.2*m, 0, 45, [100, 350, 550]), (8, 1.6*m, 1, 40, [50, 400]), 
                   (9, -1.8*m, 2, 40, [150, 210, 270]), (10, 1.3*m, 3, 55, [0, 350]), 
                   (11, -1.5*m, 1, 40, [0, 160, 320, 480]), (12, 1.9*m, 2, 40, [20, 280, 520])]
        for r, s, idx, w, pos in traffic:
            y = OFFSET_Y + (r * TILE_SIZE)
            for px in pos: self.cars.add(Car(MARGIN_X + px, y, s, idx, MARGIN_X, 640, w))
        
        # Troncos y Tortugas
        y_r = [OFFSET_Y + (i * TILE_SIZE) for i in range(5, 0, -1)]
        for i in range(4): self.logs.add(Log(MARGIN_X + (i*160), y_r[0], -1.2*m, MARGIN_X, 640, 95, 2))
        for g in range(3): 
            for i in range(2): self.turtles.add(Turtle(MARGIN_X + (g*220) + (i*46), y_r[1], 2.0*m, MARGIN_X, 640, group_offset=g*6.0))
        
        # Cocodrilos y troncos fila 3
        pos_f3 = [0, 220, 440]
        c_idx = random.randint(0, 2) if self.level >= 2 else -1
        for i, px in enumerate(pos_f3):
            if i == c_idx: self.crocodiles.add(Crocodile(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, 640))
            else: self.logs.add(Log(MARGIN_X + px, y_r[2], -1.8*m, MARGIN_X, 640, 180, 3))

        for g in range(3): 
            for i in range(3): self.turtles.add(Turtle(MARGIN_X + (g*210) + (i*46), y_r[3], 1.5*m, MARGIN_X, 640, group_offset=g*5.0))
        for i in range(3): self.logs.add(Log(MARGIN_X + (i*250), y_r[4], -2.2*m, MARGIN_X, 640, 120, 1))

        # Serpientes según nivel
        if self.level >= 2:
            self.snakes.add(Snake(MARGIN_X + 100, OFFSET_Y + (6 * TILE_SIZE), 2.0*m, MARGIN_X, 640))
        if self.level >= 3:
            self.snakes.add(Snake(MARGIN_X + 400, OFFSET_Y + (13 * TILE_SIZE), 2.0*m, MARGIN_X, 640))

    def spawn_frog(self):
        self.frog = Frog(self.start_x, self.start_y, MARGIN_X)
        self.all_sprites = pygame.sprite.Group(self.frog)
        self.time_left = MAX_TIME

    def update(self, dt):
        if self.state != "PLAYING": return
        
        if self.frog.state == "ALIVE":
            if not self.god_mode:
                self.time_left -= dt
                if self.time_left <= 0:
                    self.handle_death()
                    return
            
            # Colisiones con enemigos
            if not self.god_mode:
                for enemy in list(self.cars) + list(self.snakes):
                    if self.frog.hitbox.colliderect(enemy.hitbox): 
                        self.handle_death(); return
            
            # Lógica del río
            f_row = (self.frog.rect.y - OFFSET_Y) // TILE_SIZE
            if 1 <= f_row <= 5:
                on = False
                for l in self.logs:
                    if self.frog.hitbox.colliderect(l.hitbox): self.frog.rect.x += l.speed; on = True; break
                if not on:
                    for c in self.crocodiles:
                        if self.frog.hitbox.colliderect(c.hitbox):
                            if not self.god_mode:
                                h_x = c.rect.x if c.speed < 0 else c.rect.right - 40
                                head = pygame.Rect(h_x, c.rect.y, 40, 40)
                                if c.state == "OPEN" and self.frog.hitbox.colliderect(head): self.handle_death(); return
                            self.frog.rect.x += c.speed; on = True; break
                if not on:
                    for t in self.turtles:
                        if self.frog.hitbox.colliderect(t.hitbox):
                            if t.is_submerged and not self.god_mode: self.handle_death(); return
                            else: self.frog.rect.x += t.speed; on = True; break
                if not on and not self.god_mode: self.handle_death()

        if self.frog.is_finished:
            self.spawn_frog()

        self.all_sprites.update()
        for group in [self.cars, self.logs, self.turtles, self.snakes, self.crocodiles]:
            group.update()

        for s in self.snakes:
            if s.rect.left <= MARGIN_X: s.speed = abs(s.speed)
            elif s.rect.right >= MARGIN_X + 640: s.speed = -abs(s.speed)

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_g: self.god_mode = not self.god_mode
                if self.state == "START": self.state = "PLAYING"
                elif self.state == "PLAYING":
                    res = self.frog.move("UP", self.slots_rangos) if e.key == pygame.K_UP else \
                          self.frog.move("DOWN") if e.key == pygame.K_DOWN else \
                          self.frog.move("LEFT") if e.key == pygame.K_LEFT else \
                          self.frog.move("RIGHT") if e.key == pygame.K_RIGHT else None
                    
                    if res is not None:
                        if not self.slots_ocupados[res]:
                            self.slots_ocupados[res] = True
                            self.score += 50 
                            if all(self.slots_ocupados): 
                                self.score += 1000; self.level += 1; self.lives = 5
                                self.difficulty_multiplier += 0.15 
                                self.slots_ocupados = [False]*5; self.reset_level_entities()
                            else: self.spawn_frog()
                        else: self.frog.rect.y += TILE_SIZE 

    def handle_death(self):
        if self.frog.state == "ALIVE":
            self.lives -= 1
            if self.lives <= 0: self.state = "GAME_OVER"
            else: self.frog.die()

    def render(self, surface=None):
        if surface is None: surface = self.surface
        surface.fill((0, 0, 0))
        
        if self.state == "START":
            txt = self.font_big.render("PULSA TECLA", True, (0, 255, 0))
            surface.blit(txt, (BASE_WIDTH//2-txt.get_width()//2, 350))
        elif self.state == "PLAYING":
            if not self.background: self.background = pygame.image.load(MAP_PATH).convert()
            if not self.goal_image: self.goal_image = pygame.transform.scale(pygame.image.load(GOAL_PATH).convert_alpha(), (34, 34))
            
            # 1. Dibuja el Mapa Completo
            surface.blit(self.background, (0, 0))
            
            # 2. Recorte de Sprites (Clip) para que no se vean fuera de los 640px
            clip_rect = pygame.Rect(MARGIN_X, 0, 640, BASE_HEIGHT)
            surface.set_clip(clip_rect)
            
            if self.goal_image:
                for i, oc in enumerate(self.slots_ocupados):
                    if oc:
                        x_p = (self.slots_rangos[i][0] + self.slots_rangos[i][1]) // 2 - 17
                        surface.blit(self.goal_image, (x_p, OFFSET_Y + 3))
            
            for gp in [self.turtles, self.logs, self.crocodiles, self.snakes, self.cars, self.all_sprites]:
                gp.draw(surface)
            
            surface.set_clip(None) # Quita el recorte para la UI
            
            # 3. Dibujar UI sobre el Mapa
            # Ajusta estas posiciones (X, Y) para que queden sobre tus textos del mapa
            self._draw_text_with_shadow(surface, f"SCORE: {self.score:05d}", (MARGIN_X + 20, 20))
            self._draw_text_with_shadow(surface, f"LEVEL: {self.level}", (MARGIN_X + 500, 20))
            self._draw_text_with_shadow(surface, f"LIVES: {self.lives}", (MARGIN_X + 260, 755), (255, 50, 50))
            
            if self.god_mode:
                self._draw_text_with_shadow(surface, "GOD MODE", (10, 200), (255, 140, 0))

        elif self.state == "GAME_OVER":
            txt = self.font_big.render("GAME OVER", True, (255, 0, 0))
            surface.blit(txt, (BASE_WIDTH//2-txt.get_width()//2, 350))

    def _draw_text_with_shadow(self, surface, text, pos, color=(255, 255, 255)):
        shadow = self.font_ui.render(text, True, (0, 0, 0))
        txt = self.font_ui.render(text, True, color)
        surface.blit(shadow, (pos[0]+2, pos[1]+2))
        surface.blit(txt, pos)