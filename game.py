import pygame, sys, time, os, math, random
from pygame.locals import *

_DEBUG = False
_GAMETITLE = 'Archon Type Game!'
pygame.init()
pygame.font.init()
pygame.mixer.init()
#MUSIC
title_music = r'Resources\Sound\Music\01_-_Archon_-_NES_-_Title.ogg'
board_music = r'Resources\Sound\Music\02_-_Archon_-_NES_-_Board.ogg'
arena_music = r'Resources\Sound\Music\03_-_Archon_-_NES_-_Combat.ogg'
end_music = r'Resources\Sound\Music\04_-_Archon_-_NES_-_You_Lose.ogg'
#SOUND
sel_sound = pygame.mixer.Sound(r'Resources\Sound\audio\select2.wav')
hurt_sound = pygame.mixer.Sound(r'Resources\Sound\audio\hurt.wav')
##FONTS
myfont = pygame.font.SysFont("Comic Sans MS", 30)
title_font = pygame.font.SysFont("Comic Sans MS", 80)
option_font = pygame.font.SysFont("Comic Sans MS", 60)
small_font = pygame.font.SysFont("Comic Sans MS", 15)
debug_font = pygame.font.SysFont("lucidaconsole", 15)

title_gm_font = pygame.font.Font(r'Resources\Fonts\Langar\Langar-Regular.ttf', 80)
big_gm_font = pygame.font.Font(r'Resources\Fonts\Langar\Langar-Regular.ttf', 60)
medium_gm_font = pygame.font.Font(r'Resources\Fonts\Langar\Langar-Regular.ttf', 40)
small_medium_gm_font = pygame.font.Font(r'Resources\Fonts\Langar\Langar-Regular.ttf', 30)
small_gm_font = pygame.font.Font(r'Resources\Fonts\Langar\Langar-Regular.ttf', 20)
pygame.display.set_caption(_GAMETITLE)

_CHARS_SIZE = 128
_PROJ_SIZE = 30
width, height = 64*16, 64*10
screen=pygame.display.set_mode((width, height))


clock = pygame.time.Clock()

current_scene = ""
playing = False
animation_line = []

icon = pygame.image.load(r'Resources\Icon\Icon.png')
pygame.display.set_icon(icon)
title_background = pygame.image.load(r'Resources\Background\TitleBackground.png')
side_choice_background = pygame.image.load(r'Resources\Background\SideChoiceBackground.png')



##KEYS
sel_key = [pygame.K_LSHIFT, pygame.K_RETURN]
up_key = [pygame.K_w, pygame.K_UP]
down_key = [pygame.K_s, pygame.K_DOWN]
left_key = [pygame.K_a, pygame.K_LEFT]
right_key = [pygame.K_d, pygame.K_RIGHT]

def get_sprites(character, directory):
    spritesheet = []
    for sprite in os.listdir(r"Resources\Sprites\Characters\{0}\{1}".format(character, directory)):
        spritesheet.append(r'Resources\Sprites\Characters\{0}\{1}\{2}'.format(character,directory,sprite))
    return spritesheet


"""
~~~~PROJECTILES~~~~
"""

class DamageArea:
    obj_type = "area"
    name = ''
    sprite = ''
    team = 2
    ranged = True
    x = 0
    y = 0
    animation_sprites = ''
    radius = 46
    anim_key = 0
    dmg = 1
    exists = True
    banshee_damage = [0,1,2,3,4,5,6,7]
    owner = None
    def __init__(self, char):
        self.name = char.name
        self.owner = char
        if char.name in ["Phoenix", "Banshee"]:
            self.animation_sprites = get_sprites(char.name, "DamageArea")
        if char.name == "Banshee":
            self.banshee_damage = [0,1,2,3,4,5,6,7]
        self.team = char.team
        sprite = pygame.image.load(self.animation_sprites[0])
        sprite = pygame.transform.smoothscale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
        self.sprite = sprite
        self.radius = char.area_radius
        self.dmg = char.atk_damage
        if self.team == 0:
            light_areas.append(self)
        else:
            dark_areas.append(self)
        self.x = char.x
        self.y = char.y
    
    def hitbox(self):
        circleRect = pygame.draw.circle(screen, (0,0,0), (int(self.x + 24*2.6), int(self.y + 24*2.6)), int(self.radius*2.16))
        return circleRect

    def move(self):
        self.x = self.owner.x
        self.y = self.owner.y
        if self.name == "Banshee" or self.name == "Phoenix": 
            if not self.exists:
                return
            for rect in arena_collisions:
                if rect != self:
                    if self.hitbox().colliderect(rect.hitbox()):
                        if rect.obj_type == "player":
                            if rect.team != self.team:
                                if self.name == "Phoenix":
                                    rect.take_damage(self.dmg)
                                    self.exists = False
                                elif self.name == "Banshee":
                                    if self.anim_key in self.banshee_damage:
                                        rect.take_damage(1)
                                        self.banshee_damage.remove(self.anim_key)


    def change_sprite(self, key):
        if (key == len(self.animation_sprites) and self.name == "Phoenix") or (key == "disappear" and self.name == "Banshee"):
            if self.team == 0:
                light_areas.remove(self)
            else:
                dark_areas.remove(self)
            self.exists = False
            return
        sprite = pygame.image.load(self.animation_sprites[key % len(self.animation_sprites)])
        sprite = pygame.transform.smoothscale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
        self.sprite = sprite
        self.anim_key = key
    
    def disappear(self):
        if self.team == 0:
            light_areas.remove(self)
        else:
            dark_areas.remove(self)


class Projectile:
    melee_clock = 0
    ranged = False
    obj_type = "projectile"
    team = 2
    dmg = 0
    x = 0
    y = 0
    direction = ()
    sprite = ""
    speed = 1
    hitbox_x = 0
    hitbox_y = 0
    angle = 0
    width= 10
    height = 10
    
    def __init__(self, direction, character):
        self.ranged = character.ranged
        self.team = character.team
        self.x, self.y = (character.x, character.y)
        self.height, self.width  = min(character.proj_height, character.proj_width),min(character.proj_height, character.proj_width)
        self.direction = (direction[0], direction[1]) 
        if self.team == 0:
            light_projectiles.append(self)
        else:
            dark_projectiles.append(self)
        self.speed = character.atk_speed = 1.0 *20
        self.dmg = character.atk_damage
        if self.ranged:
            sprite = pygame.image.load(r'Resources\Sprites\Characters\{0}\Projectile\Projectile.png'.format(character.name))
            sprite = pygame.transform.smoothscale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
        if direction[0] < 0:
            if self.ranged:
                sprite = pygame.transform.flip(sprite, True, False)
            #self.hitbox_x = (48 - self.width) *2.6
        if direction[0] == 1 and direction[1] == -1:
            correction = 2
            self.angle = 45
            self.hitbox_y = -36
        elif direction[0] == -1 and direction[1] == -1:
            correction = 7
            self.angle = -45
            self.hitbox_y = -36
            self.hitbox_x = -72
        elif direction[0] == 1 and direction[1] == 1:
            correction = 3
            self.angle = 315
            self.hitbox_x = -36
        elif direction[0] == -1 and direction[1] == 1:
            correction = 8
            self.angle = -315
            self.hitbox_x = -36
        elif direction[0] == 1 and direction[1] == 0:
            correction = 0
        elif direction[0] == -1 and direction[1] == 0:
            correction = 5
            self.hitbox_x = -48
        elif direction[0] == 0 and direction[1] == 1:
            if character.orientation:
                correction= 9
            else:
                correction = 4
            self.hitbox_x = -48
            self.angle = -90
        elif direction[0] == 0 and direction[1] == -1:
            if character.orientation:
                correction= 6
            else:
                correction = 1
            self.hitbox_y = -48
            self.angle = 90
        if self.ranged:
            sprite = pygame.transform.rotate(sprite,  self.angle)
            self.sprite = sprite
        self.x, self.y = (self.x + (character.proj_correction[correction][0] + self.hitbox_x)*2.6, self.y + (character.proj_correction[correction][1] + self.hitbox_y)*2.6)

    def hitbox(self):
        return pygame.Rect(self.x- self.hitbox_x * 2.6, self.y- self.hitbox_y*2.6, self.width *2.6, self.height*2.6)

    
    def move(self):
        if self.ranged:
            speed = self.speed
            if self.direction[0] != 0 and self.direction[1] != 0:
                speed = math.cos(math.pi / 4) *self.speed
            self.x += self.direction[0] * speed
            self.y += self.direction[1] * speed
        else:
            if self.melee_clock > 20:
                if self.team == 0:
                    light_projectiles.remove(self)
                else:
                    dark_projectiles.remove(self)
            else:
                self.melee_clock += 1
        for rect in arena_collisions:
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    if rect.obj_type == "barrier":
                        if rect.team != self.team:
                            if self.team == 0:
                                light_projectiles.remove(self)
                                return
                            else:
                                dark_projectiles.remove(self)
                                return 
                    if rect.obj_type == "player":
                        if rect.team != self.team:
                            rect.take_damage(self.dmg)
                            if self.team == 0:
                                light_projectiles.remove(self)
                                return
                            else:
                                dark_projectiles.remove(self)
                                return 
        if not arena_ground.contains(self.hitbox()):
            if self.team == 0:
                light_projectiles.remove(self)
                return
            else:
                dark_projectiles.remove(self)
                return 


"""
~~~~OBSTACLE~~~~
"""
class Barrier:
    obj_type = "barrier"
    team = 1
    x = 0
    y = 0
    sprites = [r'Resources\Sprites\Tiles\Obstacle\Sprites\Obstacle2.png', r'Resources\Sprites\Tiles\Obstacle\Sprites\Obstacle1.png', r'Resources\Sprites\Tiles\Obstacle\Sprites\Obstacle3.png']
    cycle = 0
    cycle_limit = 120
    cycle_ct = 0

    def __init__(self, x, y, val):
        self.x = x
        self.y = y
        self.cycle = val
        self.sprite = pygame.transform.scale(pygame.image.load(self.sprites[self.cycle]),  (_CHARS_SIZE, _CHARS_SIZE))
    
    def hitbox(self):
        return pygame.Rect(self.x + 18 * 2.6, self.y + 17*2.6, 12*2.6, 14*2.6)
    

    def update(self):
        self.cycle_ct += 1
        if self.cycle_ct > self.cycle_limit:
            self.cycle = 0
            self.cycle_ct = 0
            self.cycle_limit = random.randint(200, 601)
            cycle_alternator = random.randint(-1, 2)
            self.cycle += cycle_alternator
            if self.cycle >= len(self.sprites):
                self.cycle = len(self.sprites) -1
            elif self.cycle < 0:
                self.cycle = 0
            self.team = self.cycle
        self.sprite = pygame.transform.scale(pygame.image.load(self.sprites[self.cycle]),  (_CHARS_SIZE, _CHARS_SIZE))


"""
~~~~CHARACTERS~~~~
"""
class Knight():
    obj_type = "player"
    #STATS
    name = "Knight"
    description = "The knights are soldiers going on foot that are armed and primed against enemies that are much bigger than they are. Although they cannot withstand more than one attack from many of their enemies, they are no cannon (or dragon) fodder. Provided that they are fast and intelligent their speed of their attacks gives them the chance to survive and to triumph."
    s_moving_type = "ground - 3"
    s_speed = "normal"
    s_attack_type = "sword"
    s_attack_strength = "low"
    s_attack_speed = "instant"
    s_attack_interval = "very short"
    s_life_span = "short"
    s_number_of_chars = "7"

    #STAT NUMBERS
    team = 0
    ranged = False
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 5
    atk_speed = 1.0 *20
    atk_cooldown = 0.33 * 60
    max_hp= 4.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 6
    proj_height = 6
    #Corrections 
    proj_correction = [
    (40,27), #RightAttackFront
    (30,9), #RightAttackUp
    (38,16), #RightAttackFrontUp
    (38,38), #RightAttackFrontDown
    (30,42), #RightAttackDown
    (2,27), #LeftAttackFront
    (12,9), #LeftAttackUp
    (5,14), #LeftAttackFrontUp
    (7,38), #LeftAttackFrontDown
    (16,42)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\human_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps2.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\sword_swing.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)
    
class Unicorn():
    name = "Unicorn"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts"
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 2
    move_limit = 4
    speed = 5
    atk_damage = 9
    atk_speed = 1.0 *20
    atk_cooldown = 1 * 60
    max_hp= 8.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 12
    char_y_offset = 21
    char_width = 24
    char_height = 16
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (41,22), #RightAttackFront
    (34,9), #RightAttackUp
    (36,14), #RightAttackFrontUp
    (40,30), #RightAttackFrontDown
    (36,34), #RightAttackDown
    (9,22), #LeftAttackFront
    (15,9), #LeftAttackUp
    (13,14), #LeftAttackFrontUp
    (9,30), #LeftAttackFrontDown
    (13,34)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\horse_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\horse_steps2.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\unicorn_magic_attack.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %6:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    
    
    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Valkyrie():
    name = "Valkyrie"
    description = "Valkyries are pretty, blonde warriors of the legion of Valhalla. Every one of it is equipped with two big talents: firstly the ability to walk through the air as if it was solid ground; and secondly a bewitched spear that after been thrown returns to its thrower." 
    s_moving_type = "air - 3"
    s_speed = "normal"
    s_attack_type = "spear"
    s_attack_strength = "moderate"
    s_attack_speed = "slow"
    s_attack_interval = "average"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 1
    move_limit = 3
    speed = 5
    atk_damage = 7
    atk_speed = 0.5 *20
    atk_cooldown = 0.75 * 60
    max_hp= 7.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 16
    char_width = 12 
    char_height = 20
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (44,16), #RightAttackFront
    (15,12), #RightAttackUp
    (37,11), #RightAttackFrontUp
    (39,29), #RightAttackFrontDown
    (34,38), #RightAttackDown
    (6,16), #LeftAttackFront
    (34,12), #LeftAttackUp
    (10,11), #LeftAttackFrontUp
    (10,29), #LeftAttackFrontDown
    (15,38)  #LeftAttackDown 
    ]

    ##AUDIO
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\spear_swing.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Djinni():
    name = "Djinni"
    description = "The djinni is a magical creature from another dimension, a flying thing from tempest and storm in the shape of a big and enormously muscular man whose body seems to be partially solid and partially turbulenced air. As cousin of the wind the djinni can rouse a small tornado with a gesture and control it with its thoughts." 
    s_moving_type = "air - 4"
    s_speed = "normal"
    s_attack_type = "twister" 
    s_attack_strength = "moderate"
    s_attack_speed = "middle"
    s_attack_interval = "short"
    s_life_span = "long"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 1
    move_limit = 4
    speed = 5
    atk_damage = 6
    atk_speed = .8 *20
    atk_cooldown = 0.66 * 60
    max_hp= 14.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 19
    char_y_offset = 18
    char_width = 10 
    char_height = 18
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (40,26), #RightAttackFront
    (30,13), #RightAttackUp
    (39,15), #RightAttackFrontUp
    (41,37), #RightAttackFrontDown
    (33,38), #RightAttackDown
    (8,26), #LeftAttackFront
    (19,13), #LeftAttackUp
    (10,15), #LeftAttackFrontUp
    (8,37), #LeftAttackFrontDown
    (16,38)  #LeftAttackDown 
    ]

    ##AUDIO
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\wizard_spell.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Archer():
    obj_type = "player"
    name = "Archer"
    description = "The archers are fearless amazones, that can handle their bows with legendary skill. They are equipped with magical quivers that never get empty." 
    s_moving_type = "ground - 3"
    s_speed = "normal"
    s_attack_type = "arrow"
    s_attack_strength = "low"
    s_attack_speed = "middle"
    s_attack_interval = "average"
    s_life_span = "short"
    s_number_of_chars = "2"

    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 5
    atk_speed = 0.7 *20
    atk_cooldown = 0.75 * 60
    max_hp= 4.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 18
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (40,29), #RightAttackFront
    (34,15), #RightAttackUp
    (42,14), #RightAttackFrontUp
    (38,41), #RightAttackFrontDown
    (34,38), #RightAttackDown
    (10,29), #LeftAttackFront
    (16,15), #LeftAttackUp
    (7,14), #LeftAttackFrontUp
    (10,41), #LeftAttackFrontDown
    (16,38)  #LeftAttackDown
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\human_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps2.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\bow_arrow_fire.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Golem():
    name = "Golem"
    description = "A golem is an artificial creature, formed out of stone and gleaming metal and brought to life by magic. The shape is roughly based on a human but well twice as big. Its weapons are stone chippings which it throws with destructive power." 
    s_moving_type = "ground - 3"
    s_speed = "slow"
    s_attack_type = "stone chippings"
    s_attack_strength = "high" 
    s_attack_speed = "slow"
    s_attack_interval = "long"
    s_life_span = "long"
    s_number_of_chars = "2"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 2
    move_limit = 3
    speed = 4
    atk_damage = 10
    atk_speed = 0.5 *20
    atk_cooldown = 0.6 * 60
    max_hp= 14.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 20
    char_width = 17
    char_height = 23
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 14
    proj_height = 10
    #Corrections 
    proj_correction = [
    (50,11), #RightAttackFront
    (45,19), #RightAttackUp
    (46,5), #RightAttackFrontUp
    (51,33), #RightAttackFrontDown
    (45,33), #RightAttackDown
    (14,11), #LeftAttackFront
    (16,19), #LeftAttackUp
    (14,5), #LeftAttackFrontUp
    (14,33), #LeftAttackFrontDown
    (16,33)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\scrape_movement_2.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\scrape_movement_throw.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %4:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Phoenix():
    name = "Phoenix"
    description = "The phoenix is a burning bird with immense size and power. In a fight it can explode in a boiling mass of fire that scorches everything in its radius and burns every opponent that was uncareful enough to come near the white glowing core. The phoenix is not only immune against its own fire but it can also - during its metamorphose - not be hurt by any known attack." 
    s_moving_type = "air - 5"
    s_speed = "normal"
    s_attack_type = "ferverent explosion"
    s_attack_strength = "high"
    s_attack_speed = "slow"
    s_attack_interval = "long"
    s_life_span = "long"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 1
    move_limit = 5
    speed = 5
    atk_damage = 10
    atk_speed = 1.0 *20
    atk_cooldown = 0.6 * 60
    max_hp= 11.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 15
    char_y_offset = 15
    char_width = 18
    char_height = 18
    #Position
    x = 0
    y = 0

    #area
    my_area = None
    area_radius = 28

    ##AUDIO
    run_sound = pygame.mixer.Sound(r'Resources\Sound\audio\phoenix_wing_flap.wav')
    explosion_sound = pygame.mixer.Sound(r'Resources\Sound\audio\phoenix_explosion.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_animation = get_sprites(name, 'Attack')


    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0
    finished_attack = False

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key == 2 and self.anim_clock == 2:
                self.run_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                self.run_sound.play()
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "Attack":
            if self.cur_key == 0 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > len(self.attack_animation):
                if self.my_area != None:
                    self.my_area.change_sprite(len(self.attack_animation))
                self.current_animation = "idle"
                self.performing_action = False
                self.finished_attack = True
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_animation[self.cur_key]
                    if self.my_area != None:
                        self.my_area.change_sprite(self.cur_key)
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self):
        self.performing_action = True
        self.can_attack = False
        self.current_animation = "Attack"
        self.finished_attack = False
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        self.explosion_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.explosion_sound.play()
        self.my_area = DamageArea(self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if self.current_animation != "Attack":
            if damage <= self.extra_hp:
                self.extra_hp -= damage
            elif damage > self.extra_hp:
                damage -= self.extra_hp
                self.extra_hp = 0
                self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack()
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack()
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_animation = get_sprites(self.name + "Shapeshifter", 'Attack')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Wizard():
    name = "Wizard"
    description = "A very old man, who juggles with supernatural powers, the wizard is the leader of the light side. In a fight it throws destructive fireballs. It seldom takes the risk to leave its force field, as it usually uses one of the seven magical spells." 
    s_moving_type = "teleport - 3"
    s_speed = "normal"
    s_attack_type = "fireball"
    s_attack_strength = "moderate"
    s_attack_speed = "middle"
    s_attack_interval = "average"
    s_life_span = "average"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 0
    move_limit = 3
    speed = 5
    atk_damage = 10
    atk_speed = 0.8 *20
    atk_cooldown = 0.75 * 60
    max_hp= 9.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (36,28), #RightAttackFront
    (33,17), #RightAttackUp
    (36,19), #RightAttackFrontUp
    (35,33), #RightAttackFrontDown
    (33,35), #RightAttackDown
    (14,26), #LeftAttackFront
    (16,18), #LeftAttackUp
    (14,19), #LeftAttackFrontUp
    (14,34), #LeftAttackFrontDown
    (16,35)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\human_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps2.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\fire_spell.wav')


    ##SPELLS
    spells = ["Teleport", "Heal", "Revive", "Exchange", "Shift Time", "Summon Elemental", "Imprison", "Cease Conjuring"]
    casting_spell = False

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    spell_animation = get_sprites(name, "SpellCast")

    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation
        if self.casting_spell:
            self.current_animation = "casting spell"
        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "casting spell":
            if self.cur_key+2 > len(self.spell_animation):
                self.current_animation = "idle"
                self.performing_action = False
                self.casting_spell = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.spell_animation[self.cur_key]
        elif self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)


#DARK#


class Sorceress():
    name = "Sorceress"
    description = "It resembles the wizard only in strength, apart from that the eternal young and pretty sorceress is exactly the counterpart. Its light beams are faster than the wizards fireballs, but a bit weaker. Boisterous in the fight, but safest on its black force field, where it is most of the time used to cast spells." 
    s_moving_type = "teleport - 3"
    s_speed = "normal"
    s_attack_type = "light beams"
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "average"
    s_life_span = "average"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
    move_type = 0
    move_limit = 3
    speed = 5
    atk_damage = 8
    atk_speed = 0.9 *20
    atk_cooldown = 0.75 * 60
    max_hp= 9.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 19
    char_y_offset = 17
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (34,26), #RightAttackFront
    (33,17), #RightAttackUp
    (36,19), #RightAttackFrontUp
    (35,33), #RightAttackFrontDown
    (33,35), #RightAttackDown
    (14,26), #LeftAttackFront
    (16,18), #LeftAttackUp
    (14,19), #LeftAttackFrontUp
    (14,34), #LeftAttackFrontDown
    (16,35)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\human_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps2.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\dark_spell_shoot.wav')
    

    ##SPELLS
    spells = ["Teleport", "Heal", "Revive", "Exchange", "Shift Time", "Summon Elemental", "Imprison", "Cease Conjuring"]
    casting_spell = False

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    spell_animation = get_sprites(name, "SpellCast")
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        if self.casting_spell:
            self.current_animation = "casting spell"
        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "casting spell":
            if self.cur_key+2 > len(self.spell_animation):
                self.current_animation = "idle"
                self.performing_action = False
                self.casting_spell = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.spell_animation[self.cur_key]
        elif self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    


    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Manticore():
    name = "Manticore"
    description = "The manticore resembles a big golden lion with a humanoid face and a tail similar to the one of a scorpion. This disgusting thing teems with big spikes which it can shoot with surprising precision." 
    s_moving_type = "ground - 3"
    s_speed = "normal"
    s_attack_type = "spikes"
    s_attack_strength = "low"
    s_attack_speed = "slow"
    s_attack_interval = "average"
    s_life_span = "average"
    s_number_of_chars = "2"

    obj_type = "player"
    team = 1
    ranged = True
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 4
    atk_speed = 0.5 *20 
    atk_cooldown = 0.75 * 60
    max_hp= 7.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 15
    char_y_offset = 26
    char_width = 18 
    char_height = 10
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (27,22), #RightAttackFront
    (23,15), #RightAttackUp
    (25,18), #RightAttackFrontUp
    (25,28), #RightAttackFrontDown
    (23,32), #RightAttackDown
    (17,22), #LeftAttackFront
    (26,15), #LeftAttackUp
    (24,18), #LeftAttackFrontUp
    (24,28), #LeftAttackFrontDown
    (26,32)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\manticore_move1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\manticore_move2.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\manticore_spike.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Troll():
    name = "Troll"
    description = 'An inhabitant of caves and dark places. The deformed troll is a "waggly" giant,' + " dull but strong, clumsy but very tough. Like the golem it doesn't carry any weapons but grabs rocks, tree stumps and whatever it gets into its hands and throws these massive items onto its enemies"
    s_moving_type = "ground - 3"
    s_speed = "slow"
    s_attack_type = "tree logs"
    s_attack_strength = "high" 
    s_attack_speed = "slow"
    s_attack_interval = "long"
    s_life_span = "long"
    s_number_of_chars = "2"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
    move_type = 2
    move_limit = 3
    speed = 4
    atk_damage = 10
    atk_speed = 0.5 *20
    atk_cooldown = 0.6 * 60
    max_hp= 13.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 20
    char_width = 17
    char_height = 23
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 14
    proj_height = 10
    #Corrections 
    proj_correction = [
    (50,11), #RightAttackFront
    (45,19), #RightAttackUp
    (46,5), #RightAttackFrontUp
    (51,33), #RightAttackFrontDown
    (45,33), #RightAttackDown
    (14,11), #LeftAttackFront
    (16,19), #LeftAttackUp
    (14,5), #LeftAttackFrontUp
    (14,33), #LeftAttackFrontDown
    (16,33)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\troll_step1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\troll_step2.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\troll_throw.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %5:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Goblin():
    obj_type = "player"
    #STATS
    name = "Goblin"
    description = "Goblins are ugly dwarfs with bad nature, unfriendly and often boisterous. Their enemies only hold them at bay on the squares of the sorceress. On the dark squares their gnarled clubs are more than up to the swords of the knights and if they are played well, they can also win against stronger enemies."
    s_moving_type = "ground - 3"
    s_speed = "normal"
    s_attack_type = "club"
    s_attack_strength = "low"
    s_attack_speed = "instant"
    s_attack_interval = "very short"
    s_life_span = "short"
    s_number_of_chars = "7"

    #STAT NUMBERS
    team = 1
    ranged = False
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 5
    atk_speed = 1.0 *20
    atk_cooldown = 0.33 * 60
    max_hp= 4.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 13
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 6
    proj_height = 6
    #Corrections 
    proj_correction = [
    (40,27), #RightAttackFront
    (30,9), #RightAttackUp
    (38,16), #RightAttackFrontUp
    (38,38), #RightAttackFrontDown
    (30,42), #RightAttackDown
    (2,27), #LeftAttackFront
    (12,9), #LeftAttackUp
    (5,14), #LeftAttackFrontUp
    (7,38), #LeftAttackFrontDown
    (16,42)  #LeftAttackDown
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\human_steps1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps2.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\human_steps3.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\sword_swing.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Banshee():
    name = "Banshee"
    description = "The banshee is an immaterialized undead that can deprive the enemies that are in its reach (the shaded area around it) of their soul with its keen." 
    s_moving_type = "air - 3"
    s_speed = "normal"
    s_attack_type = "keen"
    s_attack_strength = "moderate"
    s_attack_speed = "very fast"
    s_attack_interval = "long"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
    move_type = 1
    move_limit = 3
    speed = 5
    atk_damage = 8
    atk_speed = 1.0 *20
    atk_cooldown = 0.6 * 60
    max_hp= 7.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 
    char_height = 18
    #Position
    x = 0
    y = 0

    #area
    my_area = None
    area_radius = 28

    #AUDIO
    fire_sound = pygame.mixer.Sound(r'Resources\Sound\audio\banshee_area.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_animation = get_sprites(name, 'Attack')


    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0
    finished_atack = False

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "Attack":
            if self.cur_key == 0 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 8:
                if self.my_area != None:
                    self.my_area.change_sprite("disappear")
                self.current_animation = "idle"
                self.finished_atack = True
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_animation[self.cur_key % 4]
                    if self.my_area != None:
                        self.my_area.change_sprite(self.cur_key)
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self):
        self.can_attack = False
        self.current_animation = "Attack"
        self.finished_atack = False
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        self.my_area = DamageArea(self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack()
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack()
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action and self.can_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack and self.finished_atack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_animation = get_sprites(self.name + "Shapeshifter", 'Attack')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Dragon():
    name = "Dragon"
    description = "The dragon, a monstrous reptile, is virtually without opponent in the arena. One wave of ember of its feverent breath already kills many creatures, the second one is defintely deadly. It is very movable and very hard to kill, its value is only outranged by the sorceress."
    s_moving_type = "air - 4"
    s_speed = "normal"
    s_attack_type = "feverent breath"
    s_attack_strength = "very high"
    s_attack_speed = "middle"
    s_attack_interval = "long"
    s_life_span = "very long"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
    move_type = 1
    move_limit = 4
    speed = 5
    atk_damage = 10
    atk_speed = 0.7 *20
    atk_cooldown = 2 * 60
    max_hp= 16.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 14
    char_y_offset = 22
    char_width = 22 
    char_height = 15
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (46,21), #RightAttackFront
    (34,9), #RightAttackUp
    (43,12), #RightAttackFrontUp
    (42,27), #RightAttackFrontDown
    (40,29), #RightAttackDown
    (4,21), #LeftAttackFront
    (15,9), #LeftAttackUp
    (6,12), #LeftAttackFrontUp
    (7,27), #LeftAttackFrontDown
    (9,29)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = pygame.mixer.Sound(r'Resources\Sound\audio\dragon_wing_flap.wav')
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\dragon_howl.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 20:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key == 2 and self.anim_clock == 2:
                self.run_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                self.run_sound.play()
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Shapeshifter():
    name = "Shapeshifter"
    description = 'The shapeshifter is a so-called "look-alike", a demoniac creature without true form or shape. During a fight it turns into the reflection of its opponent, strongest at skills at which the enemy is weakest. It has no fixed life span; all wounds will heal as soon as it adopts a new shape.' 
    s_moving_type = "air - 5"
    s_speed = "variable"
    s_attack_type = "variable"
    s_attack_strength = "variable"
    s_attack_speed = "variable"
    s_attack_interval = "variable"
    s_life_span = "variable"
    s_number_of_chars = "1"
    
    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
        #type: teleport0 air1 ground2
    move_type = 1
    move_limit = 5
    speed = 5
    atk_damage = 8
    atk_speed = 1.0 *20
    atk_cooldown = 0.75 * 60
    max_hp= 9.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (34,26), #RightAttackFront
    (33,17), #RightAttackUp
    (36,19), #RightAttackFrontUp
    (35,33), #RightAttackFrontDown
    (33,35), #RightAttackDown
    (14,26), #LeftAttackFront
    (16,18), #LeftAttackUp
    (14,19), #LeftAttackFrontUp
    (14,34), #LeftAttackFrontDown
    (16,35)  #LeftAttackDown 
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    


    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Basilisk():
    name = "Basilisk"
    description = "The basilisk is a small reptile with the scabby body of a lizard. Although it is comparatively short-lived, its quick moves and deadly gaze make it a serious opponent."
    s_moving_type = "ground - 3"
    s_speed = "normal"
    s_attack_type = "eye laser"
    s_attack_strength = "high"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"

    obj_type = "player"
    #STAT NUMBERS
    team = 1
    ranged = True
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 9
    atk_speed = 1.0 *20
    atk_cooldown = 1.0 * 60
    max_hp= 5.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 15
    char_y_offset = 24
    char_width = 18 
    char_height = 12
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (38,28), #RightAttackFront
    (34,20), #RightAttackUp
    (38,23), #RightAttackFrontUp
    (39,35), #RightAttackFrontDown
    (37,36), #RightAttackDown
    (11,28), #LeftAttackFront
    (15,20), #LeftAttackUp
    (11,23), #LeftAttackFrontUp
    (10,35), #LeftAttackFrontDown
    (12,36)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\crawl.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\laser.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    run_animation = get_sprites(name, 'Run')
    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1
        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    


    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp
            
    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

##ELEMENTALS

class AirElemental():
    obj_type = "player"
    name = "Air Elemental"

    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 3
    move_limit = 20
    speed = 5
    atk_damage = 5
    atk_speed = 0.7 *20
    atk_cooldown = 0.85 * 60
    max_hp= 11.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 17
    char_y_offset = 14
    char_width = 14
    char_height = 20
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (43,28), #RightAttackFront
    (33,13), #RightAttackUp
    (44,13), #RightAttackFrontUp
    (44,36), #RightAttackFrontDown
    (33,39), #RightAttackDown
    (4,28), #LeftAttackFront
    (14,13), #LeftAttackUp
    (5,13), #LeftAttackFrontUp
    (5,36), #LeftAttackFrontDown
    (14,39)  #LeftAttackDown 
    ]

    ##AUDIO
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\air_spray.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def define_team(self, team):
        self.team = team

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class WaterElemental():
    obj_type = "player"
    name = "Water Elemental"

    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 3
    move_limit = 20
    speed = 5
    atk_damage = 6
    atk_speed = 0.5 *20
    atk_cooldown = 0.6 * 60
    max_hp= 13.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (41,27), #RightAttackFront
    (33,18), #RightAttackUp
    (37,22), #RightAttackFrontUp
    (37,34), #RightAttackFrontDown
    (34,36), #RightAttackDown
    (8,27), #LeftAttackFront
    (15,18), #LeftAttackUp
    (12,22), #LeftAttackFrontUp
    (12,34), #LeftAttackFrontDown
    (15,36)  #LeftAttackDown 
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\water_move.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\water_splash.wav')
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True
        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def define_team(self, team):
        self.team = team

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class FireElemental():
    obj_type = "player"
    name = "Fire Elemental"
    #STAT NUMBERS
    team = 0
    ranged = True
    move_type = 3
    move_limit = 20
    speed = 5
    atk_damage = 9
    atk_speed = 0.8 *20
    atk_cooldown = 1 * 60
    max_hp= 9.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 17
    char_y_offset = 17
    char_width = 14
    char_height = 18
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
    #Corrections 
    proj_correction = [
    (39,23), #RightAttackFront
    (28,10), #RightAttackUp
    (32,12), #RightAttackFrontUp
    (32,42), #RightAttackFrontDown
    (28,44), #RightAttackDown
    (9,23), #LeftAttackFront
    (20,10), #LeftAttackUp
    (16,12), #LeftAttackFrontUp
    (16,42), #LeftAttackFrontDown
    (20,44)  #LeftAttackDown
    ]

    ##AUDIO
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\fire_move1.wav'), pygame.mixer.Sound(r'Resources\Sound\audio\fire_move2.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\fire_whoosh.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False


    def define_team(self, team):
        self.team = team

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)

class EarthElemental():
    obj_type = "player"
    name = "Earth Elemental"

    #STAT NUMBERS
    team = 0
    ranged = True
        #type: teleport0 air1 ground2
    move_type = 3
    move_limit = 20
    speed = 4
    atk_damage = 9
    atk_speed = 0.5 *20
    atk_cooldown = 0.6 * 60
    max_hp= 16.5
    base_hp = max_hp
    extra_hp = 0
    hp = lambda x: x.base_hp + x.extra_hp
    alive = True
    imprisoned = False
    orientation = True
    direction = (1,0)
    performing_action = False
    can_attack = True
    char_x_offset = 17
    char_y_offset = 14
    char_width = 14
    char_height = 22
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_width = 10
    proj_height = 4
                    #Corrections 
    proj_correction = [
    (40,25), #RightAttackFront
    (17,8), #RightAttackUp
    (39,12), #RightAttackFrontUp
    (31,40), #RightAttackFrontDown
    (15,41), #RightAttackDown
    (12,25), #LeftAttackFront
    (32,8), #LeftAttackUp
    (11,12), #LeftAttackFrontUp
    (18,40), #LeftAttackFrontDown
    (33,41)  #LeftAttackDown
    ]

    ##AUDIO 
    run_sound = [pygame.mixer.Sound(r'Resources\Sound\audio\earth_move.wav')]
    fire_sound = pygame.mixer.Sound( r'Resources\Sound\audio\earth_throw.wav')

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')

    hit_animation = get_sprites(name, 'Hit')
    
    attack_front_animation = get_sprites(name, 'AttackFront')
    attack_front_up_animation = get_sprites(name, 'AttackFrontUp')
    attack_front_down_animation = get_sprites(name, 'AttackFrontDown')
    attack_up_animation = get_sprites(name, 'AttackUp')
    attack_down_animation = get_sprites(name, 'AttackDown')

    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1
    can_attack_cycle = 0

    #Masks use the opaque pixels, ignoring the transparent
    #hitbox = pygame.mask.from_surface(texture, 127)
    def handle_animation(self):
        if self.animation_change != self.current_animation:
            self.cur_key = -1
            self.animation_change = self.current_animation

        #CLOCK CHANGE
        self.anim_clock += 1

        if self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
        elif self.current_animation == "moving":
            if self.cur_key+2 > len(self.run_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 4:
                    if not self.cur_key %3:
                        sound = random.randint(0, len(self.run_sound) -1)
                        self.run_sound[sound].set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        self.run_sound[sound].play()
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.run_animation[self.cur_key]
        elif self.current_animation == "hit":
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 5:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.hit_animation[self.cur_key]
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_action = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock > 3:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_down_animation[self.cur_key]
        self.sprite = pygame.image.load(self.current_sprite)
        self.texture = pygame.transform.scale(self.sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    
    #collision
    def hitbox(self):
        return pygame.Rect(self.x + self.char_x_offset *2.6 , self.y + self.char_y_offset *2.6, self.char_width *2.6, self.char_height*2.6)
    
    def check_arena_collision(self):
        colliding = False
        if not arena_ground.contains(self.hitbox()):
            colliding = True
        for rect in arena_collisions:
            if rect != self and rect.obj_type != "player":
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_action = True
        self.can_attack = False
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        self.fire_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
        self.fire_sound.play()
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    

    def take_damage(self, damage):
        if self.alive:
            hurt_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
            hurt_sound.play()
        if damage <= self.extra_hp:
            self.extra_hp -= damage
        elif damage > self.extra_hp:
            damage -= self.extra_hp
            self.extra_hp = 0
            self.base_hp -= damage
        if self.current_animation[0] != "A":
            self.current_animation = "hit"
            self.performing_action = True
        if self.hp() <= 0:
            self.die()

    def heal(self, qtd):
        self.base_hp += qtd
        if self.base_hp > self.max_hp:
            self.base_hp = self.max_hp

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_action:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT] and self.can_attack:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN] and self.can_attack:
                    self.attack(x, -y)
        if x > 0:
            self.orientation = False
        elif x <0:
            self.orientation = True
        self.x += x* self.speed
        if self.check_arena_collision():
            self.x -= x * self.speed
            x = 0
        self.y -= y* self.speed
        if self.check_arena_collision():
            self.y += y * self.speed
            x = 0
        self.direction = (x, y)
        if not self.performing_action:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"
        if not self.can_attack:
            self.can_attack_cycle += 1
            if self.can_attack_cycle > self.atk_cooldown:
                self.can_attack_cycle = 0
                self.can_attack = True

    def die(self):
        self.alive = False

    def define_team(self, team):
        self.team = team

    def __init__(self, shapeshifter = False, hp_lock = 0):
        if shapeshifter:
            self.team = 1
            self.idle_animation = get_sprites(self.name + "Shapeshifter", 'Idle')
            self.run_animation = get_sprites(self.name + "Shapeshifter", 'Run')
            self.hit_animation = get_sprites(self.name + "Shapeshifter", 'Hit')
            self.attack_front_animation = get_sprites(self.name + "Shapeshifter", 'AttackFront')
            self.attack_front_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontUp')
            self.attack_front_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackFrontDown')
            self.attack_up_animation = get_sprites(self.name + "Shapeshifter", 'AttackUp')
            self.attack_down_animation = get_sprites(self.name + "Shapeshifter", 'AttackDown')
            self.hp_lock = hp_lock
        print(f"{self.name} instantiated")
        animation_line.append(self)


    

"""
~~~~SCENES~~~~
"""
""" 
~~~~~~MENU~~~~~~
The game's first page, here you can select "Start", "Rules" and "Exit";
I'll keep track of the "button" I am currently selecting by giving it a number,
the player will be able to keep track of the button he is selecting by a green
rectangle on the button's text.
"""
key_selected = 0

def menu():
    global playing, key_selected
    screen.blit(title_background, (0,0))
    playing = False
    if key_selected > 3:
        key_selected = 3
    if key_selected < 0:
        key_selected = 0
    label = title_gm_font.render(_GAMETITLE, 1, (00, 00, 00))
    option1 = big_gm_font.render('Start', 1, (00, 00, 00))
    option2 = big_gm_font.render('Rules', 1, (00, 00, 00))
    option3 = big_gm_font.render('Options', 1, (00, 00, 00))
    option4 = big_gm_font.render('Exit', 1, (00, 00, 00))
    # put the label object on the screen at point x=100, y=100
    screen.blit(label, ((width - len(_GAMETITLE) * 40) /2, 100))
    screen.blit(option1, ((width - len('Start') * 30) /2, 260))
    screen.blit(option2, ((width - len('Rules') * 30) /2, 340))
    screen.blit(option3, ((width - len('Options') * 30) /2, 420))
    screen.blit(option4, ((width - len('Exit') * 30) /2, 500))
    pygame.draw.rect(screen, (0,100,0), Rect((1042 - 260) / 2, 245 + key_selected * 80, 240, 80), 5)

"""
~~~~~~~~~~~~~~~~
"""

""" 
~~~~~~RULES~~~~~~
In this page the player will learn the game's basics, it will also be
possible to check the different characters' stats and abilities.
"""
rules_buttons = [(840, 570, 140, 55), (390, 194, 160, 32), (190, 194, 164, 32)]
rules_sel = 0

rules_screen = 0
rules_txt = "Archon is a chess like game where it's pieces (called icons) duel each other in order to conquer a position, there are two sides, the Light side and the Dark side, each have their own unique icons, the game's objective is to conquer all the power points or defeat all the opponent's icons. Duels are fast-paced combats where icons try to defeat each other, icons get extra health depending on the tile's color where the duel takes place, health does not accumulate after the duel so strategy is very important"
#TODO: rules
def rules():
    global rules_sel
    screen.blit(title_background, (0,0))
    #LOGIC
    
    if rules_sel > len(rules_buttons) -1:
        rules_sel = len(rules_buttons) -1
    if rules_sel < 0:
        rules_sel = 0
    #TEXT
    rules_title = medium_gm_font.render('Rules:', 1, (00, 00, 00))
    light_chars_info_button = small_gm_font.render("See Light's Icons", 1, (00,00,00))
    dark_chars_info_button = small_gm_font.render("See Dark's Icons", 1, (00,00,00))
    go_back_button = medium_gm_font.render('Back', 1, (00,00,00))

    #DRAW

    screen.blit(rules_title, (50, 50))
    screen.blit(go_back_button, (860, 580))
    screen.blit(light_chars_info_button, (200, 200))
    screen.blit(dark_chars_info_button, (400, 200))
    pygame.draw.rect(screen, (0,0,0) , Rect(rules_buttons[rules_sel][0], rules_buttons[rules_sel][1], rules_buttons[rules_sel][2], rules_buttons[rules_sel][3]), 4)

"""CHARACTER VIEWER"""
char_view_buttons = [(840, 570, 125, 55), (46, 440, 200, 50), (46, 390, 200, 50), (46, 340, 200, 50), (46, 290, 200, 50), (46, 240, 200, 50), (46, 190, 200, 50), (46, 140, 200, 50), (46, 90, 200, 50)]
char_view_sel = 0

def see_light_chars():
    global char_view_sel
    screen.fill((255, 255, 153))
    #LOGIC
    if char_view_sel > len(char_view_buttons) -1:
        char_view_sel = len(char_view_buttons) -1
    if char_view_sel < 0:
        char_view_sel = 0
    #8 buttons
    #TEXT
    valkyrie = small_medium_gm_font.render("Valkyrie", 1, (0,0,0))
    golem = small_medium_gm_font.render("Golem", 1, (0,0,0))
    unicorn = small_medium_gm_font.render("Unicorn", 1, (0,0,0))
    djinni = small_medium_gm_font.render("Djinni", 1, (0,0,0))
    wizard = small_medium_gm_font.render("Wizard", 1, (0,0,0))
    phoenix = small_medium_gm_font.render("Phoenix", 1, (0,0,0))
    archer = small_medium_gm_font.render("Archer", 1, (0,0,0))
    knight = small_medium_gm_font.render("Knight", 1, (0,0,0))
    go_back_button = medium_gm_font.render('Back', 1, (0,0,0))

    #DRAW
    screen.blit(valkyrie, (50, 100))
    screen.blit(golem, (50, 150))
    screen.blit(unicorn, (50, 200))
    screen.blit(djinni, (50, 250))
    screen.blit(wizard, (50, 300))
    screen.blit(phoenix, (50, 350))
    screen.blit(archer, (50, 400))
    screen.blit(knight, (50, 450))
    screen.blit(go_back_button, (860, 580))
    pygame.draw.rect(screen, (0,0,0) , Rect(char_view_buttons[char_view_sel][0], char_view_buttons[char_view_sel][1], char_view_buttons[char_view_sel][2], char_view_buttons[char_view_sel][3]), 4)


def see_dark_chars():
    global char_view_sel
    screen.fill((0, 0, 77))
    #LOGIC
    if char_view_sel > len(char_view_buttons) -1:
        char_view_sel = len(char_view_buttons) -1
    if char_view_sel < 0:
        char_view_sel = 0
    #8 buttons
    #TEXT
    banshee = small_medium_gm_font.render("Banshee", 1, (255, 255, 255))
    troll = small_medium_gm_font.render("Troll", 1, (255, 255, 255))
    basilisk = small_medium_gm_font.render("Basilisk", 1, (255, 255, 255))
    shapeshifter = small_medium_gm_font.render("Shapeshifter", 1, (255, 255, 255))
    sorceress = small_medium_gm_font.render("Sorceress", 1, (255, 255, 255))
    dragon = small_medium_gm_font.render("Dragon", 1, (255, 255, 255))
    manticore = small_medium_gm_font.render("Manticore", 1, (255, 255, 255))
    goblin = small_medium_gm_font.render("Goblin", 1, (255, 255, 255))
    go_back_button = medium_gm_font.render('Back', 1, (255, 255, 255))

    #DRAW
    screen.blit(banshee, (50, 100))
    screen.blit(troll, (50, 150))
    screen.blit(basilisk, (50, 200))
    screen.blit(shapeshifter, (50, 250))
    screen.blit(sorceress, (50, 300))
    screen.blit(dragon, (50, 350))
    screen.blit(manticore, (50, 400))
    screen.blit(goblin, (50, 450))
    screen.blit(go_back_button, (860, 580))
    pygame.draw.rect(screen, (255, 255, 255) , Rect(char_view_buttons[char_view_sel][0], char_view_buttons[char_view_sel][1], char_view_buttons[char_view_sel][2], char_view_buttons[char_view_sel][3]), 4)

"""CHARACTERS SHEETS"""
char_det = Knight()

_PREVIEW_SIZE = 400

def char_viewer(side):
    if side == 2:
        screen.fill((255, 255, 153))
        screen_info_c = (0,0,0)
    elif side == 4:
        screen.fill((0,0,77))
        screen_info_c = (255, 255, 255)
    else:
        screen.fill((255, 0, 0))
    #LOGIC
    picture = pygame.image.load(char_det.current_sprite)
    picture = pygame.transform.scale(picture,  (_PREVIEW_SIZE, _PREVIEW_SIZE))
    description = char_det.description

    #TEXT
    stats_tag = small_medium_gm_font.render(f'Stats:', 1, screen_info_c)
    description_tag = small_medium_gm_font.render(f'Description:', 1, screen_info_c)
    char_name = medium_gm_font.render(char_det.name, 1, screen_info_c)
    stat1 = small_gm_font.render(f'Moving type: {char_det.s_moving_type}', 1, screen_info_c)
    stat2 = small_gm_font.render(f'Speed: {char_det.s_speed}', 1, screen_info_c)
    stat3 = small_gm_font.render(f'Attack type: {char_det.s_attack_type}', 1, screen_info_c)
    stat4 = small_gm_font.render(f'Attack strength: {char_det.s_attack_strength}', 1, screen_info_c)
    stat5 = small_gm_font.render(f'Attack speed: {char_det.s_attack_speed}', 1, screen_info_c)
    stat6 = small_gm_font.render(f'Attack interval: {char_det.s_attack_interval}', 1, screen_info_c)
    stat7 = small_gm_font.render(f'Life span: {char_det.s_life_span}', 1, screen_info_c)
    stat8 = small_gm_font.render(f'Number of characters: {char_det.s_number_of_chars}', 1, screen_info_c)
    description_list = fit_in_box(description, 500, 200, screen_info_c)
    #DRAW
    screen.blit(description_tag, (475, 70))
    for i in range(len(description_list)):
        screen.blit(description_list[i], (500, 100 + 25*i))
    screen.blit(picture, (50, 100))
    pygame.draw.rect(screen, screen_info_c, (50, 100, 400, 400), 4)
    screen.blit(stats_tag, (475, 275))
    screen.blit(stat1, (500, 305))
    screen.blit(stat2, (500, 330))
    screen.blit(stat3, (500, 355))
    screen.blit(stat4, (500, 380))
    screen.blit(stat5, (500, 405))
    screen.blit(stat6, (500, 430))
    screen.blit(stat7, (500, 455))
    screen.blit(stat8, (500, 480))
    screen.blit(char_name, (50, 50))


def fit_in_box(text, width, height, color):
    div_list = []
    description_lines = []
    split_text = text.split()
    line = ""
    test_line = ""
    while len(split_text) > 0:
        test_line = line
        test_line += split_text[0] + " "
        if not (small_gm_font.size(test_line)[0] > 500):
            line += split_text[0] + " "
            split_text.pop(0)
        else:
            div_list.append(line)
            line = ""
        text = "n"
    if line != "":
        div_list.append(line)
    for j in range(0, len(div_list)):
        description_lines.append(small_gm_font.render(div_list[j], 1, color))
    return description_lines


"""
~~~~~~~~~~~~~~~~
"""

opts_buttons = [(840, 570, 140, 55), (830, 307, 154, 35), (830, 240, 154, 35)]
opts_sel = 0

#KEYS
keyboard = pygame.image.load(r'Resources\UI\Controls.png')

def options():
    global opts_sel
    #
    
    #LOGIC
    if opts_sel > len(opts_buttons) -1:
        opts_sel = len(opts_buttons) -1
    if opts_sel < 0:
        opts_sel = 0
    #TEXT
    controls = small_medium_gm_font.render("Controls", 1, (0,0,0))
    volume = small_medium_gm_font.render(f"Volume: {round(game_volume,2)}", 1, (0,0,0))
    go_back_button = medium_gm_font.render('Back', 1, (00,00,00))
    keys = small_medium_gm_font.render("Keys:", 1, (0,0,0))
    keysawsd = small_medium_gm_font.render("->  A,W,S,D moves the Light team's character and board selection.", 1, (188, 156, 88))
    keysshift = small_medium_gm_font.render("->  Left Shift selects and attacks for the Light team.", 1, (188, 156, 88))
    keysarrows = small_medium_gm_font.render("->  The arrows move the Dark team's character and board selection.", 1, (64, 94, 160))
    keysenter = small_medium_gm_font.render("->  Enter selects and attacks for the Dark team.", 1, (64, 94, 160))
    keysmute = small_medium_gm_font.render("->  By pressing M you can mute and unmute music and sound effects in game.", 1,  (255, 66, 37))
    keysnj = small_medium_gm_font.render("->  J raises and N lowers the game's volume at anytime.", 1, (214, 117, 7))
    
    #DRAW
    screen.fill((255, 255, 255))
    screen.blit(go_back_button, (860, 580))
    screen.blit(controls, (300, 60))
    screen.blit(pygame.transform.scale(keyboard, (724, 204)), (50, 100))
    screen.blit(volume, (830, 280))
    pygame.draw.polygon(screen, (0,0,0), [(877, 270), (907, 245), (937, 270)])
    pygame.draw.polygon(screen, (0,0,0), [(877, 312), (907, 337), (937, 312)])
    pygame.draw.rect(screen, (0,0,0) , Rect(opts_buttons[opts_sel][0], opts_buttons[opts_sel][1], opts_buttons[opts_sel][2], opts_buttons[opts_sel][3]), 4)
    screen.blit(keys, (200, 320))
    screen.blit(keysawsd, (7, 360))
    screen.blit(keysshift, (7, 400))
    screen.blit(keysarrows, (7, 440))
    screen.blit(keysenter, (7, 480))
    screen.blit(keysmute, (7, 520))
    screen.blit(keysnj, (7, 560))

end_clock = 0
end_clock_max = 1000

def game_ending():
    global end_clock, end_clock_max, _MAIN_BOARD
    end_clock += 1
    if end_clock > end_clock_max:
        _MAIN_BOARD = GameBoard()
        switch_scene("menu")
    if _MAIN_BOARD.game_finished == 0:
        screen.fill((164, 200, 252))
    elif _MAIN_BOARD.game_finished == 1:
        screen.fill((0, 44, 92))
    elif _MAIN_BOARD.game_finished == 2:
        screen.blit(title_background, (0,0))
    
    #TEXT
    game_end_txt = "GAME IS ENDED"
    winner_txt = ""
    game_end = medium_gm_font.render(game_end_txt, 1, (0,0,0))
    winner = medium_gm_font.render(winner_txt, 1, (0,0,0))

    if _MAIN_BOARD.game_finished == 0:
        winner_txt = "LIGHT SIDE WINS"
        game_end = medium_gm_font.render(game_end_txt, 1, (0, 44, 92))
        winner = medium_gm_font.render(winner_txt, 1, (0, 44, 92))
    elif _MAIN_BOARD.game_finished == 1:
        winner_txt = "DARK SIDE WINS"
        game_end = medium_gm_font.render(game_end_txt, 1, (164, 200, 252))
        winner = medium_gm_font.render(winner_txt, 1, (164, 200, 252))
    elif _MAIN_BOARD.game_finished == 2:
        winner_txt = "TIE"
        game_end = medium_gm_font.render(game_end_txt, 1, (0, 0, 0))
        winner = medium_gm_font.render(winner_txt, 1, (0, 0, 0))
    
    #DRAW
    screen.blit(game_end, ((width/2) - (medium_gm_font.size(game_end_txt)[0] /2), 200))
    screen.blit(winner, ((width/2) - (medium_gm_font.size(winner_txt)[0] /2), 400))
""" 
~~~~~~~~GAME~~~~~~~~
In this page the player will learn the game's basics, it will also be
possible to check the different characters' stats and abilities.
"""
#50 static tiles

text_mod = 0
def game_scene():
    global text_mod
    if text_mod < 47:
        text_mod += 1
    else:
        text_mod = 0
    screen.blit(side_choice_background, (0,0))

    #TEXT
    press_start = small_medium_gm_font.render("Press any key to start the game.", 1, (255, 255, 255))
    sel_side = small_medium_gm_font.render("Press the number to choose:", 1, (255, 255, 255))
    starts_first = small_medium_gm_font.render(("Light" if (_MAIN_BOARD.first_player == 0) else "Dark") + " starts first", 1, (255, 255, 255))
    sel_light = small_medium_gm_font.render("1: Light First", 1, (255, 255, 255))
    sel_dark = small_medium_gm_font.render("2: Dark first", 1, (255, 255, 255))
    #DRAW
    if _MAIN_BOARD.first_player != None:
        screen.blit(starts_first, ((width/2) - small_medium_gm_font.size(("Light" if (_MAIN_BOARD.first_player == 0) else "Dark") + " starts first")[0]/2, 200))
        if text_mod < 40:
            screen.blit(press_start, (300, 500))
    else:
        screen.blit(sel_side, ((width/2) - small_medium_gm_font.size("Press the number to choose:")[0]/2, 200))
        screen.blit(sel_light, (320 - small_medium_gm_font.size("1: Light First")[0], 480))
        screen.blit(sel_dark, (844 - small_medium_gm_font.size("2: Dark first")[0], 480))
"""
|||    BOARD   |||
"""

class GameBoard:
    _PIECE_SIZE = 80
    #Pieces
 
    
    _PLAYERS_COLOR = [(255, 255, 255), (0,0,0)]
    _STATIC_TILES = [(0,0), (0,1), (0,2), (0,4), (0,6), (0,7), (0,8), (1,0), (1,1), (1,3), (1,5), (1,7), (1,8), (2,0), (2,2), (2,3), (2,5), (2,6), (2,8), (3,1), (3,2), (3,3), (3,5), (3,6), (3,7), (5,1), (5,2), (5,3), (5,5), (5,6), (5,7), (6,0), (6,2), (6,3), (6,5), (6,6), (6,8), (7,0), (7,1), (7,3), (7,5), (7,7), (7,8), (8,0), (8,1), (8,2), (8,4), (8,6), (8,7), (8,8)]
                                ##LIGHT --> DARK##
    _TILE_COLORS = [(164, 200, 252), (124,156,220), (80,112,188), (56, 74, 176), (48, 32, 152), (0, 44, 92)]
    _ENERGY_SQUARES = [(0, 4), (4,0), (4,4), (4,8), (8,4)]

    board_x = 384 + 64
    board_y = 64
    light_square = pygame.image.load(r'Resources\Sprites\Tiles\220220220LightTile.png')
    board_color_data = [[ _TILE_COLORS[5] ,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5],0, _TILE_COLORS[0], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0]], [_TILE_COLORS[5] ,0,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5]], [(220,220,220) , _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0 , _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0], [_TILE_COLORS[0] ,0,_TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0]], [_TILE_COLORS[5] , _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0]]]
    board_data = None
    elementals = None
    player_turn = None
    first_player = None
    turn = 0
    game_finished = None
    moving = (0, 0)
    choosing_action = (False, None)
    choosen_spell = 0
    spell_text = ''
    
    player_board_x = 0
    player_board_y = 0
    turn_player = 0
    selected_sq = ()
    move_count = (0,0)

    light_fighter = None
    dark_fighter = None

    board_warn = ''
    board_warn_clock = 0
    board_warn_cycle = 0
    ##ENERGY SQUARE ANIMATION##
    energy_square_frames = [pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF1.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF2.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF3.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF4.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF5.png')]
    es_cur_anim = 0
    es_anim_cycle = 1
    es_clock = -1

    ##spells
    spell_selection = ''
    teleporter_placeholder = None
    exchange_placeholder = None
    reviving =  False
    chars2revive = []
    revive_opt = 0

    def __init__(self):
        Golem_Piece1 = (Golem(), pygame.transform.scale(pygame.image.load(Golem.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Golem_Piece2 = (Golem(), pygame.transform.scale(pygame.image.load(Golem.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece1 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece2 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece3 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece4 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece5 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece6 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Knight_Piece7 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Archer_Piece1 = (Archer(), pygame.transform.scale(pygame.image.load(Archer.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Archer_Piece2 = (Archer(), pygame.transform.scale(pygame.image.load(Archer.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Djinni_Piece1 = (Djinni(), pygame.transform.scale(pygame.image.load(Djinni.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Wizard_Piece1 = (Wizard(), pygame.transform.scale(pygame.image.load(Wizard.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Unicorn_Piece1 = (Unicorn(), pygame.transform.scale(pygame.image.load(Unicorn.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Unicorn_Piece2 = (Unicorn(), pygame.transform.scale(pygame.image.load(Unicorn.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Phoenix_Piece1 = (Phoenix(), pygame.transform.scale(pygame.image.load(Phoenix.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Valkyrie_Piece1 = (Valkyrie(), pygame.transform.scale(pygame.image.load(Valkyrie.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Valkyrie_Piece2 = (Valkyrie(), pygame.transform.scale(pygame.image.load(Valkyrie.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Troll_Piece1 = (Troll(), pygame.transform.scale(pygame.image.load(Troll.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Troll_Piece2 = (Troll(), pygame.transform.scale(pygame.image.load(Troll.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Sorceress_Piece1 = (Sorceress(), pygame.transform.scale(pygame.image.load(Sorceress.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Manticore_Piece1 = (Manticore(), pygame.transform.scale(pygame.image.load(Manticore.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Manticore_Piece2 = (Manticore(), pygame.transform.scale(pygame.image.load(Manticore.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece1 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece2 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece3 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece4 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece5 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece6 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Goblin_Piece7 = (Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Banshee_Piece1 = (Banshee(), pygame.transform.scale(pygame.image.load(Banshee.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Banshee_Piece2 = (Banshee(), pygame.transform.scale(pygame.image.load(Banshee.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Dragon_Piece1 = (Dragon(), pygame.transform.scale(pygame.image.load(Dragon.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Basilisk_Piece1 = (Basilisk(), pygame.transform.scale(pygame.image.load(Basilisk.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Basilisk_Piece2 = (Basilisk(), pygame.transform.scale(pygame.image.load(Basilisk.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        Shapeshifter_Piece1 = (Shapeshifter(), pygame.transform.scale(pygame.image.load(Shapeshifter.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        EarthElemental_Piece = (EarthElemental(), pygame.transform.scale(pygame.image.load(EarthElemental.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        AirElemental_Piece = (AirElemental(), pygame.transform.scale(pygame.image.load(AirElemental.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        WaterElemental_Piece = (WaterElemental(), pygame.transform.scale(pygame.image.load(WaterElemental.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))
        FireElemental_Piece = (FireElemental(), pygame.transform.scale(pygame.image.load(FireElemental.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE)))

        self.board_data = [[Valkyrie_Piece1 , Golem_Piece1, Unicorn_Piece2, Djinni_Piece1, Wizard_Piece1, Phoenix_Piece1, Unicorn_Piece1, Golem_Piece2, Valkyrie_Piece2], [Archer_Piece1, Knight_Piece1 , Knight_Piece2, Knight_Piece3, Knight_Piece4, Knight_Piece5, Knight_Piece6, Knight_Piece7, Archer_Piece2], [None , None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None , None, None, None, None, None, None, None, None], [None ,None ,None, None, None, None, None, None, None], [Manticore_Piece1 , Goblin_Piece1, Goblin_Piece2, Goblin_Piece3, Goblin_Piece4, Goblin_Piece5, Goblin_Piece6, Goblin_Piece7, Manticore_Piece2], [Banshee_Piece1 , Troll_Piece1, Basilisk_Piece1, Shapeshifter_Piece1, Sorceress_Piece1, Dragon_Piece1, Basilisk_Piece2, Troll_Piece2, Banshee_Piece2]]
        self.elementals = [EarthElemental_Piece, AirElemental_Piece, WaterElemental_Piece, FireElemental_Piece]

    ##ENERGY SQUARE ANIMATION##
    def es_handle_animation(self):
        self.es_clock += 1
        if self.es_clock == 10:
            self.es_cur_anim += 1 * self.es_anim_cycle
            self.es_clock = -1
        if self.es_cur_anim == 0 or self.es_cur_anim == len(self.energy_square_frames)-1:
            self.es_anim_cycle *= -1

    def draw_board(self):
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_color_data[i][j] != None:
                    pygame.draw.rect(screen, self.board_color_data[i][j], Rect(self.board_x + (56*i), self.board_y + 56*(j), 56, 56), 0)
        for es_sq in self._ENERGY_SQUARES:
            es_x, es_y = es_sq
            screen.blit(self.energy_square_frames[self.es_cur_anim], (self.board_x + (56*es_y), self.board_y + (56*es_x)))
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_data[i][j] != None:
                    if self.selected_sq == ():
                        screen.blit(pygame.transform.flip(pygame.transform.scale(pygame.image.load(self.board_data[i][j][0].current_sprite), (self._PIECE_SIZE, self._PIECE_SIZE)),self.board_data[i][j][0].orientation, False), (self.board_x + (56*i) - self.board_data[i][j][0].char_x_offset, self.board_y + 56*(j) - self.board_data[i][j][0].char_y_offset))
                    elif self.selected_sq[0] != self.board_data[i][j] or self.selected_sq[0][0].name in ["Wizard", "Sorceress"]:
                        screen.blit(pygame.transform.flip(pygame.transform.scale(pygame.image.load(self.board_data[i][j][0].current_sprite), (self._PIECE_SIZE, self._PIECE_SIZE)),self.board_data[i][j][0].orientation, False), (self.board_x + (56*i) - self.board_data[i][j][0].char_x_offset, self.board_y + 56*(j) - self.board_data[i][j][0].char_y_offset))
                    
    cur_color = 0
    cycle = 1

    def board_color_switch(self):
        self.cur_color += self.cycle
        if (self.cur_color == 5) or (self.cur_color == 0):
            self.cycle *= -1
        for i in range(0, 9):
            for j in range(0,9):
                if not ((i,j) in self._STATIC_TILES):
                    self.board_color_data[i][j] = self._TILE_COLORS[self.cur_color]

    def character_entry(self):
        pass

    def next_turn(self):
        self.win_condition()
        if self.player_turn == None:
            self.player_turn = self.first_player
        elif self.player_turn:
            self.player_turn = 0
        else:
            self.player_turn = 1
        
        if self.player_turn:
            self.player_board_x = 4
            self.player_board_y = 8
        else:
            self.player_board_x = 4
            self.player_board_y = 0
        
        if self.player_turn == self.first_player:
            self.turn += 1
            self.board_color_switch()
            #for every char in an energy square heal 1
            for sqr in self._ENERGY_SQUARES:
                if self.board_data[sqr[0]][sqr[1]] != None:
                    self.board_data[sqr[0]][sqr[1]][0].heal(1)
        else:
            pass
        self.update_board()
        self.board_warn =  "It is " + ("dark's" if self.player_turn == 1 else "light's") +  " turn!"

    def win_condition(self):
        game_ended = False
        ##5 power points control
        t0_controlled = 0
        t1_controlled = 0
        for power_p in self._ENERGY_SQUARES:
            if self.board_data[power_p[0]][power_p[1]] != None:
                if self.board_data[power_p[0]][power_p[1]][0].team == 1:
                    t1_controlled += 1
                elif self.board_data[power_p[0]][power_p[1]][0].team == 0:
                    t0_controlled += 1
        if t0_controlled == 5:
            game_ended = True
            self.game_finished = 0
        elif t1_controlled == 5:
            game_ended = True
            self.game_finished = 1
        ##6 icons alive
        if not game_ended:
            t0_alive = 0
            t1_alive = 0
            for i in range(0, 9):
                for j in range(0,9):
                    if self.board_data[i][j] != None:
                        if self.board_data[i][j][0].team:
                            if self.board_data[i][j][0].alive == 1:
                                t1_alive += 1
                        elif self.board_data[i][j][0].team == 0:
                            if self.board_data[i][j][0].alive:
                                t0_alive += 1
                
            if t0_alive == 0 and t1_alive == 0:
                game_ended = True
                self.game_finished = 2
            elif t0_alive == 0:
                game_ended = True
                self.game_finished = 1
            elif t1_alive == 0:
                game_ended = True
                self.game_finished = 0
        
        if game_ended:
            switch_scene("ending")
                        

    def select(self):
        if not self.choosing_action[0]:
            #sq is for square
            self.spell_text = ''
            if self.selected_sq == ():
                if self.board_data[self.player_board_y][self.player_board_x] != None:
                    if not self.board_data[self.player_board_y][self.player_board_x][0].imprisoned and self.board_data[self.player_board_y][self.player_board_x][0].team == self.player_turn:
                        self.selected_sq = (self.board_data[self.player_board_y][self.player_board_x],(self.player_board_x, self.player_board_y))
                        self.board_warn =  self.selected_sq[0][0].name + '  [' + self.selected_sq[0][0].s_moving_type + ']'
                        self.move_count = (0,0)
                    elif self.board_data[self.player_board_y][self.player_board_x][0].imprisoned:
                        self.board_warn = "Alas, game icon is imprisoned"
            else:
                is_elemental = "Elemental" in self.selected_sq[0][0].name
                if self.board_data[self.player_board_y][self.player_board_x] == None and (not is_elemental):
                    self.board_data[self.player_board_y][self.player_board_x] = self.selected_sq[0]
                    self.board_data[self.selected_sq[1][1]][self.selected_sq[1][0]] = None
                    self.board_warn =  ''
                    self.next_turn()
                    self.selected_sq = ()
                elif self.board_data[self.player_board_y][self.player_board_x] != None:
                    if self.board_data[self.player_board_y][self.player_board_x][0].team == self.selected_sq[0][0].team and not is_elemental:
                        if self.board_data[self.player_board_y][self.player_board_x][0].name == self.selected_sq[0][0].name and self.selected_sq[0][0].name in ["Wizard", "Sorceress"]:
                            self.choosing_action = (True, self.selected_sq[0][0])
                            self.choosen_spell = 0
                        elif self.board_data[self.player_board_y][self.player_board_x][0].name == self.selected_sq[0][0].name:
                            self.selected_sq = ()
                        self.board_warn = ''
                    elif not self.board_data[self.player_board_y][self.player_board_x] == self.selected_sq[0]:
                        if is_elemental and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                            if self.board_data[self.player_board_y][self.player_board_x][0].team != self.selected_sq[0][0].team:
                                if self.board_data[self.player_board_y][self.player_board_x][0].team == 0:
                                    self.light_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                                    self.dark_fighter = self.selected_sq[0]
                                else:
                                    self.light_fighter = self.selected_sq
                                    self.dark_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                                start_duel(self.selected_sq[0][0], self.board_data[self.player_board_y][self.player_board_x][0], (self.player_board_x, self.player_board_y))
                                self.board_warn =  ''
                                self.selected_sq = ()
                        elif is_elemental: 
                            self.spell_text = 'power points are spell proof'
                        else:
                            if self.board_data[self.player_board_y][self.player_board_x][0].team == 0:
                                self.light_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                                self.dark_fighter = self.selected_sq
                            else:
                                self.light_fighter = self.selected_sq
                                self.dark_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                            start_duel(self.selected_sq[0][0], self.board_data[self.player_board_y][self.player_board_x][0], (self.player_board_x, self.player_board_y))
                            self.board_warn =  ''
                            self.selected_sq = ()

    def move_on_board(self, direc, counting = True):
        def check_move(vertical, horizontal):
            if not counting:
                return True
            if self.selected_sq == ():
                return True
            move_count = (self.move_count[0] + vertical, self.move_count[1] + horizontal)
            if self.selected_sq[0][0].move_type == 0 or self.selected_sq[0][0].move_type ==1:
                if self.selected_sq[0][0].move_limit < max(abs(move_count[0]), abs(move_count[1])):
                    self.board_warn = "You have moved your limit"
                    return False
            elif self.selected_sq[0][0].move_type == 2:
                if self.selected_sq[0][0].move_limit < (abs(move_count[0]) + abs(move_count[1])):
                    self.board_warn = "You have moved your limit"
                    return False
                if self.board_data[self.player_board_y + horizontal][self.player_board_x + vertical] != None:
                    if self.board_data[self.player_board_y + horizontal][self.player_board_x + vertical][0].team == self.selected_sq[0][0].team and self.board_data[self.player_board_y + horizontal][self.player_board_x + vertical][0] != self.selected_sq[0][0]:
                        return False
            return True
        x, y = direc
        if self.player_board_x + x > -1 and self.player_board_x + x < 9 and check_move(x, 0):
            self.player_board_x += x
            self.move_count = (self.move_count[0] + x, self.move_count[1])
            if self.board_warn == "You have moved your limit" and self.selected_sq != ():
                self.board_warn =  self.selected_sq[0][0].name + ' (' + self.selected_sq[0][0].s_moving_type + ')'
        if self.player_board_y + y > -1 and self.player_board_y + y < 9 and check_move(0, y):
            self.player_board_y += y
            self.move_count = (self.move_count[0], self.move_count[1] + y)
            if self.board_warn == "You have moved your limit" and self.selected_sq != ():
                self.board_warn =  self.selected_sq[0][0].name + ' (' + self.selected_sq[0][0].s_moving_type + ')'
        
    
        
    def get_info(self):
        return self.board_warn.upper()
    
    def move_selected_piece(self):
        if not self.selected_sq[0][0].name in ["Wizard", "Sorceress"]:
            screen.blit(pygame.transform.flip(self.selected_sq[0][1],self.selected_sq[0][0].orientation, False), (self.board_x + (56*self.player_board_y) - self.selected_sq[0][0].char_x_offset, self.board_y + (56*self.player_board_x) - self.selected_sq[0][0].char_y_offset))

    def finished_fight(self, piece, position):
        if self.teleporter_placeholder != None:
            if self.teleporter_placeholder == piece:
                if piece == 0:
                    self.board_data[self.light_fighter[1][0]][self.light_fighter[1][1]] = None
                    self.board_data[position[1]][position[0]] = self.light_fighter[0]
                    self.teleporter_placeholder = None
                elif piece == 1:
                    self.board_data[self.dark_fighter[1][0]][self.dark_fighter[1][1]] = None
                    self.board_data[position[1]][position[0]] = self.dark_fighter[0]
                    self.teleporter_placeholder = None
        else:
            if piece == 0:
                if not "Elemental" in self.light_fighter[0][0].name:
                    self.board_data[self.light_fighter[1][1]][self.light_fighter[1][0]] = None
                self.board_data[position[1]][position[0]] = self.light_fighter[0]
            elif piece == 1:
                if not "Elemental" in self.dark_fighter[0][0].name:
                    self.board_data[self.dark_fighter[1][1]][self.dark_fighter[1][0]] = None
                self.board_data[position[1]][position[0]] = self.dark_fighter[0]
        self.light_fighter = None
        self.dark_fighter = None

    def update_board(self):
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_data[i][j] != None:
                    if self.board_data[i][j][0].team:
                        self.board_data[i][j][0].orientation = True
                    else:
                        self.board_data[i][j][0].orientation = False
                    if not self.board_data[i][j][0].alive or 'Elemental' in self.board_data[i][j][0].name:
                        self.board_data[i][j] = None
                        continue
                    if self.cur_color == 0 and self.board_data[i][j][0].team == 0:
                        self.board_data[i][j][0].imprisoned = False
                    elif self.cur_color == 5 and self.board_data[i][j][0].team == 1:
                        self.board_data[i][j][0].imprisoned = False
    
    def animate_board(self):
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_data[i][j] != None:
                    self.board_data[i][j][0].move(0)
    
    def show_spells(self):
        self.board_warn = "Choose your action"
        if self.choosen_spell < len(self.choosing_action[1].spells):
            self.spell_text = self.choosing_action[1].spells[self.choosen_spell]
    
    def perform_spell(self):
        if self.choosing_action[1].spells[self.choosen_spell] == "Summon Elemental":
            if self.choosing_action[1].name == "Wizard":
                elemental = self.elementals[random.randint(0, len(self.elementals) -1)]
                self.spawn_anywhere(elemental, 0)
                self.choosing_action[1].spells.remove("Summon Elemental")
                self.choosing_action[1].casting_spell = True
                self.board_warn = ("An " if elemental[0].name[0] in "A E" else "A ") + elemental[0].name + " appears!"
                self.spell_text = "Send it to the target"
            elif self.choosing_action[1].name == "Sorceress":
                elemental = self.elementals[random.randint(0, len(self.elementals) -1)]
                self.spawn_anywhere(elemental, 1)
                self.choosing_action[1].spells.remove("Summon Elemental")
                self.choosing_action[1].casting_spell = True
                self.board_warn = ("An " if elemental[0].name[0] in "A E" else "A ") + elemental[0].name + " appears!"
                self.spell_text = "Send it to the target"
            self.choosing_action = (False, None)
            self.choosen_spell = 0
        elif self.choosing_action[1].spells[self.choosen_spell] == "Shift Time":
            self.choosing_action[1].spells.remove("Shift Time")
            self.choosing_action[1].casting_spell = True
            self.board_warn = "Shift Time"
            self.spell_text = "The flow of time is reversed"
            self.cycle *= -1
            self.choosing_action = (False, None)
            self.selected_sq = ()
            self.choosen_spell = 0
            self.next_turn()
        elif self.choosing_action[1].spells[self.choosen_spell] == "Imprison":
            self.choosing_action[1].spells.remove("Imprison")
            self.choosing_action[1].casting_spell = True
            self.spell_selection = 'imprison'
            self.board_warn = "Imprison"
            self.spell_text = "Which foe will you imprison?" 
        elif self.choosing_action[1].spells[self.choosen_spell] == "Heal":
            self.choosing_action[1].spells.remove("Heal")
            self.choosing_action[1].casting_spell = True
            self.spell_selection = 'heal'
            self.board_warn = "Heal"
            self.spell_text = "Which icon will you heal?" 
        elif self.choosing_action[1].spells[self.choosen_spell] == "Teleport":
            self.choosing_action[1].casting_spell = True
            self.spell_selection = 'teleport'
            self.board_warn = "Teleport"
            self.spell_text = "Which icon will you teleport?"
        elif self.choosing_action[1].spells[self.choosen_spell] == "Exchange":
            self.choosing_action[1].spells.remove("Exchange")
            self.choosing_action[1].casting_spell = True
            self.spell_selection = 'exchange'
            self.board_warn = "Exchange"
            self.spell_text = "Choose an Icon to transpose"
        elif self.choosing_action[1].spells[self.choosen_spell] == "Revive":
            self.spell_selection = 'revive'
            allies_dead = self.find_dead_allies(self.choosing_action[1].team)
            if len(allies_dead) == 0:
                self.board_warn = "Happily Master,"
                self.spell_text = "all your icons live"  
                self.choosing_action = (False, None)
                self.selected_sq = ()
                self.choosen_spell = 0
                self.spell_selection = ''
            else:
                if not self.check_charmed():
                    self.board_warn = "Alas there is no opening"
                    self.spell_text = "in the charmed square"  
                    self.choosing_action = (False, None)
                    self.selected_sq = ()
                    self.choosen_spell = 0
                    self.spell_selection = ''
                    return
                self.choosing_action[1].spells.remove("Revive")
                self.choosing_action[1].casting_spell = True
                self.reviving = True
                for char in allies_dead:
                    while allies_dead.count(char)-1:
                        allies_dead.remove(char)
                allies_dead = self.transform(allies_dead)
                self.chars2revive = allies_dead
        elif self.choosing_action[1].spells[self.choosen_spell] == "Cease Conjuring":
            self.choosing_action = (False, None)
            self.selected_sq = ()
            self.choosen_spell = 0
            self.spell_selection = ''
            self.board_warn = ''
            self.spell_text = ''  

            
    def transform(self, chars):
        ret = []
        for char in chars:
            if char == "Knight":
                ret.append((Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Archer":
                ret.append((Archer(), pygame.transform.scale(pygame.image.load(Archer.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Unicorn":
                ret.append((Unicorn(), pygame.transform.scale(pygame.image.load(Unicorn.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Valkyrie":
                ret.append((Valkyrie(), pygame.transform.scale(pygame.image.load(Valkyrie.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Golem":
                ret.append((Golem(), pygame.transform.scale(pygame.image.load(Golem.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Djinni":
                ret.append((Djinni(), pygame.transform.scale(pygame.image.load(Djinni.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Wizard":
                ret.append((Wizard(), pygame.transform.scale(pygame.image.load(Wizard.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Phoenix":
                ret.append((Phoenix(), pygame.transform.scale(pygame.image.load(Phoenix.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Goblin":
                ret.append((Goblin(), pygame.transform.scale(pygame.image.load(Goblin.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Manticore":
                ret.append((Manticore(), pygame.transform.scale(pygame.image.load(Manticore.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Banshee":
                ret.append((Banshee(), pygame.transform.scale(pygame.image.load(Banshee.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Troll":
                ret.append((Troll(), pygame.transform.scale(pygame.image.load(Troll.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Basilisk":
                ret.append((Basilisk(), pygame.transform.scale(pygame.image.load(Basilisk.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Shapeshifter":
                ret.append((Shapeshifter(), pygame.transform.scale(pygame.image.load(Shapeshifter.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Sorceress":
                ret.append((Sorceress(), pygame.transform.scale(pygame.image.load(Sorceress.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
            elif char == "Dragon":
                ret.append((Dragon(), pygame.transform.scale(pygame.image.load(Dragon.current_sprite),  (self._PIECE_SIZE, self._PIECE_SIZE))))
        return ret
    
    def spawn_anywhere(self, piece, team = -1):
        if team == -1:
            if not piece[0].team:
                self.selected_sq = (piece, (4, 0))
            elif piece[0].team:
                self.selected_sq = (piece, (4, 8))
        else:
            if team == 0:
                piece[0].define_team(0)
                self.selected_sq = (piece, (4, 0))
            elif team == 1:
                piece[0].define_team(1)
                self.selected_sq = (piece, (4, 8))

    def heal(self):
        if self.board_data[self.player_board_y][self.player_board_x] != None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
            if self.board_data[self.player_board_y][self.player_board_x][0].team == self.selected_sq[0][0].team:
                self.board_data[self.player_board_y][self.player_board_x][0].heal(20)
                self.spell_selection = ''
                self.spell_text = ''
                self.choosing_action = (False, None)
                self.selected_sq = ()
                self.choosen_spell = 0
                self.next_turn()
        elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
            self.board_warn =  'power points are spell proof'
            self.spell_text = 'Cancelling spell'
            self.choosing_action = (False, None)
            self.choosen_spell = 0
            self.spell_selection = ''  

    def imprison(self):
        if self.board_data[self.player_board_y][self.player_board_x] != None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
            if self.board_data[self.player_board_y][self.player_board_x][0].team != self.selected_sq[0][0].team:
                self.board_data[self.player_board_y][self.player_board_x][0].imprisoned = True
                self.spell_selection = ''
                self.spell_text = ''
                self.choosing_action = (False, None)
                self.selected_sq = ()
                self.choosen_spell = 0
                self.next_turn()
        elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
            self.board_warn =  'power points are spell proof'
            self.spell_text = 'Cancelling spell'
            self.choosing_action = (False, None)
            self.choosen_spell = 0
            self.spell_selection = ''
            
    
    def teleport(self):
        if self.teleporter_placeholder == None:
            if self.board_data[self.player_board_y][self.player_board_x] != None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                if self.board_data[self.player_board_y][self.player_board_x][0].team == self.selected_sq[0][0].team:
                    self.teleporter_placeholder = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                    self.spell_text = 'where will you teleport it?'
            elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                self.board_warn =  'power points are spell proof'
                self.spell_text = 'Cancelling spell'
                self.choosing_action = (False, None)
                self.choosen_spell = 0
                self.spell_selection = ''
        elif self.teleporter_placeholder != None:
            if self.board_data[self.player_board_y][self.player_board_x] == None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                if (self.player_board_y, self.player_board_x) != self.teleporter_placeholder[1]:
                    self.choosing_action[1].spells.remove("Teleport")
                    self.board_data[self.player_board_y][self.player_board_x] = self.teleporter_placeholder[0]
                    self.board_data[self.teleporter_placeholder[1][0]][self.teleporter_placeholder[1][1]] = None
                    self.spell_selection = ''
                    self.spell_text = ''
                    self.choosing_action = (False, None)
                    self.selected_sq = ()
                    self.choosen_spell = 0
                    self.next_turn()
                    self.teleporter_placeholder = None
            elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                self.spell_text = "power points are spell proof"
            elif self.board_data[self.player_board_y][self.player_board_x] != None:
                if (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                    self.spell_text = "power points are spell proof"
                elif self.board_data[self.player_board_y][self.player_board_x][0].team != self.selected_sq[0][0].team:
                    self.choosing_action[1].spells.remove("Teleport")
                    if self.board_data[self.player_board_y][self.player_board_x][0].team == 0:
                        self.light_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                        self.dark_fighter = self.teleporter_placeholder
                    else:
                        self.light_fighter = self.teleporter_placeholder
                        self.dark_fighter = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                    start_duel(self.teleporter_placeholder[0][0], self.board_data[self.player_board_y][self.player_board_x][0], (self.player_board_x, self.player_board_y))
                    self.spell_selection = ''
                    self.spell_text = ''
                    self.choosing_action = (False, None)
                    self.selected_sq = ()
                    self.choosen_spell = 0
                    self.teleporter_placeholder = self.teleporter_placeholder[0][0].team

    def exchange(self):
        if self.exchange_placeholder == None:
            if self.board_data[self.player_board_y][self.player_board_x] != None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                if self.board_data[self.player_board_y][self.player_board_x][0].team == self.selected_sq[0][0].team:
                    self.exchange_placeholder = (self.board_data[self.player_board_y][self.player_board_x], (self.player_board_y, self.player_board_x))
                    self.spell_text = 'exchange with which icon?'
            elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                self.board_warn =  'power points are spell proof'
                self.spell_text = 'Cancelling spell'
                self.choosing_action = (False, None)
                self.choosen_spell = 0
                self.spell_selection = ''
                self.exchange_placeholder = None
        elif self.exchange_placeholder != None:
            if self.board_data[self.player_board_y][self.player_board_x] != None and not (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                if (self.player_board_y, self.player_board_x) != self.exchange_placeholder[1]:
                    exchanged = self.board_data[self.player_board_y][self.player_board_x]
                    self.board_data[self.player_board_y][self.player_board_x] = self.exchange_placeholder[0]
                    self.board_data[self.exchange_placeholder[1][0]][self.exchange_placeholder[1][1]] = exchanged
                    self.spell_selection = ''
                    self.spell_text = ''
                    self.choosing_action = (False, None)
                    self.selected_sq = ()
                    self.choosen_spell = 0
                    self.next_turn()
                    self.exchange_placeholder = None
            elif self.board_data[self.player_board_y][self.player_board_x] != None and (self.player_board_y, self.player_board_x) in self._ENERGY_SQUARES:
                self.spell_text = "power points are spell proof"

    def find_dead_allies(self, team):
        dead = []
        if team == 0:
            dead = ["Golem", "Golem", "Knight", "Knight", "Knight", "Knight", "Knight", "Knight", "Knight", "Valkyrie", "Valkyrie", "Unicorn", "Unicorn", "Djinni", "Phoenix", "Wizard", "Archer", "Archer"]
        elif team == 1:
            dead = ["Manticore", "Manticore", "Goblin", "Goblin", "Goblin", "Goblin", "Goblin", "Goblin", "Goblin", "Banshee", "Banshee", "Troll", "Troll", "Basilisk", "Basilisk", "Sorceress", "Dragon", "Shapeshifter"] 
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_data[i][j] != None:
                    if self.board_data[i][j][0].team == team:
                        if self.board_data[i][j][0].alive:
                            dead.remove(self.board_data[i][j][0].name)
        return dead


    def select_revival(self, change):
        if change == -1:
            if self.revive_opt > 0:
                self.revive_opt -= 1
        elif change == 1:
            if self.revive_opt < len(self.chars2revive) -1:
                self.revive_opt += 1
        elif change == 0:
            self.spawn_anywhere(self.chars2revive[self.revive_opt])
            self.revive_opt = 0
            self.chars2revive = []
            self.reviving = False
        elif change == 2:
            if self.check_charmed(1):
                self.board_data[self.player_board_y][self.player_board_x] = self.selected_sq[0]
                self.spell_selection = ''
                self.selected_sq = ()
                self.board_warn = ""
                self.spell_text = ""  
                self.choosing_action = (False, None)
                self.choosen_spell = 0
                self.next_turn()

    def check_charmed(self, opt=0):
        if opt == 0:
            if self.player_board_x > 0:
                if self.board_data[self.player_board_y][self.player_board_x - 1] == None:
                    return True
            if self.player_board_x < 8:
                if self.board_data[self.player_board_y][self.player_board_x + 1] == None:
                    return True
            if self.player_board_y > 0:
                if self.board_data[self.player_board_y - 1][self.player_board_x] == None:
                    return True
            if self.player_board_y < 8:
                if self.board_data[self.player_board_y + 1][self.player_board_x] == None:
                    return True
            if self.player_board_y < 8 and self.player_board_x < 8:
                if self.board_data[self.player_board_y + 1][self.player_board_x + 1] == None:
                    return True
            if self.player_board_y > 0 and self.player_board_x < 8:
                if self.board_data[self.player_board_y - 1][self.player_board_x + 1] == None:
                    return True
            if self.player_board_y > 0 and self.player_board_x > 0:
                if self.board_data[self.player_board_y - 1][self.player_board_x - 1] == None:
                    return True
            if self.player_board_y < 8 and self.player_board_x > 0:
                if self.board_data[self.player_board_y + 1][self.player_board_x - 1] == None:
                    return True
            return False
        elif opt == 1:
            if not self.board_data[self.player_board_y][self.player_board_x] == None:
                return False
            if self.player_board_x > 0:
                if self.board_data[self.player_board_y][self.player_board_x - 1] != None:
                    if self.board_data[self.player_board_y][self.player_board_x - 1][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_x < 8:
                if self.board_data[self.player_board_y][self.player_board_x + 1] != None:
                    if self.board_data[self.player_board_y][self.player_board_x + 1][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y > 0:
                if self.board_data[self.player_board_y - 1][self.player_board_x] != None:
                    if self.board_data[self.player_board_y - 1][self.player_board_x][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y < 8:
                if self.board_data[self.player_board_y + 1][self.player_board_x] != None:
                    if self.board_data[self.player_board_y + 1][self.player_board_x][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y < 8 and self.player_board_x < 8:
                if self.board_data[self.player_board_y + 1][self.player_board_x + 1] != None:
                    if self.board_data[self.player_board_y + 1][self.player_board_x + 1][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y > 0 and self.player_board_x < 8:
                if self.board_data[self.player_board_y - 1][self.player_board_x + 1] != None:
                    if self.board_data[self.player_board_y - 1][self.player_board_x + 1][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y > 0 and self.player_board_x > 0:
                if self.board_data[self.player_board_y - 1][self.player_board_x - 1] != None:
                    if self.board_data[self.player_board_y - 1][self.player_board_x - 1][0].name in ["Wizard", "Sorceress"]:
                        return True
            if self.player_board_y < 8 and self.player_board_x > 0:
                if self.board_data[self.player_board_y + 1][self.player_board_x - 1] != None:
                    if self.board_data[self.player_board_y + 1][self.player_board_x - 1][0].name in ["Wizard", "Sorceress"]:
                        return True

_MAIN_BOARD = GameBoard()

def board():
    #LOGIC
    turn_number = medium_gm_font.render(f'Turn: {_MAIN_BOARD.turn}', 1, (00, 00, 00))
    player_info = small_gm_font.render(_MAIN_BOARD.get_info(), 1, (00, 00, 00))
    spell_string = small_gm_font.render(_MAIN_BOARD.spell_text.upper(), 1, (00, 00, 00))
    
    if _MAIN_BOARD.turn == 0:
        _MAIN_BOARD.character_entry()


    #DRAW
    screen.fill((112, 40, 0))
    screen.blit(turn_number, (50, 50))
    _MAIN_BOARD.animate_board()
    

    _MAIN_BOARD.draw_board()
    if _MAIN_BOARD.reviving:
        for i in range(0, len(_MAIN_BOARD.chars2revive)):
            if _MAIN_BOARD.chars2revive[i][0].team:
                pygame.draw.rect(screen, (0, 44, 92), Rect(960, _MAIN_BOARD.board_y + 56*i + 4*i, 56, 56), 0)
                screen.blit(_MAIN_BOARD.chars2revive[i][1], (960 - _MAIN_BOARD.chars2revive[i][0].char_x_offset, _MAIN_BOARD.board_y + 56*i - _MAIN_BOARD.chars2revive[i][0].char_y_offset))
            elif not _MAIN_BOARD.chars2revive[i][0].team:
                pygame.draw.rect(screen, (164, 200, 252), Rect(384, _MAIN_BOARD.board_y + 56*i + 4*i, 56, 56), 0)
                screen.blit(_MAIN_BOARD.chars2revive[i][1], (384 - _MAIN_BOARD.chars2revive[i][0].char_x_offset, _MAIN_BOARD.board_y + 56*i - _MAIN_BOARD.chars2revive[i][0].char_y_offset))
        if _MAIN_BOARD.selected_sq[0][0].team == 0:
            pygame.draw.rect(screen, _MAIN_BOARD._PLAYERS_COLOR[_MAIN_BOARD.turn_player], Rect(384, _MAIN_BOARD.board_y + (56*_MAIN_BOARD.revive_opt) + (4*_MAIN_BOARD.revive_opt) , 56, 56), 4)
        else:
            pygame.draw.rect(screen, _MAIN_BOARD._PLAYERS_COLOR[_MAIN_BOARD.turn_player], Rect(960, _MAIN_BOARD.board_y + (56*_MAIN_BOARD.revive_opt) + (4*_MAIN_BOARD.revive_opt) , 56, 56), 4)
    else:
        pygame.draw.rect(screen, _MAIN_BOARD._PLAYERS_COLOR[_MAIN_BOARD.turn_player], Rect(_MAIN_BOARD.board_x + (56*_MAIN_BOARD.player_board_y), _MAIN_BOARD.board_y + (56*_MAIN_BOARD.player_board_x), 56, 56), 4)
    if _MAIN_BOARD.selected_sq != ():
            _MAIN_BOARD.move_selected_piece()
    pygame.draw.rect(screen, (80, 112, 188), Rect(25, 500, 320, 80), 0)
    pygame.draw.rect(screen, (56, 74, 176), Rect(25, 500, 320, 80), 3)
    screen.blit(player_info, (40, 520))
    screen.blit(spell_string, (40, 545))
    


#---
dueler1 = None
dueler0 = None
arena_collisions = []

dead = []
arena_finish_clock = 0
arena_finish_var = 0
fighting_pos = (0,0)

def start_duel(fighter1, fighter2, pos):
    global current_scene, dueler1, dueler0, arena_finish_clock, arena_finish_var, fighting_pos, transition
    transition = 3
    arena_collisions.clear()
    dead.clear()
    arena_finish_clock = 15
    arena_finish_var = 0
    switch_scene("arena")
    fighting_pos = pos
    if fighter1.team == 1:
        dueler1 = fighter1
        dueler0 = fighter2
    else:
        dueler1 = fighter2
        dueler0 = fighter1
    if dueler1.name == "Shapeshifter":
        if dueler0.name == "Knight":
            dueler1 = Knight(True, dueler0.base_hp)
        elif dueler0.name == "Archer":
            dueler1 = Archer(True, dueler0.base_hp)
        elif dueler0.name == "Unicorn":
            dueler1 = Unicorn(True, dueler0.base_hp)
        elif dueler0.name == "Valkyrie":
            dueler1 = Valkyrie(True, dueler0.base_hp)
        elif dueler0.name == "Golem":
            dueler1 = Golem(True, dueler0.base_hp)
        elif dueler0.name == "Djinni":
            dueler1 = Djinni(True, dueler0.base_hp)
        elif dueler0.name == "Wizard":
            dueler1 = Wizard(True, dueler0.base_hp)
        elif dueler0.name == "Phoenix":
            dueler1 = Phoenix(True, dueler0.base_hp)
        elif dueler0.name == "Fire Elemental":
            dueler1 = FireElemental(True, dueler0.base_hp)
        elif dueler0.name == "Water Elemental":
            dueler1 = WaterElemental(True, dueler0.base_hp)
        elif dueler0.name == "Air Elemental":
            dueler1 = AirElemental(True, dueler0.base_hp)
        elif dueler0.name == "Earth Elemental":
            dueler1 = EarthElemental(True, dueler0.base_hp)
    if _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (164, 200, 252):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 7
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 0
    elif _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (124,156,220):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 6
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 1
    elif _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (80,112,188):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 4
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 3
    elif _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (56, 74, 176):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 3
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 4
    elif _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (48, 32, 152):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 1
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 6
    elif _MAIN_BOARD.board_color_data[pos[1]][pos[0]] == (0, 44, 92):
        if not "Elemental" in dueler0.name:
            dueler0.extra_hp = 0
        if not "Elemental" in dueler1.name:
            dueler1.extra_hp = 7
    dueler0.x = 180 - dueler0.char_x_offset * 2.16
    dueler0.y = 280 - dueler0.char_y_offset * 2.16
    dueler1.x = 804 - dueler1.char_x_offset * 2.16
    dueler1.y = 280 - dueler1.char_y_offset * 2.16
    dueler1.orientation = True
    dueler0.orientation = False
    arena_collisions.append(dueler1)
    arena_collisions.append(dueler0)
    for _ in range(0, random.randint(4, 9)):
        arena_collisions.append(Barrier(random.randint(200, 640), random.randint(0, 480), random.randint(0, 2)))

def finish_duel(winner):
    global current_scene, dueler1, dueler0
    dueler0.extra_hp = 0
    dueler1.extra_hp = 0
    dueler1 = None
    dueler0 = None
    if winner == 0:
        _MAIN_BOARD.finished_fight(0, fighting_pos)
    elif winner == 1:
        _MAIN_BOARD.finished_fight(1, fighting_pos)
    _MAIN_BOARD.next_turn()
    light_projectiles.clear()
    dark_projectiles.clear()
    arena_collisions.clear()
    obstacles.clear()
    switch_scene("game")
    
fg_begun = False
arena_ground = pygame.Rect(80, 8, 864, 624)
light_projectiles = []
dark_projectiles = []
light_areas = []
dark_areas = []
obstacles = []


def arena():
    ##dueler0 Light, Dueler1 Dark
    global dueler1, dueler0, arena_finish_clock, arena_finish_var, transition
    screen.fill((255, 0, 0))
    #Logic
    dueler1_hp = 0
    dueler0_hp = 0
    if not dueler1.alive:
        dead.append(dueler1)
        dueler1_hp = 0
    else:
        if not transition:
            dueler1.move(2)
        dueler1_hp = dueler1.hp()
    if not dueler0.alive:
        dead.append(dueler0)
        dueler0_hp = 0
    else:
        if not transition:
            dueler0.move(1)
        dueler0_hp = dueler0.hp()
    for proj in light_projectiles:
        proj.move()
    for proj in dark_projectiles:
        proj.move()
    for area in dark_areas:
        area.move()
    for area in light_areas:
        area.move()

    for obs in arena_collisions:
        if obs.obj_type == "barrier":
            obs.update()
    
    if len(dead) != 0:
        if arena_finish_clock <= 0:
            if dueler0.alive and not dueler1.alive:
                return finish_duel(0)
            elif dueler1.alive and not dueler0.alive:
                return finish_duel(1)
            else:
                return finish_duel(None)
        else:
            arena_finish_var += 1
            if arena_finish_var > 10:
                arena_finish_var = 0
                arena_finish_clock -= 1
    #Draw
    pygame.draw.rect(screen, _MAIN_BOARD.board_color_data[fighting_pos[1]][fighting_pos[0]], arena_ground, 0)
    ##dueler's stats
    pygame.draw.rect(screen, (255, 255, 153), (10,(632 - dueler0_hp * 26), 50, dueler0_hp*26), 0)
    pygame.draw.rect(screen, (0, 0, 77), (964, (632 - dueler1_hp * 26), 50, dueler1_hp*26), 0)
    for area in light_areas:
        screen.blit(area.sprite, (area.x, area.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), area.hitbox(), 0)
    for area in dark_areas:
        screen.blit(area.sprite, (area.x, area.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), area.hitbox(), 0)
    for obst in arena_collisions:
        if obst.obj_type == "barrier":
            screen.blit(obst.sprite, (obst.x, obst.y))
            if _DEBUG:
                pygame.draw.rect(screen, (0,0,0), obst.hitbox(), 0)
    if dueler1.alive:
        screen.blit(pygame.transform.flip(dueler1.texture, dueler1.orientation, False), (dueler1.x, dueler1.y))
    if dueler0.alive:
        screen.blit(pygame.transform.flip(dueler0.texture, dueler0.orientation, False), (dueler0.x, dueler0.y))
    for proj in light_projectiles:
        if proj.ranged:
            screen.blit(proj.sprite, (proj.x, proj.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), proj.hitbox(), 0)
    for proj in dark_projectiles:
        if proj.ranged:
            screen.blit(proj.sprite, (proj.x, proj.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), proj.hitbox(), 0)
    if _DEBUG:
        pygame.draw.rect(screen, (155,155,155) , dueler0.hitbox(), 0) #hitbox
    if _DEBUG:
        pygame.draw.rect(screen, (155,155,155) , dueler1.hitbox(), 0)


""" 
~~~~~~~~~~~~~~~~~~
"""

es_mlsecs = 0
running = True
transition = 0 
trans_clock = 0
game_volume = 0.5
pygame.mixer.music.set_volume(game_volume)

def switch_scene(scene, board = False):
    global current_scene, playing, title_music, board_music, arena_music
    if current_scene != scene:
        if scene == "menu" and current_scene in ["menu", "rules", "options"]:
            current_scene = scene
            return
        elif scene == "rules" and current_scene in ["menu", "rules", "options"]:
            current_scene = scene
            return
        elif scene == "options" and current_scene in ["menu", "rules", "options"]:
            current_scene = scene
            return
        elif scene in ["menu", "rules", "options"]:
            pygame.mixer.music.load(title_music)
            pygame.mixer.music.play(-1)
        elif scene == "game" and playing:
            pygame.mixer.music.load(board_music)
            pygame.mixer.music.play(-1)
        elif scene == "arena":
            pygame.mixer.music.load(arena_music)
            pygame.mixer.music.play(-1)
        elif scene == "ending":
            pygame.mixer.music.load(end_music)
            pygame.mixer.music.play(0)
        current_scene = scene
    elif board:
        pygame.mixer.music.load(board_music)
        pygame.mixer.music.play(-1)


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            #menu keys
            if event.type == pygame.KEYDOWN:
                if event.key == K_m:
                    if pygame.mixer.music.get_volume() > 0.04:
                        pygame.mixer.music.set_volume(0)
                    elif pygame.mixer.music.get_volume() == 0 :
                        pygame.mixer.music.set_volume(game_volume)
                if event.key == K_n:
                    if game_volume > 0.04:
                        game_volume -= 0.05
                        pygame.mixer.music.set_volume(game_volume)
                if event.key == K_j:
                    if game_volume < 0.96:
                        game_volume += 0.05
                        pygame.mixer.music.set_volume(game_volume)
            if current_scene == 'menu':
                if event.type == pygame.KEYDOWN:
                    if event.key == up_key[0] or event.key == up_key[1]:
                        key_selected -= 1
                    elif event.key == down_key[0] or event.key == down_key[1]:
                        key_selected += 1
                    if event.key == sel_key[0] or event.key == sel_key[1]:
                        sel_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                        sel_sound.play()
                        if key_selected == 0:
                            switch_scene("game")
                        elif key_selected == 1:
                            switch_scene("rules")
                        elif key_selected == 2:
                            switch_scene("options")
                        elif key_selected == 3:
                            running = False
                            pygame.quit()
                if event.type == pygame.KEYUP:
                    pass
            #game menu keys
            elif current_scene == 'game' and not playing:
                 if event.type == pygame.KEYDOWN:
                    if _MAIN_BOARD.first_player != None:
                        playing = True
                        switch_scene("game", True)
                        _MAIN_BOARD.next_turn()
                    elif _MAIN_BOARD.first_player == None:
                        if event.key == K_1:
                            _MAIN_BOARD.first_player = 0
                        elif event.key == K_2:
                            _MAIN_BOARD.first_player = 1
            #game keys
            elif current_scene == 'game' and playing:
                if event.type == pygame.KEYDOWN:
                    if not _MAIN_BOARD.choosing_action[0]:
                        if event.key == sel_key[_MAIN_BOARD.player_turn]:
                            _MAIN_BOARD.select()
                        if event.key == up_key[_MAIN_BOARD.player_turn]:
                            _MAIN_BOARD.move_on_board((-1,0))
                        if event.key == down_key[_MAIN_BOARD.player_turn]:
                            _MAIN_BOARD.move_on_board((1,0))
                        if event.key == left_key[_MAIN_BOARD.player_turn]:
                            _MAIN_BOARD.move_on_board((0,-1))
                        if event.key == right_key[_MAIN_BOARD.player_turn]:
                            _MAIN_BOARD.move_on_board((0,1))
                    else:
                        if _MAIN_BOARD.spell_selection == '':
                            if event.key == sel_key[_MAIN_BOARD.player_turn]:
                                _MAIN_BOARD.perform_spell()
                            if event.key == up_key[_MAIN_BOARD.player_turn]:
                                if _MAIN_BOARD.choosen_spell > 0:
                                    _MAIN_BOARD.choosen_spell -= 1
                            if event.key == down_key[_MAIN_BOARD.player_turn]:
                                if _MAIN_BOARD.choosen_spell + 1 < len(_MAIN_BOARD.choosing_action[1].spells):
                                    _MAIN_BOARD.choosen_spell += 1
                        else:
                            if event.key == sel_key[_MAIN_BOARD.player_turn]:
                                if _MAIN_BOARD.spell_selection == 'imprison':
                                    _MAIN_BOARD.imprison()
                                elif _MAIN_BOARD.spell_selection == 'teleport':
                                    _MAIN_BOARD.teleport()
                                elif _MAIN_BOARD.spell_selection == 'heal':
                                    _MAIN_BOARD.heal()
                                elif _MAIN_BOARD.spell_selection == 'exchange':
                                    _MAIN_BOARD.exchange()
                                elif _MAIN_BOARD.reviving:
                                    _MAIN_BOARD.select_revival(0)
                                elif _MAIN_BOARD.spell_selection == 'revive':
                                    _MAIN_BOARD.select_revival(2)
                            if event.key == up_key[_MAIN_BOARD.player_turn]:
                                if _MAIN_BOARD.reviving:
                                    _MAIN_BOARD.select_revival(-1)
                                else:
                                    _MAIN_BOARD.move_on_board((-1,0), False)
                            if event.key == down_key[_MAIN_BOARD.player_turn]:
                                if _MAIN_BOARD.reviving:
                                    _MAIN_BOARD.select_revival(1)
                                else:
                                    _MAIN_BOARD.move_on_board((1,0), False)
                            if event.key == left_key[_MAIN_BOARD.player_turn]:
                                if not _MAIN_BOARD.reviving:
                                    _MAIN_BOARD.move_on_board((0,-1), False)
                            if event.key == right_key[_MAIN_BOARD.player_turn]:
                                if not _MAIN_BOARD.reviving:
                                    _MAIN_BOARD.move_on_board((0,1), False)
            #rules keys
            elif current_scene == 'rules':
                if event.type == pygame.KEYDOWN:
                    if rules_screen == 0 or rules_screen > 4:
                        if event.key == sel_key[0] or event.key == sel_key[1]:
                            if rules_sel == 0:
                                sel_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                                sel_sound.play()
                                switch_scene("menu")
                            if rules_sel == 1:
                                rules_screen = 3
                            if rules_sel == 2:
                                rules_screen = 1
                        if event.key == up_key[0] or event.key == up_key[1]:
                            rules_sel += 1
                        elif event.key == down_key[0] or event.key == down_key[1]:
                            rules_sel -= 1
                    elif rules_screen == 1:
                        if event.key == sel_key[0] or event.key == sel_key[1]:
                            sel_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                            sel_sound.play()
                            if char_view_sel == 0:
                                rules_screen = 0
                            elif char_view_sel == 1:
                                char_det = Knight()
                                rules_screen = 2
                            elif char_view_sel == 2:
                                char_det = Archer()
                                rules_screen = 2
                            elif char_view_sel == 3:
                                char_det = Phoenix()
                                rules_screen = 2
                            elif char_view_sel == 4:
                                char_det = Wizard()
                                rules_screen = 2
                            elif char_view_sel == 5:
                                char_det = Djinni()
                                rules_screen = 2
                            elif char_view_sel == 6:
                                char_det = Unicorn()
                                rules_screen = 2
                            elif char_view_sel == 7:
                                char_det = Golem()
                                rules_screen = 2
                            elif char_view_sel == 8:
                                char_det = Valkyrie()
                                rules_screen = 2
                            
                        if event.key == up_key[0] or event.key == up_key[1]:
                            char_view_sel += 1
                        elif event.key == down_key[0] or event.key == down_key[1]:
                            char_view_sel -= 1

                    elif rules_screen == 3:
                        if event.key == sel_key[0] or event.key == sel_key[1]:
                            sel_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                            sel_sound.play()
                            if char_view_sel == 0:
                                rules_screen = 0
                            elif char_view_sel == 1:
                                char_det = Goblin()
                                rules_screen = 4
                            elif char_view_sel == 2:
                                char_det = Manticore()
                                rules_screen = 4
                            elif char_view_sel == 3:
                                char_det = Dragon()
                                rules_screen = 4
                            elif char_view_sel == 4:
                                char_det = Sorceress()
                                rules_screen = 4
                            elif char_view_sel == 5:
                                char_det = Shapeshifter()
                                rules_screen = 4
                            elif char_view_sel == 6:
                                char_det = Basilisk()
                                rules_screen = 4
                            elif char_view_sel == 7:
                                char_det = Troll()
                                rules_screen = 4
                            elif char_view_sel == 8:
                                char_det = Banshee()
                                rules_screen = 4
                            
                        if event.key == up_key[0] or event.key == up_key[1]:
                            char_view_sel += 1
                        elif event.key == down_key[0] or event.key == down_key[1]:
                            char_view_sel -= 1
                    elif rules_screen == 2 or rules_screen == 4:
                        if rules_screen == 2:
                            rules_screen = 1
                        else:
                            rules_screen = 3
            #options keys
            elif current_scene == 'options':
                if event.type == pygame.KEYDOWN:
                    if event.key == sel_key[0] or event.key == sel_key[1]:
                        if opts_sel == 0:
                            sel_sound.set_volume(game_volume+0.8 if (pygame.mixer_music.get_volume() != 0) else 0)
                            sel_sound.play()
                            current_scene = 'menu'
                        if opts_sel == 1:
                            if game_volume > 0.04:
                                game_volume -= 0.05
                                pygame.mixer.music.set_volume(game_volume)
                        if opts_sel == 2:
                            if game_volume < 0.96:
                                game_volume += 0.05
                                pygame.mixer.music.set_volume(game_volume)
                    if event.key == up_key[0] or event.key == up_key[1]:
                        opts_sel += 1
                    elif event.key == down_key[0] or event.key == down_key[1]:
                        opts_sel -= 1

    if current_scene == "":
        switch_scene("menu")
    #SCENE MANAGEMENT
    if current_scene == 'menu':
        menu()
    elif current_scene == 'game':
        if playing == False:
            game_scene()
        else:
            if _MAIN_BOARD.choosing_action[0] and _MAIN_BOARD.spell_selection == '':
                _MAIN_BOARD.show_spells()
            board()
    elif current_scene == "ending":
        playing = False
        game_ending()
    elif current_scene == "rules":
        if rules_screen == 0:
            rules()
        elif rules_screen == 1:
            see_light_chars()
        elif rules_screen == 3:
            see_dark_chars()
        elif rules_screen == 2 or rules_screen == 4:
            char_viewer(rules_screen)
        else:
            rules_screen = 0
            rules()
    elif current_scene == 'options':
        options()
    elif current_scene == 'arena':
        arena()
    else:
        menu()
        
    build_warning = debug_font.render("UNDER DEVELOPMENT", 1, (255, 00, 00))
    screen.blit(build_warning, (0,0))
    pygame.display.update()
    _MAIN_BOARD.es_handle_animation()
    dt = clock.tick(60)

    #transition handler
    if transition > 0:
        trans_clock += 1
        if trans_clock > 50:
            transition -= 1
            trans_clock = 0
    #Animation_handler
    for char in animation_line:
        char.handle_animation()

pygame.quit()