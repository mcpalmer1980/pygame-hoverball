from constants import *
SDL2 = False if pygame.get_sdl_version()[0] < 2 else True
ANTIALIAS = True

#menu item types
SELECT = 1
OPTION = 2
SLIDER = 3
INPUT = 4
LABEL = 5
SPACER = 6
TEXT = 7
BUTTONS = 8

REPEAT_RATE = 7

ctrans = (255,255,1)

class MenuException:
	def __init__(self, message = None):
		self.message = message
	def __str__(self):
		return self.message


class Menu():
	old_mouse_pos = None
	cursor_off = 0
	def __init__(self, opt, dest, inputer = None):
		self.dest = dest
		self.back_buffer = None
		self.title_height = 0
		self.repeat = 0
		self.alpha = None
		self.space_bottom = 0
		self.space_side = 0
		self.title = 0
		self.outline = 2
		self.back_color = None
		self.title_top = 0
		self.title_bottom = 0
		self.title_mode = 'normal'
		self.body_color = (0,0,0)
		self.parse_options(opt)
		self.inputer = inputer
		self.count = 0
		self.clock = pygame.time.Clock()
		self.frozen = False

	def get_item_size(self, i):
		if len(i) > 1:
			if i[1] == OPTION:
				if len(i) < 4:
					i.append(0)
				width = 0
				for o in i[2]:
					w,h = self.body_font.size(i[0] + o)
					if w > width: width = w
				w = width
				return (w,h)

			elif i[1] == SPACER:
				if len(i) < 3:
					i.append(int(self.line_height / 4))
				return (0,i[2])

			elif i[1] == TEXT:
				just = 0 if len(i) < 4 else i[3]
				s = self.render_text(i[0], i[2], just)
				return s

			elif i[1] == SLIDER:
				if len(i) < 5:
					i.append(0)
				if len(i) < 6:
					i.append(100)
				w,h = self.body_font.size(i[0] + '  ')
				w += i[2] + 8
				return w,h

			elif i[1] == BUTTONS:
				count = min(len(i[2]), 3)
				default = 0
				if len(i) == 4:
					default = i[3]
				if len(i) <= 4:
					i.append([])
					i.append(default)
				width = 0
				for c in range(count):
					w,h = self.button_font.size(i[2][c])
					width += w + self.button_space + self.button_radius * 2
				return width, h + self.button_radius * 2

			elif i[1] == INPUT:
				# name, INPUT=4, On Enter selection, (max length), initial text
				# check the parameters, make sure i[2] is integer and i[-1] is string
				# add default values for on enter index
				l = len(i)

					
				for n in range(5 - l):
					i.append(False)
				if type(i[2]) != int: i[2] = 0
				if type(i[3]) != int: i[3] = 99
				if type(i[4]) != str and type(i[4]) != unicode: i[4] = ''

				'''
				if l == 2:
					i.append(0)
					i.append(False)
					i.append('')
				elif l == 3:
					if type(i[2]) is str:
						i.insert(2, 0)
						i.insert(3, False)
					else:
						i.append(False)
						i.append('')
				elif l > 3:
					if type(i[2]) is not int and type(i[2]) is not float: i[2] = 0
					if type(i[-1]) is not str: i[-1] = '' '''

				#handle negative and out of range values for 'on enter' index
				if i[2] < 0: i[2] = len(self.items) + i[2] - 1
				i[2] = min( max( i[2], 0 ), len(self.items)-1 )

				self.prep_input(i[-1])
				w,h = self.body_font.size(i[-1])
				w = min( w, self.max_width)
				i.append(i[-1])
				return w, h

			else:
				return self.body_font.size(i[0])

		return self.body_font.size(i[0])

	def get_item_selections(self):
		pass

	def draw_item(self, i, x, y, selected = False):
		type = SELECT
		if len(i) > 1: type = i[1]
		c = self.body_color
		bc = self.back_color
		if selected:
			c = self.select_color
			bc = self.select_back
			if self.get_item_type(self.selected) != BUTTONS:
				round_rect(self.surface, self.selections[self.selected][1], self.button_radius, bc)

		if type == OPTION:
			opt = i[-1]

			if opt in i[2]:
				opt = i[2].index(opt)
				i[3] = opt
			s = i[0] + i[2][opt]
			line = self.body_font.render(s, ANTIALIAS, c)
			w = line.get_width()
			h = line.get_height()
			c = int((self.button_width - w) / 2)

			self.surface.blit(line, (x+c, y))
			if not selected: self.add_selector(i,x+c,y, w, h, (x,y))
			y += self.line_height
			return y

		elif type == SPACER:
			y += i[2]
			return y

		elif type == LABEL:
			s = i[0].split('&&')
			if len(s) > 1:
				line = self.body_font.render(s[0], ANTIALIAS, c)
				self.surface.blit(line, (x, y))
				line = self.body_font.render(s[1], ANTIALIAS, c)
				r = self.right - line.get_width()
				self.surface.blit(line, (r, y))
			else:
				line = self.body_font.render(i[0], ANTIALIAS, c)
				c = int((self.button_width - line.get_width()) / 2)
				self.surface.blit(line, (x+c, y))
			return y + self.line_height

		elif type == TEXT:
			dif = (self.button_width - self.text_box.get_width() ) / 2
			dif = int(max(dif, 0))
			self.surface.blit(self.text_box, (x+dif,y))
			y += self.text_box.get_height()
			return y

		elif type == SLIDER:
			line = self.body_font.render(i[0], ANTIALIAS, self.body_color)
			lw = line.get_width()
			lh = line.get_height()
			space = self.right - self.left - i[2]
			cent = (space - lw) / 2

			self.surface.blit(line, (x + cent, y))

			h = lh + self.body_font.get_descent()
			r = pygame.rect.Rect(self.right - i[2], y, i[2], h)
			ri = r.inflate(self.select_inflate, self.select_inflate)
			#pygame.draw.rect(self.surface, self.body_color, ri, 0)
			#pygame.draw.rect(self.surface, bc,r, 0)
			
			round_rect(self.surface, ri, self.button_radius, self.body_color)
			round_rect(self.surface, r, self.button_radius, bc)
			
			
			if not selected: self.add_selector(i, r.x, r.y, r.width, r.height, (x,y))
			r.width = i[2] * (i[3] / 100.0 )
			#pygame.draw.rect(self.surface, c, r, 0)
			if r.width > 2:
				round_rect(self.surface, r, self.button_radius, c)

			#text label
			s = str(int(i[3]))
			s = str(round((i[5] * (i[3] / 100.0))))
			colors = (self.back_color, self.body_color) if selected else (self.body_color, self.back_color)
			c = colors[0] if self.text_font.size(s)[0] > r.width-4 else colors[1]
			num = self.text_font.render(s, ANTIALIAS, c)
			x = r.right+4 if num.get_width() > r.width-4 else r.left+4
			self.surface.blit(num, (x, r.top))
			return y + self.line_height

		elif type == BUTTONS:
			i[-2] = []
			which = i[-1]
			inflate = self.select_inflate
			colors = [(self.body_color, self.back_color), (self.select_color, self.select_back)]

			c = 1 if which == 0 and selected else 0
			line = self.button_font.render(i[2][0], ANTIALIAS, colors[c][0])
			w = line.get_width() + self.button_space*2; h = line.get_height()
			r = pygame.rect.Rect((self.right - w, y, w, h)).inflate(inflate,inflate)
			right_for_center = r.left
			i[-2].append(r)
			if self.button_outline:
				round_rect(self.surface, r, self.button_radius, self.body_color, self.button_outline)
			if selected and which == 0:
				round_rect(self.surface, r, self.button_radius, colors[c][1])
			self.surface.blit(line, (self.right - w + self.button_space, y))

			index = 2 if len(i[2]) > 2 else 1

			if len(i[2]) > 1:
				c = 1 if which == 1 and selected else 0
				line = self.button_font.render(i[2][index], ANTIALIAS, colors[c][0])
				w = line.get_width() + self.button_space * 2
				r = pygame.rect.Rect((self.left, y, w, h)).inflate(inflate,inflate)
				left_for_center = r.right
				i[-2].insert(1, r)
				if self.button_outline:
					round_rect(self.surface, r, self.button_radius, self.body_color, self.button_outline)
				if selected and which == 1:
					round_rect(self.surface, r, self.button_radius, colors[c][1])
				self.surface.blit(line, (self.left + self.button_space, y))

			if len(i[2]) > 2:
				c = 1 if which == 2 and selected else 0
				line = self.button_font.render(i[2][1], ANTIALIAS, colors[c][0])
				w = line.get_width() + self.button_space * 2
				cent = int((self.button_width - w) / 2)
				r = pygame.rect.Rect((self.left + cent, y, w, h)).inflate(inflate,inflate)
				r.centerx = left_for_center + (right_for_center - left_for_center) / 2
				i[-2].append(r)
				if self.button_outline:
					round_rect(self.surface, r, self.button_radius, self.body_color, self.button_outline)
				if selected and which == 2:
					round_rect(self.surface, r, self.button_radius, colors[c][1])
				self.surface.blit(line, (r.centerx - (line.get_width() / 2), y))




			if selected:
				pass
			else:
				self.add_selector(i, self.left,y, self.right, h, (x,y))
			return y + h

		elif type == INPUT:
			if selected:
				r = self.selections[self.selected][1]
				r.x = self.left; r.width = self.button_width
				pygame.draw.rect(self.surface, self.select_back, r)
				height = self.input_surface.get_height()
				x_off = max(self.cursor_off - self.button_width, 0)
				r = (x_off, 0, self.button_width, height)
				self.surface.blit(self.input_surface, (x, y), r)

			else:
				# set default text if input is unchanged or blank
				text = i[0] if i[-1] == i[-2] or i[-1] == '' else i[-1]
				text = i[0] if i[-1] == '' else i[-1]

				line = self.body_font.render(text, ANTIALIAS, c)
				w = line.get_width(); h = line.get_height()
				if w > self.button_width:
					cent = 0
				else:
					cent = int((self.button_width - w) / 2)
				self.surface.blit(line, (x+cent, y))
				self.add_selector(i, x+cent, y, w, h, (x,y))
				height = line.get_height()
			return y + height

			
		else:
			line = self.body_font.render(i[0], ANTIALIAS, c)
			w = line.get_width(); h = line.get_height()
			cent = int((self.button_width - w) / 2)

			self.surface.blit(line, (x+cent, y))
			if not selected: self.add_selector(i, x+cent,y, w, h, (x,y))

			y += self.line_height
			return y

	def get_item_type(self, i):
		type = None
		if len(self.selections):
			type = SELECT
			i = self.selections[i][0]
			if len(i) > 1:
				type = i[1]
		return type


	def add_selector(self, i, x, y, w, h, pos):
		#r = pygame.rect.Rect(10,10,100,100)
		r = pygame.rect.Rect(x, y, w,h).inflate(self.select_inflate, self.select_inflate)
		self.selections.append((i, r, (pos)))

	#self.menu.Create(items, self.handle_info, file_name, True, 6000 )
	def Create(self, items, call_back, title = None, cancel = False, timeout = False, check_height = False, keep_select=False):
		self.count += 1
		self.alive = 1
		self.frozen = False
		self.call_back = call_back
		self.items = items
		self.input_string = ''
		self.has_released = False
		self.old_mouse_pos = None
		self.options = {}
		self.selections = []
		self.can_cancel = cancel
		self.timeout = timeout
		self.time = 0
		self.clock.tick()

		height = self.border_thick * 2
		self.line_height = self.body_font.get_height() + self.space_between
		width = 0

		self.title = title
		self.title_height = 0
		if title:
			#self.title_bottom = max(self.title_bottom, self.space_bottom)
			self.title_height = self.title_font.get_height() + self.title_top + self.title_bottom
			width = self.title_font.size(title)[0]


		height += self.title_height + self.space_top
		self.top = height
		for i in items:
			w,h = self.get_item_size(i)
			if w > width: width = w
			height += h + self.space_between
		height = height - self.space_between + self.space_bottom
		if check_height: return height

		width = max(width, self.min_width)
		self.button_width = width
		width += self.border_thick * 2
		width += self.space_left + self.space_right

		width += self.radius * 2
		height += self.radius


		#self.surface = pygame.Surface((width, height)).convert_alpha() pygame2
		self.surface = pygame.Surface((width, height)).convert()
		self.surface.set_colorkey(ctrans)
		self.surface.set_alpha(self.alpha)
		self.left = self.border_thick + self.space_left + self.radius
		self.right = width - self.border_thick - self.space_right - self.radius
		#self.top  = self.border_thick + self.title_height
		if not keep_select:
			self.selected = 0
		self.Render()

	def Render(self):
		x = self.left
		y = self.top
		bw = self.button_width
		self.selections = []

		#fill to create border or render rounded rect
		self.surface.lock()
		if self.border_thick > 0:
			if self.radius:
				self.surface.fill(ctrans)
				c = self.border_color
				r = pygame.rect.Rect(0,0, self.surface.get_width(), self.surface.get_height())
				round_rect(self.surface, r, self.radius, c)
			else:
				self.surface.fill(self.border_color)

		#draw fill color or transparent
		if self.back_color == None:
			c = ((0,0,0,0))
		else:
			c = self.back_color
		sw = self.surface.get_width()
		sh = self.surface.get_height()
		w = sw - self.border_thick * 2
		h = sh - self.border_thick * 2

		r = pygame.rect.Rect(self.border_thick, self.border_thick, w, h)
		if self.title:
			round_rect(self.surface, r, self.radius, self.title_back)
			r.y += self.title_height
			r.height -= self.title_height
			round_rect(self.surface, r, self.radius, c)
			r.height = self.radius
			round_rect(self.surface, r, 0, c)
		else:
			round_rect(self.surface, r, self.radius, c)
		self.surface.unlock()

		# draw title
		self.render_title()
		for i in self.items:
			y = self.draw_item(i,x,y)
		self.selected = min(max(self.selected, 0), len(self.selections) - 1)
		if len(self.selections) > 0:
			s = self.selections[self.selected]
			self.draw_item(s[0], s[2][0], s[2][1], 1)

		self.item_count = len(self.items)
		self.pos = ( ( self.dest.get_width() - sw ) // 2,
									( self.dest.get_height() - sh ) // 2 )
		self.rect = pygame.rect.Rect(self.pos[0], self.pos[1], sw, sh)

	def which_button(self, sel):
		values = ((0,), (0,1), (0,2,1))[len(sel[2])-1]
		return sel[2][values[sel[-1]]]


	def render_title(self):
		if self.title == None: return
		if self.title_mode in ('normal', 'inverse'):
			x = self.left
			y = self.border_thick + self.title_top
			
			w = self.surface.get_width() - (self.border_thick * 2)
			r = pygame.rect.Rect(self.border_thick, self.border_thick, w, self.title_height*4)
			if self.title_back:
				#round_rect(self.surface, r, self.radius, (100,0,0))#self.title_back)
				#pygame.draw.rect(self.surface, (200,0,0), r, 0) #self.title_back, r, 0)
				pass
		#	r = pygame.rect.Rect(0, 0, self.border_thick, 20)
			#pygame.draw.rect(self.surface, self.title_back, r, 0)
			#round_rect(self.surface, r, self.radius, (100,0,0))
			
			#self.title_font.set_bold(1)
			line = self.title_font.render(self.title, ANTIALIAS, self.title_color)
			self.title_font.set_bold(0)
			x += (self.button_width - line.get_width() ) / 2
			self.surface.blit(line, (x,y) )
		elif self.title_mode == 'inverse':
			pass

	def Draw(self):
		if not self.alive: return
		self.dest.blit(self.surface, self.pos)

	def Freeze(self):
		self.frozen = True

	def Handle(self, dir, button, events, time):
		# menu not active
		if not self.alive:
			return
		elif self.frozen:
			self.Render()
			return
		# cancel pressed
		elif button < 0 and self.has_released:
			self.call_back('CANCEL', 'CANCEL', self)
			return
		# wait for last input to release and avoid errors if selections is empty
		if len(self.selections) == 0 or not self.has_released:
			self.time += self.clock.tick()
			if self.timeout and self.time > self.timeout: button = 99; self.has_released = True
			if dir.x or dir.y or button or pygame.mouse.get_pressed()[0]:
				#any key will exit empty menu info menus
				if len(self.selections) == 0 and self.has_released:
					self.call_back('CANCEL', 'CANCEL', self)
					self.alive = False
					return
			else:
				self.has_released = True
			return

		old_select = self.selected
		option = 0
		change_option = 0
		did_input = False
		dirty = 0
		sound = True if self.sound else False
		i = self.selections[self.selected][0]
		mouse_pressed = False


		if self.get_item_type(self.selected) == INPUT:
			button = 0
			s = self.input_string
			sel = self.selections[self.selected]
			done = self.update_input(events, sel[0][3])
			self.draw_item(sel[0], sel[2][0], sel[2][1], 1)
			did_input = sel[0]
			sound = 0
			if done:
				sound = 1

				if True: #self.input_string != sel[0][-1] or self.input_string == '':
					sel[0][-1] = self.input_string
					#sel[0][0] = self.input_string
					self.call_back(sel[0][0], sel[0][-1], self)
				# render and return so the 'enter' key doesn't process again until after REPEAT_RATE
				self.selected = sel[0][2]
				self.repeat = REPEAT_RATE
				self.Render()
				return

		if self.repeat > 0:
			self.repeat -= 1

		else:

			if dir.y < 0:
				dirty = 1
				self.selected -= 1
				if self.selected < 0:
					self.selected = len(self.selections)-1

				#if self.get_item_type(self.selected) == LABEL: self.Handle(dir, button)
			elif dir.y > 0:
				dirty = 1
				self.selected += 1
				if self.selected > len(self.selections)-1:
					self.selected = 0
				#if self.get_item_type(self.selected) == LABEL: self.Handle(dir, button)
			elif dir.x < 0:
				typ = self.get_item_type(self.selected)
				if typ == OPTION or typ == BUTTONS:
					change_option = -1
					dirty = 1
				elif typ == SLIDER:
					dirty = 1
					am = 1 if i[4] else 5
					i[3] = max(i[3] - am, 0)
					option = i[3]
					self.call_back(i[0], option, self)
			elif dir.x > 0:
				typ = self.get_item_type(self.selected)
				if typ == OPTION or typ == BUTTONS:
					dirty = 1
					change_option = 1
				elif typ == SLIDER:
					dirty = 1
					am = 1 if i[4] else 5
					i[3] = min(i[3] + am, 100)
					option = i[3]
					self.call_back(i[0], option, self)

			elif button > 0 and self.selected >= 0:
				dirty = 1
				ty = self.get_item_type(self.selected)
				if ty == OPTION:
					change_option = 1
				elif ty == BUTTONS:
					sel = self.selections[self.selected][0]
					self.AwaitRelease()
					self.call_back(i[0], self.which_button(sel), self)
				elif ty == INPUT:
					pass
				else:
					self.call_back(self.selections[self.selected][0][0], option, self)

			old_sel = self.selected
			mouse_in = 0


			# HANDLE MOUSE
			x, y = pygame.mouse.get_pos()
			mouse_pressed = pygame.mouse.get_pressed()[0] or mouse_pressed
			if not self.rect.collidepoint((x, y)) and mouse_pressed:
				self.call_back('CANCEL', 'CANCEL', self)
			elif (x,y) != self.old_mouse_pos or mouse_pressed:
				self.old_mouse_pos = (x,y)
				x -= self.pos[0]; y -= self.pos[1]
				for r in self.selections:
					if r[1].collidepoint((x,y)):
						mouse_in = 1
						self.selected = self.selections.index(r)
						if self.get_item_type(self.selected) == BUTTONS:
							mouse_in = 0
							buts = self.selections[self.selected][0]
							before = buts[-1]
							for test in buts[-2]:
								if test.collidepoint(x,y):
									mouse_in = 1
									num = buts[-2].index(test)
									self.selections[self.selected][0][-1] = num
									if buts[-1] != before: dirty = 1

				if pygame.mouse.get_pressed()[0]:
					typ = self.get_item_type(self.selected)
					if typ == OPTION:
						if mouse_in:
							change_option = 1
							self.repeat = REPEAT_RATE
					elif typ == SLIDER:
						o = self.selections[self.selected][0]
						w = o[2]
						if x > self.right - w and x < self.right:
							amount = w - (self.right - x)
							percent = round(amount / float(w) * 100, 1)
							if not o[4]:
								if percent < 5: percent = 0
								if percent > 95: percent = 100
							self.call_back(o[0], percent, self)
							o[3] = percent
							dirty = 1
							#sound = 0
					elif typ == BUTTONS:
						if mouse_in:
							dirty = True
							self.repeat = REPEAT_RATE
							sel = self.selections[self.selected][0]
							self.call_back(sel[0], self.which_button(sel), self)
					elif mouse_in:
						self.repeat = REPEAT_RATE
						self.call_back(self.selections[self.selected][0][0], option, self)
					else:
						dirty = 0
			if self.selected != old_sel:
				dirty = 1

			if change_option:
				sel = self.selections[self.selected][0]
				opts = sel[2]
				l = len(opts)
				cur = sel[-1]
				cur += change_option

				if cur < 0: cur = l-1
				if cur > l-1: cur = 0
				sel[-1] = cur

				if self.get_item_type(self.selected) == OPTION:
					self.call_back(sel[0], opts[cur], self)
				dirty = 1

		if dirty:
			if sound: PlaySound(self.sound)
			if did_input and self.get_item_type(self.selected) != INPUT:
				self.keyrepeat_counters = {}
				if self.input_string != did_input[-1]:
					did_input[-1] = self.input_string
					self.call_back(did_input[0], did_input[-1], self)
					if self.call_back == self.handle_modal:
						self.alive = True

			self.Render()
			self.repeat = REPEAT_RATE


	def get_option(self, search):
		for o in self.options:
			if o[0] == search:
				return o
		return False
		
	def parse_options(self, options):
		font = False; title = False
		border = False
		self.options = options

		#'font', pygame.font, color
		opt = self.get_option('font')
		if opt == False:
			print('Menu: no font provided, using default')
			self.body_font = pygame.font.Font(None,20)
			self.body_color = (0,0,0)
		else:
			self.body_font = opt[1]
			self.body_color = opt[2]
		self.line_height = self.body_font.get_height()

		#'background', color, image
		opt = self.get_option('background')
		self.back_color = (0,0,0,0)
		if opt == False:
			self.back_color = (0,0,0,0)
		else:
			self.back_color = opt[1]
			if len(opt) > 2: self.back_image = opt[2]

		#'border', thickness, color
		self.border_thick = 0
		self.border_color = self.body_color
		opt = self.get_option('border')
		if opt:
			self.border_thick = opt[1]
			if len(opt) > 2: self.border_color = opt[2]

		#'spacer', horiz space, bottom space
		opt = self.get_option('spacer')
		self.space_bottom = 6
		self.space_between = 2
		self.space_left = 4
		self.space_right = 4
		self.space_top = 4
		if opt:
			where = [ (1,1,1,1,1), (1,1,2,2,2), (1,1,2,2,3), (1,1,2,3,4), (1,2,3,4,5) ]
			opts = max( min( len(opt) - 2, 4 ), 0 )
			self.space_left = opt[where[opts][0]]
			self.space_right = opt[where[opts][1]]
			self.space_top = opt[where[opts][2]]
			self.space_bottom = opt[where[opts][3]]
			self.space_between = opt[where[opts][4]]

		#'title', mode, [font, color, background color, top space, bottom space]
		self.title_font = self.body_font
		self.title_color = self.body_color
		self.title_back = self.back_color
		self.title_mode = 'normal'
		opt = self.get_option('title')
		if opt:
			self.title_mode = opt[1]

			if self.title_mode == 'inverse':
				self.title_color = self.back_color
				self.title_back = self.body_color
			else:
				self.title_color = self.body_color
				self.title_back = self.back_color

			if len(opt) > 2: self.title_font = opt[2]
			if len(opt) > 3: self.title_color = opt[3]
			if len(opt) > 4: self.title_back = opt[4]
			if len(opt) > 5: self.title_top = opt[5]
			self.title_bottom = self.title_top
			if len(opt) > 6: self.title_bottom = opt[6]

		#'alpha', alpha
		opt = self.get_option('alpha')
		if opt:
			self.alpha = opt[1]
			self.SetAlpha()

		#'width', min_width, [max_width]
		opt = self.get_option('width')
		self.min_width = 0
		self.max_width = self.dest.get_width() - (self.border_thick * 2) + self.space_left + self.space_right
		if opt:
			self.min_width = opt[1]
			if len(opt) > 2:
				self.max_width = min(opt[2], self.max_width)

		#'selector', mode, inflate, text_color, back_color, outline, image, image_offset
		self.select_inflate = self.outline * 2
		self.select_color = self.back_color
		self.select_back = self.body_color
		self.select_outline = self.outline
		self.select_image = None
		self.select_offset = None

		opt = self.get_option('selector')
		if opt:
			l = len(opt)
			self.select_mode = opt[1]
			if l > 2: self.select_color = opt[2]
			if l > 3: self.select_back = opt[3]
			if l > 4: self.select_outline = opt[4]
			if l > 5: self.select_image = opt[5]
			if l > 6: self.select_offset = opt[6]

		#'sound', pymixersound
		opt = self.get_option('sound')
		self.sound = None
		if opt:
			self.sound = opt[1]

		#'text', textfont, textcolor
		opt = self.get_option('text')
		self.text_font = self.body_font
		self.text_color = self.body_color
		if opt:
			self.text_font = opt[1]
			if len(opt) > 2: self.text_color = opt[2]

		#'buttons', button_font, button_space, button_outline
		opt = self.get_option('buttons')
		self.button_font = self.title_font
		self.button_space = self.space_bottom
		self.button_outline = None
		if opt:
			self.button_font = opt[1]
			if len(opt) > 2: self.button_space = opt[2]
			if len(opt) > 3: self.button_outline = opt[3]

		# 'radius'
		self.radius = 0
		self.button_radius = 0
		opt = self.get_option('radius')
		if opt:
			self.radius = opt[1]
			if len(opt) > 2: self.button_radius = opt[2]

	def SetAlpha(self):
		alpha = self.alpha
		if self.back_color:
			self.back_color = self.back_color[:3] + (alpha,)
		if self.title_back:
			self.title_back = self.title_back[:3] + (alpha,)
		self.border_color = self.border_color[:3] + (alpha,)
		self.body_color = self.body_color[:3] + (alpha,)

	def render_text(self, string, width, justification=0):
		final_lines = []
		max_height = self.dest.get_height()
		font = self.text_font
		requested_lines = string.splitlines()

		# Create a series of lines that will fit on the provided
		# rectangle.
	
		for requested_line in requested_lines:
			if font.size(requested_line)[0] > width:
				words = requested_line.split(' ')
				# if any of our words are too long to fit, return.
				for word in words:
					if font.size(word)[0] >= width:
						raise MenuException	("The word " + word + " is too long to fit in the rect passed.")
				# Start a new line
				accumulated_line = ""
				for word in words:
					test_line = accumulated_line + word + " "
					# Build the line while the words fit.
					if font.size(test_line)[0] < width:
						accumulated_line = test_line
					else:
						final_lines.append(accumulated_line)
						accumulated_line = word + " "
				final_lines.append(accumulated_line)
			else:
				final_lines.append(requested_line)

		# Let's try to write the text out on the surface.

		line_count = len(final_lines)
		line_height = font.size('Testy')[1]
		total_height = line_height * line_count

		surface = pygame.Surface((width, total_height)).convert_alpha()
		surface.fill(self.back_color)


		accumulated_height = 0
		for line in final_lines:
			if accumulated_height + font.size(line)[1] >= max_height:
				#raise MenuException	("Once word-wrapped, the text string was too tall to fit in the rect.")
				s = "Once word-wrapped, the text string was too tall to fit in the rect."
				return self.render_text(s, width, justification)
			if line != "":
				tempsurface = font.render(line, ANTIALIAS, self.text_color) #pygame2 added ctrans, disable antialias
				if justification == 0:
					surface.blit(tempsurface, (0, accumulated_height))
				elif justification == 1:
					surface.blit(tempsurface, ((width - tempsurface.get_width()) / 2, accumulated_height))
				elif justification == 2:
					surface.blit(tempsurface, (width - tempsurface.get_width(), accumulated_height))
				else:
					raise MenuException("Invalid justification argument: " + str(justification))
			accumulated_height += font.size(line)[1]

		self.text_box = surface
		return (width, accumulated_height)


	def prep_input(self, initial):
		"""
		Args:
			initial_input: Initial input text value. Default is empty string
			font_family: Name or path of the font that should be used. Default is pygame-font
			font_size: Size of the font in pixels
			text_color: Color of the text
			cursor_color: Color of the cursor
			repeat_keys_initial_ms: ms until the keydowns get repeated when a key is not released
			repeat_keys_interval_ms: ms between to keydown-repeats if key is not released
		"""

		# Text related vars:
		self.keyrepeat_intial_interval_ms = 400
		self.keyrepeat_interval_ms = 35
		self.input_string = initial

		# Text-surface will be created during the first update call:
		self.input_surface = self.body_font.render(initial, ANTIALIAS, self.select_color)
		self.input_surface.set_alpha(0)

		# Vars to make keydowns repeat after user pressed a key for some time:
		self.keyrepeat_counters = {} # {event.key: (counter_int, event.unicode)} (look for "***")


		# Things cursor:
		size = self.body_font.size('text')
		self.cursor_surface = pygame.Surface((int(size[1]/20+1), size[1]))
		self.cursor_surface.fill(self.select_color)
		self.cursor_position = len(self.input_string)  # Inside text
		self.cursor_visible = True # Switches every self.cursor_switch_ms ms
		self.cursor_switch_ms = 500 # /|\
		self.cursor_ms_counter = 0

		self.clock = pygame.time.Clock()

	def update_input(self, events, max_length):
		if events == False: return
		for event in events:
			if event.type == pygame.KEYDOWN:
				self.cursor_visible = True # So the user sees where he writes

				# If none exist, create counter for that key:
				if not event.key in self.keyrepeat_counters:
					self.keyrepeat_counters[event.key] = [0, event.unicode]

				if event.key == K_BACKSPACE: # FIXME: Delete at beginning of line?
					self.input_string = self.input_string[:max(self.cursor_position - 1, 0)] + \
										self.input_string[self.cursor_position:]

					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)
				elif event.key == K_DELETE:
					self.input_string = self.input_string[:self.cursor_position] + \
										self.input_string[self.cursor_position + 1:]

				elif event.key == K_RETURN or event.key == K_KP_ENTER:
					self.keyrepeat_counters = {}
					return True

				elif event.key == K_RIGHT:
					# Add one to cursor_pos, but do not exceed len(input_string)
					self.cursor_position = min(self.cursor_position + 1, len(self.input_string))

				elif event.key == K_LEFT:
					# Subtract one from cursor_pos, but do not go below zero:
					self.cursor_position = max(self.cursor_position - 1, 0)

				elif event.key == K_END:
					self.cursor_position = len(self.input_string)

				elif event.key == K_HOME:
					self.cursor_position = 0
				elif len(self.input_string) <= max_length and not SDL2:
					# If no special key is pressed, add unicode of key to input_string
					self.input_string = self.input_string[:self.cursor_position] + \
										event.unicode + \
										self.input_string[self.cursor_position:]
					self.cursor_position += len(event.unicode) # Some are empty, e.g. K_UP


				#else:
			elif SDL2 and event.type == TEXTINPUT:
				if len(self.input_string) <= max_length:
					# If no special key is pressed, add unicode of key to input_string
					self.input_string = self.input_string[:self.cursor_position] + \
										event.text + \
										self.input_string[self.cursor_position:]
					self.cursor_position += len(event.text) # Some are empty, e.g. K_UP

			elif event.type == KEYUP:
				# *** Because KEYUP doesn't include event.unicode, this dict is stored in such a weird way
				if event.key in self.keyrepeat_counters:
					del self.keyrepeat_counters[event.key]

		# Update key counters:
		for key in self.keyrepeat_counters :
			self.keyrepeat_counters[key][0] += self.clock.get_time() # Update clock
			# Generate new key events if enough time has passed:
			if self.keyrepeat_counters[key][0] >= self.keyrepeat_intial_interval_ms:
				self.keyrepeat_counters[key][0] = self.keyrepeat_intial_interval_ms - \
													self.keyrepeat_interval_ms

				event_key, event_unicode = key, self.keyrepeat_counters[key][1]
				pygame.event.post(pygame.event.Event(KEYDOWN, key=event_key, unicode=event_unicode))

		# Rerender text surface:
		self.input_surface = self.body_font.render(self.input_string, ANTIALIAS, self.select_color)


		# Update self.cursor_visible
		self.cursor_ms_counter += self.clock.get_time()
		if self.cursor_ms_counter >= self.cursor_switch_ms:
			self.cursor_ms_counter %= self.cursor_switch_ms
			self.cursor_visible = not self.cursor_visible

		if self.cursor_visible:
			cursor_x_pos = self.body_font.size(self.input_string[:self.cursor_position])[0]
			# Without this, the cursor is invisible when self.cursor_position > 0:
			if self.cursor_position > 0:
				cursor_x_pos -= self.cursor_surface.get_width()
			self.input_surface.blit(self.cursor_surface, (cursor_x_pos, 0))
			self.cursor_off = cursor_x_pos + self.body_font.size('O')[0]

		#self.clock.tick()
		return False

	def handle_modal(self, item, option, menu):

		self.modal_item = item
		self.modal_option = option
		typ = self.get_item_type(self.selected)
		if item == 'CANCEL':
			typ = None
			if self.can_cancel and self.get_item_type(self.selected) != INPUT:
				cancel = True
			else:
				cancel = False
		else:
			cancel = False

		if typ == SELECT or typ == BUTTONS or len(self.selections) == 1 or typ == OPTION or cancel:
			#print 'alive = 0 in handle_modal', item, option, typ
			self.alive = 0

	def KeyInputter(self, event):
		if event.key == K_ESCAPE:
			select = -1
		elif event.key == K_UP:
			move.y = -1
		elif event.key == K_RIGHT:
			move.x = 1
		elif event.key == K_DOWN:
			move.y = 1
		elif event.key == K_LEFT:
			move.x = -1
		elif event.key == K_RETURN:
			select = 1


	def GetInput(self):
		move = Vec2d()
		select = 0
		events = pygame.event.get()

		for event in events:
			if event.type == QUIT:
				select = -1
		pressed = pygame.key.get_pressed()
		if pressed[K_ESCAPE]:
			select = -1
		elif pressed[K_UP]:
			move.y = -1
		elif pressed[K_RIGHT]:
			move.x = 1
		elif pressed[K_DOWN]:
			move.y = 1
		elif pressed[K_LEFT]:
			move.x = -1
		elif pressed[K_RETURN]:
			select = 1
		'''if self.inputer and self.get_item_type(self.selected) != INPUT:
			if not move and not select:
				move, pressed, select = self.inputer()'''
		return move, select, events

	def AwaitRelease(self):
		while True:
			move, select, events = self.GetInput()
			mouse = pygame.mouse.get_pressed()[0]
			if move.x or move.y or select or mouse: #not move and not select:
				self.clock.tick(30)
				continue
			break

	def ModalMenu(self, opt, title, can_cancel = True, timeout = None, keep_select = True):
		self.alive = True
		screen = pygame.display.get_surface()
		w = screen.get_width(); h = screen.get_height()
		back_buffer = pygame.surface.Surface((w, h)).convert()
		back_buffer.blit(screen, (0,0))


		keep = True if title == self.title and keep_select else False
		self.Create(opt, self.handle_modal, title, can_cancel, keep_select=keep)

		self.Draw()
		pygame.display.flip()
		#sel = len(self.selections)
		time = 0
		self.AwaitRelease()
		self.clock.tick()
		while self.alive:
			if timeout and time > timeout:
				self.modal_item = 0
				self.modal_option = 'TIMEOUT'
				self.alive = 0

			move, select, events = self.GetInput()
			
			if opt[-1][0] == 'navigation' and opt[-1][2] == ('Next', 'Previous') and move.x:
				self.AwaitRelease()
				self.dest.blit(back_buffer, (0,0))
				if move.x > 0:
					return ('navigation', 'Previous', {})
				elif move.x < 0:
					return ('navigation', 'Next', {})

			if pygame.mouse.get_pressed()[0]: select = False

			self.Handle(move, select, events, time)
			time += self.clock.tick(30)
			if self.alive:
				if move.x or move.y or select or events:
					#print('sure')
					self.dest.blit(back_buffer, (0,0))
					self.Draw()
					pygame.display.flip()
			else:
				break
		options = self.ModalMenuOptions()
		self.AwaitRelease()
		self.dest.blit(back_buffer, (0,0))
		self.alive = False

		return (self.modal_item, self.modal_option, options)


	def ModalMenuOptions(self):
		options = {}
		for o in self.items:
			if len(o) < 2:
				pass
			elif o[1] == OPTION:
				key = o[0] if o[0] != '' else self.items.index(o)
				options[key] = o[2][o[-1]]
			elif o[1] == SLIDER:
				key = o[0] if o[0] != '' else self.items.index(o)
				options[key] = o[3]
			elif o[1] == INPUT:
				key = o[0] if o[0] != '' else self.items.index(o)
				options[key] = o[-1]
		return options


	def get_max_height(self, title, line = ['test']):
		height = 0
		count = 0
		lines = []
		lines.append(['test', BUTTONS, ('one','two')])
		max_height = self.dest.get_height()
		while height < max_height:
			height = self.Create(lines, None, title, check_height = True)
			count += 1
			lines.append(line)
		return count-1

	def Select(self, items, title = 'Select Item', can_cancel = False):
		per_page = self.get_max_height('title') - 1
		count = len(items)-1
		pages = count // per_page + 1
		page = 0
		while True:
			page_start = page * per_page
			page_items = items[page_start: page_start + per_page]
			page_menu = []
			for item in page_items:
				if item == '' or item == '--':
					page_menu.append(['', SPACER, self.line_height / 3])
				else:
					page_menu.append([item])
			if pages > 1: page_menu.append(['navigation', BUTTONS, ('>>', '<<')])
			results = self.ModalMenu(page_menu, title, can_cancel)

			if results[0] == 'navigation':
				page = page - 1 if results[1] == '<<' else page + 1
				if page >= pages: page = 0
				if page < 0: page = pages - 1
				
			else:
				item_number = page * per_page + self.selected
				if results[0] == 'CANCEL': item_number = -1
				return (results[0], item_number)

	def Dialog(self, text, title = 'Dialog', buttons = ('Okay',), can_cancel = True, timeout = None, width = None, just = 0):
		self.selected = -1
		if not width:
			text_width = 0
			for l in text.split('\n'):
				w = self.text_font.size(l)[0]
				text_width = max(w, text_width)
			max_width = int(self.dest.get_width() * 0.85)
			if text_width < max_width:
				width = text_width * 1.1
			elif text_width < max_width * 3:
				width = int(max_width * 0.66)
			else:
				width = max_width
		while True:
			page_menu = []
			page_menu.append([text, TEXT, width, just])
			page_menu.append(['', SPACER, self.line_height / 2])
			if buttons:
				page_menu.append(['navigation', BUTTONS, buttons])

			results = self.ModalMenu(page_menu, title, can_cancel, timeout)
			return results[1]

	def GetText(self, message, default = '', max = 30, size = 600):
			width = self.min_width
			self.min_width = size
			menu = [ ['in', INPUT, 1,max, default], ['', SPACER], ['OK', BUTTONS, ('Okay', 'Cancel')] ]
			results = self.ModalMenu(menu, message,)
			self.min_width = width
			if results[1] == 'Okay':
				return results[2]['in']
			return None

	def GetNumber(self, message, default = '', size = 600, dec = False, cancel = False):
		while True:
			text = self.GetText( message, default, size = size)
			if cancel and not text:
				return None
			elif dec:
				try:
					n = float(text)
					return n
				except:
					pass
			else:
				try:
					n = int(text)
					return n
				except:
					pass