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
winWidth = 16 * 16
winHeight = 16 * 9
scaleFactor = 3
win = pygame.Surface((winWidth,winHeight))
screen = pygame.display.set_mode((winWidth * scaleFactor,winHeight * scaleFactor))

WHITE = (255,255,255)
GREY = (100,100,100)
BLACK = (0,0,0)
BACK = GREY
BORDER_COLOR = BLACK

FLOOR = 1
BORDER = 0

RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

NULL = 0
PLAYER = 1
ENEMY = 2

DOT = 0
CIRCLE = 1

DEBUG = False

################################################################################ 

tiles = pygame.image.load("assets/dungeonTiles16.png").convert_alpha()
tiles2 = pygame.image.load("assets/dungeonTiles2.png").convert_alpha()

spriteWidth = 16
camPos = Vector()
camTarget = Vector()

overallTime = 0

def updateCam(target):
	camTarget.x = target.pos.x - winWidth / 2
	camTarget.y = target.pos.y - winHeight / 2
	camPos.x = camTarget.x
	camPos.y = camTarget.y

def point2world(pos):
	return pos - camPos - Vector(8,8)

def loadDungeon():
	with open("dungeon.txt", 'r') as file:
		string = file.readline().split()
		dungeonDims = (int(string[0]), int(string[1]))
		string = file.readline()
		string = string.replace(',', '')
		string = string.replace('[', '')
		string = string.replace(']', '')
		dungeonArr = [int(i) for i in string.split()]
	return (dungeonDims, dungeonArr)
	
def blitTile(surf, dest, pos, size=16):
	surf.blit(tiles, ((point2world(Vector(dest[0] * spriteWidth + 8, dest[1] * spriteWidth + 8))), (spriteWidth, spriteWidth)), ((pos[0] * size, pos[1] * size),(spriteWidth, spriteWidth)))
	
class Dungeon:
	def __init__(self, dims, array):
		self.dims = dims
		self.array = array
		self.surf = None
		self.layer1 = None
		self.tiles = tiles
		self.makeSurf()
		
	def __getitem__(self, pos):
		x, y = pos
		if not self.inBound(pos):
			return -1
			# raise Exception("Mat: out of boundary")
		return self.array[x * self.dims[1] + y]
	def __setitem__(self, pos, value):
		x, y = pos
		if not self.inBound(pos):
			return -1
			# raise Exception("Mat: out of boundary")
		self.array[x * self.dims[1] + y] = value
	def inBound(self, pos):
		x, y = pos
		if x < 0 or x >= self.dims[0] or y < 0 or y >= self.dims[1]:
			return False
		return True
	def makeSurf(self):
		self.surf = pygame.Surface((self.dims[0] * spriteWidth, self.dims[0] * spriteWidth))
		self.layer1 = pygame.Surface((self.dims[0] * spriteWidth, self.dims[0] * spriteWidth), pygame.SRCALPHA)
		self.surf.fill(BORDER_COLOR)
		self.layer1.fill((0,0,0,0))
		for x in range(self.dims[0]):
			for y in range(self.dims[1]):
				if self[x,y] == FLOOR:
					# pygame.draw.rect(self.surf, BACK, ((x * spriteWidth, y * spriteWidth), (spriteWidth, spriteWidth)))
					if self[x, y-1] == BORDER:
						# floor under wall
						blitTile(self.surf, (x, y),(choice([0, 1, 2]), 2))
					else:
						# floor
						drawn = False
						if self[x+1, y] == BORDER:
							if randint(0, 2) == 2:
								# chance of bricks
								blitTile(self.surf, (x, y),(0, 7))
								drawn = True
						if self[x-1, y] == BORDER:
							if randint(0, 2) == 2:
								# chance of bricks
								blitTile(self.surf, (x, y),(3, 7))
								drawn = True
						if not drawn:
							# floor
							blitTile(self.surf, (x, y),(2, 3))
				elif self[x,y] == BORDER:
					if self[x, y+1] == FLOOR:
						# wall
						wallPos = (1, 1)
						if randint(0, 3) == 0:
							wallPos = (1,1)
						blitTile(self.surf, (x, y),wallPos)
					elif self[x, y-1] == FLOOR:
						# upper black
						blitTile(self.surf, (x, y),(8, 0))
				# addings
				if self[x, y+1] == BORDER and self[x, y+2] == FLOOR:
					blitTile(self.layer1, (x, y),(1, 0))
	# def blitTile(self, layer, dest, pos):
		# if layer == 0:
			# self.surf.blit(self.tiles, ((point2world(Vector(dest[0] * spriteWidth + 8, dest[1] * spriteWidth + 8))), (spriteWidth, spriteWidth)), (pos,(spriteWidth, spriteWidth)))
		# if layer == 1:
			# self.layer1.blit(self.tiles, ((point2world(Vector(dest[0] * spriteWidth + 8, dest[1] * spriteWidth + 8))), (spriteWidth, spriteWidth)), (pos,(spriteWidth, spriteWidth)))
	def draw(self, layer=0):
		if layer == 0:
			win.blit(self.surf, point2world(Vector()))
		elif layer == 1:
			win.blit(self.layer1, point2world(Vector()))
	def borderAt(self, pos):
		pos = (int(pos[0] / spriteWidth), int(pos[1] / spriteWidth))
		if not self.inBound(pos):
			return True
		return self[pos] == 0
		
		
		
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
		self.size = 16
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
			if dungeon.borderAt((ppos.x, self.pos.y)) or dungeon.borderAt((ppos.x, self.pos.y + self.size * 0.9)):
				ppos.x = self.size * int(ppos.x / self.size) + self.size
				self.vel.x = 0
		else:
			if dungeon.borderAt((ppos.x + self.size, self.pos.y)) or dungeon.borderAt((ppos.x + self.size, self.pos.y + self.size * 0.9)):
				ppos.x = self.size * int(ppos.x / self.size)
				self.vel.x = 0
		if self.vel.y <= 0:
			if dungeon.borderAt((ppos.x, ppos.y)) or dungeon.borderAt((ppos.x + self.size * 0.9, ppos.y)):
				ppos.y = self.size * int(ppos.y / self.size) + self.size
				self.vel.y = 0
		else:
			if dungeon.borderAt((ppos.x, ppos.y + self.size)) or dungeon.borderAt((ppos.x + self.size * 0.9, ppos.y + self.size)):
				ppos.y = self.size * int(ppos.y / self.size) 
				self.vel.y = 0
		return ppos
	def draw(self):
		pygame.draw.rect(win, self.color, (point2world(self.pos), (self.size,self.size)))
		
class Player(Character):
	force = 0.25
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
		self.size = 8
		self.facing = RIGHT
		self.surf = pygame.Surface((16,32), pygame.SRCALPHA)
	def applyForce(self):
		if self.stunned:
			self.acc = (self.pos + Vector(self.size, self.size)/2 - self.stunned).normalize() * 10
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
			self.facing = LEFT
		if keys[pygame.K_s] or keys[pygame.K_DOWN]:
			self.acc.y = Player.force
			self.direction[1] = 1
			self.move = True
		if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
			self.acc.x = Player.force
			self.direction[0] = 1
			self.move = True
			self.facing = RIGHT
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
			if dist(e.pos + Vector(e.size,e.size)/2, self.pos + Vector(self.size,self.size)/2) > self.size + e.size:
				continue
			self.stunned = e.pos + Vector(e.size,e.size)/2
			break
		if self.vel.getMag() < 0.01:
			self.vel *= 0
	def attack(self):
		SwordAttack()
		
	def draw(self):
		# pygame.draw.rect(win, self.color, (point2world(self.pos), (self.size,self.size)))
		# pygame.draw.circle(win, (150,150,0), point2world(self.pos + Vector(self.size,self.size)/2 + 3 * self.direction), 2)
		self.surf.fill((0,0,0,0))
		if self.vel.getMag() > 0.01:
			pos = (128 + 64 + ((overallTime//7) % 4)*16 ,64)
		else:
			pos = (128 + ((overallTime//7) % 4)*16 ,64)
		self.surf.blit(tiles2, (0,0), (pos,(16, 32)))
		
		win.blit(pygame.transform.flip(self.surf, self.facing == LEFT, False), point2world(self.pos - Vector(4,24)))
		
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
			if dist(obj.pos + Vector(player.size,player.size)/2, player.pos + Vector(player.size,player.size)/2 + player.size * (1.4) * player.direction) > 24:
				continue
			obj.direction = self.direction
			obj.mode = 2
			obj.timer = 0
		self.done = True
	def draw(self):
		extraAppend(CIRCLE, point2world(player.pos + Vector(player.size,player.size)/2 + player.size * (1.4) * player.direction), WHITE, 5, 16)
		
class Enemy(Character):
	force = 0.2
	stunned = 0
	stunTime = fps * 0.5
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
		self.size = 8
		self.surf = pygame.Surface((16,32), pygame.SRCALPHA)
		self.facing = RIGHT
	def applyForce(self):
		if self.mode == Enemy.stunned:
			self.acc *= 0
		elif self.mode == Enemy.wander:
			self.acc = Enemy.force * self.direction
		elif self.mode == Enemy.hit:
			self.acc = player.direction * 8
		elif self.mode == Enemy.chase:
			self.acc = Enemy.force * (player.pos - self.pos).normalize()
	def secondaryStep(self):
		if self.health <= 0:
				objects.remove(self)
		if self.mode == Enemy.stunned:
			self.timer += 1
			if self.timer == Enemy.stunTime:
				self.mode = Enemy.wander
				if self.search():
					self.mode = Enemy.chase
					self.timer = 0
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
			self.checkFacing()
		if self.mode == Enemy.chase:
			self.timer += 1
			if self.timer % (fps * 3) == 0:
				if not self.search():
					self.mode = Enemy.wander
			self.checkFacing()
	def checkFacing(self):
		if self.vel.x >= 0:
			self.facing = RIGHT
		else:
			self.facing = LEFT
	def search(self):
		ray = (player.pos - self.pos).normalize()
		for i in range(20):
			checkPos = self.pos + ray * (i * 10)
			if DEBUG: extraAppend(DOT, checkPos, (0,0,255), 2*fps)
			if dungeon.borderAt(checkPos):
				return False
			if dist(player.pos, checkPos) < self.size:
				return True
		
	def draw(self):
		# pygame.draw.rect(win, self.color, (point2world(self.pos), (self.size,self.size)))
		# if self.mode == 0 and self.timer < fps * 0.25:
			# pygame.draw.rect(win, (255,0,0), (point2world(self.pos), (self.size,self.size)))
			
		self.surf.fill((0,0,0,0))
		if self.vel.getMag() > 0.01:
			pos = (370 + 64 + ((overallTime//7) % 4)*16 ,160)
		else:
			pos = (370 + ((overallTime//7) % 4)*16 ,160)
		self.surf.blit(tiles2, (0,0), (pos,(16, 32)))
		
		win.blit(pygame.transform.flip(self.surf, self.facing == LEFT, False), point2world(self.pos - Vector(4,24)))
		
		

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
		elif e[0] == CIRCLE:
			pygame.draw.circle(win, e[2], e[1], e[4])
		e[3] -= 1
		if e[3] == 0:
			extra.remove(e)

player = Player()
dungeonInfo = loadDungeon()
dungeon = Dungeon(dungeonInfo[0], dungeonInfo[1])


objects = []

for i in range(40):
	e = Enemy()
	e.pos = Vector(spriteWidth * randint(0, dungeonInfo[0][0]), spriteWidth * randint(0, dungeonInfo[0][1]))

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
			# print("mouse pressed once")
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
	# if keys[pygame.K_z]:
		# print("pressing")
	
	overallTime += 1
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
	dungeon.draw(1)
	extraDraw()
	
	screen.blit(pygame.transform.scale(win, screen.get_size()), (0,0))
	pygame.display.update()
pygame.quit()














