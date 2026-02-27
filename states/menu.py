import pygame
import sys
from states.base import State
from constants import MENU_IMG_PATH
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg = None
        self.options = ["START", "OPTIONS", "EXIT"]
        self.selected_index = 0

    def on_enter(self):
        if self.bg is None:
            try:
                img = pygame.image.load(MENU_IMG_PATH)
                self.bg = pygame.transform.scale(img, (BASE_WIDTH, BASE_HEIGHT))
            except Exception as e:
                print(f"Error cargando menu.png: {e}")

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
                    if selected == "START":
                        self.game.change_state("PLAYING")
                    elif selected == "OPTIONS":
                        print("Menú de opciones en construcción...") 
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