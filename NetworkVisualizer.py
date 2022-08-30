# Known Bugs
#    - Friends Disappear if overlapping during grab.

import pygame
import pygame.freetype
import csv

# --- constants ---
SURFACE_COLOR_BLACK = BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (220, 220, 220)
RED = (255,0,0)
BLUE = (0,0,255)
MENUBLUE = (0, 100, 255)
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

LineWidth = 4
startp_x = startp_y = 0

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

class Line(pygame.sprite.Sprite):   # Used to create the lines between nodes
    def __init__(self, color, firstX, firstY, secondX, secondY):
        super().__init__()
        
        H = secondY - firstY
        W = secondX - firstX
        
        self.image = pygame.Surface([abs(W), abs(H)])
        self.image.fill(BLACK)
        self.image.set_colorkey(BLACK)
        self.color = color
        self.firstX = firstX
        self.firstY = firstY
        self.secondX = secondX
        self.secondY = secondY
                
        pygame.draw.line(self.image, self.color, (0, 0), (100, 100), LineWidth)
        self.rect = self.image.get_rect() # Do we need this?
        
        self.id = ""
        self.drag = False
        self.active = False
        self.connections = []
        
    def update(self):
        self.image.fill(BLACK)
        pygame.draw.line(self.image, self.color, (self.firstX, self.firstY), (self.secondX, self.secondY), LineWidth)
    
    def clear(self):
        self.image.fill(BLACK)
        
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
        self.connections = []
        
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

def save_objects(obj): # Creates a csv file and writes the argument list into it.
    try:
        with open("data.csv", 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(obj)
        print("Saved!")
    except Exception as ex:
        print("Error during writing csv file", ex)
        
def load_objects(): # Opens a local csv file and extracts the data as a list. Could insert an argument to allow selecting of different loads.
    NodeGroupInfo = []
    try:
        with open('data.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                NodeGroupInfo.append(row)
            return NodeGroupInfo
    except Exception as ex:
        print("Error during loading csv file", ex)
        return False

def connect(prevSP, currSP, NodeGroup): # Looks up and grabs positions of previous Sprite & current Sprite by name text.
    #print(prevSP,currSP)
    for sprite in NodeGroup: # Pull all Node sprite location and text
        if prevSP == sprite.text:
            startp_x = sprite.rect.x
            startp_y = sprite.rect.y
        if currSP == sprite.text:
            finalp_x = sprite.rect.x
            finalp_y = sprite.rect.y
    
    startp_x = startp_x + NodeTotalSizeX/2
    startp_y = startp_y + NodeSizeY/2
    finalp_x = finalp_x + NodeTotalSizeX/2
    finalp_y = finalp_y + NodeSizeY/2
    
    return startp_x, startp_y, finalp_x, finalp_y

def disconnect(text, NodeGroup):  # remove the other sprite's name from the 1st sprite's connection list.
    print(text)
    for sprite in NodeGroup:
        for k in range(0,len(sprite.connections)):
            if (sprite.connections[k] == text[0]) or (sprite.connections[k] == text[1]):
                sprite.connections.pop(k)
                #print("The line between ", sprite.connections[0], " and ", sprite.connections[1], " has been deleted.")

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
    previousSpriteName = ""
    
    # - Create The Sprites -
    all_sprites_list = pygame.sprite.Group() # Creates group for all pygame sprites
    NodeGroup = pygame.sprite.Group()
    LineGroup = pygame.sprite.Group()
    
    # Create Me
    me = Sprite(BLUE, meSizeX, meSizeY) # Calls Sprite class with args(color, width, height)
    me.rect.y = ((screenH - meSizeY) / 2)  # Rect coordintes to y postion of sprites top left corner; assigns intial location
    me.rect.x = ((screenW - meSizeX) / 2) # Rect coordinates to x position of sprites top left corner; assigns intial location
    me.id = "me"
    all_sprites_list.add(me) # Add me to the total list
    
    # Create Menu
    menu = SpriteRect(MENUBLUE, ((screenW / 6) - 25), (screenH - 100))
    menu.rect.x, menu.rect.y = menuBorder
    menu.id = "menu"
    all_sprites_list.add(menu)
    
    # Create Node
     # Create all nodes from file
    NodeGroupInfo = load_objects()
    if not NodeGroupInfo:
        print("Nothing loaded.")
        # Create original layout of 1 node at menu 
        NodeSprite = Node(GREEN, NodeTextColor, NodeTotalSizeY, NodeTotalSizeX, UserText, NodeTextSize) 
        NodeSprite.rect.x, NodeSprite.rect.y = ((menuBorder[0] + 30), (menuBorder[1] + 30)) # Create Node that starts at menu
        NodeSprite.id = "node"
        all_sprites_list.add(NodeSprite)
        NodeGroup.add(NodeSprite)
    else: # If there is a file uploaded successfully, load the position and text of all the nodes
        for i in range(0,len(NodeGroupInfo)): # Clumsy method to strip out the 4 values of the csv sprite rect & draw the loaded nodes.
            NodeRect = str(NodeGroupInfo[i][0]) # First column (0) in csv matrix is the rect string
            #print(NodeRect) # Uncomment to have list of saved nodes printed to screen
            NodeRectStr = [0,0,0,0] # Will be filled with the 4 last character positions of the 4 position values (x, y, width, height) of each sprite rect.
            fComma = 0

            for j in range(0,3):
                fComma = NodeRect.find(',',fComma+1)
                NodeRectStr[j] = (str(fComma))
            fPara = NodeRect.find(')')
            NodeRectStr[3] = str(fPara)

            NodeRect_x = NodeRect[6:int(NodeRectStr[0])] # Ripping 1st value between the established last character position.
            NodeRect_y = NodeRect[(int(NodeRectStr[0])+1):int(NodeRectStr[1])] # Ripping 2nd value between the established last character position.
            NodeRect_w = NodeRect[(int(NodeRectStr[1])+1):int(NodeRectStr[2])] # Ripping 3rd value between the established last character position.
            NodeRect_h = NodeRect[(int(NodeRectStr[2])+1):fPara] # Ripping 4th value between the established last character position.
            NodeFinalRect = pygame.Rect((int(NodeRect_x), int(NodeRect_y)), (int(NodeRect_w), int(NodeRect_h))) # Create final rect with ripped values.
            
            NodeSprite = Node(GREEN, NodeTextColor, NodeTotalSizeY, NodeTotalSizeX, NodeGroupInfo[i][1], NodeTextSize) # Second column (1) in csv matrix is the name string
            NodeSprite.rect = NodeFinalRect
            NodeSprite.id = "node"
            if menu.rect.contains(NodeSprite.rect):
                NodeSprite.atMenu = True
            else:
                NodeSprite.atMenu = False
            all_sprites_list.add(NodeSprite)
            NodeGroup.add(NodeSprite)
            
        for i in range(0,len(NodeGroupInfo)): # Now we do the line connections
            NodeConnectionsStr = str(NodeGroupInfo[i][2]) # Strip out connection strings for iterating through. Converting back from csv seems to lose matrix.
            NodeConnectionsStrRem = NodeConnectionsStr[1:-1]
            NodeConnectionsStrTem = NodeConnectionsStrRem.replace(" ","")
            NodeConnectionsStrFin = NodeConnectionsStrTem.replace("'","")
            print(NodeConnectionsStrFin)
            if not NodeConnectionsStrFin: # Check if empty, 1st condition.
                NodeConnectionName = []
            else:            
                fComma = 0
                NodeConnectionName = []
                startSlice = 0
                if NodeConnectionsStrFin.count(','): # Check if more than 1 entry, 2nd condition. If so there should be a comma separating values.
                    for j in range(0,NodeConnectionsStrFin.count(',')):
                        fComma = NodeConnectionsStrFin.find(',',fComma)
                        NodeConnectionName.append(NodeConnectionsStrFin[startSlice:fComma])
                        fComma+=1
                        startSlice = fComma
                    NodeConnectionName.append(NodeConnectionsStrFin[startSlice:]) # Can't forget to add last name after last comma.
                else:                                # If not, load the value into the first slot
                    NodeConnectionName.append(NodeConnectionsStrFin)
            print(NodeConnectionName)
            if NodeConnectionName:
                for l in range(0,len(NodeConnectionName)):
                    startp_x, startp_y, finalp_x, finalp_y = connect(NodeGroupInfo[i][1], NodeConnectionName[l], NodeGroup) # Run function to determine positions of previous and current sprite. Should return 4 values - startp_x, startp_y, finalp_x, finalp_y                            
                    LineSprite = Line(WHITE, startp_x, startp_y, finalp_x, finalp_y)
                                
                    H = finalp_y - startp_y 
                    W = finalp_x - startp_x
                    if H > 0 and W > 0:
                        LineSprite.firstX = 0
                        LineSprite.firstY = 0
                        LineSprite.secondX = abs(W)
                        LineSprite.secondY = abs(H)
                        LineSprite.rect.x, LineSprite.rect.y = (startp_x,startp_y)
                    elif H < 0 and W > 0:
                        LineSprite.firstX = 0
                        LineSprite.firstY = abs(H)
                        LineSprite.secondX = abs(W)
                        LineSprite.secondY = 0
                        LineSprite.rect.x, LineSprite.rect.y = (startp_x,finalp_y)
                    elif H < 0 and W < 0:
                        LineSprite.firstX = abs(W)
                        LineSprite.firstY = abs(H)
                        LineSprite.secondX = 0
                        LineSprite.secondY = 0
                        LineSprite.rect.x, LineSprite.rect.y = (finalp_x,finalp_y)
                    elif H > 0 and W < 0:
                        LineSprite.firstX = abs(W)
                        LineSprite.firstY = 0
                        LineSprite.secondX = 0
                        LineSprite.secondY = abs(H)
                        LineSprite.rect.x, LineSprite.rect.y = (finalp_x,startp_y)
                        
                    LineSprite.connections.append(NodeGroupInfo[i][1])
                    LineSprite.connections.append(NodeConnectionName[l])
                    all_sprites_list.add(LineSprite)
                    LineGroup.add(LineSprite)
                    # Adding connection info to sprites after loading connections lines
                    for sprite in NodeGroup:
                        if sprite.text == NodeGroupInfo[i][1] and not (NodeConnectionName[l] in sprite.connections):
                            sprite.connections.append(NodeConnectionName[l])
                        if sprite.text == NodeConnectionName[l] and not (NodeGroupInfo[i][1] in sprite.connections):
                            sprite.connections.append(NodeGroupInfo[i][1])
                           
    # -- Main Loop --
    running = True
    while running:
        
        # - Events -
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                NodeGroupInfo = []
                for sprite in NodeGroup: # On Quit, create a list to save the locations and text of each node
                    spriteinfo = [sprite.rect, sprite.text, sprite.connections]
                    NodeGroupInfo.append(spriteinfo)
                    print(spriteinfo)
                #print(NodeGroupInfo) # Uncomment to have list of saved nodes printed to screen 
                save_objects(NodeGroupInfo) # Call a function to create a csv file and save the list to it.
                running = False
            
            # - Key Board Events -
            elif event.type == pygame.KEYDOWN:
                for sprite in all_sprites_list: # Iterates over every sprite, checking for keyboard interaction
                    if sprite.active:
                        if event.key == pygame.K_BACKSPACE: # Checks for backspace seperately 
                            sprite.text = sprite.text[:-1] # Clears text?      
                        else:
                            sprite.text = sprite.text + event.unicode   
                        sprite.update() # .update() calls the sprite class' method defined as update()
                        
            # - Mouse Events -        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for sprite in NodeGroup: # Iterates over every sprite, checking for mouse interaction
                        if sprite.rect.collidepoint(event.pos): # Tests if mouse pressed on node sprite
                            sprite.drag = True
                            sprite.active = True
                            mouse_x, mouse_y = event.pos
                            offset_x = sprite.rect.x - mouse_x # Gets an offset so dragging can be done relative to mouse pos
                            offset_y = sprite.rect.y - mouse_y
                            previousSpriteName = sprite.text
                        else:
                            sprite.active = False
                 
                if event.button == 2:
                    for sprite in LineGroup:
                        if sprite.rect.collidepoint(event.pos):
                            disconnect(sprite.connections, NodeGroup) # Function pulls associated node names from line.connections & clears them.
                            sprite.kill()                            
                            sprite.clear()
                            print("The line between ", sprite.connections[0], " and ", sprite.connections[1], " has been deleted.")
                            
                if event.button == 3 and (previousSpriteName): #Ensure there is a previous sprite selected before moving forward with adding a line.
                    for sprite in NodeGroup:
                        if sprite.rect.collidepoint(event.pos) and not (sprite.text == previousSpriteName):
                            #try:
                            # Add connection text to each connected sprite. 
                            sprite.connections.append(previousSpriteName) # Add previous sprite name to current sprite's connections attribute list.
                            for nxtsprite in NodeGroup:
                                if nxtsprite.text == previousSpriteName:
                                    nxtsprite.connections.append(sprite.text) # Repeat for other end of connection
                            
                            startp_x, startp_y, finalp_x, finalp_y = connect(previousSpriteName, sprite.text, NodeGroup) # Run function to determine positions of previous and current sprite. Should return 4 values - startp_x, startp_y, finalp_x, finalp_y                            
                            LineSprite = Line(WHITE, startp_x, startp_y, finalp_x, finalp_y)
                                        
                            H = finalp_y - startp_y 
                            W = finalp_x - startp_x
                            if H > 0 and W > 0:
                                LineSprite.firstX = 0
                                LineSprite.firstY = 0
                                LineSprite.secondX = abs(W)
                                LineSprite.secondY = abs(H)
                                LineSprite.rect.x, LineSprite.rect.y = (startp_x,startp_y)
                            elif H < 0 and W > 0:
                                LineSprite.firstX = 0
                                LineSprite.firstY = abs(H)
                                LineSprite.secondX = abs(W)
                                LineSprite.secondY = 0
                                LineSprite.rect.x, LineSprite.rect.y = (startp_x,finalp_y)
                            elif H < 0 and W < 0:
                                LineSprite.firstX = abs(W)
                                LineSprite.firstY = abs(H)
                                LineSprite.secondX = 0
                                LineSprite.secondY = 0
                                LineSprite.rect.x, LineSprite.rect.y = (finalp_x,finalp_y)
                            elif H > 0 and W < 0:
                                LineSprite.firstX = abs(W)
                                LineSprite.firstY = 0
                                LineSprite.secondX = 0
                                LineSprite.secondY = abs(H)
                                LineSprite.rect.x, LineSprite.rect.y = (finalp_x,startp_y)
                                
                            LineSprite.connections.append(previousSpriteName)
                            LineSprite.connections.append(sprite.text)
                            all_sprites_list.add(LineSprite)
                            LineGroup.add(LineSprite)
                            print("The line from ", LineSprite.connections[0], " to ", LineSprite.connections[1], " has been added.")
#                            except:
#                                print("Please select a starting node.")

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    for sprite in all_sprites_list:
                        sprite.drag = False

            elif event.type == pygame.MOUSEMOTION:
                for sprite in NodeGroup: # Iterates over every sprite, checking for mouse interaction
                    if sprite.drag:
                        mouse_x, mouse_y = event.pos
                        sprite.rect.x = mouse_x + offset_x
                        sprite.rect.y = mouse_y + offset_y
                    
                    if  sprite.atMenu == True and not (menu.rect.contains(sprite.rect)): # If node leaves the menu, create another
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



