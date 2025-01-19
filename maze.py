import pygame as pg
import sys
import random
class meiro:
  def __init__(self, rows, cols):
    self.r = rows
    self.c = cols
    self.WALL = 2
    self.WALL_HARD = 3
    self.WALL_KOWARE = 1
    self.LOAD = 0
    self.maze = [[2 for _ in range(self.c)] for _ in range(self.r)]
    self.end = (0, 0)
    self.tile_img = []
    img_contena = ["data\img\maze_tile.png", "data\img\meiro_kowarekake.png",
                   "data\img\meiro_kowakabe.png", "data\img\meiro_kabe.png",
                   "data\img\kaidan.png"]
    for i in range(len(img_contena)):

      img_raw = pg.image.load(img_contena[i])

      img = img_raw.subsurface(pg.Rect((0, 0), (48, 48)))
      self.tile_img.append(pg.transform.scale(img, (48, 48)))

  def maze_create(self):
    self.maze = [[2 for _ in range(self.c)] for _ in range(self.r)]
    start = (1, 1)
    stack = [start]
    kanikama = 0
    self.end = (random.randint(1, self.r - 2), random.randint(1, self.c - 2))
    while stack:
      # print(kanikama)
      # kanikama += 1
      current = stack[-1]
      y, x = current

      self.maze[y][x] = self.LOAD
      neighbors = []
      if y > 2 and self.maze[y - 2][x] == self.WALL:
        neighbors.append((y - 2, x))
      if y < self.r - 3 and self.maze[y + 2][x] == self.WALL:
        neighbors.append((y + 2, x))
      if x > 2 and self.maze[y][x - 2] == self.WALL:
        neighbors.append((y, x - 2))
      if x < self.c - 3 and self.maze[y][x + 2] == self.WALL:
        neighbors.append((y, x + 2))
      if neighbors:
        next_cell = random.choice(neighbors)
        ny, nx = next_cell
        self.maze[(ny + y) // 2][(nx + x) // 2] = self.LOAD
        stack.append((ny, nx))
      else:
        stack.pop()  # 戻る
    self.maze[1][1] = self.LOAD
    self.maze[self.end[0]][self.end[1]] = 4
    for i in range(self.r):
      self.maze[i][0] = self.WALL_HARD
      self.maze[i][self.c - 1] = self.WALL_HARD
    for i in range(self.c):
      self.maze[0][i] = self.WALL_HARD
      self.maze[self.r - 1][i] = self.WALL_HARD

    return self.maze, start, self.end

  def maze_change(self, moto, henko, kazu):
    kabebasho = []
    for i in range(len(self.maze)):
      for j in range(len(self.maze[i])):
        if (self.maze[i][j] == moto):
          if (i == 1 and j == 1):
            pass
          else:
            kabebasho.append([i, j])
    for i in range(kazu):
      hakai = random.choice(kabebasho)
      self.maze[hakai[0]][hakai[1]] = henko

  def maze_put(self, screen, hyoji, i, j):
    if self.maze[i][j] == hyoji:
      screen.blit(self.tile_img[hyoji], pg.Vector2(
          i, j) * 48 - pg.Vector2(0, 24))
