from math import fabs, sqrt, cos, sin, pi, floor, ceil
from random import uniform, randint, choice
import pygame
#from pygame import gfxdraw
pygame.init()
from vector import *

#pygame.font.init()
#myfont = pygame.font.SysFont('Arial', 12)
fpsClock = pygame.time.Clock()
fps = 60
winWidth = 32 * 16
winHeight = 32 * 9
win = pygame.display.set_mode((winWidth,winHeight))

WHITE = (255,255,255)
GREY = (100,100,100)
BLACK = (0,0,0)
BACK = GREY
BORDER = BLACK
RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

NULL = 0
PLAYER = 1
ENEMY = 2

DOT = 0

DEBUG = False

################################################################################ 
spriteWidth = 32

camPos = Vector()
camTarget = Vector()

def updateCam(target):
	camTarget.x = target.pos.x - winWidth / 2
	camTarget.y = target.pos.y - winHeight / 2
	camPos.x = camTarget.x
	camPos.y = camTarget.y

def point2world(pos):
	return pos - camPos - Vector(8,8)

with open("dungeon.txt", 'r') as file:
	string = file.readline().split()
	dungeonDims = (int(string[0]), int(string[1]))
	string = file.readline()
	string = string.replace(',', '')
	string = string.replace('[', '')
	string = string.replace(']', '')
	dungeonArr = [int(i) for i in string.split()]
	
	

class Dungeon:
	def __init__(self):
		self.array = dungeonArr
		self.dims = dungeonDims
		self.surf = None
		self.makeSurf()
	def __getitem__(self, pos):
		x, y = pos
		if not self.inBound(pos):
			raise Exception("Mat: out of boundary")
		return self.array[x * self.dims[1] + y]
	def __setitem__(self, pos, value):
		x, y = pos
		if not self.inBound(pos):
			raise Exception("Mat: out of boundary")
		self.array[x * self.dims[1] + y] = value
	def inBound(self, pos):
		x, y = pos
		if x < 0 or x >= self.dims[0] or y < 0 or y >= self.dims[1]:
			return False
		return True
	def makeSurf(self):
		self.surf = pygame.Surface((self.dims[0] * spriteWidth, self.dims[0] * spriteWidth))
		self.surf.fill(BORDER)
		for x in range(self.dims[0]):
			for y in range(self.dims[1]):
				if self[x,y] == 1:
					pygame.draw.rect(self.surf, BACK, ((x * spriteWidth, y * spriteWidth), (spriteWidth, spriteWidth)))
	def draw(self):
		win.blit(self.surf, point2world(Vector()))
	def borderAt(self, pos):
		if pos[0] < 0 or pos[0] >= self.surf.get_width() or pos[1] < 0 or pos[1] >= self.surf.get_height():
			return True
		return self.surf.get_at((int(pos[0]), int(pos[1]))) == BORDER
		
		
		
################################################################################ Classes

class Character:
	friction = 0.8
	def __init__(self):
		self.initialize()
	def initialize(self):
		self.tag = NULL
		objects.append(self)
		self.pos = Vector()
		self.vel = Vector()
		self.acc = Vector()
		self.color = (0,255,0)
	def applyForce(self):
		pass
	def step(self):
		# force
		self.applyForce()
		# dynamics
		self.vel += self.acc
		self.vel *= Character.friction
		self.acc *= 0
		# collision
		ppos = self.pos + self.vel
		ppos = self.mapCollision(ppos)
		self.pos = ppos
		
		self.secondaryStep()
	def secondaryStep(self):
		pass
	def mapCollision(self, ppos):
		if self.vel.x <= 0:
			if dungeon.borderAt((ppos.x, self.pos.y)) or dungeon.borderAt((ppos.x, self.pos.y + 16 * 0.9)):
				ppos.x = 16 * int(ppos.x / 16) + 16
				self.vel.x = 0
		else:
			if dungeon.borderAt((ppos.x + 16, self.pos.y)) or dungeon.borderAt((ppos.x + 16, self.pos.y + 16 * 0.9)):
				ppos.x = 16 * int(ppos.x / 16)
				self.vel.x = 0
		if self.vel.y <= 0:
			if dungeon.borderAt((ppos.x, ppos.y)) or dungeon.borderAt((ppos.x + 16 * 0.9, ppos.y)):
				ppos.y = 16 * int(ppos.y / 16) + 16
				self.vel.y = 0
		else:
			if dungeon.borderAt((ppos.x, ppos.y + 16)) or dungeon.borderAt((ppos.x + 16 * 0.9, ppos.y + 16)):
				ppos.y = 16 * int(ppos.y / 16) 
				self.vel.y = 0
		return ppos
	def draw(self):
		pygame.draw.rect(win, self.color, (point2world(self.pos), (16,16)))
		

class Player(Character):
	force = 0.5
	size = 16
	def __init__(self):
		self.tag = PLAYER
		self.pos = Vector(0, 16*10)
		self.vel = Vector()
		self.acc = Vector()
		self.direction = Vector()
		self.lastKey = None
		self.move = False
		self.color = (255,255,0)
		self.stunned = None
	def applyForce(self):
		if self.stunned:
			self.acc = (self.pos + Vector(8,8) - self.stunned).normalize() * 10
			self.stunned = None
		self.direction *= 0
		self.move = False
		if keys[pygame.K_w] or keys[pygame.K_UP]:
			self.acc.y = -Player.force
			self.direction[1] = -1
			self.move = True
		if keys[pygame.K_a] or keys[pygame.K_LEFT]:
			self.acc.x = -Player.force
			self.direction[0] = -1
			self.move = True
		if keys[pygame.K_s] or keys[pygame.K_DOWN]:
			self.acc.y = Player.force
			self.direction[1] = 1
			self.move = True
		if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
			self.acc.x = Player.force
			self.direction[0] = 1
			self.move = True
		if not self.move:
			if self.lastKey == 0:
				self.direction.x = 1
			elif self.lastKey == 1:
				self.direction.y = -1
			elif self.lastKey == 2:
				self.direction.x = -1
			elif self.lastKey == 3:
				self.direction.y = 1
	def secondaryStep(self):
		for e in objects:
			if e.tag != ENEMY:
				continue
			if dist(e.pos + Vector(8,8), self.pos + Vector(8,8)) > 16:
				continue
			self.stunned = e.pos + Vector(8,8)
			break
	def attack(self):
		SwordAttack()
		
	def draw(self):
		pygame.draw.rect(win, self.color, (point2world(self.pos), (16,16)))
		pygame.draw.circle(win, (150,150,0), point2world(self.pos + Vector(8,8) + 8 * self.direction), 2)
		
class SwordAttack:
	def __init__(self):
		self.tag = NULL
		objects.append(self)
		self.done = False
		self.direction = vectorCopy(player.direction)
	def step(self):
		if self.done:
			objects.remove(self)
			return
		# sword stuff
		for obj in objects:
			if obj.tag != ENEMY:
				continue
			if dist(obj.pos + Vector(8,8), player.pos + Vector(8,8) + 16 * (1.4) * player.direction) > 24:
				continue
			obj.direction = self.direction
			obj.mode = 2
			obj.timer = 0
		self.done = True
	def draw(self):
		pygame.draw.circle(win, WHITE, point2world(player.pos + Vector(8,8) + 16 * (1.4) * player.direction), 16)
		
class Enemy(Character):
	force = 0.4
	stunned = 0
	wander = 1
	hit = 2
	chase = 3
	def __init__(self):
		self.initialize()
		self.tag = ENEMY
		self.timer = 0
		self.mode = 0
		self.direction = vectorUnitRandom()
		self.health = 3
	def applyForce(self):
		if self.mode == Enemy.stunned:
			self.acc *= 0
		elif self.mode == Enemy.wander:
			self.acc = Enemy.force * self.direction
		elif self.mode == Enemy.hit:
			self.acc = player.direction * 10
		elif self.mode == Enemy.chase:
			self.acc = Enemy.force * (player.pos - self.pos).normalize()
	def secondaryStep(self):
		if self.health <= 0:
				objects.remove(self)
		if self.mode == Enemy.stunned:
			self.timer += 1
			if self.timer == 1 * fps:
				self.mode = Enemy.wander
		if self.mode == Enemy.hit:
			self.health -= 1
			self.mode = Enemy.stunned
			self.timer = 0
		if self.mode == Enemy.wander:
			self.timer += 1
			if self.timer % fps == 0:
				self.direction = vectorUnitRandom()
			if self.timer % fps/2 == 0:
				if self.search():
					self.mode = Enemy.chase
					self.timer = 0
		if self.mode == Enemy.chase:
			self.timer += 1
			if self.timer % (fps * 3) == 0:
				if not self.search():
					self.mode = Enemy.wander
	def search(self):
		ray = (player.pos - self.pos).normalize()
		for i in range(20):
			checkPos = self.pos + ray * (i * 10)
			if DEBUG: extraAppend(DOT, checkPos, (0,0,255), 2*fps)
			if dungeon.borderAt(checkPos):
				return False
			if dist(player.pos, checkPos) < 16:
				return True
		
	def draw(self):
		pygame.draw.rect(win, self.color, (point2world(self.pos), (16,16)))
		if self.mode == 0 and self.timer < fps * 0.25:
			pygame.draw.rect(win, (255,0,0), (point2world(self.pos), (16,16)))

################################################################################ Setup
extra = []
def extraAppend(tag, pos, color, delay, params=None):
	e = [tag, pos, color, delay]
	if params: e.append(params)
	extra.append(e)
def extraDraw():
	for e in extra:
		if e[0] == DOT:
			win.set_at(point2world(e[1]).vec2tupint(), e[2])
			e[3] -= 1
			if e[3] == 0:
				extra.remove(e)

player = Player()
dungeon = Dungeon()


objects = []

for i in range(20):
	e = Enemy()
	e.pos = Vector(spriteWidth * randint(0, dungeonDims[0]), spriteWidth * randint(0, dungeonDims[1]))

################################################################################ Main Loop
run = True
while run:
	fpsClock.tick(fps)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#mouse pressed once(MOUSEBUTTONUP for release):
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			#mouse position:
			mouse_pos = pygame.mouse.get_pos()
			print("mouse pressed once")
		if event.type == pygame.KEYUP:
			# movement
			if event.key == pygame.K_UP:
				player.direction[1] = 0
				player.lastKey = 1
			if event.key == pygame.K_DOWN:
				player.direction[1] = 0
				player.lastKey = 3
			if event.key == pygame.K_RIGHT:
				player.direction[0] = 0
				player.lastKey = 0
			if event.key == pygame.K_LEFT:
				player.direction[0] = 0
				player.lastKey = 2
			# attack
			if event.key == pygame.K_SPACE:
				player.attack()
			if event.key == pygame.K_d:
				DEBUG = not DEBUG
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	#key hold:
	if keys[pygame.K_z]:
		print("pressing")
	
	updateCam(player)
	# step:
	player.step()
	for o in objects:
		o.step()
	
	# draw:
	win.fill((0,0,0))
	dungeon.draw()
	player.draw()
	for o in objects:
		o.draw()
	extraDraw()
	
	pygame.display.update()
pygame.quit()














