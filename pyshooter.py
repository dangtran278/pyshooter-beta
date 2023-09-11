import pygame, math, random

from player import Player
from enemies import *
from bullets import *

# Define some colors as global constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SLATEGRAY = (112, 128, 144)
DGRAY = (169, 169, 169)
RED = (255, 0, 0)
LSKY = (130, 202, 250)


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


def main():
    """ Main function for the game."""
    pygame.init()

    # Set the width and height of the screen [width,height]
    screen_width = 950
    screen_height = 750
    screen = pygame.display.set_mode([screen_width, screen_height])

    pygame.display.set_caption('Pyshooter')

    # --- Constants
    global hit_sound, explode_sound
    songs = ['sound/bgm/scifi_drama.ogg']
    hit_sound = pygame.mixer.Sound('sound/sfx/hit.ogg')
    explode_sound = pygame.mixer.Sound('sound/sfx/explosion.ogg')
    casting_sound = pygame.mixer.Sound('sound/sfx/spell_tinkle.ogg')
    background_image = pygame.image.load('sprites/bg/normal_sky.jpg').convert()
    player_image = pygame.image.load('sprites/ships/crimson_spaceship.png').convert_alpha()
    player_wings = pygame.image.load("sprites/fx/wings5.png").convert_alpha()
    x_equations = [eval('lambda x, i: x'), eval('lambda x, i: x + 5*math.cos(i/30)')]
    boss_moves = [[7.25, 10.25, 2500], [79.75, 13, 3500], [7.88, 5, 3500], [math.radians(15), 9.5, 3000], [7.75, 7.5, 3500], [5.12, 6, 3000]]

    # --- Variables
    current_song = random.choice(songs)
    shooter_spawn_time = 3000
    collider_spawn_time = 6000
    collider_num = 1
    boss_spawned = False
    rec_time = 0
    radvec = [0, 0, 0]
    mp_release = False
    background_y1 = 0
    background_y2 = -background_image.get_height()
    spell_angle = 0
    score = 0

    # --- Sprite lists
    global all_sprites_list, player_list, enemy_list, player_bullet_list, enemy_bullet_list, lower_layer_list, upper_layer_list
    all_sprites_list = pygame.sprite.Group()
    enemy_list = pygame.sprite.Group()
    player_bullet_list = pygame.sprite.Group()
    enemy_bullet_list = pygame.sprite.Group()
    lower_layer_list = pygame.sprite.Group()
    upper_layer_list = pygame.sprite.Group()
    player_list = pygame.sprite.Group()

    # --- Create the sprites
    # Create player
    player = Player()
    all_sprites_list.add(player)
    player_list.add(player)

    # --- Events
    # pygame.USEREVENT is a const with value of 24
    SONG_END = pygame.USEREVENT + 0
    SPAWN_SHOOTER = pygame.USEREVENT + 1
    SPAWN_CHASER = pygame.USEREVENT + 2
    SPAWN_COLLIDER = pygame.USEREVENT + 3
    PLAYER_SHOT = pygame.USEREVENT + 4
    ENEMY_SHOT = pygame.USEREVENT + 5
    BOSS_SHOT = pygame.USEREVENT + 6
    # Trigger the event on a timer
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.time.set_timer(SPAWN_SHOOTER, shooter_spawn_time)
    pygame.time.set_timer(SPAWN_CHASER, 12000)
    pygame.time.set_timer(SPAWN_COLLIDER, collider_spawn_time)
    pygame.time.set_timer(PLAYER_SHOT, 200)
    pygame.time.set_timer(ENEMY_SHOT, 1200)

    # Set up
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play()
    pygame.mouse.set_visible(0)

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates
    clock = pygame.time.Clock()

    # -------- Main Program Loop -----------
    while not done:
        # --- EVENT PROCESSING
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                done = True

            if boss_spawned == False:

                if event.type == SONG_END:
                    next_song = random.choice(songs)
                    while next_song == current_song:
                        next_song = random.choice(songs)
                    current_song = next_song
                    pygame.mixer.music.load(next_song)
                    pygame.mixer.music.play()

                if event.type == SPAWN_SHOOTER:
                    enemy = Shooter('sprites/ships/spike_spaceship.png', 48, 100, 3, 20)
                    enemy.movement_x = random.choice(x_equations)
                    enemy.update()
                    # Add enemy to list of objects
                    enemy_list.add(enemy)
                    all_sprites_list.add(enemy)

                if event.type == SPAWN_CHASER:
                    enemy = Chaser('sprites/ships/tooth_spaceship.png', player, 8, 2, 10)
                    enemy_list.add(enemy)
                    all_sprites_list.add(enemy)

                if event.type == SPAWN_COLLIDER:
                    for i in range(collider_num):
                        enemy = Collider('sprites/ships/tech_shuriken.png', player, 13, 1, 15)
                        enemy_list.add(enemy)
                        all_sprites_list.add(enemy)

            if event.type == ENEMY_SHOT:
                # Create bullet
                for enemy in enemy_list:
                    if enemy.__class__.__name__ == 'Shooter':
                        bullet = EnemyBullet('sprites/fx/enemy_hit%d.png')
                        bullet.rect.centerx = enemy.cannon_x
                        bullet.rect.centery = enemy.cannon_y
                        # Convert coordinate to float as rect is always converted to integer
                        bullet.float_x = bullet.rect.x
                        bullet.float_y = bullet.rect.y
                        vector(bullet, player, 6)
                        enemy_bullet_list.add(bullet)
                        all_sprites_list.add(bullet)

            if event.type == BOSS_SHOT:
                # Create bullet
                for enemy in enemy_list:
                    rec_time = pygame.time.get_ticks()
                    radian = 0
                    radvec = random.choice([[7.25, 10.25, 2500], [79.75, 13, 3500], [math.radians(15), 9.5, 3000], [7.88, 5, 3500], [7.75, 7.5, 3500], [5.12, 6, 3000]])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mp_release = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    mp_release = False
            if event.type == PLAYER_SHOT:
                if mp_release == True and player.mp >= 8:
                    player_shot(player, [0,-6], -7, -10)
                    player_shot(player, [-0.12,-6], -19, -6)
                    player_shot(player, [0.12,-6], 5, -6)
                    player.mp -= 8
                else:
                    player_shot(player, [0,-6], -7, -10)

            if event.type == pygame.MOUSEBUTTONDOWN and player.mp >= 275:
                player.mp -= 275
                spell_circle = SpellCircle('sprites/fx/spell_circle%d.png', player.rect.x, player.rect.y, 35, pygame.time.get_ticks())
                lower_layer_list.add(spell_circle)
                for i in range(5):
                    bullet = SpellBullet([0,-6.5], 22, 'sprites/bullets/magic_flame%d.png', 'sprites/fx/mana_burst%d.png', 22, 67, pygame.time.get_ticks())
                    player_bullet_list.add(bullet)
                    all_sprites_list.add(bullet)
                casting_sound.play()


        # --- GAME LOGIC

        # Call the update() method on all the sprites
        all_sprites_list.update()
        lower_layer_list.update()
        upper_layer_list.update()

        # Move the background image
        background_y1 += 6
        background_y2 += 6
        if background_y1 > background_image.get_height():
            background_y1 = -background_image.get_height()
        if background_y2 > background_image.get_height():
            background_y2 = -background_image.get_height()

        # Calculate mechanics for each player's bullet
        for bullet in player_bullet_list:
            # See if enemies get shot
            hit_list = pygame.sprite.spritecollide(bullet, enemy_list, False, pygame.sprite.collide_mask)
            # For each enemy get shot, reduce 1HP and check if enemy is still alive
            for enemy in hit_list:
                create_animation(bullet.hit, bullet.rect.x-bullet.hit_x, bullet.rect.y-bullet.hit_y, 60)
                if bullet.__class__.__name__ == 'SpellBullet':
                    explode_sound.play()
                enemy.hp -= bullet.damage
                if player.mp < 400:
                    player.mp += 1
                player_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
                if enemy.hp <= 0:
                    score += enemy.score
                    if player.mp < 400:
                        player.mp += 4
                        if player.mp > 400:
                           player.mp = 400
                    print(score)
                    enemy_list.remove(enemy)
                    all_sprites_list.remove(enemy)
                    # Return function to default when boss is defeated
                    if enemy.__class__.__name__ == 'Boss':
                        boss_spawned = False
                        fade = Fade()
                        upper_layer_list.add(fade)
                        pygame.mixer.music.load(random.choice(songs))
                        pygame.mixer.music.play()
                        enemy_list.remove(enemy)
                        all_sprites_list.remove(enemy)
                        pygame.event.set_blocked(BOSS_SHOT)
                    # Create explosion
                    create_animation('sprites/fx/explosion%d.png', enemy.rect.x-30, enemy.rect.y-30, 48)
                    explode_sound.play()
                    # Reduce spawn time to rise difficult level
                    if boss_spawned == False:
                        if enemy.__class__.__name__ == 'Shooter' and shooter_spawn_time > 1200:
                            shooter_spawn_time -= 300
                            pygame.time.set_timer(SPAWN_SHOOTER, shooter_spawn_time)   
                        elif enemy.__class__.__name__ != 'Shooter':
                            if collider_spawn_time > 3800:
                                collider_spawn_time -= 300
                                pygame.time.set_timer(SPAWN_COLLIDER, collider_spawn_time)
                            elif collider_spawn_time <= 3800 and collider_num < 2:
                                collider_spawn_time = 6000
                                collider_num += 1
                                pygame.time.set_timer(SPAWN_COLLIDER, collider_spawn_time)
            if bullet.__class__.__name__ == 'SpellBullet':
                wipe_list = pygame.sprite.spritecollide(bullet, enemy_bullet_list, True, pygame.sprite.collide_mask)
                for enemy_bullet in wipe_list:
                    create_animation(enemy_bullet.hit, enemy_bullet.rect.x-50, enemy_bullet.rect.y-50, 60)
                    bullet.damage += 1
            # Remove the bullet if it flies up off the screen
            if bullet.rect.bottom < 0:
                player_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # Calculate mechanics for each enemy's bullet
        for bullet in enemy_bullet_list:
            # If player gets shot, call game over
            get_killed = pygame.sprite.spritecollide(bullet, player_list, False, pygame.sprite.collide_mask)
            if player in get_killed:
                create_animation(bullet.hit, bullet.rect.centerx-75, bullet.rect.centery-75, 60)
                hit_sound.play()
                player.hp -= 1
                enemy_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
                destruction_check(player, player_list)
            # Remove the bullet if it flies off the screen
            if bullet.rect.right < 0 or bullet.rect.left > 950 or bullet.rect.bottom < 0 or bullet.rect.top > 750:
                enemy_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # Check if player collides with enemy
        for enemy in enemy_list:
            get_killed = pygame.sprite.spritecollide(enemy, player_list, False, pygame.sprite.collide_mask)
            if player in get_killed:
                enemy.hp -= 5
                player.hp -= 2
                destruction_check(player, player_list)
                destruction_check(enemy, enemy_list)
            # Calculate vector for chaser
            if enemy.__class__.__name__ == 'Chaser':
                enemy.rotation(player)
            # Remove enemy that passed the screen
            if enemy.rect.top > 950 or enemy.rect.right < 0 and enemy.rect.left > 750:
                enemy_list.remove(enemy)
                all_sprites_list.remove(enemy)
            # Boss shots on decided trajectory
            if enemy.__class__.__name__ == 'Boss' and pygame.time.get_ticks() - rec_time < radvec[2]:
                radian += radvec[0]
                boss_shot(radian, 353, 93, radvec[1])
                boss_shot(radian, 600, 93, radvec[1])

        # Spawn boss when score reaches 300
        if 200 < score < 300 and boss_spawned == False:
            boss_spawned = True
        if bool(enemy_list) == False and boss_spawned == True:
            pygame.mixer.music.load('sound/bgm/scifi_drama.ogg')
            pygame.mixer.music.play(-1)
            enemy = Boss('sprites/ships/alien_spacecraft.png', 400, 5000)
            enemy_list.add(enemy)
            all_sprites_list.add(enemy)
            pygame.time.set_timer(BOSS_SHOT, 5000)


        # --- DRAW CODE
        screen.blit(background_image, [0, background_y1])
        screen.blit(background_image, [0, background_y2])

        lower_layer_list.draw(screen)

        if player in player_list:
            screen.blit(player_wings, [player.rect.centerx-119, player.rect.y])
            screen.blit(player_image, [player.rect.centerx-60, player.rect.y])
        # Draw all the spites
        all_sprites_list.draw(screen)

        upper_layer_list.draw(screen)

        # Player's HP and MP bar
        for i in range(2):
            pygame.draw.rect(screen, SLATEGRAY, [18*i, 0, 18, 203], 2)
            pygame.draw.rect(screen, DGRAY, [2+18*i, 2, 15, 200], 0)
        if player in player_list:
            pygame.draw.rect(screen, RED, [2, 2, 15, player.hp*20], 0)
        if player.mp > 0:
            pygame.draw.rect(screen, LSKY, [20, 2, 15, math.floor(player.mp*0.5)], 0)
        pygame.draw.line(screen, SLATEGRAY, [20, 139], [35, 139], 2)

        # Boss's HP bar
        for enemy in enemy_list:
            if enemy.__class__.__name__ == 'Boss':
                pygame.draw.rect(screen, SLATEGRAY, [931, 0, 18, 378], 2)
                pygame.draw.rect(screen, DGRAY, [933, 2, 15, 375], 0)
                pygame.draw.rect(screen, RED, [933, 2, 15, int(enemy.hp*375/400)], 0)

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)

    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()

def vector(source, target, speed):
    source.dx = target.rect.centerx - source.rect.centerx
    source.dy = target.rect.centery - source.rect.centery
    source.vect = list(pygame.math.Vector2(source.dx, source.dy).normalize()*speed)
    source.mask = pygame.mask.from_surface(source.image)

def create_animation(animate_image, animate_x, animate_y, frame_time):
    animation = Animation(animate_image, animate_x, animate_y, frame_time, pygame.time.get_ticks())
    all_sprites_list.add(animation)

def destruction_check(source, source_list):
    if source.hp <=0:
        source_list.remove(source)
        all_sprites_list.remove(source)
        # Create explosion
        create_animation('sprites/fx/explosion%d.png', source.rect.x-34, source.rect.y-34, 48)
        explode_sound.play()

def player_shot(source, vect, modify_x, modify_y):
    bullet = PlayerBullet(vect, 1, 'sprites/bullets/bullet.png', 'sprites/fx/player_hit%d.png', 50, 50)
    # Set the bullet so they are at the cannons
    bullet.rect.x = source.rect.centerx + modify_x
    bullet.rect.y = source.rect.y + modify_y
    bullet.float_x = bullet.rect.x
    bullet.float_y = bullet.rect.y
    all_sprites_list.add(bullet)
    player_bullet_list.add(bullet)

def boss_shot(radian, cannon_x, cannon_y, speed):
    bullet = EnemyBullet('sprites/fx/enemy_hit%d.png')
    bullet.rect.centerx = cannon_x
    bullet.rect.centery = cannon_y
    # Convert coordinate to float as rect is always converted to integer
    bullet.float_x = bullet.rect.x
    bullet.float_y = bullet.rect.y
    bullet.vect = [speed*math.sin(radian), speed*math.cos(radian)]
    enemy_bullet_list.add(bullet)
    all_sprites_list.add(bullet)


if __name__ == "__main__":
    main()
