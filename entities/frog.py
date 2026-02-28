import pygame
import os
from constants import FROG_PATH, DEATH_PATH, TILE_SIZE

class Frog(pygame.sprite.Sprite):
    def __init__(self, x, y, margin):
        super().__init__()
        self.display_size = 36 
        self.frames, self.death_frames = {}, []
        self.state, self.direction, self.index = "ALIVE", "UP", 0
        self.anim_timer, self.death_index, self.death_speed = 0, 0, 0.15
        self.margin, self.step = margin, TILE_SIZE
        self.is_finished = False 
        self.image = pygame.Surface((self.display_size, self.display_size), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.start_pos = (x + 2, y + 2)
        self.rect.x, self.rect.y = self.start_pos
        self.hitbox = self.rect.inflate(-22, -22)

    def _prepare_frames(self):
        new_frames = {"UP": [], "DOWN": [], "LEFT": [], "RIGHT": []}
        if os.path.exists(FROG_PATH):
            sheet = pygame.image.load(FROG_PATH).convert_alpha()
            fw = sheet.get_width() // 8
            temp = [pygame.transform.scale(sheet.subsurface((i*fw, 0, fw, sheet.get_height())), (self.display_size, self.display_size)) for i in range(8)]
            new_frames["UP"], new_frames["DOWN"] = [temp[0], temp[1]], [temp[2], temp[3]]
            new_frames["LEFT"], new_frames["RIGHT"] = [temp[4], temp[5]], [temp[6], temp[7]]
        if os.path.exists(DEATH_PATH):
            d_sheet = pygame.image.load(DEATH_PATH).convert_alpha()
            dw = d_sheet.get_width() // 7
            for i in range(7):
                surf = d_sheet.subsurface((i*dw, 0, dw, d_sheet.get_height()))
                self.death_frames.append(pygame.transform.scale(surf, (self.display_size, self.display_size)))
        return new_frames

    def die(self):
        if self.state == "ALIVE":
            self.state = "DEAD"
            self.death_index = 0

    def update(self):
        if not self.frames: self.frames = self._prepare_frames()
        
        if self.state == "ALIVE":
            self.index = 1 if self.anim_timer > 0 else 0
            if self.anim_timer > 0: self.anim_timer -= 1
            if self.frames["UP"]: self.image = self.frames[self.direction][self.index]
            
        elif self.state == "DEAD":
            if self.death_frames:
                # --- AQUÍ ESTÁ EL SEGURO ANTI-CRASHEO ---
                safe_index = min(int(self.death_index), len(self.death_frames) - 1)
                self.image = self.death_frames[safe_index]
                
                self.death_index += self.death_speed
                if self.death_index >= len(self.death_frames): 
                    self.is_finished = True 
            else: 
                self.is_finished = True
                
        self.hitbox = self.rect.inflate(-22, -22)

    def move(self, direction, slots=None):
        if self.state != "ALIVE" or self.is_finished: return None
        self.direction, self.anim_timer = direction, 10
        if direction == "UP":
            if self.rect.y - self.step <= 12: 
                if slots:
                    for i, (s, e) in enumerate(slots):
                        if s <= self.rect.centerx <= e:
                            self.rect.centerx = (s + e) // 2
                            self.rect.y -= self.step
                            return i 
                    self.anim_timer = 0; return None
            if self.rect.top > 40: self.rect.y -= self.step
        elif direction == "DOWN" and self.rect.bottom < 740: self.rect.y += self.step
        elif direction == "LEFT" and self.rect.left - self.step >= self.margin: self.rect.x -= self.step
        elif direction == "RIGHT" and self.rect.right + self.step <= self.margin + 640: self.rect.x += self.step
        return None