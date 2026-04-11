"""
Snake Game - 經典貪食蛇
使用 pygame 實作
"""

import pygame
import random
import sys

# --- 初始化 ---
pygame.init()

# --- 遊戲設定常數 ---
CELL_SIZE = 20
GRID_WIDTH = 30
GRID_HEIGHT = 20
SCREEN_WIDTH = CELL_SIZE * GRID_WIDTH
SCREEN_HEIGHT = CELL_SIZE * GRID_HEIGHT

# 顏色設定
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 180, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (100, 100, 100)

# FPS 設定
BASE_FPS = 10
MAX_FPS = 30

# 速度增加門檻
SPEED_INCREMENT_SCORE = 5  # 每增加 5 分，速度提升一次

# --- 螢幕設定 ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🐍 Snake Game")
clock = pygame.time.Clock()
font_large = pygame.font.Font(None, 50)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)


class Snake:
    """蛇的類別"""

    def __init__(self):
        # 初始蛇長度 3 格，放在畫面中央偏左
        self.body = [
            (GRID_WIDTH // 4, GRID_HEIGHT // 2),
            (GRID_WIDTH // 4 - 1, GRID_HEIGHT // 2),
            (GRID_WIDTH // 4 - 2, GRID_HEIGHT // 2),
        ]
        self.direction = (1, 0)  # 初始向右
        self.grow_pending = False

    def reset(self):
        """重新設定蛇"""
        self.__init__()

    @property
    def head(self):
        return self.body[0]

    def move(self):
        """移動蛇"""
        head_x, head_y = self.head
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # 檢查是否撞牆
        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT):
            return False  # 撞牆

        # 檢查是否撞到自己
        if new_head in self.body:
            return False  # 撞到自己

        # 加入新頭
        self.body.insert(0, new_head)

        # 如果沒有要生長，移除尾巴
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

        return True

    def grow(self):
        """下次移動時生長"""
        self.grow_pending = True

    def draw(self):
        """繪製蛇"""
        for i, segment in enumerate(self.body):
            x, y = segment
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 2, CELL_SIZE - 2)
            # 頭部用亮綠色，身體用深綠色
            color = GREEN if i == 0 else DARK_GREEN
            pygame.draw.rect(screen, color, rect, border_radius=5)

    def check_food_collision(self, food):
        """檢查是否吃到食物"""
        return self.head == food.position


class Food:
    """食物類別"""

    def __init__(self):
        self.position = (0, 0)
        self.spawn()

    def spawn(self, snake_body=None):
        """生成新食物位置"""
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            self.position = (x, y)
            # 確保食物不會長在蛇身上
            if snake_body is None or self.position not in snake_body:
                break

    def draw(self):
        """繪製食物"""
        x, y = self.position
        rect = pygame.Rect(x * CELL_SIZE + 1, y * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(screen, RED, rect, border_radius=3)


class Game:
    """遊戲主類別"""

    def __init__(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.high_score = self.load_high_score()
        self.game_over = False
        self.paused = False

    def load_high_score(self):
        """讀取最高分"""
        try:
            with open("snake_high_score.txt", "r") as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        """儲存最高分"""
        try:
            with open("snake_high_score.txt", "w") as f:
                f.write(str(self.high_score))
        except:
            pass

    def calculate_fps(self):
        """根據分數計算 FPS"""
        speed_increments = self.score // SPEED_INCREMENT_SCORE
        fps = min(BASE_FPS + speed_increments * 2, MAX_FPS)
        return fps

    def handle_events(self):
        """處理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # 方向控制（不能180度轉向）
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if self.snake.direction != (0, 1):
                        self.snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if self.snake.direction != (0, -1):
                        self.snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if self.snake.direction != (1, 0):
                        self.snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if self.snake.direction != (-1, 0):
                        self.snake.direction = (1, 0)

                # 暫停切換
                elif event.key == pygame.K_SPACE:
                    if not self.game_over:
                        self.paused = not self.paused

                # 重新開始
                elif event.key == pygame.K_r:
                    self.reset()

    def update(self):
        """更新遊戲狀態"""
        if self.game_over or self.paused:
            return

        # 移動蛇
        if not self.snake.move():
            self.game_over = True
            # 更新最高分
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        # 檢查吃到食物
        if self.snake.check_food_collision(self.food):
            self.snake.grow()
            self.score += 1
            self.food.spawn(self.snake.body)

    def draw_background(self):
        """繪製背景"""
        screen.fill(BLACK)
        # 繪製格線（可選）
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y))

    def draw_score(self):
        """繪製分數"""
        score_text = font_small.render(f"分數: {self.score}", True, WHITE)
        high_score_text = font_small.render(f"最高分: {self.high_score}", True, LIGHT_GRAY)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 35))

    def draw_game_over(self):
        """繪製遊戲結束畫面"""
        # 半透明覆蓋
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        # 遊戲結束文字
        game_over_text = font_large.render("遊戲結束!", True, RED)
        score_text = font_medium.render(f"最終分數: {self.score}", True, WHITE)
        restart_text = font_small.render("按 R 鍵重新開始", True, GREEN)
        menu_text = font_small.render("按 ESC 離開", True, LIGHT_GRAY)

        # 置中顯示
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 60))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - 10))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 40))
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2,
                                 SCREEN_HEIGHT // 2 + 70))

    def draw_paused(self):
        """繪製暫停畫面"""
        pause_text = font_large.render("暫停", True, WHITE)
        resume_text = font_small.render("按空白鍵繼續", True, GREEN)
        screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2,
                                   SCREEN_HEIGHT // 2 - 30))
        screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + 20))

    def draw_instructions(self):
        """繪製操作說明"""
        inst_text = font_small.render("方向鍵/WASD: 移動 | 空白鍵: 暫停 | R: 重新開始", True, LIGHT_GRAY)
        screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2,
                                 SCREEN_HEIGHT - 30))

    def reset(self):
        """重新開始遊戲"""
        self.snake.reset()
        self.food.spawn()
        self.score = 0
        self.game_over = False
        self.paused = False

    def run(self):
        """遊戲主迴圈"""
        while True:
            self.handle_events()
            self.update()

            # 繪製
            self.draw_background()
            self.food.draw()
            self.snake.draw()
            self.draw_score()
            self.draw_instructions()

            if self.game_over:
                self.draw_game_over()
            elif self.paused:
                self.draw_paused()

            pygame.display.flip()
            clock.tick(self.calculate_fps())


# --- 啟動遊戲 ---
if __name__ == "__main__":
    game = Game()
    game.run()
