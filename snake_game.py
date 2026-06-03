import pygame
import random
import sys

pygame.init()

W, H = 600, 400
CELL = 20
FPS = 12

WHITE = (255,255,255)
GREEN = (0,200,0)
DARK_GREEN = (0,150,0)
RED = (200,0,0)
GRAY = (200,200,200)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

def reset():
    return [(W//2, H//2)], [(W//2 + CELL, H//2)], (CELL, 0), 0, True

snake, food, direction, score, running = reset()

def new_food():
    while True:
        pos = (random.randint(0, (W-CELL)//CELL) * CELL,
               random.randint(0, (H-CELL)//CELL) * CELL)
        if pos not in snake:
            return pos

food = new_food()

while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if e.type == pygame.KEYDOWN:
            if running and e.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                if e.key == pygame.K_UP and direction != (0, CELL): direction = (0, -CELL)
                elif e.key == pygame.K_DOWN and direction != (0, -CELL): direction = (0, CELL)
                elif e.key == pygame.K_LEFT and direction != (CELL, 0): direction = (-CELL, 0)
                elif e.key == pygame.K_RIGHT and direction != (-CELL, 0): direction = (CELL, 0)
            if not running and e.key == pygame.K_r:
                snake, food, direction, score, running = reset()
                food = new_food()
            if e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    if running:
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        if head[0] < 0 or head[0] >= W or head[1] < 0 or head[1] >= H or head in snake:
            running = False
        else:
            snake = [head] + snake
            if head == food:
                score += 1
                food = new_food()
            else:
                snake.pop()

    screen.fill(WHITE)
    for i, seg in enumerate(snake):
        color = GREEN if i == 0 else DARK_GREEN
        pygame.draw.rect(screen, color, (*seg, CELL-2, CELL-2), border_radius=4)
    pygame.draw.rect(screen, RED, (*food, CELL-2, CELL-2), border_radius=4)

    # Grid
    for x in range(0, W, CELL):
        pygame.draw.line(screen, GRAY, (x,0), (x,H))
    for y in range(0, H, CELL):
        pygame.draw.line(screen, GRAY, (0,y), (W,y))

    score_txt = font.render(f"Score: {score}", True, (0,0,0))
    screen.blit(score_txt, (10, 5))

    if not running:
        go_txt = font.render("Game Over! Press R to Restart", True, RED)
        screen.blit(go_txt, (W//2 - go_txt.get_width()//2, H//2 - 20))

    pygame.display.flip()
    clock.tick(FPS)