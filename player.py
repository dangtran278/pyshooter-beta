import pygame

hitbox_dir = 'sprites/auxil/crimson_spaceship_hitbox.png'

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(hitbox_dir).convert_alpha()
        self.rect = self.image.get_rect()
        #self.real_image = pygame.image.load('crimson_spaceship.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = 10
        self.mp = 0
    def update(self):
        player_pos = pygame.mouse.get_pos()
        # Adjust image to its center
        self.rect.centerx = player_pos[0]
        self.rect.y = player_pos[1] - 48