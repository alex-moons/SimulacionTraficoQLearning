from turtle import pos
import agentpy as ap
import numpy as np


class car(ap.Agent):
    def setup(self):
        self.speed=0

    def speedup(self):
        speed= speed + 10;

    def slowdown(self):
        if (speed<= 0):
            speed = speed -10;
    
