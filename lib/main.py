"""This example lets you dynamically create static walls and dynamic balls

shape_query(shape)
"""
__docformat__ = "reStructuredText"
from constants import *

class Game():
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((RESX, RESY))
		pygame.display.set_caption("HoverBall .1b")
		self.clock = pygame.time.Clock()

		#title = monton-black
		#regular = play-bold
		#small = play-regular

		font = pygame.font.Font(pics+'font.ttf', int(RESY / 16))
		sfont = pygame.font.Font(pics+'font.ttf', int(RESY / 20))
		tfont = pygame.font.Font(pics+'font.ttf', int(RESY / 12))
		menu_options = (
				('font', font, (200,200,200), (0,0,0)),
				('spacer', int(RESY *.05), 4, int(RESY * .05), 4),
				('alpha', 200),
				('background', (0,0,0) ),
				#('radius', 4, 2),
				('border', 6,),
				('width', int (RESY*.33), int(RESY*.66)),
				('title', 'inverse', tfont, (0,0,0), (200,200,200) ),
				#('sound', 'switch'),
				('buttons', tfont, 8, 2),
				('text', sfont, (200,200,200)) )

		self.menu = menu_lib.Menu(menu_options, self.screen)
		scene = HoverBall(self)
		self.Terminate()

	def Terminate(self):
		pygame.quit()
		end = self.clock.get_fps()
		print('average frames per second: {}'.format(self.clock.get_fps()))
		sys.exit()

print('main scene manager loaded')
game = Game()