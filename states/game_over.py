import pygame
from states.base import State
from arcade_machine_sdk import BASE_WIDTH

class GameOverState(State):
    def handle_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.game.change_state("START")

    def render(self, surface):
        surface.fill((0, 0, 0))
        txt = self.game.font_big.render("GAME OVER", False, (255, 0, 0))
        surface.blit(txt, (BASE_WIDTH//2 - txt.get_width()//2, 350))
        
        score_txt = self.game.font_ui.render(f"SCORE FINAL: {self.game.score}", False, (255, 255, 255))
        surface.blit(score_txt, (BASE_WIDTH//2 - score_txt.get_width()//2, 450))