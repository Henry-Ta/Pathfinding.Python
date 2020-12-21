import pygame, sys, os
from pygame.locals import *

from states.State import *

vector = pygame.math.Vector2
class About(State):
    def __init__(self):
        super().__init__()
        self.currentState = "ABOUT"
        self.loadProperties()
        
    def loadProperties(self):
        self.hoverMenu  = False
        self.hoverPathfinding  = False
        
    def update(self, dt):
        pass
    
    def draw(self, surface):
        surface.fill(Color(BACKGROUND_COLOR))
        pygame.draw.rect(surface, Color("white"),((0,HEIGHT),(WIDTH,TILE_SIZE+20)))
        drawGrid(surface)
        
        self.drawButtons(surface)
        self.showContentScreen(surface)
        #----------------------------------------------------------------------------------------------------------------------#
            
            
    def getEvent(self,event): 
        if event.type == pygame.MOUSEBUTTONDOWN:      
            if event.button == 1 and self.hoverPathfinding :
                self.nextState = "PATHFINDING"
                self.done = True
            elif event.button == 1 and self.hoverMenu:
                self.nextState = "MENU"
                self.done = True
                
    def drawButtons(self, surface):
         #---------------------------------------------------------Buttons-----------------------------------------------------#
        self.menuButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Main Menu", Color(TEXT_COLOR), TEXT_SIZE)
        self.pathfindingButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Path Finding", Color(TEXT_COLOR), TEXT_SIZE)
        
        mousePosition = vector(pygame.mouse.get_pos())
        if self.menuButton.collidepoint(mousePosition):
            self.hoverMenu =  True
            self.menuButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Main Menu", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverMenu  = False
            
        if self.pathfindingButton.collidepoint(mousePosition):
            self.hoverPathfinding =  True
            self.pathfindingButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Path Finding", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverPathfinding  = False
            
    def showContentScreen(self, surface):
        drawRectangle(WIDTH/2,HEIGHT/2,460,490, surface, Color("black"))
        drawRectangle(WIDTH/2,HEIGHT/2,450,480, surface, Color("white"))
        drawText("About", surface, 40, Color("red"), WIDTH/2, HEIGHT/2 - 200)
        drawText("*---------Author---------*" , surface, 30, Color("#178134"), WIDTH/2, HEIGHT/2 - 150)
        drawText("Name: Henry Ta" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 105)
        drawText("Email: hieu.td291294@zoho.com" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 - 65)
        drawText("Github: Henry-Ta" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2-25)
        drawText("*------------Project------------*" , surface, 30, Color("#178134"), WIDTH/2, HEIGHT/2 + 20)
        drawText("This project briefly shows some " , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 65)
        drawText("examples of path finding in games," , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 105)
        drawText("or in real life. Non-commercial use" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 145)
        drawText("From: Mar-07-2020 to Mar-28-2020" , surface, 25, Color("Black"), WIDTH/2, HEIGHT/2 + 185)