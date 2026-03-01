import pygame
import os
import math
import json  # <--- IMPORTANTE: Para leer y escribir el archivo
from states.base import State
from constants import IMG_DIR, GAME_OVER_SOUND_PATH, BASE_PATH # <--- Traemos BASE_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

class GameOverState(State):
    def __init__(self, game):
        super().__init__(game)
        self.frames = []
        self.index = 0
        self.anim_speed = 0.15
        self.bg_image = None  
        
        self.options = ["RETRY", "MENU"]
        self.selected_index = 0
        
        self.is_new_record = False

    def on_enter(self):
        if self.bg_image is None:
            bg_path = os.path.join(IMG_DIR, "FondoGameOver.png")
            if os.path.exists(bg_path):
                img = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
            else:
                print(f"Advertencia: No se encontro el fondo {bg_path}")

        if not self.frames:
            for i in range(1, 8):
                path = os.path.join(IMG_DIR, f"gameover_{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.frames.append(img)
                else:
                    print(f"Advertencia: No se encontro la imagen {path}")
        
        self.index = 0
        self.selected_index = 0
        self.is_new_record = False

        # --- LOGICA DIRECTA AL ARCHIVO JSON ---
        config_path = os.path.join(BASE_PATH, "config.json")
        config_data = {}

        # 1. Leer el JSON actual para saber cual es el record
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    config_data = json.load(f)
            except Exception as e:
                print(f"Error leyendo el config.json: {e}")

        # 2. Asignar el high_score (si no existe en el json, sera 0)
        self.game.high_score = config_data.get("high_score", 0)

        # 3. Comprobar si superaste el record
        if self.game.score > self.game.high_score and self.game.score > 0:
            self.game.high_score = self.game.score
            self.is_new_record = True
            
            # 4. Actualizar el diccionario y GUARDAR a la fuerza en el JSON
            config_data["high_score"] = self.game.high_score
            try:
                with open(config_path, "w") as f:
                    json.dump(config_data, f, indent=4)
                print("¡Record guardado en config.json!")
            except Exception as e:
                print(f"Error escribiendo en el config.json: {e}")

        # ----------------------------------------

        if os.path.exists(GAME_OVER_SOUND_PATH):
            pygame.mixer.music.load(GAME_OVER_SOUND_PATH)
            pygame.mixer.music.set_volume(self.game.volume * 0.2) 
            pygame.mixer.music.play(0) 

    def update(self, dt):
        if self.frames:
            self.index += self.anim_speed
            if self.index >= len(self.frames):
                self.index = 0

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.selected_index -= 1
                    if self.selected_index < 0:
                        self.selected_index = len(self.options) - 1
                elif e.key == pygame.K_DOWN:
                    self.selected_index += 1
                    if self.selected_index >= len(self.options):
                        self.selected_index = 0
                        
                elif e.key == pygame.K_RETURN:
                    pygame.mixer.music.stop() 
                    selected = self.options[self.selected_index]
                    if selected == "RETRY":
                        self.game.lives = 5
                        self.game.level = 1
                        self.game.score = 0
                        self.game.difficulty_multiplier = 1.0
                        self.game.slots_ocupados = [False] * 5
                        self.game.change_state("PLAYING")
                    elif selected == "MENU":
                        self.game.change_state("START")

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((0, 0, 0)) 
        
        # 1. Animacion de Game Over
        if self.frames:
            current_frame = self.frames[int(self.index)]
            x = (BASE_WIDTH // 2) - (current_frame.get_width() // 2)
            y_anim = 5  
            surface.blit(current_frame, (x, y_anim))
        else:
            txt = self.game.font_big.render("GAME OVER", False, (255, 0, 0))
            surface.blit(txt, (BASE_WIDTH // 2 - txt.get_width() // 2, 30))
            
        # 2. Letrero de NEW RECORD
        if self.is_new_record:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            color_nr = (255, int(215 * pulse) + 40, 0) 
            
            nr_txt = self.game.font_ui.render("NEW RECORD!", False, color_nr)
            nr_bg = self.game.font_ui.render("NEW RECORD!", False, (0, 0, 0))
            x_nr = BASE_WIDTH // 2 - nr_txt.get_width() // 2
            y_nr = 325 
            
            surface.blit(nr_bg, (x_nr + 2, y_nr + 2))
            surface.blit(nr_txt, (x_nr, y_nr))
        
        # 3. Score Final y High Score
        y_score = 360 
        y_high = 395  
        
        score_txt = self.game.font_ui.render(f"SCORE FINAL: {self.game.score}", False, (255, 255, 255))
        score_bg = self.game.font_ui.render(f"SCORE FINAL: {self.game.score}", False, (0, 0, 0))
        x_score = BASE_WIDTH // 2 - score_txt.get_width() // 2
        surface.blit(score_bg, (x_score + 2, y_score + 2))
        surface.blit(score_txt, (x_score, y_score))
        
        high_txt = self.game.font_ui.render(f"HIGH SCORE: {self.game.high_score}", False, (0, 255, 255))
        high_bg = self.game.font_ui.render(f"HIGH SCORE: {self.game.high_score}", False, (0, 0, 0))
        x_high = BASE_WIDTH // 2 - high_txt.get_width() // 2
        surface.blit(high_bg, (x_high + 2, y_high + 2))
        surface.blit(high_txt, (x_high, y_high))

        # 4. Opciones (RETRY / MENU)
        start_y = 460 
        spacing = 62

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                text_str = f"{option}"
                color = (125, 33, 129)
            else:
                text_str = option
                color = (255, 255, 255)

            txt_borde = self.game.font_menu.render(text_str, False, (0, 0, 0))
            txt_color = self.game.font_menu.render(text_str, False, color)
            
            x = (BASE_WIDTH // 2) - (txt_color.get_width() // 2)
            y_opcion = start_y + (i * spacing)
            
            surface.blit(txt_borde, (x + 3, y_opcion + 3))
            surface.blit(txt_color, (x, y_opcion))