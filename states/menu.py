import pygame
import sys
import os
from states.base import State
from constants import MENU_IMG_PATH, MENU_MUSIC_PATH, SELECT_SOUND_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg = None
        self.options = ["START", "OPTIONS", "EXIT"]
        self.selected_index = 0
        
        # --- VARIABLES DEL SONIDO DE MENÚ ---
        self.select_sound = None
        self.last_play_time = 0

    def on_enter(self):
        if self.bg is None:
            try:
                img = pygame.image.load(MENU_IMG_PATH)
                self.bg = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
            except Exception as e:
                print(f"Error cargando menu.png: {e}")

        # Cargar efecto de sonido
        if self.select_sound is None:
            if os.path.exists(SELECT_SOUND_PATH):
                self.select_sound = pygame.mixer.Sound(SELECT_SOUND_PATH)
            else:
                print(f"Advertencia: No se encontró {SELECT_SOUND_PATH}")

        if os.path.exists(MENU_MUSIC_PATH):
            if not pygame.mixer.music.get_busy(): 
                pygame.mixer.music.load(MENU_MUSIC_PATH)
                pygame.mixer.music.set_volume(self.game.volume * 0.2) 
                pygame.mixer.music.play(-1) 
        else:
            print(f"Advertencia: No se encontró {MENU_MUSIC_PATH}")

    # --- FUNCIÓN DE SONIDO CON DELAY (COOLDOWN) ---
    def play_select_sound(self):
        current_time = pygame.time.get_ticks()
        # Solo suena si han pasado más de 150 milisegundos desde la última vez
        if current_time - self.last_play_time > 150:
            if self.select_sound:
                # Usa el volumen de efectos nerfeado al 15% por ser MP3
                self.select_sound.set_volume(self.game.sfx_volume * 0.15) 
                self.select_sound.play()
            self.last_play_time = current_time

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.selected_index -= 1
                    if self.selected_index < 0:
                        self.selected_index = len(self.options) - 1
                    self.play_select_sound() # Suena al mover
                    
                elif e.key == pygame.K_DOWN:
                    self.selected_index += 1
                    if self.selected_index >= len(self.options):
                        self.selected_index = 0
                    self.play_select_sound() # Suena al mover
                    
                elif e.key == pygame.K_RETURN:
                    self.play_select_sound() # Suena al seleccionar
                    selected = self.options[self.selected_index]
                    if selected == "START":
                        pygame.mixer.music.stop() 
                        self.game.change_state("PLAYING")
                    elif selected == "OPTIONS":
                        self.game.change_state("OPTIONS") 
                    elif selected == "EXIT":
                        pygame.quit()
                        sys.exit()

    def render(self, surface):
        if self.bg:
            surface.blit(self.bg, (0, 0))
        else:
            surface.fill((0, 0, 0))
            
        start_y = 350 
        spacing = 62

        for i, option in enumerate(self.options):
            if i == self.selected_index:
                text_str = f">{option}<"
                color = (125, 33, 129)
            else:
                text_str = option
                color = (255, 255, 255)

            txt_borde = self.game.font_menu.render(text_str, False, (0, 0, 0))
            txt_color = self.game.font_menu.render(text_str, False, color)
            
            x = (BASE_WIDTH // 2) - (txt_color.get_width() // 2)
            y = start_y + (i * spacing)
            
            surface.blit(txt_borde, (x + 3, y + 3))
            surface.blit(txt_color, (x, y))