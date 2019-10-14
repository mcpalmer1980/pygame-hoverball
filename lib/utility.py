
from constants import *

def flipy(y):
	return -y+RESY
def tflipy(t):
	return (t[0], -t[1]+RESY)
def vflipy(v):
	v.y = -v.y
	return v

def round_rect(surf, rect, rad, color, thick=0):
	trans = (255,255,1)

	if not rad:
		pygame.draw.rect(surf, color, rect, thick)
		return
	elif rad > rect.width / 2 or rad > rect.height / 2:
		rad = min(rect.width/2, rect.height/2)

	if thick > 0:
		r = rect.copy()
		x, r.x = r.x, 0
		y, r.y = r.y, 0
		buf = pygame.surface.Surface((rect.width, rect.height)).convert()
		buf.set_colorkey(trans)
		buf.fill(trans)
		round_rect(buf, r, rad, color, 0)
		r = r.inflate(-thick*2, -thick*2)
		round_rect(buf, r, rad, trans, 0)
		surf.blit(buf, (x,y))


	else:
		r  = rect.inflate(-rad * 2, -rad * 2)
		for corn in (r.topleft, r.topright, r.bottomleft, r.bottomright):
			pygame.draw.circle(surf, color, corn, rad)
		pygame.draw.rect(surf, color, r.inflate(rad*2, 0))
		pygame.draw.rect(surf, color, r.inflate(0, rad*2))

def Vary( n, amount = 50, INT = False):
	variance = rand.triangular( -amount, amount )
	n *= ( 1 + variance / 100.0 )
	if INT: n = int(n)
	return n
	
def Between(mi, ma, mean, integer=False):
	perc = rand.gauss(1, .35) - 1
	if perc < 0:
		v = mean - ((mean - mi) * -perc)
	else:
		v = mean + (ma - mean) * perc
	return min(max(mi, v), ma)
def BetweenI(mi, ma, mean, tolerance=0):
	perc = rand.gauss(1, .35) - 1
	if perc < 0:
		v = mean - ((mean - mi) * -perc)
	else:
		v = mean + (ma - mean) * perc
	val = min(max(mi, v), ma)
	if abs(val-mean) < tolerance: val = mean
	return int(val)

def WeightedChoice(options):
	l = []
	for o in options:
		l = l + [o] * options[o]
	return rand.choice(l)


class SoundPlayer:

	def __init__(self):
		self.volume = 0.8
		self.sounds = {}
		self.channels = {}
	def __call__(self, name, chan = None, loop = 0, cancel = False, once = False):
		if name not in self.sounds: return

		sound = self.sounds[name]

		if type(sound) == list:
			sound = sound[rand.randrange(len(sound))]
		if chan in self.channels:
			self.channels[chan].play(sound, loop)
			#self.channels[chan].set_volume(self.volume)
		else:
			c = sound.play(loop)


	def Load(self, filename, count = 1):
		if type(filename) is tuple:
			self.LoadArray(filename[0], filename[1])
		elif count > 1:
			self.LoadArray(filename, count)
		else:
			if filename.count('.') < 1:
				filename += '.wav'
			name = filename.rpartition('.')[0]
			self.sounds[name] = pygame.mixer.Sound(sound_dir+filename)
			self.sounds[name].set_volume(self.volume)

	def LoadArray(self, filename, count):
		sounds = []
		name, dot, ext = filename.rpartition('.')
		if ext == '':
			ext = 'wav'
		ext = '.' + ext

		for s in range(count):
			filename = sound_dir + name + str(s + 1) + ext
			sound = pygame.mixer.Sound(filename)
			sound.set_volume(self.volume)
			sounds.append(sound)
		self.sounds[name] = sounds

	def Stop(self, chan = -1):
		if chan in self.sounds:
			self.sounds[chan].stop()
		elif chan in self.channels:
			self.channels[chan].stop()
		else:
			pygame.mixer.stop()

	def GetVolume(self):
		return int(self.volume * 100)
	def SetVolume(self, volume):
		self.volume = volume / 100.0
		for s in self.sounds:
			if type(self.sounds[s]) == list:
				for ss in self.sounds[s]:
					ss.set_volume(self.volume)
			else:
				self.sounds[s].set_volume(self.volume)
PlaySound = SoundPlayer()
