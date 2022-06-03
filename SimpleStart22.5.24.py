# Known Bugs
#    - Friends Disappear if overlapping during grab.

import pygame
import pygame.freetype

# --- constants ---
SURFACE_COLOR = (0,0,0)
COLOR = (255,255,255)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
WHITE = (0,0,0)
meSizeY = 50
meSizeX = 50
friendSizeY = 50
friendSizeX = 50
Gravity = .5


# --- classes ---
class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(COLOR)
        self.image.set_colorkey(COLOR)
        
        pygame.draw.ellipse(self.image, color, pygame.Rect(0,0,width,height))
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False
        self.atMenu = True
        
class SpriteRect(pygame.sprite.Sprite):   # Used to create the Menu, probably didn't have to use Classes for this in hindsight, could clean up
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(COLOR)
        self.image.set_colorkey(COLOR)
        
        pygame.draw.rect(self.image, color, pygame.Rect(0,0,width,height), 5)
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False

class SpriteText(pygame.sprite.Sprite):   # Used to create text object
    def __init__(self, color, width, height, text):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(COLOR)
        self.image.set_colorkey(COLOR)
        
        self.text = text
        self.font = pygame.freetype.SysFont('Arial', 30)
        pygame.draw.rect(self.image, color, pygame.Rect(0,0,width,height), 2)
        self.font.render_to(self.image, (0,0), self.text)
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False
        
# --- functions ---

   # empty

# --- main function ---
def main():
    
    # --Initiatilize The Pygame --
    pygame.init()
    clock = pygame.time.Clock()
    
    # - Create The Screen -
    screenflags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((0,0))#,screenflags) # Add screenflags back in to go fullscreen.
    
    pygame.display.set_caption("Simple Start in Pygame")
    screenH = screen.get_height() # Grab whatever screen size resulted from (0,0) above.
    screenW = screen.get_width() # Grab whatever screen size resulted from (0,0) above.
    menuBorder = ((screenW - (screenW / 6)),25) # Defines leftuppermost point of the menu
    
    # - Create The Sprites -
    
    all_sprites_list = pygame.sprite.Group() # Creates group for all pygame sprites
    friendGroup = pygame.sprite.Group()
    
    # Create Me
    me = Sprite(BLUE, meSizeX, meSizeY) # Calls Sprite class with args(color, width, height)
    me.rect.y = ((screenH + meSizeY) / 2)  # Rect coordintes to y postion of sprites top left corner; assigns intial location
    me.rect.x = ((screenW + meSizeX) / 2) # Rect coordinates to x position of sprites top left corner; assigns intial location
    me.id = "me"
    all_sprites_list.add(me) # Add me to the total list

    # Create MenuSubtitles&Borders
    submenu = SpriteText(WHITE, 100, 50, "Test")
    submenu.rect.x = 200
    submenu.rect.y = 200
    submenu.id = "submenu"
    all_sprites_list.add(submenu)
    
    for i in range(0,3):
        for j in range(0,3):
            friend = Sprite(GREEN, friendSizeY, friendSizeX)
            friend.rect.y = (menuBorder[1] + 60 + (120 * j)) # Defines leftuppermost point of starting friend sprite array
            friend.rect.x = (menuBorder[0] + 30 + (60 * i)) # Defines leftuppermost point of starting friend sprite array
            friend.id = "friend"
            all_sprites_list.add(friend)
            friendGroup.add(friend)
    
    # Create Menu
    menu = SpriteRect((0, 100, 255), ((screenW / 6) - 25), (screenH - 100))
    menu.rect.x, menu.rect.y = menuBorder
    menu.id = "menu"
    all_sprites_list.add(menu)
            
    # -- Main Loop --
    running = True
    while running:
        
        # - Events -
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # - Key Board Events -
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    running = False
                    
            # Sprite Mouse Stuff        
            for sprite in all_sprites_list: # Iterates over every sprite, checking for mouse interaction
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if sprite.rect.collidepoint(event.pos) and sprite.id == "friend": # Test if mouse pressed on friend sprite
                            sprite.drag = True
                            mouse_x, mouse_y = event.pos
                            offset_x = sprite.rect.x - mouse_x
                            offset_y = sprite.rect.y - mouse_y
                            print("Clicked inside sprite!")
                            print(offset_x,offset_y)
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        sprite.drag = False
                
                elif event.type == pygame.MOUSEMOTION:
                    if sprite.drag:
                        mouse_x, mouse_y = event.pos
                        sprite.rect.x = mouse_x + offset_x
                        sprite.rect.y = mouse_y + offset_y
                    if sprite.id == "friend" and sprite.atMenu == True and not (menu.rect.contains(sprite.rect)): # If friend leaves the menu, create another
                        friend = Sprite(GREEN, friendSizeY, friendSizeX)
                        friend.rect.x = menuBorder[0] + 30
                        friend.rect.y = menuBorder[1] + 60
                        all_sprites_list.add(friend)
                        friendGroup.add(friend)
                        friend.id = "friend"
                        sprite.atMenu = False
                        
        # - Updates (without draws) -
        
#         for sprite in all_sprites_list: # Adds gravity (change in y) to all sprites for lolz
#             sprite.rect.y = sprite.rect.y + Gravity
        
        all_sprites_list.update()
        
        # - Draws (without updates) -
        screen.fill(SURFACE_COLOR)
        all_sprites_list.draw(screen)
        pygame.display.flip() # Updates the contents of the entire display.
        
        # - Tick the Clock -
        clock.tick(60) # Prevents program from running faster than 60 frames per second. Uses SDL_Delay function which is not that accurate but saves CPU.
        

    # - End while loop when running=False -
    pygame.quit()


# ---- Call The Function ----
main()


