import pygame, math, random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, spaceship, health, score_val):
        self.image = pygame.image.load(spaceship).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.hp = health
        self.score = score_val

class Shooter(pygame.sprite.Sprite):
    def __init__(self, spaceship, cannon_pos_x, cannon_pos_y, health, score_val):
        super().__init__()
        self.image = pygame.image.load(spaceship).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(int(950 - self.image.get_width()/2))
        self.rect.bottom = random.randrange(-300, 0)
        self.pin_x = self.rect.x
        self.modify_cannon_x = cannon_pos_x
        self.modify_cannon_y = cannon_pos_y
        self.i = -1
        self.hp = health
        self.score = score_val
    def update(self):
        self.i += 1
        if self.movement_x == eval('lambda x, i: x + 5*math.cos(i/30)'):
            self.rect.x = int(self.movement_x(self.pin_x, self.i))
        else:
            self.rect.x = int(self.movement_x(self.rect.x, self.i))
        self.rect.y += 2
        self.cannon_x = self.rect.x + self.modify_cannon_x
        self.cannon_y = self.rect.y + self.modify_cannon_y

class Chaser(pygame.sprite.Sprite):
    def __init__(self, spaceship, target, speed, health, score_val):
        super().__init__()
        self.base_image = pygame.image.load(spaceship).convert_alpha()
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(950 - self.image.get_width()/2)
        self.rect.bottom = random.randrange(-300, 0)
        # Convert coordinate to float as rect is always converted to integer
        self.float_x = self.rect.x
        self.float_y = self.rect.y
        self.vector(target, speed)
        self.image = pygame.transform.rotozoom(self.image, math.atan2(self.vect[0], self.vect[1])*180/math.pi, 1)
        self.mask = pygame.mask.from_surface(self.image)
        self.hp = health
        self.score = score_val
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)
    def rotation(self, target):
        self.dx = target.rect.centerx - self.rect.centerx
        self.dy = target.rect.centery - self.rect.centery
        try:
            self.vect = list(pygame.math.Vector2(self.dx, self.dy).normalize()*8)
        # Can't normalize vector of magnitude zero
        except ValueError:
            pass
        self.image = pygame.transform.rotozoom(self.base_image, math.atan2(self.vect[0], self.vect[1])*180/math.pi, 1)
        self.mask = pygame.mask.from_surface(self.image)
    def vector(self, target, speed):
        self.dx = target.rect.centerx - self.rect.centerx
        self.dy = target.rect.centery - self.rect.centery
        self.vect = list(pygame.math.Vector2(self.dx, self.dy).normalize()*speed)
        self.mask = pygame.mask.from_surface(self.image)

class Collider(Chaser):
    def __init__(self, spaceship, target, speed, health, score_val):
        super().__init__(spaceship, target, speed, health, score_val)
        self.angle = 0
    def update(self):
        self.angle += 15
        self.rect.x += int(self.vect[0])
        self.rect.y += int(self.vect[1])
        self.image = pygame.transform.rotozoom(self.base_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

class Boss(pygame.sprite.Sprite):
    def __init__(self, spaceship, health, score_val):
        super().__init__()
        self.image = pygame.image.load(spaceship).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.centerx = 475
        self.rect.bottom = -50
        self.i = -1
        self.hp = health
        self.score = score_val
    def update(self):
        if self.rect.bottom != 250:
            self.rect.y += 4
