import pygame
import os
import math
import sys
from states.base import State
from constants import MENU_IMG_PATH, MENU_MUSIC_PATH, SELECT_SOUND_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.options = ["PLAY", "OPTIONS", "EXIT"]
        self.selected_index = 0
        self.bg_image = None
        self.select_sound = None

    def on_enter(self):
        self.selected_index = 0
        if os.path.exists(MENU_IMG_PATH):
            img = pygame.image.load(MENU_IMG_PATH) # <-- Sin el .convert() para que no crashee
            self.bg_image = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
        
        if os.path.exists(SELECT_SOUND_PATH):
            self.select_sound = pygame.mixer.Sound(SELECT_SOUND_PATH)
            
        if os.path.exists(MENU_MUSIC_PATH):
            pygame.mixer.music.load(MENU_MUSIC_PATH)
            pygame.mixer.music.set_volume(self.game.volume * 0.2)
            pygame.mixer.music.play(-1)

    def update(self, dt):
        pass

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == self.game.controls["UP"]:
                    self.selected_index -= 1
                    if self.selected_index < 0:
                        self.selected_index = len(self.options) - 1
                    if self.select_sound:
                        self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                        self.select_sound.play()
                elif e.key == self.game.controls["DOWN"]:
                    self.selected_index += 1
                    if self.selected_index >= len(self.options):
                        self.selected_index = 0
                    if self.select_sound:
                        self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                        self.select_sound.play()
                elif e.key == pygame.K_RETURN:
                    if self.select_sound:
                        self.select_sound.set_volume(self.game.sfx_volume * 0.15)
                        self.select_sound.play()
                        
                    selected = self.options[self.selected_index]
                    if selected == "PLAY" or selected == "START":
                        self.game.change_state("PLAYING")
                    elif selected == "OPTIONS":
                        self.game.change_state("OPTIONS") 
                    elif selected == "EXIT":
                        self.game.stop()

    def render(self, surface):
        if self.bg_image:
            surface.blit(self.bg_image, (0, 0))
        else:
            surface.fill((0, 0, 0))
            
        # =================================================================
        # ¡AQUÍ! CAMBIA ESTOS NÚMEROS POR LOS QUE TENÍAS EN TU VERSIÓN ORIGINAL
        start_y = 350    # <-- Coordenada Y (arriba/abajo) donde empieza la primera opción
        spacing = 62    # <-- Espacio en píxeles que hay entre "PLAY", "OPTIONS" y "EXIT"
        # =================================================================
        
        for i, opt in enumerate(self.options):
            if i == self.selected_index:
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

        # --- TEXTO DE INSTRUCCIONES EN LA PARTE INFERIOR (INTACTO) ---
        instrucciones = "USE ARROW KEYS TO NAVIGATE  -  PRESS ENTER TO SELECT"
        
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        color_inst = (int(100 + 155 * pulse), int(100 + 155 * pulse), int(100 + 155 * pulse)) 
        
        txt_borde_inst = self.game.font_ui.render(instrucciones, False, (0, 0, 0))
        txt_color_inst = self.game.font_ui.render(instrucciones, False, color_inst)
        
        x_inst = (BASE_WIDTH // 2) - (txt_color_inst.get_width() // 2)
        y_inst = BASE_HEIGHT - 40  
        
        surface.blit(txt_borde_inst, (x_inst + 2, y_inst + 2))
        surface.blit(txt_color_inst, (x_inst, y_inst))