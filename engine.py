import pygame
import os
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT
from constants import MAX_TIME, BASE_PATH
from states.menu import MenuState
from states.gameplay import GameplayState
from states.game_over import GameOverState

class Game(GameBase):
    def __init__(self, metadata: GameMeta) -> None:
        super().__init__(metadata)
        pygame.font.init()
        
        # --- CONFIGURACIÓN DE FUENTES ---
        font_path = os.path.join(BASE_PATH, "assest", "fonts", "pixelmix.ttf")
        if os.path.exists(font_path):
            self.font_ui = pygame.font.Font(font_path, 20)  
            self.font_menu = pygame.font.Font(font_path, 30) # Fuente para el menú
            self.font_big = pygame.font.Font(font_path, 40) 
        else:
            self.font_ui = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_menu = pygame.font.SysFont("Arial", 30, bold=True)
            self.font_big = pygame.font.SysFont("Arial", 40, bold=True)
        
        self.lives = 5
        self.level = 1
        self.score = 0
        self.time_left = MAX_TIME
        self.difficulty_multiplier = 1.0
        self.god_mode = False 
        self.slots_ocupados = [False] * 5
        
        # Sistema de Estados
        self.states = {
            "START": MenuState(self),
            "PLAYING": GameplayState(self),
            "GAME_OVER": GameOverState(self)
        }
        
        # Iniciar estado
        self.current_state = self.states["START"]
        if hasattr(self.current_state, "on_enter"):
            self.current_state.on_enter()

    def _add_score(self, points):
        old_score = self.score
        self.score += points
        if (self.score // 5000) > (old_score // 5000):
            self.lives += (self.score // 5000) - (old_score // 5000)

    def change_state(self, state_name):
        if state_name == "START" or (state_name == "PLAYING" and self.lives <= 0):
            self.lives = 5
            self.level = 1
            self.score = 0
            self.difficulty_multiplier = 1.0
            self.slots_ocupados = [False] * 5
            
        self.current_state = self.states[state_name]
        if hasattr(self.current_state, "on_enter"):
            self.current_state.on_enter()

    def update(self, dt):
        self.current_state.update(dt)

    def handle_events(self, events):
        self.current_state.handle_events(events)

    def render(self, surface=None):
        if surface is None: surface = self.surface
        self.current_state.render(surface)

    def _draw_text_with_shadow(self, surface, text, pos, color=(255, 255, 255)):
        # OPTIMIZACIÓN DE FPS: Se renderiza la fuente negra una sola vez y se copia
        txt_borde = self.font_ui.render(text, False, (0, 0, 0))
        
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
        for ox, oy in offsets:
            surface.blit(txt_borde, (pos[0] + ox, pos[1] + oy))
        
        surface.blit(txt_borde, (pos[0] + 4, pos[1] + 4))
        
        txt_color = self.font_ui.render(text, False, color)
        surface.blit(txt_color, pos)