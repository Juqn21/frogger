import pygame
import os
import json  # <--- NUEVO IMPORT PARA GUARDAR DATOS
from arcade_machine_sdk import GameBase, GameMeta, BASE_WIDTH, BASE_HEIGHT
from constants import MAX_TIME, BASE_PATH
from states.menu import MenuState
from states.gameplay import GameplayState
from states.game_over import GameOverState
from states.options import OptionsState

class Game(GameBase):
    def __init__(self, metadata: GameMeta) -> None:
        super().__init__(metadata)
        pygame.font.init()
        
        font_path = os.path.join(BASE_PATH, "assest", "fonts", "pixelmix.ttf")
        if os.path.exists(font_path):
            self.font_ui = pygame.font.Font(font_path, 20)  
            self.font_menu = pygame.font.Font(font_path, 30) 
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
        
        # --- SISTEMA DE GUARDADO ---
        self.config_path = os.path.join(BASE_PATH, "config.json")
        
        self.volume = 1.0 
        self.controls = {
            "UP": pygame.K_UP,
            "DOWN": pygame.K_DOWN,
            "LEFT": pygame.K_LEFT,
            "RIGHT": pygame.K_RIGHT
        }
        
        # Cargamos los datos guardados antes de iniciar los estados
        self.load_config()
        
        self.states = {
            "START": MenuState(self),
            "PLAYING": GameplayState(self),
            "GAME_OVER": GameOverState(self),
            "OPTIONS": OptionsState(self) 
        }
        
        self.current_state = self.states["START"]
        if hasattr(self.current_state, "on_enter"):
            self.current_state.on_enter()

    # --- NUEVAS FUNCIONES DE GUARDADO ---
    def load_config(self):
        """Lee el archivo JSON y aplica los controles y volumen guardados."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    self.volume = data.get("volume", 1.0)
                    saved_controls = data.get("controls", {})
                    for key, val in saved_controls.items():
                        if key in self.controls:
                            self.controls[key] = val
            except Exception as e:
                print(f"Error cargando config: {e}")

    def save_config(self):
        """Escribe los controles y volumen actuales en el archivo JSON."""
        data = {
            "volume": self.volume,
            "controls": self.controls
        }
        try:
            with open(self.config_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error guardando config: {e}")
    # ------------------------------------

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
        txt_borde = self.font_ui.render(text, False, (0, 0, 0))
        offsets = [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]
        for ox, oy in offsets:
            surface.blit(txt_borde, (pos[0] + ox, pos[1] + oy))
        
        surface.blit(txt_borde, (pos[0] + 4, pos[1] + 4))
        txt_color = self.font_ui.render(text, False, color)
        surface.blit(txt_color, pos)