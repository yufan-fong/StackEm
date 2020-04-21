import pygame
import numpy as np

class SM:    
    '''Custom state machine parent class that does not require input'''
    def __init__(self):
        self.state = None
        
    def start(self):
        self.state = self.start_state
        
    def step(self):
        state = self.state
        ns, output = self.get_next_values(state)
        self.state = ns
        return output    
    
class oscillateSM(SM):
    '''To vary the speed of the tower as the game progresses'''
    start_state = ['RIGHT',0]
    coeff = 1
    
    def get_next_values(self, state):
        x_norm = np.pi/2/10
        unit = x_norm*state[1]
        if state[0] == 'RIGHT':
            if state[1] <= 10:
                output = self.coeff*np.cos(unit)
                ns = ['RIGHT', state[1]+1]
            else:
                output = 0
                ns = ['LEFT', state[1]-1]
                
        if state [0] == 'LEFT':
            if state[1] >= -10:
                output = -self.coeff*np.cos(unit)
                ns = ['LEFT', state[1]-1]
            else:
                output = 0
                ns = ['RIGHT', state[1]+1]
        return ns, output

class colourSM(SM):
    '''To vary the colour of the building block'''
    start_state = (255,0,0)
    
    def get_next_values(self,state):
        if state == (255,0,0):
            output = (0,255,0)
        elif state == (0,255,0):
            output = (0,0,255)
        elif state == (0,0,255):
            output = (255,0,0)
        ns = output
        return ns, output
            
class buildingBlock:
    def __init__(self, x,y,width,height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        colourMachine.step()
        self.colour = colourMachine.state
    
    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x,self.y,self.width,self.height))

def redrawGameWindow():
    win.fill((0,0,0))
    pygame.draw.line(win,(200,200,200),(0,80),(screenWidth,80), 3)    
    nextBlock.draw(win)
    for block in tower:
        block.draw(win)
    pygame.display.update()
    
    
# Main Code
pygame.init()
(screenWidth,screenHeight) = (500,650)
win = pygame.display.set_mode((screenWidth,screenHeight))
pygame.display.set_caption("Stack 'Em!")

# start state machines
colourMachine = colourSM()
colourMachine.start()
moveTower = oscillateSM()
moveTower.start()
moveNextBlock = oscillateSM()
moveNextBlock.start()

x_start, y_start = (230,20)
r_width, r_height = (40, 60)
run,drop, next_level, lose = (True, False, False, False)
loopCount = 1

tower = []
startBlock = buildingBlock(230,screenHeight-r_height,r_width,r_height)
tower.append(startBlock)
nextBlock = buildingBlock(x_start,y_start,r_width,r_height)

# main loop
while run:
    pygame.time.delay(20)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    # towerList
    if len(tower) == 6:
        tower.pop(0)
        for block in tower:
            block.y += r_height
    
    # drop the buildingblock onto the landingLine
    topBlock = len(tower)-1
    landingLine = tower[topBlock].y
    if nextBlock.y < landingLine-r_height and drop == True:
        nextBlock.y += 10
        if nextBlock.y == landingLine-r_height:
            drop = False
            next_level = True
    
    # create new buildingblock upon landing
    topBlock_x = tower[topBlock].x
    if nextBlock.y == landingLine - r_height and next_level == True:
        
        # failed landing
        if nextBlock.x < topBlock_x-40 or nextBlock.x > topBlock_x+40:
            lose = True
            
        # accurate landing
        if nextBlock.x < topBlock_x-5 and nextBlock.x < topBlock_x+5:
            moveTower.coeff -= 1
            moveNextBlock.coeff -= 1
            
        # bad landing
        if nextBlock.x < topBlock_x-5 or nextBlock.x > topBlock_x+5:
            moveTower.coeff += 1
            moveNextBlock.coeff += 1
            
        tower.append(nextBlock)
        nextBlock = buildingBlock(x_start,y_start,r_width,r_height)
        next_level = False

    # change position of buildingblock within the boundary
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and lose == False:
        drop = True
    
    # move nextBlock before it drops
    if drop == False:
        nextBlock.x += moveNextBlock.step()
    
    # moveTower every 2 loops
    if loopCount == 2:
        output = moveTower.step()
        for block in tower:
            block.x += output
        loopCount = 1
    else:
        loopCount += 1
            
    redrawGameWindow()
                    
pygame.quit()