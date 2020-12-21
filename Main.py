import pygame,sys, os
from states.StateManager import *

def Main():
    sm = StateManager()
    sm.run()
    
if __name__ == '__main__':
    Main()