import pygame, sys, os
from pygame.locals import *
from os import path
from Settings import * 

class State():
    def __init__(self):
        self.done =  False
        self.currentState = None
        self.nextState = None

    def new(self):
        pass
    def update(self, dt):
        pass
    def draw(self, surface):
        pass
    def getEvent(self,event):
        pass
    
    def loadDirectories(self):
        self.currentDir = path.dirname(__file__)
        self.parentDir = path.abspath(path.join(self.currentDir, os.pardir))
        self.resourceDir = path.join(self.parentDir, "resource")
        self.imagesDir = path.join(self.resourceDir, 'images')
    
def drawText(text, surface, size, color, x, y):
    font = pygame.font.Font(FONT_NAME, size)
    # render: calcualtes exactly what pattern of pixels is needed
    textObj = font.render(text, True, color)       #render(text, on/off anti-aliasing, color)
    textRect = textObj.get_rect()
    textRect.center = (x,y)
    surface.blit(textObj, textRect)
    return textRect
    
def drawRectangle(x,y,w,h, surface, color):
    rectangle = pygame.Rect(x,y,w,h)
    rectangle.center = (x,y)  
    pygame.draw.rect(surface, color, rectangle)
    return rectangle
    
def drawTextRectangle(x,y,w,h, surface, rectColor, text, textColor, size):
    rect = drawRectangle(x,y,w,h, surface, rectColor)
    drawText(text, surface, size, textColor, x, y)
    return rect

def drawGrid(surface):
    for x in range(0, WIDTH, TILE_SIZE):
        pygame.draw.line(surface, Color(GRID_COLOR),(x,0),(x,HEIGHT))
    for y in range(0, HEIGHT, TILE_SIZE):
        pygame.draw.line(surface, Color(GRID_COLOR),(0,y),(WIDTH,y))
    
    # draw the last line 
    pygame.draw.line(surface, Color(GRID_COLOR),(0,HEIGHT),(WIDTH,HEIGHT))
    
