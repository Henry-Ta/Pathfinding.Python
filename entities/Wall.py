import pygame 
from pygame.locals import *
from Settings import *

class Wall(pygame.sprite.Sprite):
    def __init__(self, main, node, image):
        self.groups = main.allSprites, main.allWalls
        super().__init__(self.groups)
        self.main = main
        #self.image = pygame.Surface((TILE_SIZE,TILE_SIZE))
        #self.image.fill(Color(WALL_COLOR))
        self.image = image
        self.rect = self.image.get_rect()
        self.x = node.x
        self.y = node.y 
        self.rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE)       # update size of rectangle for collisions with mouse
        self.rect.x = self.x * TILE_SIZE - 3
        self.rect.y = self.y * TILE_SIZE - 5    
        
class WeightedWall(pygame.sprite.Sprite):
    def __init__(self, main, node, image):
        self.groups = main.allSprites, main.allWeightedWalls
        super().__init__(self.groups)
        self.main = main
        self.image = image
        self.rect = self.image.get_rect()
        self.x = node.x
        self.y = node.y 
        self.rect = pygame.Rect(self.rect.x, self.rect.y, TILE_SIZE, TILE_SIZE)       # update size of rectangle for collisions with mouse
        self.rect.x = self.x * TILE_SIZE - 3
        self.rect.y = self.y * TILE_SIZE - 5   