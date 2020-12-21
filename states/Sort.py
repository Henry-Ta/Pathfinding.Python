import pygame, sys, os
from pygame.locals import *

from states.State import *

vector = pygame.math.Vector2
class Sort(State):
    def __init__(self):
        super().__init__()
        self.currentState = "SORT"
        self.loadProperties()
        
    def loadProperties(self):
        self.hoverMenu  = False
        self.hoverPathfinding  = False
        
    def update(self, dt):
        pass
    
    def draw(self, surface):
        surface.fill(Color("lightgrey"))
        
        #---------------------------------------------------------Buttons-----------------------------------------------------#
        self.menuButton = drawTextRectangle(WIDTH/2,HEIGHT/4,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Main Menu", Color(TEXT_COLOR), TEXT_SIZE)
        self.pathfindingButton = drawTextRectangle(WIDTH/2,HEIGHT-200,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Path Finding", Color(TEXT_COLOR), TEXT_SIZE)
        
        mousePosition = vector(pygame.mouse.get_pos())
        if self.menuButton.collidepoint(mousePosition):
            self.hoverMenu =  True
            self.menuButton = drawTextRectangle(WIDTH/2,HEIGHT/4,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Main Menu", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverMenu  = False
            
        if self.pathfindingButton.collidepoint(mousePosition):
            self.hoverPathfinding =  True
            self.pathfindingButton = drawTextRectangle(WIDTH/2,HEIGHT-200,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Path Finding", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverPathfinding  = False
         #----------------------------------------------------------------------------------------------------------------------#
            
            
    def getEvent(self,event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.nextState = "PATHFINDING"
                self.done = True
            if event.key == pygame.K_m:
                self.nextState = "MENU"
                self.done = True
                
        if event.type == pygame.MOUSEBUTTONDOWN:      
            if event.button == 1 and self.hoverPathfinding :
                self.nextState = "PATHFINDING"
                self.done = True
            elif event.button == 1 and self.hoverMenu:
                self.nextState = "MENU"
                self.done = True