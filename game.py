import pygame, sys, time
from pygame.locals import *


_GAMETITLE = 'Archon Type Game!'
pygame.init()
pygame.font.init()

##FONTS
myfont = pygame.font.SysFont("Comic Sans MS", 30)
title_font = pygame.font.SysFont("Comic Sans MS", 80)
option_font = pygame.font.SysFont("Comic Sans MS", 60)
small_font = pygame.font.SysFont("Comic Sans MS", 15)
debug_font = pygame.font.SysFont("lucidaconsole", 15)

title_gm_font = pygame.font.Font(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Fonts\Langar\Langar-Regular.ttf', 80)
big_gm_font = pygame.font.Font(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Fonts\Langar\Langar-Regular.ttf', 60)
medium_gm_font = pygame.font.Font(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Fonts\Langar\Langar-Regular.ttf', 40)
small_gm_font = pygame.font.Font(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Fonts\Langar\Langar-Regular.ttf', 20)
pygame.display.set_caption(_GAMETITLE)


width, height = 64*16, 64*10
screen=pygame.display.set_mode((width, height))

clock = pygame.time.Clock()


current_scene = 'menu'
playing = False
"""
~~~~CHARACTERS~~~~
"""


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
s_l_buttons = [(840, 570, 140, 55)]

def see_light_chars():
    screen.fill((255, 255, 153))
    #DRAW

s_d__buttons = [(840, 570, 140, 55)]
def see_dark_chars():
    screen.fill((0, 0, 77))
    #DRAW

"""CHARACTERS SHEETS"""
#TODO: Add character description, sprite and details
def char_viewer(side):
    if side == 2:
        screen.fill((255, 255, 153))
        screen_info_c = (0,0,0)
    elif side == 4:
        screen.fill((0,0,77))
        screen_info_c = (255, 255, 255)
    else:
        screen.fill((255, 0, 0))
    print(screen_info_c)
    #LOGIC
##   picture = pygame.image.load(filename)
##  picture = pygame.transform.scale(picture, (1280, 720))
##  rect = rect.move((x, y))
##  screen.blit(picture, rect)
    #TODO: make description fit the screen
    description = 'Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn.'

    #TEXT
    char_name = medium_gm_font.render('Unicorn', 1, screen_info_c)
    description = small_gm_font.render(description, 1, screen_info_c)
    stat1 = small_gm_font.render(f'Moving type: {"ground"}', 1, screen_info_c)
    stat2 = small_gm_font.render(f'Speed: {"normal"}', 1, screen_info_c)
    stat3 = small_gm_font.render(f'Attack type: {"energy bolts"}', 1, screen_info_c)
    stat4 = small_gm_font.render(f'Attack strength: {"moderate"}', 1, screen_info_c)
    stat5 = small_gm_font.render(f'Attack speed: {"fast"}', 1, screen_info_c)
    stat6 = small_gm_font.render(f'Attack interval: {"short"}', 1, screen_info_c)
    stat7 = small_gm_font.render(f'Life span: {"average"}', 1, screen_info_c)
    stat8 = small_gm_font.render(f'Number of characters: {"2"}', 1, screen_info_c)

    #DRAW
    pygame.draw.rect(screen, screen_info_c, (50, 100, 400, 400), 4)
    screen.blit(description, (500, 100))
    screen.blit(stat1, (500, 340))
    screen.blit(stat2, (500, 360))
    screen.blit(stat3, (500, 380))
    screen.blit(stat4, (500, 400))
    screen.blit(stat5, (500, 420))
    screen.blit(stat6, (500, 440))
    screen.blit(stat7, (500, 460))
    screen.blit(stat8, (500, 480))
    screen.blit(char_name, (50, 50))

"""
NAME: unicorn
DESCRIPTION: Resembles a big white horse with a lions tail and a sharp, spiral horn on its forehead. The unicorn is quick and agile. This wonderful creature can fire a glaring energy bolt from its magical horn.
STATS:
Moving type: ground - 4
Speed: normal
Attack type: energy bolts
Attack strength: moderate
Attack speed: fast
Attack interval: short
Life span: average
Number of characters: 2
"""


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
_STATIC_TILES = [(0,0), (0,1), (0,2), (0,4), (0,6), (0,7), (0,8), (1,0), (1,1), (1,3), (1,5), (1,7), (1,8), (2,0), (2,2), (2,3), (2,5), (2,6), (2,8), (3,1), (3,2), (3,3), (3,5), (3,6), (3,7), (5,1), (5,2), (5,3), (5,5), (5,6), (5,7), (6,0), (6,2), (6,3), (6,5), (6,6), (6,8), (7,0), (7,1), (7,3), (7,5), (7,7), (7,8), (8,0), (8,1), (8,2), (8,4), (8,6), (8,7), (8,8)]
                                ##LIGHT --> DARK##
_TILE_COLORS = [(164, 200, 252), (124,156,220), (80,112,188), (56, 74, 176), (48, 32, 152), (0, 44, 92)]
_ENERGY_SQUARES = [(0, 4), (4,0), (4,4), (4,8), (8,4)]

board_x = 256 + 128
board_y = 64
light_square = pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\220220220LightTile.png')
board_data = [[ _TILE_COLORS[5] ,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5],0, _TILE_COLORS[0], 0, _TILE_COLORS[0], 0, _TILE_COLORS[5], _TILE_COLORS[0]], [_TILE_COLORS[5] ,0,_TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5]], [(220,220,220) , _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0], 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [0 , _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[5], _TILE_COLORS[0], _TILE_COLORS[5], 0], [_TILE_COLORS[0] ,0,_TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[0], _TILE_COLORS[5], 0, _TILE_COLORS[0]], [_TILE_COLORS[5] , _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5]], [_TILE_COLORS[0] , _TILE_COLORS[5], _TILE_COLORS[0], 0, _TILE_COLORS[5], 0, _TILE_COLORS[0], _TILE_COLORS[5], _TILE_COLORS[0]]]
turn = 0



def game_scene():
    screen.fill((220,220,0))

"""
|||    BOARD   |||
"""
player_board_x = 0
player_board_y = 0
turn_player = 0
_PLAYERS_COLOR = [(255, 255, 255), (0,0,0)]

##ENERGY SQUARE ANIMATION##
energy_square_frames = [pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF1.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF1.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF1.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF2.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF2.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF3.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF3.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF4.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF4.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF5.png'), pygame.image.load(r'C:\Users\asus\uni\fpro\ProjetoFPRO\projfpro\projetofpro\Resources\Sprites\Tiles\EnergySquare\EnergySquareF5.png')]
es_cur_anim = 0
es_anim_cycle = 1
##ENERGY SQUARE ANIMATION##
def es_handle_animation():
    global es_cur_anim, es_anim_cycle
    es_cur_anim += 1 * es_anim_cycle
    if es_cur_anim == 0 or es_cur_anim == len(energy_square_frames)-1:
        es_anim_cycle *= -1

_start = True
def board():
    global es_cur_anim
    turn_number = medium_gm_font.render(f'Turn: {turn}', 1, (00, 00, 00))

    #LOGIC


    #DRAW
    screen.fill((112, 40, 0))
    for i in range(0, 9):
        for j in range(0,9):
            if board_data[i][j] != None:
                pygame.draw.rect(screen, board_data[i][j], Rect(board_x + (56*i), board_y + 56*(j), 56, 56), 0)
    screen.blit(turn_number, (50, 50))
    for es_sq in _ENERGY_SQUARES:
        es_x, es_y = es_sq
        screen.blit(energy_square_frames[es_cur_anim], (board_x + (56*es_y), board_y + (56*es_x)))

    pygame.draw.rect(screen, _PLAYERS_COLOR[turn_player], Rect(board_x + (56*player_board_y), board_y + (56*player_board_x), 56, 56), 4)

cur_color = 0
cycle = 1

def board_color_switch():
    global cur_color
    global cycle
    cur_color += cycle
    if (cur_color == 5) or (cur_color == 0):
        cycle *= -1
    for i in range(0, 9):
        for j in range(0,9):
            if not ((i,j) in _STATIC_TILES):
                board_data[i][j] = _TILE_COLORS[cur_color]

def next_turn():
    global turn
    turn += 1
    board_color_switch()
    
def move_on_board(direc):
    x, y = direc
    global player_board_x
    global player_board_y
    if player_board_x + x > -1 and player_board_x + x < 9:
        player_board_x += x
    if player_board_y + y > -1 and player_board_y + y < 9:
        player_board_y += y


#---

def arena():
    pass

""" 
~~~~~~~~~~~~~~~~~~
"""

es_mlsecs = 0
running = True

while running:
    pygame.time.delay(100)
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
                    if event.key == K_UP or event.key == K_w:
                        playing = True
                        next_turn()
            #game keys
            elif current_scene == 'game' and playing:
                if event.type == pygame.KEYDOWN:
                    if event.key == K_UP or event.key == K_w:
                        move_on_board((-1,0))
                    if event.key == K_DOWN or event.key == K_s:
                        move_on_board((1,0))
                    if event.key == K_LEFT or event.key == K_a:
                        move_on_board((0,-1))
                    if event.key == K_RIGHT or event.key == K_d:
                        move_on_board((0,1))
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
                        """
                        if event.key == K_RETURN or event.key == K_SPACE:
                            if rules_sel == 0:
                                current_scene = 'menu'
                            if rules_sel == 1:
                                rules_screen = 1
                            if rules_sel == 2:
                                rules_screen = 3
                        if event.key == K_UP or event.key == K_w:
                            rules_sel += 1
                        elif event.key == K_DOWN or event.key == K_s:
                            rules_sel -= 1
                        """
                        rules_screen = 2
                    elif rules_screen == 3:
                        """
                        if event.key == K_RETURN or event.key == K_SPACE:
                            if rules_sel == 0:
                                current_scene = 'menu'
                            if rules_sel == 1:
                                rules_screen = 1
                            if rules_sel == 2:
                                rules_screen = 3
                        if event.key == K_UP or event.key == K_w:
                            rules_sel += 1
                        elif event.key == K_DOWN or event.key == K_s:
                            rules_sel -= 1
                        """
                        rules_screen = 4
                    elif rules_screen == 2 or rules_screen == 4:
                        if rules_screen == 2:
                            rules_screen = 3
                        else:
                            rules_screen = 1


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
    else:
        menu()
        
    build_warning = debug_font.render("UNDER DEVELOPMENT", 1, (255, 00, 00))
    screen.blit(build_warning, (0,0))
    pygame.display.update()
    es_handle_animation()
    dt = clock.tick(30)

pygame.quit()