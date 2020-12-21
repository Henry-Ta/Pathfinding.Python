import pygame, sys, os, time, math, random
import ast        # convert string to list
from pygame.locals import *
from os import path
from collections import deque       # the double-ended queue, cannot access items in the middle, but perfect for either ends ( faster than using list )

from Settings import *
from states.State import *
from entities.Grid import *
from entities.Wall import *

vector = pygame.math.Vector2
class PathFinding(State):
    def __init__(self):
        super().__init__()
        self.currentState = "PATHFINDING"
        self.loadProperties()
        self.loadData()
        self.new()
        
    def new(self):
        self.allSprites = pygame.sprite.Group()
        self.allWalls = pygame.sprite.Group()
        self.allWeightedWalls = pygame.sprite.Group()

        self.sg = SquareGrid(GRID_WIDTH,GRID_HEIGHT) 
        self.wg = WeightedGrid(GRID_WIDTH,GRID_HEIGHT) 
        
    def update(self, dt):
        if self.pressedRandomMap == True:
            self.randomMap()
        else:
            self.width = 0
            self.height= 0
            
        if self.pathLine == "Diagonal":
                self.sg.connection = [vector(1,0),vector(-1,0),vector(0,1),vector(0,-1),
                                      vector(1,1),vector(-1,1),vector(1,-1),vector(-1,-1)]
        else:
                self.sg.connection = [vector(1,0),vector(-1,0),vector(0,1),vector(0,-1)]
        self.wg.connection = self.sg.connection
        
        if self.countTime == True:
            self.startTime = pygame.time.get_ticks()
                 
        if self.search == "BFS" or self.search == "DFS":
            self.breadthDepthFirstSearch(self.sg,self.location, self.destination)
        elif self.search == "Dijkstra":
            self.dijkstraSearch(self.wg, self.location, self.destination)
        elif self.search == "A* Manhattan" or self.search == "A* Diagonal" or self.search == "A* Euclidean":
            self.aStarSearch(self.wg, self.location, self.destination)
        elif self.search == "Greedy B*":
            self.greedyBFS(self.wg, self.location, self.destination)
        
        if self.activedPathAnimation == True:
            self.drawPathAnimation()
        
        #-----------------------------------------------------------------------------------#
        self.allSprites.update()
        self.allWalls.update()
        
    def draw(self, surface):
        surface.fill(Color(BACKGROUND_COLOR))
        pygame.draw.rect(surface, Color("white"),((0,HEIGHT),(WIDTH,TILE_SIZE+20)))
        drawGrid(surface)
        #----------------------------------------------------------------------------------------------------------------------#
        self.drawButtons(surface)
        
        if self.pressedMapButton == True:
            self.showMapOption(surface)
            self.pressedMapButton = False
        
        if self.pressedInstructionButton == True:
            self.showInstruction(surface)
            self.pressedInstructionButton = False
        
        if self.pressedAlgorithmButton == True:
            self.showAlgorithmOptions(surface)
            self.pressedAlgorithmButton = False
        
        if self.pressedPathButton == True:
            self.showPathOption(surface)
            self.pressedPathButton = False
        
        
        if self.search is not None:
            drawText(self.search, surface, 25, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2 - 13)
            if self.search == "BFS" or self.search == "DFS":
                self.drawB_DFSExploredArea(surface)
                self.drawPathB_DFS(surface)  
            elif self.search == "Dijkstra":
                self.drawDijkstraExploredArea(surface)
                self.drawPathDijkstra(surface)  
            elif self.search == "A* Manhattan" or self.search == "A* Diagonal" or self.search == "A* Euclidean":
                self.drawAStarExploredArea(surface)
                self.drawPathAStar(surface)  
            elif self.search == "Greedy B*":
                self.drawGreedyBStarExploredArea(surface)
                self.drawPathGreedyBStar(surface)
        else:
            drawText("HELLO", surface, 35, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2) 
        #----------------------------------------------------------------------------------------------------------------------#
        self.drawIcons(surface)
        
        self.allSprites.draw(surface)
        
    def getEvent(self,event):
        mousePosition = vector(pygame.mouse.get_pos()) // TILE_SIZE     # Division(floor)
        #----------------------------------------------------------Input from key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.pressedMouse = True 
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT: 
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:            # not make wall on "start" and "end" icon
                        if mousePosition in self.sg.walls :
                            pygame.sprite.spritecollide(Wall(self,vector(mousePosition),self.wallImg), self.allSprites, True)
                            self.sg.walls.remove(mousePosition)
                        else:
                            Wall(self,vector(mousePosition),self.wallImg)
                            self.sg.walls.append(mousePosition)
                    self.wg.walls = self.sg.walls    
                self.loadSearch()
            elif event.key == pygame.K_q:
                self.pressedWeightedNode = True
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT: 
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:            # not make wall on "start" and "end" icon
                        if self.vec2int(mousePosition) in self.wg.weights :
                            pygame.sprite.spritecollide(WeightedWall(self,vector(mousePosition),self.weightedWallImg), self.allSprites, True)
                            self.wg.weights.pop(self.vec2int(mousePosition), None)      # return none if that element not in dictionary
                        else:
                            WeightedWall(self,vector(mousePosition),self.weightedWallImg)
                            self.wg.weights[self.vec2int(mousePosition)] = 50       # low priority == hight cost       
                        
                self.loadSearch()
            elif event.key == pygame.K_l:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT:
                    if not mousePosition in self.sg.walls :         # the new location should not be a wall
                        self.location = mousePosition
                        self.loadSearch()
            elif event.key == pygame.K_d:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT:
                    if not mousePosition in self.sg.walls :         # the new location should not be a wall
                        self.destination = mousePosition
                        self.loadSearch()
            elif event.key == pygame.K_a:
                self.activedAllPaths = not self.activedAllPaths
            elif event.key == pygame.K_m:
                self.activedPathAnimation = True
            elif event.key == pygame.K_e:
                self.activedExploredArea = not self.activedExploredArea
            elif event.key == pygame.K_p:
                # dump the wall list for saving
                print([(int(grid.x), int(grid.y)) for grid in self.sg.walls])
                
        elif event.type == pygame.KEYUP:
            self.pressedMouse = False 
            self.pressedWeightedNode = False

        #----------------------------------------------------------Input from mouse
        if event.type == pygame.MOUSEBUTTONDOWN:   
            if event.button == 1 and self.hoverMenuButton :
                self.nextState = "MENU"
                self.done = True
            elif event.button == 1 and self.hoverInstructionButton:
                self.pressedInstructionButton = True 
            elif event.button == 1 and self.hoverMapButton:
                self.pressedMapButton = True
            elif event.button == 1 and self.hoverRemoveButton:
                self.allSprites = pygame.sprite.Group()
                self.sg.walls = []                      #Need to update ( remove or sth, not neccessary because we alread had allSprites)
                self.wg.walls = []
                self.pressedRandomMap = False
                # reset search value    
                self.newSearchProperties()  
                self.search = None
            elif event.button == 1 and self.hoverAlgorithmButton:
                self.pressedAlgorithmButton = True
            elif event.button == 1 and self.hoverPathButton:
                self.pressedPathButton = True
            elif event.button == 1:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT: 
                    self.pressedMouse = True 
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:            # not make wall on "start" and "end" icon
                        if mousePosition in self.sg.walls :
                            pygame.sprite.spritecollide(Wall(self,vector(mousePosition),self.wallImg), self.allSprites, True)
                            self.sg.walls.remove(mousePosition)
                        else:
                            Wall(self,vector(mousePosition),self.wallImg)
                            self.sg.walls.append(mousePosition)
                    self.wg.walls = self.sg.walls                      
                    self.loadSearch()
            elif event.button == 3:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT:
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:
                        if not mousePosition in self.sg.walls :
                            self.destination = mousePosition
                            self.loadSearch()
            elif event.button == 2:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT:
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:
                        if not mousePosition in self.sg.walls :
                            self.location = mousePosition
                            self.loadSearch()
                            
        elif event.type == pygame.MOUSEMOTION:
            if self.pressedMouse:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT: 
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:            # not make wall on "start" and "end" icon
                        if mousePosition not in self.sg.walls :
                            Wall(self,vector(mousePosition),self.wallImg)
                            self.sg.walls.append(mousePosition)
                    self.wg.walls = self.sg.walls 
            elif self.pressedWeightedNode:
                if 0 <= int(mousePosition.x) < GRID_WIDTH and 0 <= int(mousePosition.y) < GRID_HEIGHT: 
                    if self.checkCollision(mousePosition, self.location) == False and self.checkCollision(mousePosition, self.destination) == False:            # not make wall on "start" and "end" icon
                        if self.vec2int(mousePosition) not in self.wg.weights :
                            WeightedWall(self,vector(mousePosition),self.weightedWallImg)
                            self.wg.weights[self.vec2int(mousePosition)] = 50       # low priority == hight cost
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.pressedMouse = False
            self.pressedWeightedNode = False
        
                                    
    #-------------------------------------------------Load Data-----------------------------------------------------------#
    def loadWalls(self, mapWalls):
        data = []
        for wall in mapWalls:
            data.append(vector(wall))
            Wall(self,vector(wall),self.wallImg)
        return data
    
    def loadProperties(self):    
        self.originalWalls = []
        self.savedWalls = []
        
        self.width = 0
        self.height = 0
        
        self.hoverMenuButton  = False
        self.hoverInstructionButton  = False
        self.hoverMapButton = False
        self.hoverRemoveButton = False
        self.hoverAlgorithmButton = False
        self.hoverBfsButton  = False
        self.hoverDfsButton = False
        self.hoverDijkstraButton  = False
        self.hoverAStarManhattanButton = False
        self.hoverAStarDiagonalButton = False
        self.hoverAStarEuclideanButton = False
        self.hoverGreedyBStarButton = False
        self.hoverNextButton = False
        self.hoverCloseButton = False
        self.hoverDiagonalButton = False
        self.hoverStraightButton = False
        self.hoverFileButton = False
        self.hoverRandomButton = False
        
        self.closedInstruction = False
        
        self.pressedMouse = False
        self.pressedWeightedNode = False
        self.pressedAlgorithmButton = False
        self.pressedInstructionButton = False
        self.pressedPathButton = False
        self.pressedMapButton = False
        self.pressedRandomMap = False
        
        self.activedAllPaths = False
        self.activedPathAnimation = False
        self.activedExploredArea =  True
        
        self.newSearchProperties()
        self.location = vector(20,0)            # start location
        self.destination = vector(3,13)         # end location
        
        self.B_DFSdone = False
        self.dijkstraDone = False
        self.aStarDone = False
        self.greedyBStarDone = False
        
        self.search = None             # track "search" that applying
        self.pathLine = None            # change line to Diagonal or Straight
         
        self.countTime = False
           
    def loadData(self):
        super().loadDirectories()
        #---------------------------------------Load Map
        data = ""
        # Choose file to open here, original or new walls
        f = open(path.join(self.resourceDir,"originalwalls.txt"),"rt")
        for line in f:
            data += line.strip()
        
        #ast.literal_eval(...)     string representation of list to list 
        self.originalWalls = ast.literal_eval(data) 
        
        #----------------------------------------Load Images
        self.wallImg = pygame.image.load(path.join(self.imagesDir, 'icons8-brick-wall-58.png')).convert_alpha()
        self.wallImg = pygame.transform.scale(self.wallImg, (TILE_SIZE + 6, TILE_SIZE + 8))       #(54,58)
        
        self.weightedWallImg = pygame.image.load(path.join(self.imagesDir, 'icons8-brick-wall-58_orange.png')).convert_alpha()
        self.weightedWallImg = pygame.transform.scale(self.weightedWallImg, (TILE_SIZE + 6, TILE_SIZE + 8))
        
        self.destinationImg = pygame.image.load(path.join(self.imagesDir, 'icons8-roulette-51.png')).convert_alpha()
        self.destinationImg = pygame.transform.scale(self.destinationImg, (TILE_SIZE + 3, TILE_SIZE + 3))     #(51,51)
        #self.destinationImg.fill((0, 255, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)        # paint color on image
        
        self.locationImg = pygame.image.load(path.join(self.imagesDir, 'icons8-home-address-48.png')).convert_alpha()
        self.locationImg = pygame.transform.scale(self.locationImg, (TILE_SIZE, TILE_SIZE))
        #self.locationImg.fill((255, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
        
        self.arrows = {}
        self.arrowImg = pygame.image.load(path.join(self.imagesDir, 'arrowRight.png')).convert_alpha()
        self.arrowImg = pygame.transform.scale(self.arrowImg, (TILE_SIZE + 2, TILE_SIZE + 2))       #(50,50) change size of image to (newWidth,newHeight)
        for direction in [(1, 0), (0, 1), (-1, 0), (0, -1), (1,1), (-1,1),(1,-1),(-1,-1)]:
            self.arrows[direction] = pygame.transform.rotate(self.arrowImg, vector(direction).angle_to(vector(1, 0)))  
        
        '''
        self.arrows[(1,0)] = pygame.transform.rotate(self.arrowImg, 0)       
        self.arrows[(0,1)] = pygame.transform.rotate(self.arrowImg, 270)     
        self.arrows[(-1,0)] = pygame.transform.rotate(self.arrowImg, 180)        
        self.arrows[(0,-1)] = pygame.transform.rotate(self.arrowImg, 90) 
        self.arrows[(1,1)] = pygame.transform.rotate(self.arrowImg, 315)       
        self.arrows[(-1,1)] = pygame.transform.rotate(self.arrowImg, 225)     
        self.arrows[(1,-1)] = pygame.transform.rotate(self.arrowImg, 45)        
        self.arrows[(-1,-1)] = pygame.transform.rotate(self.arrowImg, 135)    
        '''  
    
    def loadSearchProperties(self):
        self.B_DFrontier.append(self.location) 
        self.B_DVisited.append(self.location)
        self.B_DPath[self.vec2int(self.location)] = None  

        self.dijkstraFrontier.push(self.vec2int(self.location), 0)
        self.dijkstraVisited.append(self.location)
        self.dijkstraPath[self.vec2int(self.location)] = None  
        self.dijkstraCost[self.vec2int(self.location)] = 0
        
        self.aStarFrontier.push(self.vec2int(self.location), 0)
        self.aStarVisited.append(self.location)
        self.aStarPath[self.vec2int(self.location)] = None  
        self.aStarCost[self.vec2int(self.location)] = 0
        
        self.greedyBStarFrontier.push(self.vec2int(self.location), 0)
        self.greedyBStarVisited.append(self.location)
        self.greedyBStarPath[self.vec2int(self.location)] = None  
        
        self.startTime = 0
        self.endTime = 0
        self.countTime = True
        self.gotNodePath = False            # need to check in case loop of program add up more path in "nodePath"
        self.nodePath = deque()
        
    def newSearchProperties(self):
        self.B_DFrontier = deque()
        self.B_DVisited = []
        self.B_DPath = {}      # {node( int(vector) ) : direction(vector)}
        
        self.dijkstraFrontier = PriorityQueue()
        self.dijkstraVisited = []
        self.dijkstraPath = {}
        self.dijkstraCost = {}
        
        self.aStarFrontier = PriorityQueue()
        self.aStarVisited = []
        self.aStarPath = {}
        self.aStarCost = {}
        
        self.greedyBStarFrontier = PriorityQueue()
        self.greedyBStarVisited = []
        self.greedyBStarPath = {}
        
        self.nodePath = deque()          # save only node of "main path" to pop out
    
    def loadSearch(self):
        if self.search == "BFS" or self.search == "DFS":
            # reset search value    
            self.B_DFSdone = False
        elif self.search == "Dijkstra":
            # reset search value    
            self.dijkstraDone = False
        elif self.search == "A* Manhattan" or self.search == "A* Diagonal" or self.search == "A* Euclidean":
            # reset search value    
            self.aStarDone = False
        elif self.search == "Greedy B*":
            # reset search value    
            self.greedyBStarDone = False
        self.newSearchProperties() 
        self.loadSearchProperties()
    
        
    #-------------------------------------------------Support functions------------------------------------------------#
    def vec2int(self,v):
        return (int(v.x),int(v.y))    
    
    def checkCollision(self, a, b):
        if a == b:
            return True 
        return False 
    
    def heuristic(self, fromNode, toNode):
        # Manhattan Distance  : move only in four directions only (right, left, top, bottom)
        if self.search == "A* Manhattan" or self.search == "Greedy B*":
            return abs(fromNode.x - toNode.x) + abs(fromNode.y - toNode.y)          # * 10 if cost of movement is 10 or 14 ( in Grid.py )
    
        # Diagonal Distance  : move in eight directions only
        elif self.search == "A* Diagonal":
            return max(abs(fromNode.x - toNode.x),abs(fromNode.y - toNode.y)) 
    
        # Euclidean Distance:  move in any direction
        elif self.search == "A* Euclidean":
            return math.sqrt( (fromNode.x - toNode.x)**2 +  (fromNode.y - toNode.y)**2 ) 
    
    def randomMap(self):
        '''
        for y in range(0, GRID_HEIGHT, 1):
            h = random.randrange(0,4,1)
            for x in range(0, GRID_WIDTH, 1):
                w = random.randrange(0,5,1)
                if w == h and vector(x,y) != self.location and vector(x,y) != self.destination:
                    Wall(self,vector(x,y),self.wallImg)
                    self.sg.walls.append(vector(x,y))
        self.wg.walls = self.sg.walls
        '''
        if self.height < GRID_HEIGHT:
            h = random.randrange(0,4,1)
            if self.width < GRID_WIDTH:
                w = random.randrange(0,5,1)
                if w == h and vector(self.width,self.height) != self.location and vector(self.width,self.height) != self.destination:
                    Wall(self,vector(self.width,self.height),self.wallImg)
                    self.sg.walls.append(vector(self.width,self.height))
                    self.wg.walls = self.sg.walls
                self.width+=1
            else:
                self.height+=1
                self.width = 0
        else:
            self.pressedRandomMap = False

        
    #-------------------------------------------------Rendering-------------------------------------------#
    def drawGrid(self, surface):
        for x in range(0, WIDTH, TILE_SIZE):
            pygame.draw.line(surface, Color(GRID_COLOR),(x,0),(x,HEIGHT))
        for y in range(0, HEIGHT, TILE_SIZE):
            pygame.draw.line(surface, Color(GRID_COLOR),(0,y),(WIDTH,y))
        
        # draw the last line 
        pygame.draw.line(surface, Color(GRID_COLOR),(0,HEIGHT),(WIDTH,HEIGHT))
    
    def drawButtons(self,surface):
        self.menuButton         = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH*3 - 150  ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Main Menu", Color(TEXT_COLOR), TEXT_SIZE)
        self.instructionButton  = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH*2 - 83   ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Instruction", Color(TEXT_COLOR), TEXT_SIZE)
        self.mapButton          = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Load Map", Color(TEXT_COLOR), TEXT_SIZE)
        self.removeButton       = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Remove Map", Color(TEXT_COLOR), TEXT_SIZE)
        self.algorithmButton    = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH*2 + 83   ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Algorithm", Color(TEXT_COLOR), TEXT_SIZE)
        self.pathButton         = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH*3 + 150  ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Path Setting", Color(TEXT_COLOR), TEXT_SIZE)
        
        mousePosition = vector(pygame.mouse.get_pos())
        if self.menuButton.collidepoint(mousePosition):
            self.hoverMenuButton =  True
            self.menuButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH*3 - 150,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Main Menu", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverMenuButton  = False
            
        if self.instructionButton.collidepoint(mousePosition):
            self.hoverInstructionButton =  True
            self.instructionButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH*2 - 83,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Instruction", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverInstructionButton  = False
        self.closedInstruction = False          # check to close all instructions 
            
        if self.mapButton.collidepoint(mousePosition):
            self.hoverMapButton =  True
            self.mapButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Load Map", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverMapButton  = False
            
        if self.removeButton.collidepoint(mousePosition):
            self.hoverRemoveButton =  True
            self.removeButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Remove Map", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverRemoveButton  = False
            
        if self.algorithmButton.collidepoint(mousePosition):
            self.hoverAlgorithmButton =  True
            self.algorithmButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH*2 + 83,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Algorithm", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverAlgorithmButton  = False
            
        if self.pathButton.collidepoint(mousePosition):
            self.hoverPathButton =  True
            self.pathButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH*3 + 150,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Path Setting", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverPathButton  = False
    
    def drawIcons(self, surface):
        self.destinationCenter = (self.destination.x * TILE_SIZE + TILE_SIZE / 2, self.destination.y * TILE_SIZE + TILE_SIZE / 2)
        surface.blit(self.destinationImg, self.destinationImg.get_rect(center=self.destinationCenter))
        
        self.locationCenter = (self.location.x * TILE_SIZE + TILE_SIZE / 2, self.location.y * TILE_SIZE + TILE_SIZE / 2)
        surface.blit(self.locationImg, self.locationImg.get_rect(center=self.locationCenter))
    
    def drawB_DFSExploredArea(self, surface):
        if self.activedExploredArea == True:
            if self.pathLine == "Diagonal":
                #visitedColor = "#456e82"
                visitedColor = "#318889"
                frontierColor = "#00fff3"
            else:
                #visitedColor = "#456e82"
                visitedColor = "#31897f"
                frontierColor = "#00ff9e"
                
            # filled visited areas
            for loc in self.B_DVisited:
                x, y = loc
                r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE +1, TILE_SIZE -1, TILE_SIZE-1)
                pygame.draw.rect(surface, Color(visitedColor), r)
            
            # filled frontier areas
            if len(self.B_DFrontier) > 0:   
                for node in self.B_DFrontier:
                    x, y = node
                    r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE + 1, TILE_SIZE -1, TILE_SIZE -1)
                    pygame.draw.rect(surface, Color(frontierColor), r)            

    def drawPathB_DFS(self, surface):
        if self.B_DFSdone == True and self.activedPathAnimation == False:
            self.B_DPath = self.getPathB_DFS(self.sg, self.location, self.destination)
            mainPath = {}               # save the final path from location to destination

            ''' Start rendering from destination back to location, due to the sign of arrows '''
            currentNode = self.destination - self.B_DPath[self.vec2int(self.destination)]
            while currentNode != self.location:   
                # save the final path for path animation
                mainPath[self.vec2int(currentNode)] = self.B_DPath[self.vec2int(currentNode)]
                # find nextNode in path
                currentNode = currentNode - self.B_DPath[self.vec2int(currentNode)]    
                
            if self.gotNodePath == False:
                for node in mainPath:          # save node of the main path
                    self.nodePath.append(node)      # use nodePath[] instead of assigning directly mainPath{} for splitting up node, from direction in mainMap 
                self.gotNodePath = True
        
            if self.countTime == True:   
                self.endTime = pygame.time.get_ticks() - self.startTime 
                self.countTime = False      
            drawText(str(self.endTime)+"'", surface, 22, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2 + 15)

        if self.activedAllPaths == True:
            self.drawAllPaths(surface, self.B_DPath) 

        if self.gotNodePath:            
            """ Update nodePath as well as exclude updating mainPath with new location"""
            for currentNode in self.nodePath:
                currentNode = vector(currentNode)
                x = currentNode.x * TILE_SIZE + TILE_SIZE / 2
                y = currentNode.y * TILE_SIZE + TILE_SIZE / 2
                img = self.arrows[self.vec2int(self.B_DPath[self.vec2int(currentNode)])]
                r = img.get_rect(center=(x, y))
                surface.blit(img, r)
        
    def drawDijkstraExploredArea(self, surface):
        if self.activedExploredArea == True:
            if self.pathLine == "Diagonal":
                #visitedColor = "#456e82"
                visitedColor = "#318889"
                frontierColor = "#00fff3"
            else:
                #visitedColor = "#456e82"
                visitedColor = "#31897f"
                frontierColor = "#00ff9e"
                
            # filled visited areas
            for loc in self.dijkstraVisited:
                x, y = loc
                r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE +1, TILE_SIZE -1, TILE_SIZE-1)
                pygame.draw.rect(surface, Color(visitedColor), r)
            
            # filled frontier areas
            if not self.dijkstraFrontier.isEmpty():
                for n in self.dijkstraFrontier.nodes:
                    x, y = n[1]
                    r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE + 1, TILE_SIZE -1, TILE_SIZE -1)
                    pygame.draw.rect(surface, Color(frontierColor), r) 
    
    def drawPathDijkstra(self,surface):
        if self.dijkstraDone == True and self.activedPathAnimation == False:
            self.dijkstraPath = self.getPathDijkstra(self.wg,self.location, self.destination)
            mainPath = {}               # save the final path from location to destination

            ''' Start rendering from destination back to location, due to the sign of arrows '''
            currentNode = self.destination - self.dijkstraPath[self.vec2int(self.destination)]
            while currentNode != self.location:
                # save the final path for path animation
                mainPath[self.vec2int(currentNode)] = self.dijkstraPath[self.vec2int(currentNode)]
                # find nextNode in path
                currentNode = currentNode -  self.dijkstraPath[self.vec2int(currentNode)]    
                
            if self.gotNodePath == False:
                for node in mainPath:          # save node of the main path
                    self.nodePath.append(node)
                self.gotNodePath = True
        
            if self.countTime == True:   
                self.endTime = pygame.time.get_ticks() - self.startTime 
                self.countTime = False      
            drawText(str(self.endTime)+"'", surface, 22, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2 + 15)

        if self.activedAllPaths == True:
            self.drawAllPaths(surface, self.dijkstraPath) 

        if self.gotNodePath:            
            """ Update nodePath as well as exclude updating mainPath with new location"""
            for currentNode in self.nodePath:
                currentNode = vector(currentNode)
                x = currentNode.x * TILE_SIZE + TILE_SIZE / 2
                y = currentNode.y * TILE_SIZE + TILE_SIZE / 2
                img = self.arrows[self.vec2int(self.dijkstraPath[self.vec2int(currentNode)])]
                r = img.get_rect(center=(x, y))
                surface.blit(img, r)
    
    def drawAStarExploredArea(self, surface):
        if self.activedExploredArea == True:
            if self.pathLine == "Diagonal":
                #visitedColor = "#456e82"
                visitedColor = "#318889"
                frontierColor = "#00fff3"
            else:
                #visitedColor = "#456e82"
                visitedColor = "#31897f"
                frontierColor = "#00ff9e"
                
            # filled visited areas
            for loc in self.aStarVisited:
                x, y = loc
                r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE +1, TILE_SIZE -1, TILE_SIZE-1)
                pygame.draw.rect(surface, Color(visitedColor), r)
            
            # filled frontier areas
            if not self.aStarFrontier.isEmpty():
                for n in self.aStarFrontier.nodes:
                    x, y = n[1]
                    r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE + 1, TILE_SIZE -1, TILE_SIZE -1)
                    pygame.draw.rect(surface, Color(frontierColor), r) 
    
    def drawPathAStar(self,surface):
        if self.aStarDone == True and self.activedPathAnimation == False:
            self.aStarPath = self.getPathAStar(self.wg, self.location, self.destination)
            mainPath = {}               # save the final path from location to destination

            ''' Start rendering from destination back to location, due to the sign of arrows '''
            currentNode = self.destination - self.aStarPath[self.vec2int(self.destination)]
            while currentNode != self.location:    
                # save the final path for path animation
                mainPath[self.vec2int(currentNode)] = self.aStarPath[self.vec2int(currentNode)]
                # find nextNode in path
                currentNode -=  self.aStarPath[self.vec2int(currentNode)]    
    
            if self.gotNodePath == False:
                for node in mainPath:          # save node of the main path
                    self.nodePath.append(node)
                self.gotNodePath = True
                
            if self.countTime == True:   
                self.endTime = pygame.time.get_ticks() - self.startTime 
                self.countTime = False      
            drawText(str(self.endTime)+"'", surface, 22, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2 + 15)
        
        if self.activedAllPaths == True:
            self.drawAllPaths(surface, self.aStarPath) 

        if self.gotNodePath == True:            
            """ Update nodePath as well as exclude updating mainPath with new location"""
            for currentNode in self.nodePath:
                currentNode = vector(currentNode)
                x = currentNode.x * TILE_SIZE + TILE_SIZE / 2
                y = currentNode.y * TILE_SIZE + TILE_SIZE / 2
                img = self.arrows[self.vec2int(self.aStarPath[self.vec2int(currentNode)])]
                r = img.get_rect(center=(x, y))
                surface.blit(img, r)
    
    def drawGreedyBStarExploredArea(self, surface):
        if self.activedExploredArea == True:
            if self.pathLine == "Diagonal":
                #visitedColor = "#456e82"
                visitedColor = "#318889"
                frontierColor = "#00fff3"
            else:
                #visitedColor = "#456e82"
                visitedColor = "#31897f"
                frontierColor = "#00ff9e"
                
            # filled visited areas
            for loc in self.greedyBStarVisited:
                x, y = loc
                r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE +1, TILE_SIZE -1, TILE_SIZE-1)
                pygame.draw.rect(surface, Color(visitedColor), r)
            
            # filled frontier areas
            if not self.greedyBStarFrontier.isEmpty():
                for n in self.greedyBStarFrontier.nodes:
                    x, y = n[1]
                    r = pygame.Rect(x * TILE_SIZE +1, y * TILE_SIZE + 1, TILE_SIZE -1, TILE_SIZE -1)
                    pygame.draw.rect(surface, Color(frontierColor), r) 
          
    def drawPathGreedyBStar(self, surface):
        if self.greedyBStarDone == True and self.activedPathAnimation == False:
            self.greedyBStarPath = self.getPathGreedyBStar(self.wg, self.location, self.destination)
            mainPath = {}               # save the final path from location to destination

            ''' Start rendering from destination back to location, due to the sign of arrows '''
            currentNode = self.destination - self.greedyBStarPath[self.vec2int(self.destination)]
            while currentNode != self.location:    
                # save the final path for path animation
                mainPath[self.vec2int(currentNode)] = self.greedyBStarPath[self.vec2int(currentNode)]
                # find nextNode in path
                currentNode -=  self.greedyBStarPath[self.vec2int(currentNode)]    
    
            if self.gotNodePath == False:
                for node in mainPath:          # save node of the main path
                    self.nodePath.append(node)
                self.gotNodePath = True
                
            if self.countTime == True:   
                self.endTime = pygame.time.get_ticks() - self.startTime 
                self.countTime = False      
            drawText(str(self.endTime)+"'", surface, 22, Color("red"), WIDTH/2 ,HEIGHT + (TILE_SIZE+20)/2 + 15)
        
        if self.activedAllPaths == True:
            self.drawAllPaths(surface, self.greedyBStarPath) 

        if self.gotNodePath == True:            
            """ Update nodePath as well as exclude updating mainPath with new location"""
            for currentNode in self.nodePath:
                currentNode = vector(currentNode)
                x = currentNode.x * TILE_SIZE + TILE_SIZE / 2
                y = currentNode.y * TILE_SIZE + TILE_SIZE / 2
                img = self.arrows[self.vec2int(self.greedyBStarPath[self.vec2int(currentNode)])]
                r = img.get_rect(center=(x, y))
                surface.blit(img, r)
                  
    def drawAllPaths(self, surface, path):
        """ Draw all nodes in path """
        for node, direction in path.items(): 
            if direction:
                x, y = node
                x = x * TILE_SIZE + TILE_SIZE / 2
                y = y * TILE_SIZE + TILE_SIZE / 2
                img = self.arrows[self.vec2int(direction)]
                r = img.get_rect(center=(x, y))
                surface.blit(img, r) 
    
    def drawPathAnimation(self):
        if len(self.nodePath) == 0:
            self.activedPathAnimation = False
        elif len(self.nodePath) > 0 and self.activedPathAnimation:
            node = vector(self.nodePath.pop())
            #direction = self.location - node
            self.location = node

            pygame.time.delay(150)


    #-------------------------------------------------Choose Options-------------------------------------------#
    def showAlgorithmOptions(self, surface):
        while True:
            drawRectangle(WIDTH/2,HEIGHT/2,560,410, surface, Color("black"))
            drawRectangle(WIDTH/2,HEIGHT/2,550,400, surface, Color("white"))
            drawText("Algorithm", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 190 + 30)
            
            self.bfsButton              = drawTextRectangle(WIDTH/2         ,HEIGHT/2-120 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "BFS", Color(TEXT_COLOR), TEXT_SIZE)
            self.dfsButton              = drawTextRectangle(WIDTH/2 + 190   ,HEIGHT/2-120 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "DFS", Color(TEXT_COLOR), TEXT_SIZE)
            self.dijkstraButton         = drawTextRectangle(WIDTH/2         ,HEIGHT/2+40 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Dijkstra", Color(TEXT_COLOR), TEXT_SIZE)
            self.aStarManhattanButton   = drawTextRectangle(WIDTH/2         ,HEIGHT/2-40 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "A* Manhattan", Color(TEXT_COLOR), TEXT_SIZE)
            self.aStarDiagonalButton    = drawTextRectangle(WIDTH/2 + 190   ,HEIGHT/2-40 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "A* Diagonal", Color(TEXT_COLOR), TEXT_SIZE)
            self.aStarEuclideanButton   = drawTextRectangle(WIDTH/2 - 190   ,HEIGHT/2-40 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "A* Euclidean", Color(TEXT_COLOR), TEXT_SIZE)
            self.greedyBStarButton      = drawTextRectangle(WIDTH/2 - 190   ,HEIGHT/2-120 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Greedy B*", Color(TEXT_COLOR), TEXT_SIZE)
            self.closeButton             = drawTextRectangle(WIDTH/2         ,HEIGHT/2+120 + 30 ,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Close", Color(TEXT_COLOR), TEXT_SIZE)
                
            mousePosition = vector(pygame.mouse.get_pos())
            if self.bfsButton.collidepoint(mousePosition):
                self.hoverBfsButton  = True
                self.bfsButton = drawTextRectangle(WIDTH/2,HEIGHT/2-120 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "BFS", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverBfsButton  = False
            
            if self.dfsButton.collidepoint(mousePosition):
                self.hoverDfsButton  = True
                self.dfsButton = drawTextRectangle(WIDTH/2 + 190   ,HEIGHT/2-120 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "DFS", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverDfsButton  = False
                
            if self.dijkstraButton.collidepoint(mousePosition):
                self.hoverDijkstraButton  = True
                self.dijkstraButton = drawTextRectangle(WIDTH/2         ,HEIGHT/2+40 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Dijkstra", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverDijkstraButton  = False
                
            if self.aStarManhattanButton.collidepoint(mousePosition):
                self.hoverAStarManhattanButton  = True
                self.aStarManhattanButton = drawTextRectangle(WIDTH/2         ,HEIGHT/2-40 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "A* Mahattan", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverAStarManhattanButton  = False
                
            if self.aStarDiagonalButton.collidepoint(mousePosition):
                self.hoverAStarDiagonalButton  = True
                self.aStarDiagonalButton = drawTextRectangle(WIDTH/2 + 190   ,HEIGHT/2-40 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "A* Diagonal", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverAStarDiagonalButton  = False
                
            if self.aStarEuclideanButton.collidepoint(mousePosition):
                self.hoverAStarEuclideanButton  = True
                self.aStarEuclideanButton = drawTextRectangle(WIDTH/2 - 190   ,HEIGHT/2-40 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "A* Euclidean", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverAStarEuclideanButton  = False
                
            if self.greedyBStarButton.collidepoint(mousePosition):
                self.hoverGreedyBStarButton  = True
                self.greedyBStarButton = drawTextRectangle(WIDTH/2 - 190   ,HEIGHT/2-120 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Greedy B*", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverGreedyBStarButton  = False
                
            if self.closeButton.collidepoint(mousePosition):
                self.hoverCloseButton  = True
                self.closeButton = drawTextRectangle(WIDTH/2,HEIGHT/2+120 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Close", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverCloseButton  = False
               
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hoverBfsButton:
                        self.search = "BFS"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverDfsButton:
                        self.search = "DFS"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverDijkstraButton:
                        self.search = "Dijkstra"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverAStarManhattanButton:
                        self.search = "A* Manhattan"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverAStarDiagonalButton:
                        self.search = "A* Diagonal"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverAStarEuclideanButton:
                        self.search = "A* Euclidean"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverGreedyBStarButton:
                        self.search = "Greedy B*"
                        self.newSearchProperties()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverCloseButton:
                        return
            pygame.display.update()   
    
    def showInstruction(self, surface):
        while True and self.closedInstruction == False:
            drawRectangle(WIDTH/2,HEIGHT/2,460,490, surface, Color("black"))
            drawRectangle(WIDTH/2,HEIGHT/2,450,480, surface, Color("white"))
            drawText("Instruction", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 200)
            drawText("*---------Keyboard---------*" , surface, 30, Color("blue"), WIDTH/2, HEIGHT/2 - 150)
            drawText("Press W to place Wall" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 100)
            drawText("Press L to place Start Marker" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 60)
            drawText("Press D to place End Marker" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2-20)
            drawText("*------------Mouse------------*" , surface, 30, Color("blue"), WIDTH/2, HEIGHT/2 + 20)
            drawText("Left Mouse to place Wall" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 60)
            drawText("Middle Mouse to place Start Marker" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 100)
            drawText("Right Mouse to place End Marker" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 140)
            
            self.nextButton = drawTextRectangle(WIDTH/2-100,HEIGHT/2+200,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Next", Color(TEXT_COLOR), TEXT_SIZE)
            self.closeButton = drawTextRectangle(WIDTH/2+100,HEIGHT/2+200,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Close", Color(TEXT_COLOR), TEXT_SIZE)
            
            mousePosition = vector(pygame.mouse.get_pos())
            if self.nextButton.collidepoint(mousePosition):
                self.hoverNextButton  = True
                self.nextButton = drawTextRectangle(WIDTH/2-100,HEIGHT/2+200,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Next", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverNextButton  = False
                
            if self.closeButton.collidepoint(mousePosition):
                self.hoverCloseButton  = True
                self.closeButton = drawTextRectangle(WIDTH/2+100,HEIGHT/2+200,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Close", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverCloseButton  = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.closedInstruction = True
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hoverNextButton :
                        self.showInstruction2(surface)
                    elif event.button == 1 and self.hoverCloseButton:
                        self.closedInstruction = True
                        return
            #---------------------------------------------------------------------------------------#
            pygame.display.update()
    
    def showInstruction2(self, surface):
        while True and self.closedInstruction == False:
            drawRectangle(WIDTH/2,HEIGHT/2,460,490, surface, Color("black"))
            drawRectangle(WIDTH/2,HEIGHT/2,450,480, surface, Color("white"))
            drawText("Instruction", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 200)
            drawText("*---------Keyboard---------*" , surface, 30, Color("blue"), WIDTH/2, HEIGHT/2 - 150)
            drawText("Press Q to place Weighted Wall" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 100)
            drawText("Press A to show/hide full path" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 60)
            drawText("Press E to show/hide explored area" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2-20)
            drawText("Press M to animate the path" , surface, 25, Color("black"), WIDTH/2, HEIGHT/2 + 20)
            drawText("Press P to print out the wall list" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 60)
            drawText("Press Esc to exit" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 100)
            
            self.backButton = drawTextRectangle(WIDTH/2-100,HEIGHT/2+200,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Back", Color(TEXT_COLOR), TEXT_SIZE)
            self.closeButton = drawTextRectangle(WIDTH/2+100,HEIGHT/2+200,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Close", Color(TEXT_COLOR), TEXT_SIZE)
            
            mousePosition = vector(pygame.mouse.get_pos())
            if self.backButton.collidepoint(mousePosition):
                self.hoverBackButton  = True
                self.backButton = drawTextRectangle(WIDTH/2-100,HEIGHT/2+200,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Back", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverBackButton  = False
                
            if self.closeButton.collidepoint(mousePosition):
                self.hoverCloseButton  = True
                self.closeButton = drawTextRectangle(WIDTH/2+100,HEIGHT/2+200,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Close", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverCloseButton  = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.closedInstruction = True
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hoverBackButton:
                        self.showInstruction(surface)
                    elif event.button == 1 and self.hoverCloseButton:
                        self.closedInstruction = True
                        return
            #---------------------------------------------------------------------------------------#
            pygame.display.update()
    
    def showPathOption(self,surface):
        while True:
            drawRectangle(WIDTH/2,HEIGHT/2,250,350, surface, Color("black"))
            drawRectangle(WIDTH/2,HEIGHT/2,240,340, surface, Color("white"))
            drawText("Path Line", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 160 + 30)
            
            self.diagonalButton = drawTextRectangle(WIDTH/2,HEIGHT/2- 80 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Diagonal", Color(TEXT_COLOR), TEXT_SIZE)
            self.straightButton = drawTextRectangle(WIDTH/2,HEIGHT/2 +30 ,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Straight", Color(TEXT_COLOR), TEXT_SIZE)
            self.closeButton     = drawTextRectangle(WIDTH/2,HEIGHT/2+80 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Close", Color(TEXT_COLOR), TEXT_SIZE)
            
            mousePosition = vector(pygame.mouse.get_pos())
            if self.diagonalButton.collidepoint(mousePosition):
                self.hoverDiagonalButton  = True
                self.diagonalButton = drawTextRectangle(WIDTH/2,HEIGHT/2-80 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Diagonal", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverDiagonalButton  = False
                
            if self.straightButton.collidepoint(mousePosition):
                self.hoverStraightButton  = True
                self.straightButton = drawTextRectangle(WIDTH/2,HEIGHT/2 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Straight", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverStraightButton  = False
                
            if self.closeButton.collidepoint(mousePosition):
                self.hoverCloseButton  = True
                self.closeButton = drawTextRectangle(WIDTH/2,HEIGHT/2+80 + 30 ,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Close", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverCloseButton  = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hoverDiagonalButton:
                        self.pathLine = "Diagonal"
                        self.loadSearch()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverStraightButton:
                        self.pathLine = "Straight"
                        self.loadSearch()
                        self.loadSearchProperties()
                        return
                    if event.button == 1 and self.hoverCloseButton:
                        return
            #---------------------------------------------------------------------------------------#
            pygame.display.update()
              
    def showMapOption(self,surface):
         while True:
            drawRectangle(WIDTH/2,HEIGHT/2,250,350, surface, Color("black"))
            drawRectangle(WIDTH/2,HEIGHT/2,240,340, surface, Color("white"))
            drawText("Load Map", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 160 + 30)
            
            self.fileButton = drawTextRectangle(WIDTH/2,HEIGHT/2- 80 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "File", Color(TEXT_COLOR), TEXT_SIZE)
            self.randomButton = drawTextRectangle(WIDTH/2,HEIGHT/2 +30 ,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Random", Color(TEXT_COLOR), TEXT_SIZE)
            self.closeButton     = drawTextRectangle(WIDTH/2,HEIGHT/2+80 + 30,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Close", Color(TEXT_COLOR), TEXT_SIZE)
            
            mousePosition = vector(pygame.mouse.get_pos())
            if self.fileButton.collidepoint(mousePosition):
                self.hoverFileButton  = True
                self.fileButton = drawTextRectangle(WIDTH/2,HEIGHT/2-80 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "File", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverFileButton  = False
                
            if self.randomButton.collidepoint(mousePosition):
                self.hoverRandomButton  = True
                self.randomButton = drawTextRectangle(WIDTH/2,HEIGHT/2 + 30,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Random", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverRandomButton  = False
                
            if self.closeButton.collidepoint(mousePosition):
                self.hoverCloseButton  = True
                self.closeButton = drawTextRectangle(WIDTH/2,HEIGHT/2+80 + 30 ,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Close", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
            else:
                self.hoverCloseButton  = False
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1 and self.hoverFileButton:
                        self.allSprites = pygame.sprite.Group()
                        self.location = vector(20,0)            # restart location of "start" to original, in case of collision with walls
                        self.destination = vector(3,13)          # restart location of "destination" to original
                        self.sg.walls = []
                        self.wg.walls = []
                        self.pressedRandomMap = False
                        self.sg.walls = self.loadWalls(self.originalWalls)
                        self.wg.walls = self.sg.walls
                        # reset search value    
                        self.newSearchProperties()   
                        self.search = None
                        return
                    if event.button == 1 and self.hoverRandomButton:
                        self.allSprites = pygame.sprite.Group()
                        self.location = vector(20,0)            # restart location of "start" to original, in case of collision with walls
                        self.destination = vector(3,13)          # restart location of "destination" to original
                        self.sg.walls = []
                        self.wg.walls = []
                        self.pressedRandomMap = True
                        # reset search value    
                        self.newSearchProperties()   
                        self.search = None
                        return
                    if event.button == 1 and self.hoverCloseButton:
                        return
            #---------------------------------------------------------------------------------------#
            pygame.display.update()
                        
                        
                                     
    #-------------------------------------------------Search Algorithms-------------------------------------------#
    def checkB_DFS(self,frontier):
        if self.search ==  "BFS":
            node = frontier.popleft()       # Queue FIFO, first node in frontier will be checked
        elif self.search == "DFS":
            node = frontier.pop()           # stack LIFO
        return node 
    
    def breadthDepthFirstSearch(self, graph,start,end): 
        if len(self.B_DFrontier)>0 and self.B_DFSdone == False:     # as long as there are things in frontier
            currentNode = self.checkB_DFS(self.B_DFrontier)     
            if currentNode == end:
                self.B_DFSdone = True
            for nextNode in graph.findNeighbors(currentNode, graph.connection):       # find neightbor of currentNode node
                if nextNode not in self.B_DVisited:
                    self.B_DFrontier.append(nextNode)
                    self.B_DVisited.append(nextNode)
    
    def getPathB_DFS(self, graph, start, end):
        """ Rerun BFS but from destination to location to draw the path"""
        frontier = deque()
        frontier.append(start)
        path = {}
        path[self.vec2int(start)] = None
        while len(frontier) > 0:
            currentNode = self.checkB_DFS(frontier)            
            if currentNode == end:
                break
            for nextNode in graph.findNeighbors(currentNode, graph.connection):
                if self.vec2int(nextNode) not in path:
                    frontier.append(nextNode)
                    path[self.vec2int(nextNode)] = nextNode - currentNode 
        return path    
                              
    def dijkstraSearch(self, graph,start,end): 
        if not self.dijkstraFrontier.isEmpty() and not self.dijkstraDone:     # as long as there are things in frontier
            currentNode = self.dijkstraFrontier.pop()
            if currentNode == end:
                self.dijkstraDone = True
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                nextNodeCost = self.dijkstraCost[currentNode] + graph.cost(currentNode, nextNode)
                if nextNode not in self.dijkstraCost or nextNodeCost < self.dijkstraCost[nextNode]:
                    self.dijkstraCost[nextNode] = nextNodeCost
                    priority = nextNodeCost
                    self.dijkstraFrontier.push(nextNode, priority)
                    self.dijkstraVisited.append(nextNode)

    def getPathDijkstra(self, graph, start, end):
        """ Rerun BFS but from destination to location to draw the path"""
        frontier = PriorityQueue()
        frontier.push(self.vec2int(start), 0)
        path = {}
        cost = {}
        path[self.vec2int(start)] = None
        cost[self.vec2int(start)] = 0

        while not frontier.isEmpty():
            currentNode = frontier.pop()
            if currentNode == end:
                break
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                nextNodeCost = cost[currentNode] + graph.cost(currentNode, nextNode)
                if nextNode not in cost or nextNodeCost < cost[nextNode]:
                    cost[nextNode] = nextNodeCost
                    priority = nextNodeCost
                    frontier.push(nextNode, priority)
                    path[nextNode] = vector(nextNode) - vector(currentNode)
        return path    
    
    def aStarSearch(self, graph,start,end): 
        if not self.aStarFrontier.isEmpty() and not self.aStarDone:     # as long as there are things in frontier
            currentNode = self.aStarFrontier.pop()
            if currentNode == end:
                self.aStarDone = True
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                nextNodeCost = self.aStarCost[currentNode] + graph.cost(currentNode, nextNode)
                if nextNode not in self.aStarCost or nextNodeCost < self.aStarCost[nextNode]:
                    self.aStarCost[nextNode] = nextNodeCost
                    priority = nextNodeCost + self.heuristic(end, vector(nextNode))     # f(n) = g(n) + h(n)    || g cost: distance from starting node, h cost: distance from end node
                    self.aStarFrontier.push(nextNode, priority)
                    self.aStarVisited.append(nextNode)
                    
    def getPathAStar(self, graph, start, end):
        """ Rerun BFS but from destination to location to draw the path"""
        frontier = PriorityQueue()
        frontier.push(self.vec2int(start), 0)
        path = {}
        cost = {}
        path[self.vec2int(start)] = None
        cost[self.vec2int(start)] = 0

        while not frontier.isEmpty():
            currentNode = frontier.pop()
            if currentNode == end:
                break
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                nextNodeCost = cost[currentNode] + graph.cost(currentNode, nextNode)
                if nextNode not in cost or nextNodeCost < cost[nextNode]:
                    cost[nextNode] = nextNodeCost
                    priority = nextNodeCost + self.heuristic(end, vector(nextNode))
                    frontier.push(nextNode, priority)
                    path[nextNode] = vector(nextNode) - vector(currentNode)
        return path    
        
    def greedyBFS(self, graph, start, end):
        if not self.greedyBStarFrontier.isEmpty() and not self.greedyBStarDone:     # as long as there are things in frontier
            currentNode = self.greedyBStarFrontier.pop()
            if currentNode == end:
                self.greedyBStarDone = True
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                if nextNode not in self.greedyBStarVisited:
                    priority = self.heuristic(end, vector(nextNode))        #f(n) = h   -  Manhattan Distance
                    self.greedyBStarFrontier.push(nextNode, priority)         
                    self.greedyBStarVisited.append(nextNode)
                    
    def getPathGreedyBStar(self,graph, start, end):
        frontier = PriorityQueue()
        frontier.push(self.vec2int(start), 0)
        path = {}
        path[self.vec2int(start)] = None

        while not frontier.isEmpty():
            currentNode = frontier.pop()
            if currentNode == end:
                break
            for nextNode in graph.findNeighbors(vector(currentNode),graph.connection):
                nextNode = self.vec2int(nextNode)
                if nextNode not in path:
                    priority = self.heuristic(end, vector(nextNode))
                    frontier.push(nextNode, priority)
                    path[nextNode] = vector(nextNode) - vector(currentNode)
        return path  