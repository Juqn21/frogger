import os
from arcade_machine_sdk import BASE_WIDTH, BASE_HEIGHT

# Directorios
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE_PATH, "assest", "images")

# Dimensiones
GAME_WIDTH = 640
MARGIN_X = (BASE_WIDTH - GAME_WIDTH) // 2
OFFSET_Y = 8
TILE_SIZE = 40

#Tiempo de vida de la rana
MAX_TIME = 30  #Segundos

# Rutas de Imágenes
MAP_PATH = os.path.join(IMG_DIR, "Map.png")
GOAL_PATH = os.path.join(IMG_DIR, "goal.png")
FROG_PATH = os.path.join(IMG_DIR, "frog.png")
DEATH_PATH = os.path.join(IMG_DIR, "FroggerMuerte.png")

# Rutas Adicionales
MENU_IMG_PATH = os.path.join(IMG_DIR, "menu.png")
FONT_PATH = os.path.join(BASE_PATH, "assest", "fonts")