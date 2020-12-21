import pygame, sys, os

from Settings import *

from states.Menu import *
from states.PathFinding import *
from states.About import * 

class StateManager:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + TILE_SIZE+20))
        self.clock = pygame.time.Clock()
        
        #---------------------------------------------------------------------------------------#
        self.stateDict = {"MENU" : Menu(),
                          "PATHFINDING" : PathFinding(),
                          "ABOUT" : About()
                          }
        
        self.loadState("MENU")
        
    def loadState(self, stateName):
        self.state = self.stateDict[stateName]
        
    def flipState(self):
        self.state.done = False
        self.stateName = self.state.nextState
        self.loadState(self.stateName)

    def run(self):
        while(self.running):
            self.deltaTime = self.clock.tick(FPS) / 1000
            self.eventHandler()
            self.update(self.deltaTime)
            self.draw(self.screen)
            pygame.display.flip()
        self.end()
        
    def end(self):
        pygame.quit()
        sys.exit()
    
    def update(self, dt):
        if self.state.done == True:
            self.flipState()
            
        self.state.update(dt)
        
    def draw(self, surface):
        pygame.display.set_caption("{} - FPS: {:.2f}".format(TITLE, self.clock.get_fps() ))
        self.state.draw(surface)
        
    def eventHandler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
            self.state.getEvent(event)