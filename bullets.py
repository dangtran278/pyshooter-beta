import pygame, random

BLACK = (0, 0, 0)
DRED = (255, 36, 36)
LRED = (255, 102, 102)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, vect, damage, image, hit, hit_x, hit_y):
        super().__init__()
        self.vect = vect
        self.image = pygame.image.load(image).convert_alpha()
        '''self.image = pygame.transform.rotozoom(pygame.image.load(image).convert_alpha(), math.atan2(self.vect[0],self.vect[1]), 1)'''
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.damage = damage
        self.hit = hit
        self.hit_x = hit_x
        self.hit_y = hit_y
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, hit):
        super().__init__()
        self.image = pygame.Surface([12, 12])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.float_x = 0
        self.float_y = 0
        pygame.draw.circle(self.image, DRED, [self.rect.x + 6, self.rect.y + 6], 6, 0)
        pygame.draw.circle(self.image, LRED, [self.rect.x + 6, self.rect.y + 6], 4, 0)
        self.mask = pygame.mask.from_surface(self.image)
        self.hit = hit
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

class SpellBullet(PlayerBullet):
    def __init__(self, vect, damage, image, hit, hit_x, hit_y, record_time):
        super().__init__([0,-5], damage, image %(1), hit, hit_x, hit_y)
        self.animate_image = image
        self.image = pygame.image.load(self.animate_image %(1)).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(950 - self.image.get_width()/2)
        self.rect.top = random.randrange(850, 950)
        self.float_x = self.rect.x
        self.float_y = self.rect.y
        self.vect = vect
        self.time = record_time
    def update(self):
        super().update()
        self.i = int((pygame.time.get_ticks() - self.time)/30+1)
        if self.i < 20:
            self.image = pygame.image.load(self.animate_image %(self.i)).convert_alpha()
        else:
            self.image = pygame.image.load(self.animate_image %(self.i%20+20)).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
