from constants import *
import hb_globals as g
from arena import *


#background, walls, player, bar+tail, next_ball, next_ball, next_ball, other balls
'''
color_options = (
		(0,0,0), (255,255,255), (

'''
class HoverBall():
	BALL_SPEED = 600
	TAIL_LENGTH = 100

	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.clock = game.clock
		self.menu = game.menu
		self.menu.sound = 'boing'
		pygame.display.set_caption("HoverBall .1b")
		self.playing = True
		self.running = True

		PlaySound.Load('bloop')
		PlaySound.Load('boing')
		PlaySound.Load('crash.ogg')
		PlaySound.SetVolume(10)
		self.font = pygame.font.Font(None, 32)
		asc = self.font.get_ascent()
		thick = RESY // 75
		self.bonus_box = Rect(thick, thick + asc // 4, RESX//2.5, asc/2)

		### Physics stuff
		self.space = pymunk.Space()
		self.space.gravity = 0.0, 0.0

		ch = self.space.add_collision_handler(g.COLLIDE_PLAYER, g.COLLIDE_BALL)
		ch.pre_solve=self.pre_ball_collide
		ch.post_solve=self.post_ball_collide
		self.space.add_collision_handler(g.COLLIDE_PLAYER, g.COLLIDE_BORDER).pre_solve=self.border_collide_warp
		self.space.add_collision_handler(g.COLLIDE_BALL, g.COLLIDE_BORDER).pre_solve=self.border_collide_warp
		self.space.add_collision_handler(g.COLLIDE_PLAYER, g.COLLIDE_WALL).post_solve=self.wall_player_collide

		self.frames = 0
		self.score = 0
		self.velocity = Vec2d()
		self.thrust = Vec2d()
		self.thrust_from = Vec2d()
		self.game_count = 0
		self.arena = Arena(self)
		self.options = {}

		#self.options = {'arena': 'Acrossin', 'size': 'Big'}
		self.options = OptionStore.Get()
		self.SetOptions()
		self.NewGame()
		self.SetColors(self.options.get('color', 0))
		self.MainLoop()
		OptionStore.Save()

	def _del__():
		OptionStore.Save()

	def ArenaMenu(self):
		border_options = ('Any', 'Bounce', 'Wrap')

		while True:
			arena_option = 'Arena: {}'.format(self.options.get('arena', 'Any'))
			border_option = border_options.index(self.options.get('border', 'Any'))
			sizes = ('Normal', 'Big', 'Huge')
			size = sizes.index(self.options.get('size', 'Normal'))
			menu = [
				[arena_option],
				['Border: ', menu_lib.OPTION, border_options, border_option],
				['Ghost: ', menu_lib.OPTION, ('Off', 'On'), self.options.get('ghostwalls', False)],
				['Pain: ', menu_lib.OPTION, ('Off', 'On'), self.options.get('wallpain', False)],
				['Size: ', menu_lib.OPTION, sizes, size],
				['', menu_lib.SPACER],
				['Jitter: ', menu_lib.SLIDER, 200, self.options.get('jitter', 0)],
				['Spin: ', menu_lib.SLIDER, 200, self.options.get('spin', 50)],
				['', menu_lib.SPACER],
				['Done'] ]

			results = self.menu.ModalMenu(menu, 'Arena')
			self.options['border'] = results[2]['Border: ']
			self.options['ghostwalls'] = True if results[2]['Ghost: '] == 'On' else False
			self.options['wallpain'] = True if results[2]['Pain: '] == 'On' else False
			self.options['size'] = results[2]['Size: ']
			self.options['spin'] = results[2]['Spin: ']
			self.options['jitter'] = results[2]['Jitter: ']
			if self.options['spin'] > 45 and self.options['spin'] < 55: self.options['spin'] = 50

			if results[0].startswith('Arena:'):
				arena_option = 'Arena: {}'.format(self.options.get('arena', 'Any'))
				l = ['Any'] + list(sorted(self.arena.arenas.keys()))
				result = self.menu.Select(l, 'Arena')[0]
				self.options['arena'] = None if result == 'Random' else result

			elif results[0] in ('Done', 'CANCEL'):
				return

	def GameMenu(self):
		while True:
			games = ('Break', 'Collect', 'Escape')
			game = self.options.get('game', 'Collect')
			menu = [
					['Game: ', menu_lib.OPTION, games, games.index(self.options.get('game', 'Collect'))]]
			if game == 'Collect':
				menu += [
						['Bonus Boom: ', menu_lib.OPTION, ('Off', 'On'), self.options.get('bonusboom', False)],
						['Fueling: ', menu_lib.OPTION, ('Off', 'On'), self.options.get('fueling', False) ] ]

			menu += [
					['Color'],
					['File'],
					['', menu_lib.SPACER],
					['Done'] ]
			choice, n, options = self.menu.ModalMenu(menu, 'Game')

			self.options['game'] = options.get('Game: ', 'Collect')
			if 'Bonus Boom: ' in options:
				self.options['bonusboom'] = True if options.get('Bonus Boom: ', False) == 'On' else False
			if 'Fueling: ' in options:
				self.options['fueling'] = True if options.get('Fueling: ', False) == 'On' else False


			if choice=='Color':
				c = self.options.get('color', 0)
				c = c + 1 if c < len(g.COLOR_OPTIONS) -1 else 0
				self.SetColors(c)
				self.Draw()
			elif choice == 'File':
				self.FileMenu()
			elif choice in ('Done', 'CANCEL'):
				break

	def FileMenu(self):
		PlaySound('bloop')
		while True:
			menu = [
				['Load'],
				['Save'],
				['Remove'],
				['Reset'],
				['', menu_lib.SPACER],
				['Done'] ]

			choice, n, results = self.menu.ModalMenu(menu, 'File')

			if choice == 'Load':
				names = list(sorted(OptionStore.saved_options.keys()))
				if len(names) > 0:
					self.options = OptionStore.Get(self.menu.Select(names, "Select File")[0])
					self.SetColors()
					self.NewGame()
			elif choice == 'Save':
				name = self.menu.GetText('File Name')
				OptionStore.Add(name)
			elif choice == 'Remove':
				names = list(sorted(OptionStore.saved_options.keys()))
				if len(names) > 0:
					name = self.menu.Select(names, "Select File")[0]
					del OptionStore.saved_options[name]
			elif choice == 'Reset':
				self.options = OptionStore.Reset()
				self.SetColors(0)
				self.NewGame()
			if choice == 'Done':
				PlaySound('bloop')
				return



	def GoodBallMenu(self):
		while True:
			menu = [
				['Bonus: ', menu_lib.SLIDER, 200, self.options.get('bonusttime', 35)],
				['Immunity: ', menu_lib.SLIDER, 200, self.options.get('immunetime', 20)],
				['Life: ', menu_lib.SLIDER, 200, self.options.get('life', 35)],
				['Mend: ', menu_lib.SLIDER, 200, self.options.get('lifebonus', 35)],
				['Threshold: ', menu_lib.SLIDER, 200, self.options.get('maxdamage', 35)],
				['Thrust: ', menu_lib.SLIDER, 200, self.options.get('thrust', 50)],
				['', menu_lib.SPACER],
				['Done'] ]

			results = self.menu.ModalMenu(menu, 'Good Ball')
			self.options['thrust'] = results[2]['Thrust: ']
			self.options['life'] = results[2]['Life: ']
			self.options['lifebonus'] = results[2]['Mend: ']
			self.options['maxdamage'] = results[2]['Threshold: ']
			self.options['bonustime'] = results[2]['Bonus: ']
			self.options['immunetime'] = results[2]['Immunity: ']

			if False:
				pass
			elif results[0] in ('Done', 'CANCEL'):
				break

	def BadBallMenu(self):
		while True:
			count_opt = 100 * (self.options.get('balls', g.BALL_COUNT) / float(g.MAX_BALL_COUNT))
			ghost_opt = self.options.get('ghostballs', False)
			menu = [
				['Ghost: ', menu_lib.OPTION, ('Off', 'On'), ghost_opt],
				['', menu_lib.SPACER],
				['Count: ', menu_lib.SLIDER, 200, count_opt, False, g.MAX_BALL_COUNT],
				['Gain: ', menu_lib.SLIDER, 200, self.options.get('ballgain', 30)],
				['Speed: ', menu_lib.SLIDER, 200, self.options.get('ballspeed', 30)],
				['', menu_lib.SPACER],
				['Done'] ]

			results = self.menu.ModalMenu(menu, 'Bad Balls')
			c = round(g.MAX_BALL_COUNT * (results[2]['Count: '] / 100))
			self.options['balls']  = int(min(max(1, c), 100))
			self.options['ghostballs'] = True if results[2]['Ghost: '] == 'On' else False
			self.options['ballspeed'] = results[2]['Speed: ']
			self.options['ballgain'] = results[2]['Gain: ']
			if False:
				pass
			elif results[0] in ('Done', 'CANCEL'):
				break



	def Draw(self):
		### Draw stuff
		self.screen.fill(g.BACK_COLOR)

		if self.scale > 1:
			transx = self.playball.body.position.x - HALF_SCREEN.x
			transy = self.playball.body.position.y - HALF_SCREEN.y
			transx = min(max(0, transx), (RESX*self.scale) - RESX)
			transy = min(max(0, transy), (RESY*self.scale) - RESY)
		else:
			transx = 0
			transy = 0

		self.arena.Draw(transx, transy)

		r = self.playball.radius
		r2 = r - ((r*.8) / g.LIFE_START) * self.life
		v = self.playball.body.position
		rot = self.playball.body.rotation_vector
		p = int(v.x-transx), int(flipy(v.y-transy))
		p2 = p[0] - self.thrust.x*self.TAIL_MOD, p[1] -self.thrust.y * -self.TAIL_MOD
		if self.immune < 1 or self.immune % 30 > 6:
			pygame.draw.circle(self.screen, g.PLAY_COLOR, p, int(r))
			if self.life < g.LIFE_START:
				pygame.draw.circle(self.screen, g.TAIL_COLOR, p, int(r2))
		if self.thrust_from:
			pygame.draw.line(self.screen, g.TAIL_COLOR, p, p2, 3)

		if self.scale > 1:
			delta = vflipy(self.balls[0].body.position - self.playball.body.position)
			if delta.length > RESY // 3:
				delta.length /= self.scale*2
				pygame.draw.circle(self.screen, (0,0,255), p+delta, int(r), 3)

		for i, ball in enumerate(self.balls):
			r = ball.radius
			v = ball.body.position
			rot = ball.body.rotation_vector
			p = int(v.x-transx), int(flipy(v.y-transy))
			#p2 = Vec2d(rot.x, -rot.y) * r * 0.9
			pygame.draw.circle(self.screen, g.BALL_COLORS.get(i, g.LAST_BALL_COLOR), p, int(r))

		text = self.font.render(str(int(self.score)), 1, g.WALL_COLOR)
		self.screen.blit(text, (RESX-text.get_width() - 8, 8))
		if self.bonus > 0:
			wi = (RESX//2.5) * (self.bonus / (self.BONUS_TIME * 60))
			self.bonus_box.width = wi
			pygame.draw.rect(self.screen, g.BAR_COLOR, self.bonus_box)

	def GetInput(self):
		## Handle events
		for event in pygame.event.get():
			if event.type == QUIT:
				self.Terminate()

			if self.playing:
				if event.type == KEYDOWN:
					if event.key == K_SPACE or event.key == K_ESCAPE:
						self.ShowMenu()
					elif event.key in (K_m, K_a):
						self.NewGame()
				if event.type == MOUSEBUTTONDOWN:
					if event.button == 1:
						self.thrust_from = Vec2d(tflipy(pygame.mouse.get_pos()))
					elif event.button == 3:
						self.ShowMenu()
				elif event.type == MOUSEBUTTONUP and event.button == 1:
					self.thrust_from = Vec2d()
					self.thrust = self.thrust_from
					pygame.mouse.set_pos(RESX//2, RESY//2)

			else:
				p = pygame.mouse.get_pos()
				if event.type == KEYDOWN:
					if event.key == K_ESCAPE:
						self.Terminate()
					else:
						pygame.event.set_grab(True)
						self.playing = True
				elif event.type == MOUSEBUTTONDOWN:
					if event.button == 3:
						self.NewGame()
					pygame.event.set_grab(True)
					self.playing = True

	def MainLoop(self):
		while self.running:
			self.GetInput()
			if self.playing:
				self.Update()
				self.Draw()
			self.clock.tick(30) # 50
			pygame.display.flip()

	def NewGame(self):
		# PRINT STATUS OF LAST GAME
		if self.game_count > 0 :
			time_played = (pygame.time.get_ticks() - self.game_start) / 1000
			minutes = int(time_played / 60)
			seconds = int(time_played - (minutes * 60))
			print('game #{}({}): {} points in {}:{:02d}'.format(
					self.game_count, self.arena.current, self.score, minutes, seconds))

		# INCREMENT AND RESET VARIABLES
		self.SetOptions()
		self.frames = 0
		self.game_start = pygame.time.get_ticks()
		self.game_count += 1
		self.bonus = self.BONUS_TIME * 60
		self.immune = self.IMMUNE_TIME

		#PREPARE AND POPULATE NEW ARENA
		self.arena.Next(self.options, self.scale)
		self.playball = self.make_ball(True)
		self.balls = []
		for b in range(self.BALL_COUNT):
			self.balls.append(self.make_ball())
		self.Draw()

	def SetColors(self, c=None):
		if c == None:
			c = self.options.get('color', 0)
		c = c if c < len(g.COLOR_OPTIONS) else 0
		self.options['color'] = c
		colors = g.COLOR_OPTIONS[c]
		for i, o in enumerate(g.COLOR_OPTION_NAMES):
			setattr(g, o, colors[i])
		g.LAST_BALL_COLOR = g.BALL_COLORS[-1]
		g.BALL_COLORS = dict(enumerate(g.BALL_COLORS))

		self.menu.body_color = g.WALL_COLOR
		self.menu.back_color = g.BACK_COLOR
		self.menu.border_color = g.WALL_COLOR
		self.menu.title_color = g.BACK_COLOR
		self.menu.title_back = g.WALL_COLOR
		#self.menu.text_font = g.WALL_COLOR
		self.menu.text_color = g.BACK_COLOR
		self.menu.select_color = g.BACK_COLOR
		self.menu.select_back = g.WALL_COLOR

	def SetOptions(self):
		self.playing = True
		pygame.event.set_grab(True)
		self.MAX_THRUST = float(RESY*2) * self.options.get('thrust', 50) / 50.0
		self.THRUST_MOD = self.MAX_THRUST / (RESY / 2.0)
		self.TAIL_MOD = self.TAIL_LENGTH / self.MAX_THRUST
		self.BALL_COUNT = min(self.options.get('balls', g.BALL_COUNT), g.MAX_BALL_COUNT)

		bfilter = 0b1111 #g.ALL_MASKS
		if self.options.get('ghostballs', False):
			bfilter = bfilter ^ g.COLLIDE_BALL
		if self.options.get('ghostwalls', False):
			bfilter = bfilter ^ g.COLLIDE_WALL
		self.ball_filter = pymunk.ShapeFilter(categories=g.COLLIDE_BALL, mask=bfilter )
		self.life = g.LIFE_START * self.options.get('life', 35) / 35.0
		self.wall_pain = self.options.get('wallpain', False)
		self.BALL_SPEED = g.BALL_SPEED * (self.options.get('ballspeed', 30) / 30.0)
		self.BALL_GAIN = g.BALL_GAIN * (self.options.get('ballgain', 30) / 30.0)
		self.LIFE_BONUS = (self.life / 10) * (self.options.get('lifebonus', 35) / 35.0)
		self.LIFE_MAX = self.life + (self.life / 3)
		self.MAX_DAMAGE = self.life * (self.options.get('maxdamage', 35) / 100.0)
		self.BONUS_TIME = g.BONUS_TIME * (self.options.get('bonustime', 35) / 35.0)
		self.IMMUNE_TIME = g.IMMUNE_TIME * (self.options.get('immunetime', 20) / 20.0)
		self.BONUS_BOOM = self.options.get('bonusboom', False)
		self.FUELING = self.options.get('fueling', False)
		self.scale = {'Normal': 1, 'Big': 2, 'Huge': 4}.get(self.options.get('size', 'Normal'), 1)

		options = ['BALL_COUNT', 'ball_filter', 'life', 'wall_pain', 'BALL_SPEED', 'BALL_GAIN', 'LIFE_BONUS', 'LIFE_MAX',
				'MAX_DAMAGE', 'BONUS_TIME', 'IMMUNE_TIME', 'BONUS_BOOM', 'FUELING']
		print('OPTIONS SET:')
		for o in sorted(options):
			print('\t{}: {}'.format(o, getattr(self, o)))

	def ShowMenu(self, new_game = True):
		PlaySound('bloop')
		game_options = ('Break', 'Collect', 'Escape')
		game_option = game_options.index(self.options.get('game', 'Collect'))
		pygame.event.set_grab(False)
		menu = [
			['Begin',],
			['Game: {}'.format(self.options.get('game', 'Collect'))],
			['',menu_lib.SPACER],
			['Arena',],
			['Bad Balls'],
			['Good Ball'],
			['',menu_lib.SPACER],
			['Shuffle'],
			['Exit',] ]
		choice, n, options = self.menu.ModalMenu(menu, 'Menu')
		PlaySound('bloop')
		#self.options['game'] = options['Game: ']

		if choice == 'Begin':
			pygame.event.set_grab(True)
			if new_game:
				self.NewGame()
			return
		elif choice.startswith('Game:'):
			self.GameMenu()
		elif choice == 'Arena':
			self.ArenaMenu()
		elif choice == 'Bad Balls':
			self.BadBallMenu()
		elif choice == 'Good Ball':
			self.GoodBallMenu()
		elif choice == 'Shuffle':
			self.Shuffle()
			self.ShowMenu(False)
			return
		elif choice == 'CANCEL':
			pygame.event.set_grab(True)
			return
		elif choice == 'Exit':
			self.Terminate()
		self.ShowMenu()

	def Shuffle(self):

		# THIS DICTIONARY REPRESENTS THE RANGES FOR A SHUFFLED GAME
		options = {
				# THESE ARE OPTIONS THAT WILL BE WEIGHTED DURING SHUFFLE PROCESS
				'game': {'Break': 5, 'Collect': 15, 'Escape': 3},
				'border' : {'Any': 1, 'Bounce': 1, 'Wrap': 1},
				'ghostwalls':{True: 1, False: 4},
				'wallpain': {True: 1, False: 2},
				'ghost': {True: 1, False: 4},
				'bonusboom': {True: 1, False: 2},
				'fueling': {True: 1, False: 3},
				'size': {'Normal': 6, 'Big': 2, 'Huge': 1},

				# THESE ARE THE RANGES AND MEAN VALUES USED FOR RANGED VARIABLES
				'bonustime': (0, 100, 35),
				'immunetime': (0, 100, 35),
				'ballspeed': (10, 100, 30),
				'ballgain': (0, 100, 30),
				'life': (10, 100, 35),
				'thrust': (10, 100, 50),
				'jitter': (-10, 100, 0, 10),
				'spin': (10, 90, 50),
				'balls': (1, 16, 6) }


		# PROCESS SHUFFLE DICTIONARY
		for o in options:
			opt = options[o]
			if type(opt) == dict:
				self.options[o] = WeightedChoice(opt)
			else:
				self.options[o] = BetweenI(*opt)
		self.options['arena'] = 'Any' if rand.randrange(4) else rand.choice(list(self.arena.arenas.keys()))

		# APPLY CONSTRAINTS
		if self.options['bonusboom']: self.options['bonustime'] = min(self.options['bonustime'], 30)
		if self.options['fueling']: self.options['bonustime'] = min(self.options['bonustime'], 15)
		if rand.randrange(100) < 60: self.options['spin'] = 50
		if rand.randrange(100) < 20: self.SetColors(self.options['color'] + 1)

		print('Shuffled Options:')
		for o in sorted(self.options):
			print('\t{}: {}'.format(o, self.options[o]))
		self.NewGame()

	def Terminate(self):
		PlaySound.Stop()
		PlaySound('crash')
		for _ in range(2):
			self.clock.tick(1)
		OptionStore.Save()
		self.game.Terminate()

	def Update(self):
		dt = 1.0/60.0
		for x in range(2):
			self.frames += 1
			self.immune -= 1
			if self.FUELING:
				self.bonus += g.REFUEL
				self.bonus -= self.thrust.length * g.FUEL_MOD
			else:
				self.bonus -= 1

			if self.bonus < 0:
				if self.BONUS_BOOM:
					PlaySound('crash')
					self.life -= self.MAX_DAMAGE
					impulse = Vec2d(self.BALL_SPEED*2, 0)
					impulse.rotate_degrees(rand.randrange(360))
					self.playball.body.apply_impulse_at_local_point(impulse, (0,0))
					self.bonus = self.BONUS_TIME * 60
				if self.FUELING:
					self.thrust = Vec2d()
					self.thrust_from = False

			if self.thrust_from:
				self.thrust = Vec2d(tflipy(pygame.mouse.get_pos()) - self.thrust_from) * self.THRUST_MOD
				if self.thrust.length > self.MAX_THRUST: self.thrust.length = self.MAX_THRUST
				self.playball.body.apply_force_at_local_point(self.thrust, (0,0))
			self.space.step(dt)

		if self.life < 0:
			PlaySound('crash')
			self.NewGame()


	def pre_ball_collide(self, arbiter, space, data):
		player, ball = arbiter.shapes
		s = 'boing'
		if ball == self.balls[0]:
			self.life = min(self.life+self.LIFE_BONUS, self.LIFE_MAX)
			bonus_points = int(g.BONUS_VALUE * (self.bonus / (self.BONUS_TIME * 60)))
			self.score += 100 + max(bonus_points, 0)
			self.bonus = min(max(self.bonus, 0) + self.BONUS_TIME * 60, self.BONUS_TIME * 120)
			PlaySound('bloop')
			space.remove(ball, ball.body)
			self.balls.pop(0)
			self.balls.append(self.make_ball())
			return False
		PlaySound('boing')
		return True

	def post_ball_collide(self, arbiter, space, data):
		if self.immune < 1:
			self.immune = self.IMMUNE_TIME
			print('playball hit ball: impulse={}, maxdamage={}'.format(arbiter.total_impulse.length, self.MAX_DAMAGE))
			self.life -= min(arbiter.total_impulse.length, self.MAX_DAMAGE)

	def border_collide_warp(self, arbiter, space, data):
		ball, wall = arbiter.shapes
		old = ball.body.position
		new = Vec2d(wall.other_border[0] or old.x, wall.other_border[1] or old.y)
		ball.body.position = new
		return False

	def wall_player_collide(self, arbiter, space, data):
		if arbiter.is_first_contact:
			PlaySound('boing')
			playball, wall = arbiter.shapes
			if self.wall_pain and self.immune < 1:
				self.immune = self.IMMUNE_TIME
				print('playball hit wall: impulse={}, maxdamage={}'.format(arbiter.total_impulse.length, self.MAX_DAMAGE))
				self.life -= min(arbiter.total_impulse.length, self.MAX_DAMAGE)

	def make_ball(self, playball=False, pos=None, vel=None):
		if not pos:
			xscale = RESX * self.scale
			yscale = RESY * self.scale
			for _ in range(30):
				x = rand.randrange(int(xscale * .15), int(xscale* .85))
				y = rand.randrange(int(yscale * .15), int(yscale* .85))
				pos = x, y
				q = self.space.point_query_nearest(pos, g.BALL_SIZE * 4, pymunk.ShapeFilter())
				if not q:
					break
			else:
				print('no clear space found for ball, using', pos)
		if not vel:
			vel = Vec2d(Vary(self.BALL_SPEED+(self.frames*self.BALL_GAIN), 40), 0)
			vel.angle_degrees = rand.randrange(360)
		body = pymunk.Body(10, 100)
		body.position = pos
		body.apply_impulse_at_local_point(vel, (0,0))
		shape = pymunk.Circle(body, g.BALL_SIZE, (0,0))
		shape.elasticity = 1
		shape.friction = 0
		if playball:
			shape.collision_type = g.COLLIDE_PLAYER
			shape.filter = pymunk.ShapeFilter(categories=g.COLLIDE_PLAYER)
		else:
			shape.collision_type = g.COLLIDE_BALL
			shape.filter = self.ball_filter
		self.space.add(body, shape)
		return shape

print('Hoverball scene loaded')