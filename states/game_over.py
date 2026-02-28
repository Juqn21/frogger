import pygame
import os
from states.base import State
from constants import IMG_DIR
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

    def on_enter(self):
        if self.bg_image is None:
            bg_path = os.path.join(IMG_DIR, "FondoGameOver.png")
            if os.path.exists(bg_path):
                img = pygame.image.load(bg_path).convert()
                self.bg_image = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
            else:
                print(f"Advertencia: No se encontró el fondo {bg_path}")

        if not self.frames:
            for i in range(1, 8):
                path = os.path.join(IMG_DIR, f"gameover_{i}.png")
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    self.frames.append(img)
                else:
                    print(f"Advertencia: No se encontró la imagen {path}")
        
        self.index = 0
        self.selected_index = 0

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
                    selected = self.options[self.selected_index]
                    if selected == "RETRY":
                        self.game.change_state("PLAYING")
                    elif selected == "MENU":
                        self.game.change_state("START")

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((0, 0, 0)) 
        
        # --- 1. ANIMACIÓN DE GAME OVER ---
        if self.frames:
            current_frame = self.frames[int(self.index)]
            x = (BASE_WIDTH // 2) - (current_frame.get_width() // 2)
            y_anim = 10  # <--- GAME OVER EN 30 COMO ESTABA BIEN ANTES
            surface.blit(current_frame, (x, y_anim))
        else:
            txt = self.game.font_big.render("GAME OVER", False, (255, 0, 0))
            surface.blit(txt, (BASE_WIDTH // 2 - txt.get_width() // 2, 30))
        
        # --- 2. SCORE FINAL ---
        score_txt = self.game.font_ui.render(f"SCORE FINAL: {self.game.score}", False, (255, 255, 255))
        y_score = 350 # <--- LO BAJAMOS A 400 PARA QUE SALGA DEBAJO DE LA IMAGEN ANIMADA
        surface.blit(score_txt, (BASE_WIDTH // 2 - score_txt.get_width() // 2, y_score))

        # --- 3. OPCIONES (RETRY / MENU) ---
        start_y = 430 # <--- LAS OPCIONES EMPIEZAN AUN MÁS ABAJO
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