import pygame as pg
import maze
import random
import heapq
import concurrent.futures
def heuristic(a, b):
  return abs(a[0] - b[0]) + abs(a[0] - b[0])
# PlayerCharacterクラスの定義 [ここから]

class PlayerCharacter:

  # コンストラクタ
  def __init__(self, init_pos, img_path):
    self.pos = pg.Vector2(init_pos)
    self.size = pg.Vector2(48, 64)
    self.dir = 2
    self.maxlife = 10
    img_raw = pg.image.load(img_path)
    self.__img_arr = []
    for i in range(4):
      self.__img_arr.append([])
      for j in range(3):
        p = pg.Vector2(24 * j, 32 * i)
        tmp = img_raw.subsurface(pg.Rect(p, (24, 32)))
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

  def atack(self, enemy, muki, llsc):
    atakcksaki = self.pos + muki[self.dir]
    if (self.pos + muki[self.dir] == enemy.pos):
      enemy.life -= 1
    if (llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] > 0 and not llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] == 4):
      llsc.maze[int(atakcksaki[0])][int(atakcksaki[1])] -= 1

  def life_reset(self):
    self.life = self.maxlife

  def warp_to(self, vec):
    self.pos = vec
# PlayerCharacterクラスの定義[ここまで]
class Tekikyara(PlayerCharacter):
  def __init__(self, init_pos, img_path):
    super().__init__(init_pos, img_path)
    self.pos = init_pos
    self.size = (48, 48)
    self.dir = 0
    self.maxlife = 1
    self.life = 1
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
    print(end)
    neighbors = [(0, 1),
                 (0, -1),
                 (1, 0),
                 (-1, 0)]
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


def main():

  # 初期化処理
  chip_s = 48  # マップチップの基本サイズ
  map_s = pg.Vector2(25, 13)  # マップの横・縦の配置数
  llsc = maze.meiro(20, 13)
  atackfrequency = 20
  maizflag = True
  atackflag = True
  atackframe = 0
  pg.init()
  pg.display.set_caption('探検家の冒険')
  disp_w = int(chip_s * map_s.x)
  disp_h = int(chip_s * map_s.y)
  screen = pg.display.set_mode((disp_w, disp_h))
  clock = pg.time.Clock()
  font = pg.font.Font(None, 15)
  frame = 0
  exit_flag = False
  exit_code = '000'
  path_n = -1
  # グリッド設定
  grid_c = '#bbbbbb'

  # 自キャラ移動関連
  cmd_move = -1  # 移動コマンドの管理変数
  m_vec = [
      pg.Vector2(0, -1),
      pg.Vector2(1, 0),
      pg.Vector2(0, 1),
      pg.Vector2(-1, 0)
  ]  # 移動コマンドに対応したXYの移動量
  t_idou = [pg.Vector2(0, 1),
            pg.Vector2(0, -1),
            pg.Vector2(1, 0),
            pg.Vector2(-1, 0)
            ]

  # 自キャラの生成・初期化
  reimu = PlayerCharacter((2, 3), './data/img/reimu.png')
  teki = Tekikyara((3, 4), "data/img/tekikyara.png")
  # ゲームループ
  while not exit_flag:
    if maizflag:
      llsc.maze_create()  # 迷路のスタート,ゴール,道を定める.
      reimu.warp_to(pg.Vector2(1, 1))
      tekibasho = []
      for i in range(len(llsc.maze)):
        for j in range(len(llsc.maze[i])):
          if (llsc.maze[i][j] == llsc.LOAD):
            tekibasho.append(pg.Vector2(i, j))  # 敵キャラ設置
      tekistart = random.choice(tekibasho)
      teki.warp_to(tekistart)
      teki.life_reset()
      maizflag = False
    # futures = []
    # with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
      # executor.map(
      # futures.append(future)

    # システムイベントの検出
    cmd_move = -1
    for event in pg.event.get():
      if event.type == pg.QUIT:  # ウィンドウ[X]の押下
        exit_flag = True
        exit_code = '001'
      # 移動操作の「キー入力」の受け取り処理
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_UP:
          cmd_move = 0
        elif event.key == pg.K_RIGHT:
          cmd_move = 1
        elif event.key == pg.K_DOWN:
          cmd_move = 2
        elif event.key == pg.K_LEFT:
          cmd_move = 3
        elif event.key == pg.K_SPACE:
          if atackflag:  # 攻撃するコマンド
            reimu.atack(teki, m_vec, llsc)
            atackflag = False
            atackframe = frame
    if (atackframe + atackfrequency == frame):  # 攻撃頻度を求めてる
      atackflag = True

    # 背景描画
    screen.fill(pg.Color('BLACK'))

    # グリッド
    for x in range(0, disp_w, chip_s):  # 縦線
      pg.draw.line(screen, grid_c, (x, 0), (x, disp_h))
    for y in range(0, disp_h, chip_s):  # 横線
      pg.draw.line(screen, grid_c, (0, y), (disp_w, y))

    # 移動コマンドの処理
    if cmd_move != -1:
      reimu.turn_to(cmd_move)
      af_pos = reimu.pos + m_vec[cmd_move]  # 移動(仮)した座標
      if (0 <= af_pos.x <= map_s.x - 1) and (0 <= af_pos.y <= map_s.y - 1):
        if (not llsc.maze[int(af_pos.x)][int(af_pos.y)] > 0):
          reimu.move_to(m_vec[cmd_move])  # 画面範囲内なら実際に移動
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

    screen.blit(reimu.get_img(frame), reimu.get_dp())  # 自キャラ
    print(reimu.pos)
    path = teki.a_star_search(llsc.maze, teki.pos, reimu.pos)
    # concurrent.futures.wait(futures)

    # # 全てのタスクが終わっているので結果を取得
    # for future in futures:
    #   path = future.result()
    if (teki.life > 0):
      if (path):

        # path_n = -1 * frame // 50
        # if (abs(path_n) < len(path)):
        #   p = path[path_n]
        # else:
        if (frame % 20 == 0):
          path_n = -1
          p = path[path_n]
          teki.pos = (pg.Vector2(p[0], p[1]))
      else:
        print("pass")

      screen.blit(teki.teki_get_img(frame), teki.get_dp())  # 敵キャラ
    # フレームカウンタの描画
    frame += 1
    frm_str = f'{frame:05}'
    screen.blit(font.render(frm_str, True, 'BLACK'), (10, 10))
    screen.blit(font.render(f'{reimu.pos}', True, 'BLACK'), (10, 20))

    # 画面の更新と同期
    pg.display.update()
    clock.tick(30)

  # ゲームループ [ここまで]
  pg.quit()
  return exit_code

if __name__ == "__main__":
  code = main()
  print(f'プログラムを「コード{code}」で終了しました。')
