# Known Bugs
#    - Friends Disappear if overlapping during grab.

import pygame
import pygame.freetype
import sys

# --- constants ---
SURFACE_COLOR_BLACK = BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (220, 220, 220)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
Gravity = .5

meSizeY = 50
meSizeX = 50

NodeTotalSizeY = 100
NodeTotalSizeX = 100
NodeSizeY = NodeTotalSizeY / 2
NodeSizeX = NodeTotalSizeX / 2
NodeTextBufferY = NodeSizeY * 1.2
NodeTextBufferX = 0
NodeTextColor = GREY
NodeTextSize = 20

# --- classes ---
class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        
        pygame.draw.ellipse(self.image, color, pygame.Rect(0,0,width,height))
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False
        self.atMenu = True
        self.active = False
        
class SpriteRect(pygame.sprite.Sprite):   # Used to create the Menu, probably didn't have to use Classes for this in hindsight, could clean up
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)
        
        pygame.draw.rect(self.image, color, pygame.Rect(0,0,width,height), 5)
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False
        self.active = False

class Node(pygame.sprite.Sprite):
    def __init__(self, nodecolor, nodetextcolor, width, height, text, size):
        super().__init__()
        
        self.text = text
        self.nodecolor = nodecolor
        self.nodetextcolor = nodetextcolor
        self.width = width
        self.size = size
        self.image = pygame.Surface([width, height])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE) # Anything on this Surface that is the color 'WHITE' will appear transparent 
        self.font = pygame.freetype.SysFont('Arial', self.size)
        pygame.draw.ellipse(self.image, nodecolor, pygame.Rect(width*.25,0,NodeSizeX,NodeSizeY))
        self.font.render_to(self.image, (NodeTextBufferX,NodeTextBufferY), self.text, nodetextcolor)
        
        self.rect = self.image.get_rect()
        self.id = ""
        self.drag = False
        self.active = False
        self.atMenu = True
        
    def update(self): # Called when .update is called for all sprites in sprite list below 
        if self.active: # Swap colors of the selected node for easier identification when typing
            self.nodecolor = RED
            self.nodetextcolor = RED
        else:
            self.nodecolor = GREEN
            self.nodetextcolor = GREY
        self.image.fill(WHITE)    
        pygame.draw.ellipse(self.image, self.nodecolor, pygame.Rect(self.width*.25,0,NodeSizeX,NodeSizeY))
        self.font.render_to(self.image, (NodeTextBufferX,NodeTextBufferY), self.text, self.nodetextcolor)
        
# --- functions ---

   # empty

# --- main function --- Runs Once
def main(): 
    
    # --Initiatilize The Pygame --
    pygame.init()
    clock = pygame.time.Clock()
    
    # - Create The Screen & Local Variables -
    screenflags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((0,0))#,screenflags) # Add screenflags back in to go fullscreen.
    
    pygame.display.set_caption("Simple Start in Pygame")
    screenH = screen.get_height() # Grab whatever screen size resulted from (0,0) above.
    screenW = screen.get_width() # Grab whatever screen size resulted from (0,0) above.
    menuBorder = ((screenW - (screenW / 6)),25) # Defines leftuppermost point of the menu
    UserText = "Type Name"
    
    # - Create The Sprites -
    all_sprites_list = pygame.sprite.Group() # Creates group for all pygame sprites
    NodeGroup = pygame.sprite.Group()
    
    # Create Me
    me = Sprite(BLUE, meSizeX, meSizeY) # Calls Sprite class with args(color, width, height)
    me.rect.y = ((screenH - meSizeY) / 2)  # Rect coordintes to y postion of sprites top left corner; assigns intial location
    me.rect.x = ((screenW - meSizeX) / 2) # Rect coordinates to x position of sprites top left corner; assigns intial location
    me.id = "me"
    all_sprites_list.add(me) # Add me to the total list
    
    # Create Node
    NodeSprite = Node(GREEN, NodeTextColor, NodeTotalSizeY, NodeTotalSizeX, UserText, NodeTextSize)
    NodeSprite.rect.x, NodeSprite.rect.y = ((menuBorder[0] + 30), (menuBorder[1] + 30))
    NodeSprite.id = "node"
    all_sprites_list.add(NodeSprite)
    NodeGroup.add(NodeSprite)
    
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
            elif event.type == pygame.KEYDOWN:
                for sprite in all_sprites_list: # Iterates over every sprite, checking for keyboard interaction
                    if sprite.active:
                        if event.key == pygame.K_BACKSPACE: # Checks for backspace seperately 
                            sprite.text = sprite.text[:-1] # Clears text?
                        else:
                            sprite.text = sprite.text + event.unicode
                            
                        sprite.update()
            # - Mouse Events -        
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for sprite in all_sprites_list: # Iterates over every sprite, checking for mouse interaction
                        if sprite.rect.collidepoint(event.pos) and sprite.id == "node": # Tests if mouse pressed on friend sprite
                            sprite.drag = True
                            sprite.active = True

                            mouse_x, mouse_y = event.pos
                            offset_x = sprite.rect.x - mouse_x
                            offset_y = sprite.rect.y - mouse_y
                            
                        else:
                            sprite.active = False

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for sprite in all_sprites_list: # Iterates over every sprite, checking for mouse interaction
                        sprite.drag = False
                
            elif event.type == pygame.MOUSEMOTION:
                for sprite in all_sprites_list: # Iterates over every sprite, checking for mouse interaction
                    if sprite.drag:
                        mouse_x, mouse_y = event.pos
                        sprite.rect.x = mouse_x + offset_x
                        sprite.rect.y = mouse_y + offset_y
                    
                    if sprite.id == "node" and sprite.atMenu == True and not (menu.rect.contains(sprite.rect)): # If node leaves the menu, create another
                        NodeSprite = Node(GREEN, NodeTextColor, NodeTotalSizeY, NodeTotalSizeX, UserText, NodeTextSize)
                        NodeSprite.rect.x, NodeSprite.rect.y = ((menuBorder[0] + 30), (menuBorder[1] + 30))
                        NodeSprite.id = "node"
                        all_sprites_list.add(NodeSprite)
                        NodeGroup.add(NodeSprite)
                    
                        sprite.atMenu = False
                            
        # - Updates (without draws) -
        all_sprites_list.update()
        
        # - Draws (without updates) -
        screen.fill(SURFACE_COLOR_BLACK)
        all_sprites_list.draw(screen)
        pygame.display.flip() # Updates the contents of the entire display.
        
        # - Tick the Clock -
        clock.tick(60) # Prevents program from running faster than 60 frames per second. Uses SDL_Delay function which is not that accurate but saves CPU.
        
    # - End while loop when running=False -
    pygame.quit()

# ---- Call The Function ----
main()


