from math import fabs, sqrt, cos, sin, pi, floor, ceil
from random import uniform, randint, choice
import pygame


################################################################################ 
# enters:
#  1
# 2 0
#  3

class Mat:
	def __init__(self, dims, values=0):
		self.dims = dims
		self.array = [values] * dims[0] * dims[1]
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
	def __str__(self):
		string = "mat " + str(self.dims[0]) + "x" +str(self.dims[1]) + ":\n"
		for y in range(self.dims[1]):
			for x in range(self.dims[0]):
				string += str(self.array[x * self.dims[1] + y]) + " "
			string += "\n"
		string += "\n"
		return string
	def copy(self):
		copied = Mat(self.dims)
		for y in range(self.dims[1]):
			for x in range(self.dims[0]):
				copied[x,y] = self[x,y]
		return copied
	def inBound(self, pos):
		x, y = pos
		if x < 0 or x >= self.dims[0] or y < 0 or y >= self.dims[1]:
			return False
		return True

def fillRoom(enters, dims):
	mat = Mat(dims)
	
	if sum(enters) == 0:
		return mat
	
	ends = []
	if enters[0]:
		ends.append((dims[0] - 1, dims[1]//2))
	if enters[1]:
		ends.append((dims[0]//2, 0))
	if enters[2]:
		ends.append((0, dims[1]//2))
	if enters[3]:
		ends.append((dims[0]//2, dims[1] - 1))
	
	for i in ends:
		mat[i] = 1
	
	accessible = False
	while not accessible:
		if len(ends) == 1:
			break
		if len(ends) == 2:
			if bfs(mat, ends[0], ends[1]):
				break
		if len(ends) == 3:
			if bfs(mat, ends[0], ends[1]) and bfs(mat, ends[0], ends[2]):
				break
		if len(ends) == 4:
			if bfs(mat, ends[0], ends[1]) and bfs(mat, ends[0], ends[2]) and bfs(mat, ends[0], ends[3]):
				break
		x = randint(0,dims[0]-1)
		y = randint(0,dims[1]-1)
		mat[x, y] = 1
	
	
	
	# print(mat)
	return mat

def inmat(pos, dims):
	# print("inmat:", pos, end=" ")
	res = not (pos[0] >= dims[0] or pos[0] < 0 or pos[1] >= dims[1] or pos[1] < 0)
	# print(res)
	return res

def bfs(mat, start, end):
	visited = mat.copy()
	que = [start]
	
	found = False
	while not found:
		if len(que) == 0:
			break
		start = que.pop(0)
		visited[start] = 2
		if end in que:
			found = True
		if inmat((start[0] + 1, start[1]), mat.dims) and visited[start[0] + 1, start[1]] == 1:
			que.append((start[0] + 1, start[1]))
			visited[start[0] + 1, start[1]] = 3
		if inmat((start[0], start[1] + 1), mat.dims) and visited[start[0], start[1] + 1] == 1:
			que.append((start[0], start[1] + 1))
			visited[start[0], start[1] + 1] = 3
		if inmat((start[0] - 1, start[1]), mat.dims) and visited[start[0] - 1, start[1]] == 1:
			que.append((start[0] - 1, start[1]))
			visited[start[0] - 1, start[1]] = 3
		if inmat((start[0], start[1] - 1), mat.dims) and visited[start[0], start[1] - 1] == 1:
			que.append((start[0], start[1] - 1))
			visited[start[0], start[1] - 1] = 3
		
	return found
	
def bfs2kill(mat, start, end):
	visited = mat.copy()
	que = [start]
	count = 0
	# print("bfs to kill", start, end)
	# print(mat[start], mat[end])
	while True:
		# print(len(que), "", end=" ")
		if len(que) == 0:
			break
		start = que.pop(0)
		visited[start] = 2
		if inmat((start[0] + 1, start[1]), mat.dims) and visited[start[0] + 1, start[1]] == 1:
			que.append((start[0] + 1, start[1]))
			visited[start[0] + 1, start[1]] = 3
		if inmat((start[0], start[1] + 1), mat.dims) and visited[start[0], start[1] + 1] == 1:
			que.append((start[0], start[1] + 1))
			visited[start[0], start[1] + 1] = 3
		if inmat((start[0] - 1, start[1]), mat.dims) and visited[start[0] - 1, start[1]] == 1:
			que.append((start[0] - 1, start[1]))
			visited[start[0] - 1, start[1]] = 3
		if inmat((start[0], start[1] - 1), mat.dims) and visited[start[0], start[1] - 1] == 1:
			que.append((start[0], start[1] - 1))
			visited[start[0], start[1] - 1] = 3
		# print(visited)
		
	for i in range(mat.dims[0]):
		for j in range(mat.dims[1]):
			if visited[i,j] == 1:
				mat[i,j] = 0
	

################################################################################ Classes
outerGrid = (7,4)
innerGrid = (5,5)
globalEnter = (1,0,1,0)

scale = 5
colorBack = (255,255,255)
colorPath = (0,0,0)

start = None
end = None
if globalEnter[0]:
	pos = (outerGrid[0] * innerGrid[0] - 1, (outerGrid[1] * innerGrid[1]) // 2)
	if not start:
		start = pos
	else:
		end = pos
if globalEnter[1]:
	pos = ((outerGrid[0] * innerGrid[0]) // 2, 0)
	if not start:
		start = pos
	else:
		end = pos
if globalEnter[2]:
	pos = (0, (outerGrid[1] * innerGrid[1]) // 2)
	if not start:
		start = pos
	else:
		end = pos
if globalEnter[3]:
	pos = ((outerGrid[0] * innerGrid[0]) // 2, outerGrid[1] * innerGrid[1] - 1)
	if not start:
		start = pos
	else:
		end = pos

print(start, end)

################################################################################ Setup

M = fillRoom(globalEnter, outerGrid)
print("level:", M)

Mentries = Mat(outerGrid, None)
for i in range(len(M.array)):
	enters = [0,0,0,0]
	pos = (i % M.dims[0], i // M.dims[0])
	# print("check for pos:", pos, end=" ")
	if globalEnter[0] and pos == (M.dims[0] - 1, M.dims[1]//2): enters[0] = 1
	if globalEnter[1] and pos == (M.dims[0]//2, 0): enters[1] = 1
	if globalEnter[2] and pos == (0, M.dims[1]//2): enters[2] = 1
	if globalEnter[3] and pos == (M.dims[0]//2, M.dims[1] - 1): enters[3] = 1
	
	if M[pos] == 1:
		if inmat((pos[0] + 1, pos[1]), M.dims) and M[pos[0] + 1, pos[1]] == 1: enters[0] = 1#; print("neighbor at 0", end=" ")
		if inmat((pos[0], pos[1] - 1), M.dims) and M[pos[0], pos[1] - 1] == 1: enters[1] = 1#; print("neighbor at 1", end=" ")
		if inmat((pos[0] - 1, pos[1]), M.dims) and M[pos[0] - 1, pos[1]] == 1: enters[2] = 1#; print("neighbor at 2", end=" ")
		if inmat((pos[0], pos[1] + 1), M.dims) and M[pos[0], pos[1] + 1] == 1: enters[3] = 1#; print("neighbor at 3", end=" ")
	# print("enter:", enters)
	Mentries[pos] = enters
# print("entries:", Mentries)

# print(1/0)

dun = Mat(outerGrid, None)
for i in range(len(dun.array)):
	pos = (i % dun.dims[0], i // dun.dims[0])
	# print(pos, end=" ")
	if M[pos] == 1: dun[pos] = fillRoom(Mentries[pos], innerGrid)

dungeon = Mat((outerGrid[0] * innerGrid[0], outerGrid[1] * innerGrid[1]))
for i in range(outerGrid[0]):
	for j in range(outerGrid[1]):
		for k in range(innerGrid[0]):
			for l in range(innerGrid[1]):
				dungeonPos = (i * innerGrid[0] + k, j * innerGrid[1] + l)
				dunPos = ((i,j), (k,l))
				if dun[dunPos[0]]:
					# print(dungeonPos, dunPos)
					dungeon[dungeonPos] = dun[dunPos[0]][dunPos[1]]
	
# print("dungeon is complete")
# print(dungeon)

bfs2kill(dungeon, start, end)

def pixelSurf(dungeon):
	surf = pygame.Surface((outerGrid[0] * innerGrid[0], outerGrid[1] * innerGrid[1]))
	surf.fill(colorBack)
	for x in range(outerGrid[0] * innerGrid[0]):
		for y in range(outerGrid[1] * innerGrid[1]):
			if dungeon[x,y] == 1:
				surf.set_at((x,y), colorPath)
	return surf

def octagons(dungeon):
	octSize = 20
	surf = pygame.Surface((dungeon.dims[0] * octSize, dungeon.dims[1] * octSize))
	surf.fill(colorBack)
	quart = octSize//4
	octPoints = [(quart, 0), (3*quart, 0), (octSize, quart), (octSize, 3*quart), (3*quart, octSize), (quart, octSize), (0, 3*quart), (0, quart)]
	for x in range(outerGrid[0] * innerGrid[0]):
		for y in range(outerGrid[1] * innerGrid[1]):
			if dungeon[x,y] == 1:
				pos = (x * octSize, y * octSize)
				
				octPoints = [(quart, 0), (3*quart, 0), (octSize, quart), (octSize, 3*quart), (3*quart, octSize), (quart, octSize), (0, 3*quart), (0, quart)]
				
				if dungeon.inBound((x + 1, y)) and dungeon[x + 1, y] == 1:
					octPoints[1] = (octSize, 0); octPoints[2] = (octSize, 0); octPoints[3] = (octSize, octSize); octPoints[4] = (octSize, octSize)
				if dungeon.inBound((x - 1, y)) and dungeon[x - 1, y] == 1:
					octPoints[0] = (0,0); octPoints[5] = (0, octSize); octPoints[6] = (0, octSize); octPoints[7] = (0,0)
				if dungeon.inBound((x, y - 1)) and dungeon[x, y - 1] == 1:
					octPoints[0] = (0,0); octPoints[1] = (octSize, 0); octPoints[2] = (octSize, 0); octPoints[7] = (0,0)
				if dungeon.inBound((x, y + 1)) and dungeon[x, y + 1] == 1:
					octPoints[3] = (octSize, octSize); octPoints[4] = (octSize, octSize); octPoints[5] = (0, octSize); octPoints[6] = (0, octSize)
				
				pygame.draw.polygon(surf, colorPath, [(pos[0] + i[0], pos[1] + i[1]) for i in octPoints])
	return surf



pygame.init()
fpsClock = pygame.time.Clock()
winWidth = 800#outerGrid[0] * innerGrid[0] * scale
winHeight = 600#outerGrid[1] * innerGrid[1] * scale
win = pygame.display.set_mode((winWidth,winHeight))

surf = octagons(dungeon)

# win.blit(pygame.transform.scale(surf, (winWidth, winHeight)), (0,0))
win.blit(surf, (0,0))
pygame.image.save(surf, "dungeon" + ".png")
# worms.py -map dun -rg -ratio 800 -dark -used

################################################################################ Main Loop
run = True
while run:
	fpsClock.tick(60)
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		#mouse pressed once(MOUSEBUTTONUP for release):
		if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			#mouse position:
			mouse_pos = pygame.mouse.get_pos()
			print("mouse pressed once")
		if event.type == pygame.KEYDOWN:
			#key pressed once:
			if event.key == pygame.K_x:
				print("pressed once")
	keys = pygame.key.get_pressed()
	if keys[pygame.K_ESCAPE]:
		run = False
	#key hold:
	if keys[pygame.K_z]:
		print("pressing")
	
	# step:
	
	
	
	# draw:
	# win.fill((255,255,255))
	
	pygame.display.update()
pygame.quit()














