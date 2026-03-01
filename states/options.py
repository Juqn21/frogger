import pygame
import os
from states.base import State
from constants import OPTIONS_IMG_PATH, SELECT_SOUND_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

class OptionsState(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg = None
        self.options = ["MUSIC", "EFFECTS", "UP", "DOWN", "LEFT", "RIGHT", "BACK"]
        self.selected_index = 0
        self.waiting_for_key = False
        
        # --- VARIABLES DEL SONIDO ---
        self.select_sound = None
        self.last_play_time = 0

    def on_enter(self):
        if self.bg is None:
            if os.path.exists(OPTIONS_IMG_PATH):
                img = pygame.image.load(OPTIONS_IMG_PATH).convert()
                self.bg = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
            else:
                print("Warning: Options.png not found")
                
        # Cargar efecto de sonido
        if self.select_sound is None:
            if os.path.exists(SELECT_SOUND_PATH):
                self.select_sound = pygame.mixer.Sound(SELECT_SOUND_PATH)
            else:
                print(f"Advertencia: No se encontró {SELECT_SOUND_PATH}")

    # --- FUNCIÓN DE SONIDO CON DELAY (COOLDOWN) ---
    def play_select_sound(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_play_time > 150:
            if self.select_sound:
                self.select_sound.set_volume(self.game.sfx_volume * 0.15) 
                self.select_sound.play()
            self.last_play_time = current_time

    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                if self.waiting_for_key:
                    action = self.options[self.selected_index]
                    self.game.controls[action] = e.key
                    self.game.save_config() 
                    self.waiting_for_key = False
                    self.play_select_sound() # Suena al guardar la tecla
                    return

                if e.key == pygame.K_UP:
                    self.selected_index -= 1
                    if self.selected_index < 0: self.selected_index = len(self.options) - 1
                    self.play_select_sound()
                elif e.key == pygame.K_DOWN:
                    self.selected_index += 1
                    if self.selected_index >= len(self.options): self.selected_index = 0
                    self.play_select_sound()

                elif self.options[self.selected_index] == "MUSIC":
                    if e.key == pygame.K_LEFT:
                        self.game.volume = max(0.0, self.game.volume - 0.1)
                        self.game.save_config() 
                        pygame.mixer.music.set_volume(self.game.volume * 0.2) 
                        self.play_select_sound()
                    elif e.key == pygame.K_RIGHT:
                        self.game.volume = min(1.0, self.game.volume + 0.1)
                        self.game.save_config() 
                        pygame.mixer.music.set_volume(self.game.volume * 0.2) 
                        self.play_select_sound()
                        
                elif self.options[self.selected_index] == "EFFECTS":
                    if e.key == pygame.K_LEFT:
                        self.game.sfx_volume = max(0.0, self.game.sfx_volume - 0.1)
                        self.game.save_config() 
                        self.play_select_sound()
                    elif e.key == pygame.K_RIGHT:
                        self.game.sfx_volume = min(1.0, self.game.sfx_volume + 0.1)
                        self.game.save_config() 
                        self.play_select_sound()

                elif e.key == pygame.K_RETURN:
                    self.play_select_sound()
                    selected = self.options[self.selected_index]
                    if selected == "BACK":
                        self.game.change_state("START")
                    elif selected in ["UP", "DOWN", "LEFT", "RIGHT"]:
                        self.waiting_for_key = True

    def render(self, surface):
        if self.bg: surface.blit(self.bg, (0, 0))
        else: surface.fill((0, 0, 0))

        start_y = 170 
        spacing = 58  

        for i, opt in enumerate(self.options):
            if opt == "MUSIC":
                vol_pct = int(self.game.volume * 100)
                if i == self.selected_index: text_str = f"> MUSIC: < {vol_pct}% > <"
                else: text_str = f"MUSIC: {vol_pct}%"
            elif opt == "EFFECTS":
                vol_pct = int(self.game.sfx_volume * 100)
                if i == self.selected_index: text_str = f"> EFFECTS: < {vol_pct}% > <"
                else: text_str = f"EFFECTS: {vol_pct}%"
            elif opt == "BACK":
                text_str = "> RETURN <" if i == self.selected_index else "RETURN"
            else:
                key_name = pygame.key.name(self.game.controls[opt]).upper()
                if i == self.selected_index:
                    if self.waiting_for_key: text_str = f"{opt}: [ PRESS NEW KEY ]"
                    else: text_str = f">{opt}: {key_name}<"
                else:
                    text_str = f"{opt}: {key_name}"

            color = (125, 33, 129) if i == self.selected_index else (255, 255, 255)
            if self.waiting_for_key and i == self.selected_index: color = (255, 255, 0) 

            txt_borde = self.game.font_menu.render(text_str, False, (0, 0, 0))
            txt_color = self.game.font_menu.render(text_str, False, color)

            x = (BASE_WIDTH // 2) - (txt_color.get_width() // 2)
            y = start_y + (i * spacing)

            surface.blit(txt_borde, (x + 3, y + 3))
            surface.blit(txt_color, (x, y))