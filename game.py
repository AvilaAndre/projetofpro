import pygame, sys, time, os
from pygame.locals import *

_DEBUG = True
_GAMETITLE = 'Archon Type Game!'
pygame.init()
pygame.font.init()

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

current_scene = 'menu'
playing = False
animation_line = []

def get_sprites(character, directory):
    spritesheet = []
    for sprite in os.listdir(r"Resources\Sprites\Characters\{0}\{1}".format(character, directory)):
        spritesheet.append(r'Resources\Sprites\Characters\{0}\{1}\{2}'.format(character,directory,sprite))
    return spritesheet


"""
~~~~PROJECTILES~~~~
"""

class Projectile():
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
        self.team = character.team
        self.x, self.y = (character.x, character.y)
        self.height, self.width  = min(character.proj_height, character.proj_width),min(character.proj_height, character.proj_width)
        self.direction = (direction[0], direction[1]) 
        if self.team == 0:
            light_projectiles.append(self)
        else:
            dark_projectiles.append(self)
        self.speed = character.atk_speed
        self.dmg = character.atk_damage
        sprite = pygame.image.load(r'Resources\Sprites\Characters\{0}\Projectile\Projectile.png'.format(character.name))
        sprite = pygame.transform.smoothscale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
        if direction[0] < 0:
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
        sprite = pygame.transform.rotate(sprite,  self.angle)
        self.x, self.y = (self.x + (character.proj_correction[correction][0] + self.hitbox_x)*2.6, self.y + (character.proj_correction[correction][1] + self.hitbox_y)*2.6)
        self.sprite = sprite

    ##TODO: FIX
    def hitbox(self):
        return pygame.Rect(self.x- self.hitbox_x * 2.6, self.y- self.hitbox_y*2.6, self.width *2.6, self.height*2.6)

    
    def move(self):
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        for rect in arena_collisions:
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    print(rect)
                    print(light_projectiles, dark_projectiles)
                    if rect.obj_type == "player":
                        if rect.team != self.team:
                            rect.take_damage(self.dmg)
                            if self.team == 0:
                                light_projectiles.remove(self)
                            else:
                                dark_projectiles.remove(self)

"""
~~~~CHARACTERS~~~~
"""
class Knight():
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
    speed = 5
    atk_damage = 2
    atk_speed = 3
    atk_cooldown = 2
    alive = True
    orientation = False
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
    
    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1

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
                if self.anim_clock == 10:
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
        elif self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if player == 1:
            if keys[pygame.K_w]:
                y += 1         
            if keys[pygame.K_s]:
                y -= 1
            if keys[pygame.K_d]:
                x += 1          
            if keys[pygame.K_a]:
                x -= 1              
        elif player == 2:
            if keys[pygame.K_UP]:
                y += 1            
            if keys[pygame.K_DOWN]:
                y -= 1             
            if keys[pygame.K_RIGHT]:
                x += 1               
            if keys[pygame.K_LEFT]:
                x -= 1
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
        if x != 0 or y != 0:
            self.current_animation = "moving"
        else:
            self.current_animation = "idle"

    def __init__(self):
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
    
    #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 20
    atk_cooldown = 2
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_size = 30
                    #Corrections #TODO:Get it right
    proj_correction = [
    (15,7), #RightAttackFront
    (14,-3), #RightAttackUp
    (17,-3), #RightAttackFrontUp
    (16,15), #RightAttackFrontDown
    (6,16), #RightAttackDown
    (-9,7), #LeftAttackFront
    (-6,-3), #LeftAttackUp
    (-11,-3), #LeftAttackFrontUp
    (-8,15), #LeftAttackFrontDown
    (-6,16)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    def take_damage(self):
        pass

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
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
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Valkyrie():
    name = "Valkyrie"
    description = "Valkyries are pretty, blonde warriors of the legion of Valhalla. Every one of it is equipped with two big talents: firstly the ability to walk through the air as if it was solid ground; and secondly a bewitched spear that after been thrown returns to its thrower." #TODO: Valkyrie's description 
    s_moving_type = "air - 3"
    s_speed = "normal"
    s_attack_type = "spear"
    s_attack_strength = "moderate"
    s_attack_speed = "slow"
    s_attack_interval = "average"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 3
    atk_cooldown = 2
    alive = True
    orientation = False
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    print(idle_animation)
    
    run_animation = get_sprites(name, 'Run')
    
    
    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    print(current_sprite)
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1

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
                if self.anim_clock == 10:
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
        elif self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if player == 1:
            if keys[pygame.K_w]:
                y += 1         
            if keys[pygame.K_s]:
                y -= 1
            if keys[pygame.K_d]:
                x += 1          
            if keys[pygame.K_a]:
                x -= 1              
        elif player == 2:
            if keys[pygame.K_UP]:
                y += 1            
            if keys[pygame.K_DOWN]:
                y -= 1             
            if keys[pygame.K_RIGHT]:
                x += 1               
            if keys[pygame.K_LEFT]:
                x -= 1
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
        if x != 0 or y != 0:
            self.current_animation = "moving"
        else:
            self.current_animation = "idle"
    
    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Djinni():
    name = "Djinni"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts" #TODO:Djinni's description
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 8
    atk_cooldown = 2
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_size = 30
                    #Corrections #TODO:Get it right
    proj_correction = [
    (15,7), #RightAttackFront
    (14,-3), #RightAttackUp
    (17,-3), #RightAttackFrontUp
    (16,15), #RightAttackFrontDown
    (6,16), #RightAttackDown
    (-9,7), #LeftAttackFront
    (-6,-3), #LeftAttackUp
    (-11,-3), #LeftAttackFrontUp
    (-8,15), #LeftAttackFrontDown
    (-6,16)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    def take_damage(self):
        pass

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
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
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def __init__(self):
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
        #type: teleport0 air1 ground2
    move_type = 2
    move_limit = 3
    speed = 5
    atk_damage = 8
    atk_speed = 9
    atk_cooldown = 0.75
    base_hp = 9.5
    max_hp= 16.5
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
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
    (16,35)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
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
        self.base_hp -= damage
        if self.base_hp <= 0:
            self.die()

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_SPACE]:
                    self.take_damage(3)
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_SPACE]:
                    self.take_damage(3)
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def die(self):
        self.alive = False

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Golem():
    name = "Golem"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts"
    s_attack_strength = "moderate" #TODO: GOLEM's description
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 5
    atk_cooldown = 2
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
                    #Corrections #TODO:Get it right
    proj_correction = [
    (15,7), #RightAttackFront
    (14,-3), #RightAttackUp
    (17,-3), #RightAttackFrontUp
    (16,15), #RightAttackFrontDown
    (6,16), #RightAttackDown
    (-9,7), #LeftAttackFront
    (-6,-3), #LeftAttackUp
    (-11,-3), #LeftAttackFrontUp
    (-8,15), #LeftAttackFrontDown
    (-6,16)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    def take_damage(self):
        pass

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
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
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Phoenix():
    name = "Phoenix"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts"
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
        #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 3
    atk_cooldown = 2
    alive = True
    orientation = False
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
    
    #Animation Managing
    cur_key = 0
    current_sprite = idle_animation[0]
    animation_change = "idle"
    current_animation = "idle"
    sprite = pygame.image.load(current_sprite)
    texture = pygame.transform.scale(sprite,  (_CHARS_SIZE, _CHARS_SIZE))
    anim_clock = -1

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
                if self.anim_clock == 10:
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
        elif self.current_animation == "idle":
            if self.cur_key+2 > len(self.idle_animation):
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.idle_animation[self.cur_key]
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if player == 1:
            if keys[pygame.K_w]:
                y += 1         
            if keys[pygame.K_s]:
                y -= 1
            if keys[pygame.K_d]:
                x += 1          
            if keys[pygame.K_a]:
                x -= 1              
        elif player == 2:
            if keys[pygame.K_UP]:
                y += 1            
            if keys[pygame.K_DOWN]:
                y -= 1             
            if keys[pygame.K_RIGHT]:
                x += 1               
            if keys[pygame.K_LEFT]:
                x -= 1
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
        if x != 0 or y != 0:
            self.current_animation = "moving"
        else:
            self.current_animation = "idle"

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Wizard():
    name = "Wizard"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts"
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    #STAT NUMBERS
    speed = 5
    atk_damage = 2
    atk_speed = 8
    atk_cooldown = 2
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_size = 30
                    #Corrections 
    proj_correction = [
    (15,7), #RightAttackFront
    (14,-3), #RightAttackUp
    (17,-3), #RightAttackFrontUp
    (16,15), #RightAttackFrontDown
    (6,16), #RightAttackDown
    (-9,7), #LeftAttackFront
    (-6,-3), #LeftAttackUp
    (-11,-3), #LeftAttackFrontUp
    (-8,15), #LeftAttackFrontDown
    (-6,16)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    def take_damage(self):
        pass

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
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
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)
#DARK#


class Sorceress():
    obj_type = "player"
    #TODO: Sorceress info
    name = "Sorceress"
    description = "Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn." 
    s_moving_type = "ground - 4"
    s_speed = "normal"
    s_attack_type = "energy bolts"
    s_attack_strength = "moderate"
    s_attack_speed = "fast"
    s_attack_interval = "short"
    s_life_span = "average"
    s_number_of_chars = "2"
    
    #STAT NUMBERS
    team = 1
        #type: teleport0 air1 ground2
    move_type = 0
    move_limit = 3
    speed = 5
    atk_damage = 8
    atk_speed = 9
    atk_cooldown = 0.75
    base_hp = 9.5
    max_hp= 16.5
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
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
    (16,35)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
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
        self.base_hp -= damage
        if self.base_hp <= 0:
            self.die()

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_SPACE]:
                    self.take_damage(3)
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
                    self.attack(x, -y)
            elif player == 2:
                if keys[pygame.K_SPACE]:
                    self.take_damage(3)
                if keys[pygame.K_UP]:
                    y += 1            
                if keys[pygame.K_DOWN]:
                    y -= 1             
                if keys[pygame.K_RIGHT]:
                    x += 1               
                if keys[pygame.K_LEFT]:
                    x -= 1
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def die(self):
        self.alive = False

    def __init__(self):
        print(f"{self.name} instantiated")
        animation_line.append(self)

class Manticore():
    name = "Manticore"
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
    speed = 5
    atk_damage = 2
    atk_speed = 8
    atk_cooldown = 2
    alive = True
    orientation = True
    direction = (1,0)
    performing_attack = False
    char_x_offset = 18
    char_y_offset = 17
    char_width = 12 #TODO: get character dimensions
    char_height = 19
    #Position
    x = 0
    y = 0

    #projectile
    proj_dir = (0,0)
    proj_size = 30
                    #Corrections #TODO:Get it right
    proj_correction = [
    (15,7), #RightAttackFront
    (14,-3), #RightAttackUp
    (17,-3), #RightAttackFrontUp
    (16,15), #RightAttackFrontDown
    (6,16), #RightAttackDown
    (-9,7), #LeftAttackFront
    (-6,-3), #LeftAttackUp
    (-11,-3), #LeftAttackFrontUp
    (-8,15), #LeftAttackFrontDown
    (-6,16)  #LeftAttackDown #    AQUI
    ]
    ##SPRITES
    idle_animation = get_sprites(name, 'Idle')
    
    run_animation = get_sprites(name, 'Run')
    
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
                if self.anim_clock == 10:
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
        elif self.current_animation == "AttackFront":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_animation[self.cur_key]
        elif self.current_animation == "AttackFrontUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_up_animation[self.cur_key]
        elif self.current_animation == "AttackFrontDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_front_down_animation[self.cur_key]
        elif self.current_animation == "AttackUp":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
                    self.cur_key += 1
                    self.anim_clock = -1
                    self.current_sprite = self.attack_up_animation[self.cur_key]
        elif self.current_animation == "AttackDown":
            if self.cur_key == 2 and self.anim_clock == 0:
                self.shoot()
            if self.cur_key+2 > 3:
                self.current_animation = "idle"
                self.performing_attack = False
                self.cur_key = 0
                self.anim_clock = -1
            else: 
                if self.anim_clock == 10:
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
            if rect != self:
                if self.hitbox().colliderect(rect.hitbox()):
                    colliding = True

        return colliding
    
    def attack(self, x, y):
        self.proj_dir = (x, y)
        attack_anim = "Attack"
        if x==0 and y == 0:
            return
        self.performing_attack = True
        if x != 0:
            attack_anim += "Front"
        if y == -1:
            attack_anim += "Up"
        elif y == 1:
            attack_anim += "Down"
        self.current_animation = attack_anim
    
    def shoot(self):
        Projectile((self.proj_dir[0], self.proj_dir[1]), self)
    
    def take_damage(self):
        pass

    #movement
    def move(self, player):
        keys = pygame.key.get_pressed()  #checking pressed keys
        x, y = (0, 0)
        if not self.performing_attack:
            if player == 1:
                if keys[pygame.K_w]:
                    y += 1         
                if keys[pygame.K_s]:
                    y -= 1
                if keys[pygame.K_d]:
                    x += 1          
                if keys[pygame.K_a]:
                    x -= 1              
                if keys[pygame.K_LSHIFT]:
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
                if keys[pygame.K_RETURN]:
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
        if not self.performing_attack:
            if x != 0 or y != 0:
                self.current_animation = "moving"
            else:
                self.current_animation = "idle"

    def __init__(self):
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
    playing = False
    if key_selected > 3:
        key_selected = 3
    if key_selected < 0:
        key_selected = 0
    screen.fill((255,255,255))
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
def rules():
    global rules_sel
    screen.fill((255,255,255))
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
    pygame.draw.rect(screen, (0,0,0), (400, 400, 200, 200), 4)


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

opts_buttons = [(840, 570, 140, 55), (840, 270, 140, 55)]
opts_sel = 0


def options():
    global opts_sel
    #
    
    #LOGIC
    if opts_sel > len(opts_buttons) -1:
        opts_sel = len(opts_buttons) -1
    if opts_sel < 0:
        opts_sel = 0
    #TEXT

    go_back_button = medium_gm_font.render('Back', 1, (00,00,00))
    
    #DRAW
    screen.fill((255, 100, 100))
    screen.blit(go_back_button, (860, 580))
    pygame.draw.rect(screen, (0,0,0) , Rect(opts_buttons[opts_sel][0], opts_buttons[opts_sel][1], opts_buttons[opts_sel][2], opts_buttons[opts_sel][3]), 4)




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
    screen.fill((220,220,0))

    #TEXT
    press_start = small_medium_gm_font.render("Press any key to start the game.", 1, (255, 255, 255))
    #DRAW
    if text_mod < 40:
        screen.blit(press_start, (300, 500))
"""
|||    BOARD   |||
"""

class GameBoard:
    _PIECE_SIZE = 80
    #Pieces
 
    Golem_Piece1 = (Golem(), pygame.transform.scale(pygame.image.load(Golem.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Golem_Piece2 = (Golem(), pygame.transform.scale(pygame.image.load(Golem.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece1 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece2 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece3 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece4 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece5 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece6 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Knight_Piece7 = (Knight(), pygame.transform.scale(pygame.image.load(Knight.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Archer_Piece1 = (Archer(), pygame.transform.scale(pygame.image.load(Archer.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Archer_Piece2 = (Archer(), pygame.transform.scale(pygame.image.load(Archer.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Djinni_Piece1 = (Djinni(), pygame.transform.scale(pygame.image.load(Djinni.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Wizard_Piece1 = (Wizard(), pygame.transform.scale(pygame.image.load(Wizard.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Unicorn_Piece1 = (Unicorn(), pygame.transform.scale(pygame.image.load(Unicorn.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Unicorn_Piece2 = (Unicorn(), pygame.transform.scale(pygame.image.load(Unicorn.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Phoenix_Piece1 = (Phoenix(), pygame.transform.scale(pygame.image.load(Phoenix.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Valkyrie_Piece1 = (Valkyrie(), pygame.transform.scale(pygame.image.load(Valkyrie.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Valkyrie_Piece2 = (Valkyrie(), pygame.transform.scale(pygame.image.load(Valkyrie.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Sorceress_Piece1 = (Sorceress(), pygame.transform.scale(pygame.image.load(Sorceress.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Manticore_Piece1 = (Manticore(), pygame.transform.scale(pygame.image.load(Manticore.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    Manticore_Piece2 = (Manticore(), pygame.transform.scale(pygame.image.load(Manticore.current_sprite),  (_PIECE_SIZE, _PIECE_SIZE)))
    _PLAYERS_COLOR = [(255, 255, 255), (0,0,0)]
    _STATIC_TILES = [(0,0), (0,1), (0,2), (0,4), (0,6), (0,7), (0,8), (1,0), (1,1), (1,3), (1,5), (1,7), (1,8), (2,0), (2,2), (2,3), (2,5), (2,6), (2,8), (3,1), (3,2), (3,3), (3,5), (3,6), (3,7), (5,1), (5,2), (5,3), (5,5), (5,6), (5,7), (6,0), (6,2), (6,3), (6,5), (6,6), (6,8), (7,0), (7,1), (7,3), (7,5), (7,7), (7,8), (8,0), (8,1), (8,2), (8,4), (8,6), (8,7), (8,8)]
                                ##LIGHT --> DARK##
    _TILE_COLORS = [(164, 200, 252), (124,156,220), (80,112,188), (56, 74, 176), (48, 32, 152), (0, 44, 92)]
    _ENERGY_SQUARES = [(0, 4), (4,0), (4,4), (4,8), (8,4)]

    board_x = 256 + 128
    board_y = 64
    light_square = pygame.image.load(r'Resources\Sprites\Tiles\220220220LightTile.png')
    board_color_data = [[ _TILE_COLORS[5] ,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5],0, _TILE_COLORS[0], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0]], [_TILE_COLORS[5] ,0,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5]], [(220,220,220) , _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0 , _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0], [_TILE_COLORS[0] ,0,_TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0]], [_TILE_COLORS[5] , _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0]]]
    board_data = [[Valkyrie_Piece1 , Golem_Piece1, Unicorn_Piece2, Djinni_Piece1, Wizard_Piece1, Phoenix_Piece1, Unicorn_Piece1, Golem_Piece2, Valkyrie_Piece2], [Archer_Piece1, Knight_Piece1 , Knight_Piece2, Knight_Piece3, Knight_Piece4, Knight_Piece5, Knight_Piece6, Knight_Piece7, Archer_Piece2], [None , None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None, None, None, None, None, None, None, None, None], [None , None, None, None, None, None, None, None, None], [None ,None ,None, None, None, None, None, None, None], [Manticore_Piece2 , None, None, None, None, None, None, None, Manticore_Piece2], [None , None, None, None, Sorceress_Piece1, None, None, None, None]]
    turn = 0


    player_board_x = 0
    player_board_y = 0
    turn_player = 0
    selected_sq = ()

    ##ENERGY SQUARE ANIMATION##
    energy_square_frames = [pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF1.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF2.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF3.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF4.png'), pygame.image.load(r'Resources\Sprites\Tiles\EnergySquare\EnergySquareF5.png')]
    es_cur_anim = 0
    es_anim_cycle = 1
    es_clock = -1
    ##ENERGY SQUARE ANIMATION##
    def es_handle_animation(self):
        self.es_clock += 1
        if self.es_clock == 10:
            self.es_cur_anim += 1 * self.es_anim_cycle
            self.es_clock = -1
        if self.es_cur_anim == 0 or self.es_cur_anim == len(self.energy_square_frames)-1:
            self.es_anim_cycle *= -1

    _start = True

    def draw_board(self):
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_color_data[i][j] != None:
                    pygame.draw.rect(screen, self.board_color_data[i][j], Rect(self.board_x + (56*i), self.board_y + 56*(j), 56, 56), 0)
        for es_sq in self._ENERGY_SQUARES:
            es_x, es_y = es_sq
            screen.blit(self.energy_square_frames[self.es_cur_anim], (self.board_x + (56*es_y), self.board_y + (56*es_x)))
        if self.selected_sq != ():
            self.move_selected_piece()
        for i in range(0, 9):
            for j in range(0,9):
                if self.board_data[i][j] != None:
                    if self.selected_sq == ():
                        screen.blit(pygame.transform.flip(self.board_data[i][j][1],self.board_data[i][j][0].orientation, False), (self.board_x + (56*i) - self.board_data[i][j][0].char_x_offset, self.board_y + 56*(j) - self.board_data[i][j][0].char_y_offset))
                    elif self.selected_sq[0] != self.board_data[i][j]:
                        screen.blit(pygame.transform.flip(self.board_data[i][j][1],self.board_data[i][j][0].orientation, False), (self.board_x + (56*i) - self.board_data[i][j][0].char_x_offset, self.board_y + 56*(j) - self.board_data[i][j][0].char_y_offset))
                    
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
        self.turn += 1
        self.board_color_switch()

    def select(self):
        #sq is for square
        if self.selected_sq == ():
            if self.board_data[self.player_board_y][self.player_board_x] != None:
                self.selected_sq = (self.board_data[self.player_board_y][self.player_board_x],(self.player_board_x, self.player_board_y))
        else:
            if self.board_data[self.player_board_y][self.player_board_x] == None:
                self.board_data[self.player_board_y][self.player_board_x] = self.selected_sq[0]
                self.board_data[self.selected_sq[1][1]][self.selected_sq[1][0]] = None
            elif not self.board_data[self.player_board_y][self.player_board_x] == self.selected_sq[0]:
                start_duel(self.selected_sq[0][0], self.board_data[self.player_board_y][self.player_board_x][0])
            self.selected_sq = ()

    def move_on_board(self, direc):
        x, y = direc
        if self.player_board_x + x > -1 and self.player_board_x + x < 9:
            self.player_board_x += x
        if self.player_board_y + y > -1 and self.player_board_y + y < 9:
            self.player_board_y += y
        
    def get_info(self):
        if self.selected_sq != ():
            return self.selected_sq[0][0].name + ' - ' + self.selected_sq[0][0].s_moving_type
        character = self.board_data[self.player_board_y][self.player_board_x]
        if character == None:
            return ''
        else:
            return character[0].name + ' - ' + character[0].s_moving_type
    
    def move_selected_piece(self):
        screen.blit(pygame.transform.flip(self.selected_sq[0][1],self.selected_sq[0][0].orientation, False), (self.board_x + (56*self.player_board_y) - self.selected_sq[0][0].char_x_offset, self.board_y + (56*self.player_board_x) - self.selected_sq[0][0].char_y_offset))

_MAIN_BOARD = GameBoard()

def board():

    #LOGIC
    turn_number = medium_gm_font.render(f'Turn: {_MAIN_BOARD.turn}', 1, (00, 00, 00))
    player_info = small_gm_font.render(_MAIN_BOARD.get_info(), 1, (00, 00, 00))
    if _MAIN_BOARD.turn == 0:
        _MAIN_BOARD.character_entry()


    #DRAW
    screen.fill((112, 40, 0))
    screen.blit(turn_number, (50, 50))

    

    _MAIN_BOARD.draw_board()
    pygame.draw.rect(screen, _MAIN_BOARD._PLAYERS_COLOR[_MAIN_BOARD.turn_player], Rect(_MAIN_BOARD.board_x + (56*_MAIN_BOARD.player_board_y), _MAIN_BOARD.board_y + (56*_MAIN_BOARD.player_board_x), 56, 56), 4)
    pygame.draw.rect(screen, (80, 112, 188), Rect(25, 500, 320, 80), 0)
    pygame.draw.rect(screen, (56, 74, 176), Rect(25, 500, 320, 80), 3)
    screen.blit(player_info, (95, 530))


#---
dueler1 = None
dueler2 = None
arena_collisions = []

dead = []
arena_finish_clock = 0
arena_finish_var = 0
def start_duel(fighter1, fighter2):
    global current_scene, dueler1, dueler2, arena_finish_clock, arena_finish_var
    arena_collisions.clear()
    dead.clear()
    arena_finish_clock = 15
    arena_finish_var = 0
    current_scene = "arena"
    dueler1 = fighter1
    dueler2 = fighter2
    dueler2.x = 180 - dueler2.char_x_offset * 2.16
    dueler2.y = 280 - dueler2.char_y_offset * 2.16
    dueler1.x = 804 - dueler1.char_x_offset * 2.16
    dueler1.y = 280 - dueler1.char_y_offset * 2.16
    dueler1.orientation = True
    dueler2.orientation = False
    arena_collisions.append(dueler1)
    arena_collisions.append(dueler2)

def finish_duel():
    global current_scene
    current_scene = "game"
    light_projectiles.clear()
    dark_projectiles.clear()
    arena_collisions.clear()
    
fg_begun = False
arena_ground = pygame.Rect(160, 20, 704, 600)
light_projectiles = []
dark_projectiles = []

def arena():
    global dueler1, dueler2, arena_finish_clock, arena_finish_var
    screen.fill((255, 0, 0))
    #Logic
    dueler1_name = small_gm_font.render(dueler1.name, 1, (00, 00, 00))
    dueler2_name = small_gm_font.render(dueler2.name, 1, (00, 00, 00))
    dueler1_hp = 0
    dueler2_hp = 0
    if not dueler1.alive:
        dead.append(dueler1)
        dueler1_hp = 0
    else:
        dueler1.move(1)
        dueler1_hp = dueler1.base_hp
    if not dueler2.alive:
        dead.append(dueler2)
        dueler2_hp = 0
    else:
        dueler2.move(2)
        dueler2_hp = dueler2.base_hp
    for proj in light_projectiles:
        proj.move()
    for proj in dark_projectiles:
        proj.move()
    if len(dead) != 0:
        if arena_finish_clock <= 0:
            finish_duel()
        else:
            arena_finish_var += 1
            if arena_finish_var > 10:
                arena_finish_var = 0
                arena_finish_clock -= 1
    #Draw
    pygame.draw.rect(screen, (100, 155, 155), arena_ground, 0)
        ##dueler's stats
    pygame.draw.rect(screen, (89, 89, 89), (10,20 + (620 - dueler2_hp * 24), 140, dueler2_hp*24), 0)
    pygame.draw.rect(screen, (0, 0, 0), (15 , 15, 130, 610), 1)
    screen.blit(dueler2_name, (20, 40))
    pygame.draw.rect(screen, (89, 89, 89), (874, 20 + (620 - dueler1_hp * 24), 140, dueler1_hp*24), 0)
    pygame.draw.rect(screen, (0, 0, 0), (879 , 15, 130, 610), 1)
    screen.blit(dueler1_name, (886, 40))
    if dueler1.alive:
        screen.blit(pygame.transform.flip(dueler1.texture, dueler1.orientation, False), (dueler1.x, dueler1.y))
    if dueler2.alive:
        screen.blit(pygame.transform.flip(dueler2.texture, dueler2.orientation, False), (dueler2.x, dueler2.y))
    for proj in light_projectiles:
        screen.blit(proj.sprite, (proj.x, proj.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), proj.hitbox(), 0)
    for proj in dark_projectiles:
        screen.blit(proj.sprite, (proj.x, proj.y))
        if _DEBUG:
            pygame.draw.rect(screen, (0,0,0), proj.hitbox(), 0)
    if _DEBUG:
        pygame.draw.rect(screen, (155,155,155) , dueler2.hitbox(), 0) #hitbox
    if _DEBUG:
        pygame.draw.rect(screen, (155,155,155) , dueler1.hitbox(), 0)

""" 
~~~~~~~~~~~~~~~~~~
"""

es_mlsecs = 0
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            #menu keys
            if current_scene == 'menu':
                if event.type == pygame.KEYDOWN:
                    if event.key == K_UP or event.key == K_w:
                        key_selected -= 1
                    elif event.key == K_DOWN or event.key == K_s:
                        key_selected += 1
                    if event.key == K_RETURN or event.key == K_SPACE:
                        if key_selected == 0:
                            current_scene = "game"
                        elif key_selected == 1:
                            current_scene = "rules"
                        elif key_selected == 2:
                            current_scene = "options"
                        elif key_selected == 3:
                            running = False
                            pygame.quit()
                if event.type == pygame.KEYUP:
                    pass
            #game menu keys
            elif current_scene == 'game' and not playing:
                 if event.type == pygame.KEYDOWN:
                    playing = True
                    _MAIN_BOARD.next_turn()
            #game keys
            elif current_scene == 'game' and playing:
                if event.type == pygame.KEYDOWN:
                    if _MAIN_BOARD.turn == 2:
                        start_duel(Valkyrie(), Knight())
                    if event.key == K_RETURN or event.key == K_SPACE:
                        #_MAIN_BOARD.next_turn()
                        _MAIN_BOARD.select()
                    if event.key == K_UP or event.key == K_w:
                        _MAIN_BOARD.move_on_board((-1,0))
                    if event.key == K_DOWN or event.key == K_s:
                        _MAIN_BOARD.move_on_board((1,0))
                    if event.key == K_LEFT or event.key == K_a:
                        _MAIN_BOARD.move_on_board((0,-1))
                    if event.key == K_RIGHT or event.key == K_d:
                        _MAIN_BOARD.move_on_board((0,1))

            #rules keys
            elif current_scene == 'rules':
                if event.type == pygame.KEYDOWN:
                    if rules_screen == 0 or rules_screen > 4:
                        if event.key == K_RETURN or event.key == K_SPACE:
                            if rules_sel == 0:
                                current_scene = 'menu'
                            if rules_sel == 1:
                                rules_screen = 3
                            if rules_sel == 2:
                                rules_screen = 1
                        if event.key == K_UP or event.key == K_w:
                            rules_sel += 1
                        elif event.key == K_DOWN or event.key == K_s:
                            rules_sel -= 1
                    elif rules_screen == 1:
                        
                        if event.key == K_RETURN or event.key == K_SPACE:
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
                            
                        if event.key == K_UP or event.key == K_w:
                            char_view_sel += 1
                        elif event.key == K_DOWN or event.key == K_s:
                            char_view_sel -= 1

                    elif rules_screen == 3:
                        if event.key == K_RETURN or event.key == K_SPACE:
                            if char_view_sel == 0:
                                rules_screen = 0
                            elif char_view_sel == 1:
                                char_det = Goblin()
                                rules_screen = 4
                            elif char_view_sel == 2:
                                char_det = Manticore()
                                rules_screen = 4
                            elif char_view_sel == 3:
                                #char_det = Dragon()
                                rules_screen = 4
                            elif char_view_sel == 4:
                                char_det = Sorceress()
                                rules_screen = 4
                            elif char_view_sel == 5:
                                #char_det = Shapeshifter()
                                rules_screen = 4
                            elif char_view_sel == 6:
                                #char_det = Basilisk()
                                rules_screen = 4
                            elif char_view_sel == 7:
                                #char_det = Troll()
                                rules_screen = 4
                            elif char_view_sel == 8:
                                #char_det = Banshee()
                                rules_screen = 4
                            
                        if event.key == K_UP or event.key == K_w:
                            char_view_sel += 1
                        elif event.key == K_DOWN or event.key == K_s:
                            char_view_sel -= 1
                    elif rules_screen == 2 or rules_screen == 4:
                        if rules_screen == 2:
                            rules_screen = 1
                        else:
                            rules_screen = 3


            elif current_scene == 'options':
                if event.type == pygame.KEYDOWN:
                    if event.key == K_RETURN or event.key == K_SPACE:
                        if opts_sel == 0:
                            current_scene = 'menu'
                    if event.key == K_UP or event.key == K_w:
                        opts_sel += 1
                    elif event.key == K_DOWN or event.key == K_s:
                        opts_sel -= 1
            

    #SCENE MANAGEMENT
    if current_scene == 'menu':
        menu()
    elif current_scene == 'game':
        if playing == False:
            game_scene()
        else:
            board()
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

    #Animation_handler
    for char in animation_line:
        char.handle_animation()

pygame.quit()