import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Animation(pygame.sprite.Sprite):
    def __init__(self, animate_image, animate_x, animate_y, frame_time, record_time):
        super().__init__()
        self.image = pygame.Surface([0, 0])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = animate_x
        self.rect.y = animate_y
        self.animate_image = animate_image
        self.frame_time = frame_time
        self.time = record_time
    def update(self):
        try:
            self.image = pygame.image.load(self.animate_image %(int((pygame.time.get_ticks() - self.time)/self.frame_time+1))).convert_alpha()
        # Remove animation when effect is over
        except FileNotFoundError: # OR except pygame.error:
            all_sprites_list.remove(self)

class SpellCircle(Animation):
    def __init__(self, animate_image, animate_x, animate_y, frame_time, record_time):
        super().__init__(animate_image, animate_x, animate_y, frame_time, record_time)
    def update(self):
        player_pos = pygame.mouse.get_pos()
        self.rect.centerx = player_pos[0]-160
        self.rect.centery = player_pos[1]-164
        try:
            self.image = pygame.image.load(self.animate_image %(int((pygame.time.get_ticks() - self.time)/self.frame_time+1))).convert_alpha()
        # Remove animation when effect is over
        except FileNotFoundError: # OR except pygame.error: 
            lower_layer_list.remove(self)

class Fade(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((950, 750))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = 0
        self.rect.y = 0
        self.alpha = 0
        self.phase_over = False
    def update(self):
        self.image.set_alpha(self.alpha)
        if self.alpha < 300 and self.phase_over == False:
            self.alpha += 7
        else:
            self.alpha -= 7
        if self.alpha >= 300:
            self.image.set_alpha(self.alpha)
            pygame.time.delay(2000)
            self.phase_over = True
        if self.alpha == 0 and self.phase_over == True:
            upper_layer_list.remove(self)