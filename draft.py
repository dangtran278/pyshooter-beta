import pygame, math, random
 
# Define some colors as global constants
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DRED = (255, 36, 36)
LRED = (255, 102, 102)
AZURE = (0, 128, 255)
ELECTRIC = (101, 241, 242)

# --- Classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.hitbox = pygame.Surface([56, 90])
        self.hitbox.set_colorkey(BLACK)
        self.rect = self.hitbox.get_rect()
        self.image = pygame.image.load('azure_spaceship.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        player_pos = pygame.mouse.get_pos()
        # Adjust the mouse to image's center
        self.rect.x = player_pos[0] - 60
        self.rect.y = player_pos[1] - 62

class Shooter(pygame.sprite.Sprite):
    def __init__(self, spaceship, cannon_pos_x, cannon_pos_y):
        super().__init__()
        self.image = pygame.image.load(spaceship).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.modify_cannon_x = cannon_pos_x
        self.modify_cannon_y = cannon_pos_y
    def update(self):
        self.rect.y += 1
        self.cannon_x = self.rect.x + self.modify_cannon_x
        self.cannon_y = self.rect.y + self.modify_cannon_y
    def reset_pos(self):
        self.rect.x = random.randrange(940)
        self.rect.y = random.randrange(-450, -100)

class Chaser(pygame.sprite.Sprite):
    def __init__(self, spaceship, target):
        super().__init__()
        self.image = pygame.image.load(spaceship).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(940)
        self.rect.y = random.randrange(-300, -80)
        # Convert coordinate to float as rect is always converted to integer
        self.float_x = self.rect.x
        self.float_y = self.rect.y
        self.dx = target.rect.x + 60 - self.rect.x
        self.dy = target.rect.y + 62 - self.rect.y
        self.vect = list(pygame.math.Vector2(self.dx, self.dy).normalize()*10)
        self.image = pygame.transform.rotate(self.image, math.atan2(self.vect[0], self.vect[1])*180/math.pi)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([8, 30])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        pygame.draw.ellipse(self.image, AZURE, [self.rect.x, self.rect.y, 8, 24])
        pygame.draw.ellipse(self.image, ELECTRIC, [self.rect.x + 2, self.rect.y + 2, 4, 20])
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([14, 14])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, DRED, [self.rect.x + 7, self.rect.y + 7], 7, 0)
        pygame.draw.circle(self.image, LRED, [self.rect.x + 7, self.rect.y + 7], 5, 0)
        self.mask = pygame.mask.from_surface(self.image)
    def update(self):
        self.float_x += self.vect[0]
        self.float_y += self.vect[1]
        self.rect.x = int(self.float_x)
        self.rect.y = int(self.float_y)
        
class Explosion(pygame.sprite.Sprite):
    def __init__(self, explode_x, explode_y, explode_time):
        super().__init__()
        self.image = pygame.Surface([100, 100])
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = explode_x
        self.rect.y = explode_y
        self.time = explode_time
    def update(self):
        try:
            self.image = pygame.image.load('explosion%d.png' %(int((pygame.time.get_ticks() - self.time)/60+1))).convert_alpha()
        except pygame.error:
            pass

def main():
    """ Main function for the game."""
    pygame.init()
 
    # Set the width and height of the screen [width,height]
    screen_width = 1050
    screen_height = 750
    screen = pygame.display.set_mode([screen_width, screen_height])
 
    pygame.display.set_caption('Galatic Saga X')

    # --- Constants
    global explode_sound
    songs = ['aerial_fight.ogg', 'fight!.ogg', 'gunland.ogg', 'leviathan.ogg', 'light_your_sword.ogg', 'scifi_drama.ogg', 'swordland.ogg', 'this_psychedelic_world.ogg']
    click_sound = pygame.mixer.Sound('laser.ogg')
    explode_sound = pygame.mixer.Sound('explosion.ogg')
    background_image = pygame.image.load('starry_sky.png').convert()

    # --- Variables
    current_song = random.choice(songs)
    shooter_spawn_time = 2500
    chaser_spawn_time = 5000
    background_y1 = 0
    background_y2 = -background_image.get_height()
    crosshair_vx = 0
    crosshair_vy = 0
    score = 0

    # --- Sprite lists
    global all_sprites_list, player_list, enemy_list, player_bullet_list, enemy_bullet_list, explosion_list
    all_sprites_list = pygame.sprite.Group()
    enemy_list = pygame.sprite.Group()
    shooter_list = pygame.sprite.Group()
    player_bullet_list = pygame.sprite.Group()
    enemy_bullet_list = pygame.sprite.Group()
    explosion_list = pygame.sprite.Group()
    player_list = pygame.sprite.Group()

    # --- Create the sprites
    # Create player
    player = Player()
    all_sprites_list.add(player)
    player_list.add(player)

    # --- Create crosshair
    crosshair_image = pygame.image.load('scope.png').convert_alpha()
    crosshair_x = 437
    crosshair_y = 287

    # --- Events
    # pygame.USEREVENT is a const with value of 24
    SONG_END = pygame.USEREVENT + 0
    SPAWN_SHOOTER = pygame.USEREVENT + 1
    SPAWN_CHASER = pygame.USEREVENT + 2
    PLAYER_SHOT = pygame.USEREVENT + 3
    ENEMY_SHOT = pygame.USEREVENT + 4
    # Trigger the event on a timer
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.time.set_timer(SPAWN_SHOOTER, shooter_spawn_time)
    pygame.time.set_timer(SPAWN_CHASER, chaser_spawn_time)
    pygame.time.set_timer(PLAYER_SHOT, 400)
    pygame.time.set_timer(ENEMY_SHOT, 1500)

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
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and crosshair_x > -30:
                    crosshair_vx -= 3
                elif event.key == pygame.K_d and crosshair_x < 1020:
                    crosshair_vx = 3
                elif event.key == pygame.K_w and crosshair_y > -30:
                    crosshair_vy = -3
                elif event.key == pygame.K_s and crosshair_y < 720:
                    crosshair_vy = 3
                # If the crosshair passes the screen, reset vector back to zero
                if (crosshair_x < 30 and event.key == pygame.K_a) or (crosshair_x > 1020 and event.key == pygame.K_d):
                    crosshair_vx = 0
                if (crosshair_y < 30 and event.key == pygame.K_w) or (crosshair_y > 720 and event.key == pygame.K_s):
                    crosshair_vy = 0
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    crosshair_vx = 0
                elif event.key == pygame.K_w or event.key == pygame.K_s:
                    crosshair_vy = 0
 
            if event.type == SONG_END:
                next_song = random.choice(songs)
                while next_song == current_song:
                    next_song = random.choice(songs)
                current_song = next_song
                pygame.mixer.music.load(next_song)
                pygame.mixer.music.play()
                
            if event.type == SPAWN_SHOOTER:
                enemy = Shooter('tooth_spaceship.png', 44, 100)
                enemy.rect.x = random.randrange(screen_width - 110)
                enemy.rect.y = random.randrange(-300, -80)
                enemy.cannon_x = 0
                enemy.cannon_y = 0
                enemy.update()
                # Add enemy to list of objects
                enemy_list.add(enemy)
                shooter_list.add(enemy)
                all_sprites_list.add(enemy)
            if event.type == SPAWN_CHASER:
                enemy = Chaser('lancelot_mammoth.png', player)
                enemy_list.add(enemy)
                all_sprites_list.add(enemy)

            if event.type == PLAYER_SHOT:
                # Fire a bullet if the user clicks the mouse button
                bullet = PlayerBullet()
                # Set the bullet so they are at the cannons
                bullet.rect.x = player.rect.x + 56
                bullet.rect.y = player.rect.y - 2
                # Calculate vector of bullet
                bullet.float_x = bullet.rect.x
                bullet.float_y = bullet.rect.y
                bullet.dx = crosshair_x - bullet.rect.x + 15
                bullet.dy = crosshair_y - bullet.rect.y + 21
                bullet.vect = list(pygame.math.Vector2(bullet.dx, bullet.dy).normalize()*5)
                bullet.image = pygame.transform.rotate(bullet.image, math.atan2(bullet.dx,bullet.dy)*180/math.pi)
                bullet.mask = pygame.mask.from_surface(bullet.image)
                all_sprites_list.add(bullet)
                player_bullet_list.add(bullet)
                
            if event.type == ENEMY_SHOT:
                # Create bullet
                for enemy in shooter_list:
                    bullet = EnemyBullet()
                    bullet.rect.x = enemy.cannon_x
                    bullet.rect.y = enemy.cannon_y
                    # Convert coordinate to float as rect is always converted to integer
                    bullet.float_x = bullet.rect.x
                    bullet.float_y = bullet.rect.y
                    bullet.dx = player.rect.x + 60 - bullet.rect.x
                    bullet.dy = player.rect.y + 62 - bullet.rect.y
                    bullet.vect = list(pygame.math.Vector2(bullet.dx, bullet.dy).normalize()*4.5)
                    enemy_bullet_list.add(bullet)
                    all_sprites_list.add(bullet)
                    

        # --- GAME LOGIC
        # Call the update() method on all the sprites
        all_sprites_list.update()

        # Move the background image
        background_y1 += 6
        background_y2 += 6
        if background_y1 > background_image.get_height():
            background_y1 = -background_image.get_height()
        if background_y2 > background_image.get_height():
            background_y2 = -background_image.get_height()

        # Re-adjust crosshair if passes screen
        if crosshair_x < -30:
            crosshair_x = -30
        elif crosshair_x > 1020:
            crosshair_x = 1020
        if crosshair_y < -30:
            crosshair_y = -30
        elif crosshair_y > 720:
            crosshair_y = 720
        # Move the crosshair
        crosshair_x += crosshair_vx
        crosshair_y += crosshair_vy

        # Calculate mechanics for each player's bullet
        for bullet in player_bullet_list:
            # See if enemies get shot
            kill_list = pygame.sprite.spritecollide(bullet, enemy_list, True, pygame.sprite.collide_mask)
            # For each enemy get shot, remove the bullets and add to the score
            for enemy in kill_list:
                player_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)
                score += 1
                # Create explosion
                create_explosion(enemy)
                # Reduce spawn time to rise difficult level
                if enemy in shooter_list and shooter_spawn_time > 400:
                    shooter_spawn_time -= 200
                    pygame.time.set_timer(SPAWN_SHOOTER, shooter_spawn_time)
                elif enemy not in shooter_list and chaser_spawn_time > 2000:
                    chaser_spawn_time -= 200
                    pygame.time.set_timer(SPAWN_CHASER, chaser_spawn_time)
            # Remove the bullet if it flies up off the screen
            if bullet.rect.y < -30:
                player_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # Calculate mechanics for each enemy's bullet
        for bullet in enemy_bullet_list:
            # If player gets shot, call game over
            get_killed = pygame.sprite.spritecollide(bullet, player_list, True, pygame.sprite.collide_mask)
            if player in get_killed:
                # Create explosion
                create_explosion(player)
            # Remove the bullet if it flies off the screen
            if bullet.rect.x < -14 or bullet.rect.x > 1064 or bullet.rect.y < -14 or bullet.rect.y > 764:
                enemy_bullet_list.remove(bullet)
                all_sprites_list.remove(bullet)

        # Check if player collides with enemy
        for enemy in enemy_list:
            get_killed = pygame.sprite.spritecollide(enemy, player_list, True, pygame.sprite.collide_mask)
            if player in get_killed:
                enemy_list.remove(enemy)
                all_sprites_list.remove(enemy)
                # Create explosion
                create_explosion(player)
                create_explosion(enemy)

        # Reset shooter to the top if passed the screen
        for enemy in enemy_list:
            if enemy.rect.y > 880 and enemy in shooter_list:
                    enemy.reset_pos()
            # Remove chaser that passed the screen
            elif enemy.rect.y > 880:
                enemy_list.remove(enemy)
                all_sprites_list.remove(enemy)
        
        # Remove explosion when effect is over
        for explosion in explosion_list:
            if pygame.time.get_ticks() - explosion.time > 959:
                explosion_list.remove(explosion)
                all_sprites_list.remove(explosion)

        # --- DRAW CODE
        screen.blit(background_image, [0, background_y1])
        screen.blit(background_image, [0, background_y2])
        # Draw all the spites
        all_sprites_list.draw(screen)
        screen.blit(crosshair_image, [crosshair_x, crosshair_y])
                    
        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 60 frames per second
        clock.tick(60)
 
    # Close the window and quit.
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()

def create_explosion(source):
    x = source.rect.x - 24
    y = source.rect.y - 24
    explosion = Explosion(x, y, pygame.time.get_ticks())
    explosion_list.add(explosion)
    all_sprites_list.add(explosion)
    explode_sound.play()
 
if __name__ == "__main__":
    main()
