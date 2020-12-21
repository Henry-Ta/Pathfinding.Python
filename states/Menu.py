import pygame, sys, os
from pygame.locals import *
from Settings import *
from states.State import *

vector = pygame.math.Vector2
class Menu(State):
    def __init__(self):
        super().__init__()
        self.currentState = "MENU"
        self.loadProperties()
        
    def loadProperties(self):
        self.hoverPathfinding  = False
        self.hoverAbout  = False
        
    def update(self, dt):
        pass
            
    def draw(self, surface):
        surface.fill(Color(BACKGROUND_COLOR))
        pygame.draw.rect(surface, Color("white"),((0,HEIGHT),(WIDTH,TILE_SIZE+20)))
        drawGrid(surface)
        
        self.drawButtons(surface)
        self.drawLetters(surface)
        
        #-----------------------------------------------------------------------------------#
        
    def getEvent(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:      
            if event.button == 1 and self.hoverPathfinding :
                self.nextState = "PATHFINDING"
                self.done = True
            elif event.button == 1 and self.hoverAbout:
                self.nextState = "ABOUT"
                self.done = True
    
    def drawButtons(self,surface):
        self.pathfindingButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "Start", Color(TEXT_COLOR), TEXT_SIZE)
        self.aboutButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_WIDTH,BUTTON_HEIGHT, surface, Color(BUTTON_COLOR), "About", Color(TEXT_COLOR), TEXT_SIZE)
        
        mousePosition = vector(pygame.mouse.get_pos())
        if self.pathfindingButton.collidepoint(mousePosition):
            self.hoverPathfinding =  True
            self.pathfindingButton = drawTextRectangle(WIDTH/2 - BUTTON_WIDTH - 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "Start", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverPathfinding  = False
            
        if self.aboutButton.collidepoint(mousePosition):
            self.hoverAbout =  True
            self.aboutButton = drawTextRectangle(WIDTH/2 + BUTTON_WIDTH + 15      ,HEIGHT + (TILE_SIZE+20)/2,BUTTON_HOVER_WIDTH,BUTTON_HOVER_HEIGHT, surface, Color(BUTTON_HOVER_COLOR), "About", Color(TEXT_HOVER_COLOR), TEXT_HOVER_SIZE)
        else:
            self.hoverAbout  = False
            
    def drawLetters(self,surface):
        super().loadDirectories()
        
        self.pImg = pygame.image.load(path.join(self.imagesDir, 'letter_P.png')).convert_alpha()
        self.pImg = pygame.transform.scale(self.pImg, (LETTER_SIZE, LETTER_SIZE))
        self.pCenter = (WIDTH/2-240, HEIGHT/2-100)
        surface.blit(self.pImg, self.pImg.get_rect(center=self.pCenter))
        
        self.aImg = pygame.image.load(path.join(self.imagesDir, 'letter_A.png')).convert_alpha()
        self.aImg = pygame.transform.scale(self.aImg, (LETTER_SIZE, LETTER_SIZE))
        self.aCenter = (WIDTH/2-80, HEIGHT/2-100)
        surface.blit(self.aImg, self.aImg.get_rect(center=self.aCenter))
        
        self.tImg = pygame.image.load(path.join(self.imagesDir, 'letter_T.png')).convert_alpha()
        self.tImg = pygame.transform.scale(self.tImg, (LETTER_SIZE, LETTER_SIZE))
        self.tCenter = (WIDTH/2+80, HEIGHT/2-100)
        surface.blit(self.tImg, self.tImg.get_rect(center=self.tCenter))
        
        self.hImg = pygame.image.load(path.join(self.imagesDir, 'letter_H.png')).convert_alpha()
        self.hImg = pygame.transform.scale(self.hImg, (LETTER_SIZE, LETTER_SIZE))
        self.hCenter = (WIDTH/2+240, HEIGHT/2-100)
        surface.blit(self.hImg, self.hImg.get_rect(center=self.hCenter))
        
        self.fImg = pygame.image.load(path.join(self.imagesDir, 'letter_F.png')).convert_alpha()
        self.fImg = pygame.transform.scale(self.fImg, (LETTER_SIZE, LETTER_SIZE))
        self.fCenter = (WIDTH/2-480, HEIGHT/2+100)
        surface.blit(self.fImg, self.fImg.get_rect(center=self.fCenter))
        
        self.iImg = pygame.image.load(path.join(self.imagesDir, 'letter_I.png')).convert_alpha()
        self.iImg = pygame.transform.scale(self.iImg, (LETTER_SIZE, LETTER_SIZE))
        self.iCenter = (WIDTH/2-320, HEIGHT/2+100)
        surface.blit(self.iImg, self.iImg.get_rect(center=self.iCenter))
        surface.blit(self.iImg, self.iImg.get_rect(center = (WIDTH/2+320, HEIGHT/2+100)))
        
        self.nImg = pygame.image.load(path.join(self.imagesDir, 'letter_N.png')).convert_alpha()
        self.nImg = pygame.transform.scale(self.nImg, (LETTER_SIZE, LETTER_SIZE))
        self.nCenter = (WIDTH/2-160, HEIGHT/2+100)
        surface.blit(self.nImg, self.nImg.get_rect(center=self.nCenter))
        surface.blit(self.nImg, self.nImg.get_rect(center=(WIDTH/2+160, HEIGHT/2+100)))
        
        self.gImg = pygame.image.load(path.join(self.imagesDir, 'letter_G.png')).convert_alpha()
        self.gImg = pygame.transform.scale(self.gImg, (LETTER_SIZE, LETTER_SIZE))
        self.gCenter = (WIDTH/2+480, HEIGHT/2+100)
        surface.blit(self.gImg, self.gImg.get_rect(center=self.gCenter))
        
        self.dImg = pygame.image.load(path.join(self.imagesDir, 'letter_D.png')).convert_alpha()
        self.dImg = pygame.transform.scale(self.dImg, (LETTER_SIZE, LETTER_SIZE))
        self.dCenter = (WIDTH/2, HEIGHT/2+100)
        surface.blit(self.dImg, self.dImg.get_rect(center=self.dCenter))