import pygame as pg
import maze
import random
import heapq
import concurrent.futures
import time
def heuristic(a, b):
  return abs(a[0] - b[0]) + abs(a[0] - b[0])
# PlayerCharacterクラスの定義 [ここから]

class PlayerCharacter:

  # コンストラクタ
  def __init__(self, init_pos, img_path):
    self.atackflag = False
    self.cmd_move = [False] * 4
    self.pos = pg.Vector2(init_pos)
    self.size = pg.Vector2(48, 48)
    self.lv = 1
    self.exp = 0
    self.dir = 0
    self.maxlife = 10
    self.life = 10
    img_raw = pg.image.load(img_path)
    self.__img_arr = []
    for i in range(4):
      self.__img_arr.append([])
      for j in range(3):
        p = pg.Vector2(32 * j, 32 * i)
        tmp = img_raw.subsurface(pg.Rect(p, (32, 32)))
        tmp = pg.transform.scale(tmp, self.size)
        self.__img_arr[i].append(tmp)
      self.__img_arr[i].append(self.__img_arr[i][1])

  def turn_to(self, dir):
    self.dir = dir

  def move_to(self, vec):
    self.pos += vec

  def get_dp(self):
    return self.pos * 48 - pg.Vector2(0, 24)

  def get_img(self, frame):
    return self.__img_arr[self.dir][frame // 6 % 4]

  def atack(self, enemy, muki, llsc, K_SE, H_SE):
    atakcksaki = self.pos + muki[self.dir]
    for i in range(len(enemy)):
      if (self.pos + muki[self.dir] == enemy[i].pos):
        enemy[i].life -= 1
        K_SE.play()
        self.exp += 1
    if (llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] > 0 and llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] < 4):
      llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] -= 1
      H_SE.play()

  def life_reset(self):
    self.life = self.maxlife

  def warp_to(self, vec):
    self.pos = vec

  def lvup(self):
    if (self.exp > 10):  # 敵を10体倒したらlvアップ
      self.lv += 1
      self.exp = self.exp - 10
      self.maxlife += 1
      if (self.maxlife < self.life + self.lv + 1):
        self.life += 1 + self.lv
      else:
        self.life = self.maxlife

  def shokika(self):
    self.maxlife = 10
    self.life = 10
    self.lv = 1
    self.exp = 0
    # PlayerCharacterクラスの定義[ここまで]


class Tekikyara(PlayerCharacter):
  def __init__(self, init_pos, img_path):
    super().__init__(init_pos, img_path)
    self.pos = init_pos
    self.size = (48, 48)
    self.dir = 2
    self.maxlife = 1
    self.life = 1
    self.power = 1
    img_raw = pg.image.load(img_path)
    self.__teki_img_arr = []

    for i in range(4):
      self.__teki_img_arr.append([])
      for j in range(3):
        p = pg.Vector2(48 * j, 48 * i)
        tmp = img_raw.subsurface(pg.Rect(p, (48, 48)))
        tmp = pg.transform.scale(tmp, self.size)
        self.__teki_img_arr[i].append(tmp)
      self.__teki_img_arr[i].append(self.__teki_img_arr[i][1])

  def teki_get_img(self, frame):
    return self.__teki_img_arr[self.dir][frame // 6 % 4]

  def a_star_search(self, maze, st, en):
    start = (int(st[0]), int(st[1]))
    end = (int(en[0]), int(en[1]))
    neighbors = [(1, 0),
                 (-1, 0),
                 (0, 1),
                 (0, -1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, end)}
    oheap = []
    oheap = []

    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
      current = heapq.heappop(oheap)[1]

      if current == end:
        data = []
        while current in came_from:
          data.append(current)
          current = came_from[current]
        return data

      close_set.add(current)
      for i, j in neighbors:
        neighbor = current[0] + i, current[1] + j
        tentative_g_score = gscore[current] + 1

        if 0 <= neighbor[0] < len(maze):
          if 0 <= neighbor[1] < len(maze[0]):
            if maze[neighbor[0]][neighbor[1]] > 0 and not maze[neighbor[0]][neighbor[1]] == 4:
              continue
          else:
            # maze boundary
            continue
        else:
          # maze boundary
          continue

        if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
          continue

        if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
          came_from[neighbor] = current
          gscore[neighbor] = tentative_g_score
          fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
          heapq.heappush(oheap, (fscore[neighbor], neighbor))

    return False

  def atack_shori(self, enemy, muki, llsc, SE):
    atakcksaki = self.pos + muki[self.dir]
    if (self.pos + muki[self.dir] == enemy.pos):
      enemy.life -= self.power
      SE.play()

  def atack(self, teki, m_vec, llsc, atackflag, SE):
    if atackflag:  # 攻撃するコマンド
      self.atack_shori(teki, m_vec, llsc, SE)
      return False

  def powerup(self, kaisou):
    self.power = 1 + int(kaisou / 3)


def main():

  # 初期化処理
  chip_s = 48  # マップチップの基本サイズ
  map_s = pg.Vector2(25, 13)  # マップの横・縦の配置数
  llsc = maze.meiro(20, 13)
  atackfrequency = 30
  kaisou = 0  # 今が何階かを示す
  maizflag = True
  atackframe = 0  # 攻撃したタイミングを記録する
  pg.init()
  path = []
  pg.display.set_caption('探検家の冒険')
  disp_w = int(chip_s * map_s.x)
  disp_h = int(chip_s * map_s.y)
  screen = pg.display.set_mode((disp_w, disp_h))
  clock = pg.time.Clock()
  font = pg.font.Font(None, 15)
  frame = 0  # 現在のフレーム
  exit_flag = False
  exit_code = '000'
  path_n = -1
  tekikazu = 0  # 敵の数
  karyoku = 1  # 敵の攻撃力
  heart_img = pg.image.load("data\img\heart.png")
  tekik_kougeki_SE = pg.mixer.Sound("data\music\maou_se_battle17.wav")
  kougeki_SE = pg.mixer.Sound("data\music\maou_se_battle14.wav")
  hakai_SE = pg.mixer.Sound("data\music\maou_se_battle18.wav")
  # グリッド設定
  grid_c = '#bbbbbb'
  font1 = pg.font.SysFont("hg正楷書体pro", 30)
  gameover_font = pg.font.SysFont("hg正楷書体pro", 70)

  bgm = "data\music\maou_bgm_8bit09.mp3"
  # 自キャラ移動関連
  m_vec = [pg.Vector2(0, 1),


           pg.Vector2(-1, 0),
           pg.Vector2(1, 0),
           pg.Vector2(0, - 1)

           ]  # 移動コマンドに対応したXYの移動量
  t_idou = [pg.Vector2(0, 1),
            pg.Vector2(-1, 0),
            pg.Vector2(1, 0),
            pg.Vector2(0, -1)
            ]

  # 自キャラの生成・初期化
  reimu = PlayerCharacter((2, 3), './data/img/tankenka.png')
  pg.mixer.music.load(bgm)
  pg.mixer.music.play(loops=-1)
  # while flag:
  #   screen.fill((255, 255, 255))
  # ゲームループ
  while not exit_flag:
    if (reimu.life <= 0):
      screen.fill((0, 0, 0))

      screen.blit(gameover_font.render(
          f"GAMEOVER", True, 'RED'), (50, 100))
      screen.blit(gameover_font.render(
          f"{kaisou}階", True, 'RED'), (50, 200))
      screen.blit(gameover_font.render(
          f"SPACEで再開", True, 'RED'), (50, 300))
      for event in pg.event.get():
        if event.type == pg.KEYDOWN:
          if event.key == pg.K_SPACE:
            kaisou = 0
            maizflag = True
            reimu.shokika()
        if event.type == pg.QUIT:  # ウィンドウ[X]の押下
          exit_flag = True
          exit_code = '001'
      pg.display.update()

      continue
    if maizflag:
      teki = []
      kaisou += 1
      tekikazu = kaisou - 1 if kaisou < 6 else 5 + int(kaisou / 5)
      if (tekikazu > 20):
        tekikazu = 20
      llsc.maze_create()  # 迷路のスタート,ゴール,道を定める.
      llsc.maze_change(llsc.WALL, llsc.LOAD, random.randint(6, 11))
      llsc.maze_change(llsc.WALL, llsc.WALL_KOWARE, random.randint(2, 6))
      llsc.maze_change(llsc.WALL, llsc.WALL_HARD, random.randint(0, 3))
      llsc.maze_change(llsc.LOAD, llsc.WALL, random.randint(0, 5))
      llsc.maze_change(llsc.LOAD, llsc.WALL_KOWARE, random.randint(0, 2))
      llsc.maze_change(llsc.LOAD, llsc.WALL_HARD, random.randint(0, 3))
      reimu.warp_to(pg.Vector2(1, 1))
      for x in range(tekikazu):
        tekibasho = []
        for i in range(len(llsc.maze)):
          for j in range(len(llsc.maze[i])):
            if (llsc.maze[i][j] == llsc.LOAD):
              tekibasho.append(pg.Vector2(i, j))  # 敵キャラ設置
        tekistart = random.choice(tekibasho)
        teki.append(Tekikyara(tekistart, "data/img/tekikyara.png"))
        teki_atackflag = []
        teki_atackflag.append(True)
        teki_atackframe = []
        teki_atackframe.append(0)
        teki_atackflag.append(True)
        teki_atackframe.append(frame)
        teki[x].life_reset()

      maizflag = False
    # futures = []
    # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
      # executor.map(
      # futures.append(future)

    # システムイベントの検出

    for event in pg.event.get():
      if event.type == pg.QUIT:  # ウィンドウ[X]の押下
        exit_flag = True
        exit_code = '001'
      # 移動操作の「キー入力」の受け取り処理
      key = pg.key.get_pressed()
      reimu.cmd_move[3] = True if key[pg.K_UP] else False
      reimu.cmd_move[2] = True if key[pg.K_RIGHT] else False
      reimu.cmd_move[0] = True if key[pg.K_DOWN] else False
      reimu.cmd_move[1] = True if key[pg.K_LEFT] else False
      reimu.atackflag = True if key[pg.K_SPACE] else False
    if (reimu.atackflag):
      if (atackframe + atackfrequency < frame):  # 攻撃頻度を求めてる
        atackframe = frame
        reimu.atack(teki, m_vec, llsc, kougeki_SE, hakai_SE)

    # 背景描画
    screen.fill(pg.Color('BLACK'))

    # 移動コマンドの処理
    if (frame % 5 == 0):
      for x in range(len(reimu.cmd_move)):
        if reimu.cmd_move[x] == True:
          reimu.turn_to(x)
          af_pos = reimu.pos + m_vec[x]  # 移動(仮)した座標
          if (0 <= af_pos.x <= map_s.x - 1) and (0 <= af_pos.y <= map_s.y - 1):
            if (not llsc.maze[int(af_pos.x)][int(af_pos.y)] > 0):
              reimu.move_to(m_vec[x])  # 画面範囲内なら実際に移動
          if (llsc.maze[int(af_pos.x)][int(af_pos.y)] == 4):
            maizflag = True
            for i in range(len(llsc.maze)):
              for j in range(len(llsc.maze[i])):
                llsc.maze[i][j] = llsc.WALL

    # 自キャラの描画

    for i in range(len(llsc.maze)):
      for j in range(len(llsc.maze[i])):
        llsc.maze_put(screen, llsc.LOAD, i, j)
        llsc.maze_put(screen, llsc.WALL, i, j)
        llsc.maze_put(screen, llsc.WALL_HARD, i, j)
        llsc.maze_put(screen, llsc.WALL_KOWARE, i, j)
    llsc.maze_put(screen, 4, llsc.end[0], llsc.end[1])
    if (reimu.life > 0):
      screen.blit(reimu.get_img(frame), reimu.get_dp())  # 自キャラ

    for i in range(tekikazu):
      path.append([])
      path[i] = (teki[i].a_star_search(llsc.maze, teki[i].pos, reimu.pos))
    # concurrent.futures.wait(futures)
    # # 全てのタスクが終わっているので結果を取得
    # for future in futures:
    #   path = future.result()

    # フレームカウンタの描画
    frame += 1
    frm_str = f'{frame:05}'
    pg.draw.rect(screen, ("WHITE"), (1008, 10, 144, 96))

    screen.blit(heart_img, (1010, 130))  # 体力のハート
    screen.blit(font1.render(
        f"{reimu.maxlife}/{reimu.life}", True, 'BLACK'), (1038, 180))
    pg.draw.rect(screen, ("YELLOW"), (1008, 300, 144, 150))
    screen.blit(font1.render(f"LV:{reimu.lv}", True, 'BLACK'), (1056, 320))
    screen.blit(font1.render(
        f"next:{reimu.exp}/10", True, 'BLACK'), (1011, 380))

    screen.blit(font1.render(f"{kaisou}階", True, 'BLACK'), (1056, 45))
    screen.blit(font.render(f'{reimu.life}', True, 'WHITE'), (30, 20))
    for x in range(tekikazu):

      if (teki[x].life > 0):
        if (path[x]):
          if (not len(path[x]) == 1):

            # path_n = -1 * frame // 50
            # if (abs(path_n) < len(path)):
            #   p = path[path_n]
            # else:
            if (frame % 20 == 0):
              path_n = -1  # 20フレームごとに移動
              p = path[x][path_n]
              tekimuki = pg.Vector2(p[0], p[1]) - teki[x].pos
              teki[x].pos = (pg.Vector2(p[0], p[1]))
              for muki in range(len(t_idou)):
                if (t_idou[muki] == tekimuki):
                  teki[x].dir = muki
          elif (teki_atackflag[x]):  # 敵の攻撃
            teki_atackflag[x] = teki[x].atack(
                reimu, t_idou, llsc, teki_atackflag[x], tekik_kougeki_SE)
            teki_atackframe[x] = frame
          if (teki_atackframe[x] + atackfrequency < frame):  # 攻撃頻度
            teki_atackflag[x] = True
        screen.blit(teki[x].teki_get_img(frame), teki[x].get_dp())  # 敵キャラ
    reimu.lvup()
    for i in range(tekikazu):
      teki[i].powerup(kaisou)
    # 画面の更新と同期
    pg.display.update()
    clock.tick(30)

  # ゲームループ [ここまで]
  pg.quit()
  return exit_code

if __name__ == "__main__":
  code = main()
  print(f'プログラムを「コード{code}」で終了しました。')
