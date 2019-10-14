import os, sys, pickle
source_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.normpath(os.path.join(source_dir, '..',))
pics = os.path.join(os.path.join(root_dir, 'pics'), '')
sound_dir = os.path.join(os.path.join(root_dir, 'sounds'), '')
root_dir = os.path.join(root_dir, '')

test = open('run_game.py')
test.close()

import pygame
from pygame.locals import *
from pygame.color import *

import pymunk
from pymunk import Vec2d

RESX = 600
RESY = 600
RES = (RESX, RESY)
VRES = Vec2d(RES)
HALF_SCREEN = Vec2d(RESX//2, RESY//2)

ALL_MASKS = pymunk.ShapeFilter.ALL_MASKS

import random as rand
from utility import *
import menu as menu_lib
from hoverball import *
