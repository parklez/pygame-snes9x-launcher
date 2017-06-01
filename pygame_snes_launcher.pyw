#############################
directory = 'Roms/'

screenshots_dir = 'Screenshots/'

emulator_file = 'snes9x-x64'

launch_options = '-fullscreen'
#############################
#Pygame window
resolution = (800, 600)

fullscreen = False

#Other
hide_mouse_pointer = True

mouse_hider_exe = 'AutoHideMouseCursor_x64'
#############################
import pygame, subprocess, os
from random import randint
from math import sqrt

#Folders
if not os.path.exists(directory):
    os.makedirs(directory)
    
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)

#initialize pygame
pygame.mixer.pre_init(44100, -16, 2, 512)

pygame.init()

#Display
def set_display_mode(fullscreen):
    global display
    
    if fullscreen:
        display = pygame.display.set_mode((resolution), pygame.FULLSCREEN)
    else:
        display = pygame.display.set_mode((resolution))
        
set_display_mode(fullscreen)

#Clock
tick_rate = pygame.time.Clock()

#Scaling
scale = 16
di = sqrt(resolution[0]**2+resolution[1]**2)/scale
xu = resolution[0]/scale
yu = resolution[1]/scale

#Fonts
if di > 100:
    font_size = 28
else:
    font_size = 15
font = pygame.font.Font('pygame/pixelmix.ttf', font_size)

#Images
icon = pygame.image.load('pygame/icon.ico')
dark_overlay = pygame.transform.scale(pygame.image.load('pygame/dark.png'), (resolution[0], resolution[1]))
menu_bg = pygame.transform.scale(pygame.image.load('pygame/menu.png').convert(), (resolution[0], resolution[1]))
missing_texture = pygame.image.load('pygame/default.png').convert()
playing_bg = pygame.image.load('pygame/playing.png').convert()
tile_overlay = pygame.image.load('pygame/tile_options.png')

#Icon and window title
pygame.display.set_icon(icon)
pygame.display.set_caption('Pygame SNES Launcher')

#Colors
grey = (29,29,29)
grey2 = (16,16,16)
green2 = (189,219,159)

#Variables
games_list = sorted(os.listdir(directory))
games_screenshots_list = (os.listdir(screenshots_dir))

#Classes & Functions
class FancyText():
    def __init__(self, surface, text):
        'Renders text with shadow.'
        self.surface = surface
        self.text = font.render(text, False, (255, 255, 255))
        self.text_shadow = font.render(text, False, (0, 0, 0))
        
    def render(self, pos):
        #Borders / Shadows
        self.surface.blit(self.text_shadow, (pos[0] - 1, pos[1] - 1)) # up right
        self.surface.blit(self.text_shadow, (pos[0] + 1, pos[1] - 1)) # up left
        self.surface.blit(self.text_shadow, (pos[0] - 1, pos[1] + 1)) # down left
        self.surface.blit(self.text_shadow, (pos[0] + 1, pos[1] + 1)) # down right
        
        #White
        self.surface.blit(self.text, (pos[0], pos[1]))
        
        
class Tile():
    def __init__(self, game_file, surface, rect=[xu, yu, xu*5, yu*6]):
        'Creates a Tile for a game.'
        self.surface = surface
        self.game = game_file
        self.name = self.game.split('.')[0]
        self.name_display = self.shorten_game_name_display(self.name)
        self.rect = pygame.Rect(rect)
        
        self.tile_file = self.get_tile_frame()
        self.tile = pygame.transform.scale(self.tile_file, (int(self.rect[2]), int(self.rect[3])))
        
        self.tile_options = pygame.transform.scale(tile_overlay, (int(self.rect[2]), int(self.rect[3])))
        
        self.is_selected = False
        self.game_name_text = FancyText(self.surface, self.name_display)
        self.selected_color = (176,196,222)

        
    def shorten_game_name_display(self, name):
        name_size = font.size(name)
        
        if name_size[0] < xu*5:
            return name

        while name_size[0] > xu*5:
            name = name[:-1]
            name_size = font.size(name)
        
        return name + '[...]'
        
    def get_tile_frame(self):
        'Returns an image for the tile.'
        if self.name + '000.png' in games_screenshots_list:
            return pygame.image.load(screenshots_dir + self.name + '000.png').convert()
        else:
            return missing_texture
    
    def move_tile(self, direction):
        if direction == 'left':
            self.rect[0] -= xu*6
            
        if direction == 'right':
            self.rect[0] += xu*6
            
        if direction == 'up':
            self.rect[1] -= yu*8
            
        if direction == 'down':
            self.rect[1] += yu*8

    def render(self):
        #Selected border
        if self.is_selected:
            pygame.draw.rect(self.surface, self.selected_color, self.rect, int(xu/3))
            
        #Text
        self.game_name_text.render((self.rect[0], self.rect[1] - yu/2))
            
        #Tile
        self.surface.blit(self.tile, (self.rect[0], self.rect[1]))
        if self.is_selected:
            self.surface.blit(self.tile_options, (self.rect[0], self.rect[1]))

        
class Selector():
    'This simulates some kind of mouse pointer to select over the options on the screen.'
    def __init__(self, surface, object_list, rect=[xu*3, yu*4, xu, yu]):
        self.rect = pygame.Rect(rect)
        self.surface = surface
        self.sound = pygame.mixer.Sound('pygame/select.ogg')
        self.sound_nope = pygame.mixer.Sound('pygame/nope.ogg')
        self.sound_play = pygame.mixer.Sound('pygame/play.ogg')
        self.object_list = object_list
        self.game_selected = 'None'
        
    def move_pointer(self, direction):
        if direction == 'left':
            self.rect[0] += int(xu*6)
            
        if direction == 'right':
            self.rect[0] -= int(xu*6)
        
        if direction == 'up':
            self.rect[1] -= int(yu*7)
            
        if direction == 'down':
            self.rect[1] += int(yu*7)
            
        self.sound.play()
        
    def check_collision(self):
        for tile in self.object_list:
            if self.rect.colliderect(tile.rect):
                tile.is_selected = True
                self.game_selected = tile.game
            else:
                tile.is_selected = False

    def render(self):
        'Shows the pointer rectangle.'
        pygame.draw.rect(self.surface, green2, self.rect)
        
        
def create_tiles(surface):
    'Returns a list of Tiles.'
    tiles = [Tile(rom, surface) for rom in games_list]
    return tiles

def grid2(screen, scale=16, color=(255,255,255), width=1):
    'Creates a grid within the screen resolution to see how "xu" and "yu" are.'
    info = pygame.display.Info()
    res = (info.current_w, info.current_h)
    if scale <= 0:
        scale = 1
    xu = res[0]/scale
    yu = res[1]/scale
    array = [0,0]
    for lines in range(scale):
        #Horizontal
        pygame.draw.line(screen,color,(0,array[0]),(res[0],array[0]), width)
        #Vertical
        pygame.draw.line(screen,color,(array[1],0),(array[1],res[1]), width)
        array[0] += yu
        array[1] += xu

#Launcher
def launch(game):
    #The following line uses 'os' module instead of subprocess.
    #os.system(emulator_file + ' ' + launch_options + ' ' + '"' + game + '"')
    subprocess.call(emulator_file + ' ' + launch_options + ' ' + '"' + game + '"')
        
#Tiling
tiles_list = create_tiles(display)
        
def arrange_tiles(tiles_list, rows=2):
    'Maybe in future this will allow users to choose how many tiles they want.'
    tile_rect = tiles_list[0].rect #Tile rect sample
    x, y = tile_rect[0], tile_rect[1]
    i = 0
    
    for tile in tiles_list:
        if i == 0: #The first doesn't change...
            i = 1

        elif i < rows: #Tiles that will move down
            y += tile_rect[1] + tile_rect[3]
            i += 1

        elif i == rows: #Tile that will move up and right.
            x += tile_rect[0] + tile_rect[2]
            y = tile_rect[1]
            i = 1
            
        tile.rect[0], tile.rect[1] = x, y

if tiles_list:
    arrange_tiles(tiles_list)

#Game Selector
selector = Selector(display, tiles_list)
    
#Text
tile_menu_text_exit = FancyText(display, 'EXIT GAME: RIGHT CTRL + ENTER')
tile_menu_text_screenshot = FancyText(display, 'SCREENSHOT: F9')
text_get_games = FancyText(display, 'Roms folder empty! Go get some games at "www.emuparadise.me"! C:')
text_games_available = FancyText(display, 'GAMES: ' + str(len(games_list)))

#Main loop
def main_menu():
    global display
    
    running = True
    selector_row = 0
    selector_col = 0
    selector_pos = 'left'
    frames = 0
    
    if len(games_list) % 2:
        tiles_length = int(len(games_list)/2)
    else:
        tiles_length = int(len(games_list)/2) - 1
    
    while running:
        for x in pygame.event.get():
            if x.type == pygame.QUIT:
                running = False
                
            if x.type == pygame.KEYDOWN:
                if x.key == pygame.K_ESCAPE:
                    running = False
                    
                if x.key == pygame.K_a:
                    if selector_pos == 'left':
                        if selector_col > 0:
                            for tile in tiles_list:
                                tile.move_tile('right')
                            selector.sound.play()
                            selector_col -= 1
                        else:
                            selector.sound_nope.play()
                    else:
                        if selector_col > 0:
                            selector.move_pointer('right')
                            selector_pos = 'left'
                            selector_col -= 1
                
                if x.key == pygame.K_d:
                    if selector_pos == 'right':
                        if selector_col < tiles_length:
                            for tile in tiles_list:
                                tile.move_tile('left')
                            selector.sound.play()
                            selector_col += 1
                        else:
                            selector.sound_nope.play()
                    else:
                        if selector_col < tiles_length:
                            selector.move_pointer('left')
                            selector_pos = 'right'
                            selector_col += 1
                            
                        else:
                            selector.sound_nope.play()
                    
                if x.key == pygame.K_w:
                    if selector_row > 0:
                        selector.move_pointer('up')
                        selector_row -= 1
                    
                if x.key == pygame.K_s:
                    if selector_row < 1:
                        selector.move_pointer('down')
                        selector_row += 1
                        
                if x.key == pygame.K_e:
                    pass #future: make L and R move tiles faster
                    
                if x.key == pygame.K_u:
                    pass #future: make L and R move tiles faster
                        
                if x.key == pygame.K_RETURN:
                    selector.sound_play.play()
                    
                    #Change the display to a small window
                    display = pygame.display.set_mode((200,200))
                    display.blit(playing_bg, (0,0))
                    pygame.display.update()
                    
                    #Launch the emulator and perhaps cursor hider
                    if hide_mouse_pointer:
                        subprocess.Popen(mouse_hider_exe)
                        
                    launch(selector.game_selected)
                    
                    #Kill the cursor hider
                    if hide_mouse_pointer:
                        subprocess.call('taskkill /f /im ' + mouse_hider_exe + '.exe')
                    
                    #Reset pygame display to how it was before
                    set_display_mode(fullscreen)

                    #May it help to restore the focus?!
                    pygame.display.get_active()
                    
                    #Sound
                    #pygame.mixer.Sound('pygame/quit.ogg').play()
        
        #Updates
        #Game selector
        selector.check_collision() #It could check for collision only when it moves...
        
        #Graphics
        display.fill(grey2)
        grid2(display, color=grey)
        display.blit(menu_bg, (0,0))
        display.blit(dark_overlay, (0,0))
        
        #Tiles
        for tile in tiles_list:
            tile.render()
            
        #Overlay & Text
        tile_menu_text_exit.render((xu, yu*15))
        tile_menu_text_screenshot.render((xu*8, yu*15))
        text_games_available.render((xu*12, yu*15))
        
        #Selector
        #selector.render()
        
        if not games_list:
            text_get_games.render((xu, yu*6))
        
        #Update the display
        pygame.display.update()
        tick_rate.tick(60)
    
    #The End c:
    pygame.quit()
    quit()
        
#Options Menu
def options_menu():
    pass
    
if __name__ == "__main__":
    main_menu()
    