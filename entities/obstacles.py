import pygame
import os
import random 
from constants import IMG_DIR, COIN_PATH, TILE_SIZE, MARGIN_X, OFFSET_Y, GAME_WIDTH

class Snake(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, margin_x, game_width):
        super().__init__()
        self.path = os.path.join(IMG_DIR, "Serpiente.png")
        self.frames = []
        self.image_size = (100, 25)
        self.image = pygame.Surface(self.image_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y + 8
        self.speed, self.margin_x, self.game_width = speed, margin_x, game_width
        self.index, self.anim_speed = 0, 0.15
        self.hitbox = self.rect.inflate(-10, -5)

    def _load_frames(self):
        if os.path.exists(self.path):
            sheet = pygame.image.load(self.path).convert_alpha()
            fw = sheet.get_width() // 3
            for i in range(3):
                surf = sheet.subsurface((i * fw, 0, fw, sheet.get_height()))
                self.frames.append(pygame.transform.scale(surf, self.image_size))

    def update(self):
        if not self.frames: self._load_frames()
        if self.frames:
            self.index += self.anim_speed
            if self.index >= len(self.frames): self.index = 0
            img = self.frames[int(self.index)]
            self.image = img if self.speed < 0 else pygame.transform.flip(img, True, False)
        self.rect.x += self.speed
        if self.rect.right > self.margin_x + self.game_width or self.rect.left < self.margin_x:
            self.speed *= -1 
        self.hitbox = self.rect.inflate(-10, -5)

class Crocodile(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, margin_x, game_width):
        super().__init__()
        self.path = os.path.join(IMG_DIR, "cocodrilo.png")
        self.frames = []
        self.image_size = (120, 40)
        self.image = pygame.Surface(self.image_size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.speed, self.margin_x, self.game_width = speed, margin_x, game_width
        self.timer, self.state, self.anim_speed = 0, "CLOSED", 0.02 
        self.hitbox = self.rect.inflate(-15, -10)

    def _load_frames(self):
        if os.path.exists(self.path):
            sheet = pygame.image.load(self.path).convert_alpha()
            fw = sheet.get_width() // 2
            for i in range(2):
                surf = sheet.subsurface((i * fw, 0, fw, sheet.get_height()))
                self.frames.append(pygame.transform.scale(surf, self.image_size))

    def update(self):
        if not self.frames: self._load_frames()
        self.timer += self.anim_delay if hasattr(self, 'anim_delay') else 0.02
        self.timer += 0.02
        if (int(self.timer) % 2) == 0:
            self.state, img = "CLOSED", self.frames[1] if self.frames else self.image
        else:
            self.state, img = "OPEN", self.frames[0] if self.frames else self.image
        
        self.image = img if self.speed > 0 else pygame.transform.flip(img, True, False)
        self.rect.x += self.speed
        
        ref_w = 180
        if self.speed > 0:
            if self.rect.left > self.margin_x + self.game_width:
                self.rect.right = self.margin_x - (ref_w - 120)
        else:
            if self.rect.right < self.margin_x:
                self.rect.left = self.margin_x + self.game_width + (ref_w - 120)
        self.hitbox = self.rect.inflate(-15, -10)

class Car(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, car_idx, margin_x, game_width, width=45):
        super().__init__()
        self.path = os.path.join(IMG_DIR, "cars.png")
        self.h = 32
        self.speed, self.margin_x, self.game_width, self.car_idx = speed, margin_x, game_width, car_idx
        self.image = pygame.Surface((width, self.h), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y + 4
        self.hitbox = self.rect.inflate(-4, -8)

    def update(self):
        if not hasattr(self, 'loaded'):
            if os.path.exists(self.path):
                sheet = pygame.image.load(self.path).convert_alpha()
                w_ind = sheet.get_width() // 4
                surf = sheet.subsurface((self.car_idx * w_ind, 0, w_ind, sheet.get_height()))
                self.image = pygame.transform.scale(surf, (self.rect.width, self.h))
                if self.speed < 0: self.image = pygame.transform.flip(self.image, True, False)
            self.loaded = True
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > self.margin_x + self.game_width: self.rect.right = self.margin_x
        elif self.speed < 0 and self.rect.right < self.margin_x: self.rect.left = self.margin_x + self.game_width
        self.hitbox = self.rect.inflate(-4, -8)

class Log(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, margin_x, game_width, width, log_type=1):
        super().__init__()
        self.img_path = os.path.join(IMG_DIR, f"log{log_type}.png")
        self.width = width
        self.image = pygame.Surface((width, 34), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y + 3
        self.speed, self.margin_x, self.game_width = speed, margin_x, game_width
        self.hitbox = self.rect.inflate(6, 0)

    def update(self):
        if not hasattr(self, 'loaded'):
            if os.path.exists(self.img_path):
                raw_img = pygame.image.load(self.img_path).convert_alpha()
                self.image = pygame.transform.scale(raw_img, (self.width, 34))
            self.loaded = True
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > self.margin_x + self.game_width: self.rect.right = self.margin_x
        elif self.speed < 0 and self.rect.right < self.margin_x: self.rect.left = self.margin_x + self.game_width
        self.hitbox = self.rect.inflate(6, 0)

class Turtle(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, margin_x, game_width, group_offset=0):
        super().__init__()
        self.path = os.path.join(IMG_DIR, "turtle.png")
        self.frames = []
        self.image = pygame.Surface((40, 32), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y + 4
        self.speed, self.margin_x, self.game_width = speed, margin_x, game_width
        self.timer, self.anim_delay = group_offset, 0.06
        self.is_submerged = False
        self.hitbox = self.rect.inflate(2, 0)
        self.empty_surface = pygame.Surface((40, 32), pygame.SRCALPHA)

    def _load_frames(self):
        if os.path.exists(self.path):
            sheet = pygame.image.load(self.path).convert_alpha()
            fw = sheet.get_width() // 9
            for i in range(9):
                surf = sheet.subsurface((i * fw, 0, fw, sheet.get_height()))
                self.frames.append(pygame.transform.scale(surf, (40, 32)))

    def update(self):
        if not self.frames: self._load_frames()
        self.timer += self.anim_delay
        cycle = self.timer % 18 
        if cycle < 5: 
            if self.frames: self.image = self.frames[int(cycle)]
            self.is_submerged = (int(cycle) == 4)
        elif cycle < 9: 
            self.is_submerged = True
            self.image = self.empty_surface 
        elif cycle < 13: 
            self.is_submerged = False
            if self.frames: self.image = self.frames[min(int(cycle)-9+5, 8)]
        else: 
            self.is_submerged = False
            if self.frames: self.image = self.frames[0]
        self.rect.x += self.speed
        if self.speed > 0 and self.rect.left > self.margin_x + self.game_width: self.rect.right = self.margin_x
        elif self.speed < 0 and self.rect.right < self.margin_x: self.rect.left = self.margin_x + self.game_width
        self.hitbox = self.rect.inflate(2, 0)


# --- MONEDA AUTÓNOMA (CADA UNA VIVE SUS PROPIOS 15 SEGUNDOS) ---
class Coin(pygame.sprite.Sprite):
    def __init__(self, platforms):
        super().__init__()
        self.size = 34  
        self.image_orig = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        if os.path.exists(COIN_PATH):
            img = pygame.image.load(COIN_PATH).convert_alpha()
            self.image_orig = pygame.transform.scale(img, (self.size, self.size))
        else:
            print(f"Advertencia: No se encontró {COIN_PATH}")
            
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.copy() 
        
        # Guarda el momento exacto en el que nació
        self.spawn_time = pygame.time.get_ticks()
        
        self.parent_platform = None
        self.offset_x = 0
        
        # Le decimos que se posicione ni bien nazca
        self._place_coin(platforms)

    def _place_coin(self, platforms):
        in_water = random.choice([True, False])
        
        if in_water and platforms:
            plat = random.choice(platforms)
            self.parent_platform = plat
            self.offset_x = (plat.rect.width - self.size) // 2
            self.rect.x = plat.rect.x + self.offset_x
            self.rect.y = plat.rect.y + (plat.rect.height - self.size) // 2
        else:
            self.parent_platform = None
            row = random.randint(6, 13)
            col = random.randint(0, 15)
            self.rect.x = MARGIN_X + (col * TILE_SIZE) + (TILE_SIZE - self.size) // 2
            self.rect.y = OFFSET_Y + (row * TILE_SIZE) + (TILE_SIZE - self.size) // 2
            
        self.hitbox = self.rect.copy()

    def update(self):
        # Si pasaron 15 segundos (15000 ms) desde que nació, se destruye sola
        if pygame.time.get_ticks() - self.spawn_time > 15000:
            self.kill()
            return

        # Si está montada en algo, se mueve con ese algo
        if self.parent_platform:
            self.rect.x = self.parent_platform.rect.x + self.offset_x
            self.hitbox = self.rect.copy()