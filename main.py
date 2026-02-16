import pygame
from engine import Game
from arcade_machine_sdk import GameMeta

if not pygame.get_init():
    pygame.init()

metadata = (GameMeta()
            .with_title("Frogger v0.9 Alpha")
            .with_description("Juego de rana ")
            .with_release_date("16/12/2025")
            .with_group_number(2)
            .add_tag("Plataforma")
            .add_author("Juan Fernandez")
            .add_author("Daniela Suniaga"))

game = Game(metadata)

if __name__ == "__main__":
    game.run_independently()