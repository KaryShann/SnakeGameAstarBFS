import pygame
import random
from queue import PriorityQueue
import csv
from datetime import datetime

# Constants
GRID_SIZE = 50
BLOCK_SIZE = 10
WINDOW_SIZE = (GRID_SIZE * BLOCK_SIZE, GRID_SIZE * BLOCK_SIZE)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
#GAME_SEED = randint()

# Snake class
class Snake:
    def __init__(self, color, start_pos):
        self.color = color
        self.positions = [start_pos]
        self.direction = (0, 0)
        self.score = 0

    def move(self, direction):
        self.direction = direction
        head = self.positions[0]
        new_head = (head[0] + direction[0], head[1] + direction[1])
        self.positions.insert(0, new_head)
        if len(self.positions) > self.score + 1:
            self.positions.pop()

    def grow(self):
        self.score += 1

    def draw(self, screen):
        for i, pos in enumerate(self.positions):
            if i == 0:  # Head
                pygame.draw.circle(screen, self.color, (pos[0] * BLOCK_SIZE + BLOCK_SIZE // 2, pos[1] * BLOCK_SIZE + BLOCK_SIZE // 2), BLOCK_SIZE // 2)
            elif i == len(self.positions) - 1:  # Tail
                pygame.draw.polygon(screen, self.color, [
                    (pos[0] * BLOCK_SIZE + BLOCK_SIZE // 4, pos[1] * BLOCK_SIZE + BLOCK_SIZE // 4),
                    (pos[0] * BLOCK_SIZE + BLOCK_SIZE // 4, pos[1] * BLOCK_SIZE + BLOCK_SIZE * 3 // 4),
                    (pos[0] * BLOCK_SIZE + BLOCK_SIZE * 3 // 4, pos[1] * BLOCK_SIZE + BLOCK_SIZE // 2)
                ])
            else:  # Body
                pygame.draw.rect(screen, self.color, (pos[0] * BLOCK_SIZE, pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

# A* algorithm
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(snake, apple, obstacles):
    start = snake.positions[0]
    goal = apple
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not open_set.empty():
        current = open_set.get()[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_pos = (current[0] + neighbor[0], current[1] + neighbor[1])
            if next_pos[0] < 0 or next_pos[0] >= GRID_SIZE or next_pos[1] < 0 or next_pos[1] >= GRID_SIZE:
                continue
            if next_pos in snake.positions or next_pos in obstacles:
                continue

            tentative_g_score = g_score[current] + 1
            if next_pos not in g_score or tentative_g_score < g_score[next_pos]:
                came_from[next_pos] = current
                g_score[next_pos] = tentative_g_score
                f_score[next_pos] = tentative_g_score + heuristic(next_pos, goal)
                open_set.put((f_score[next_pos], next_pos))

    return []

# BFS algorithm
def bfs(snake, apple, obstacles):
    start = snake.positions[0]
    goal = apple
    queue = [start]
    visited = set()
    came_from = {}

    while queue:
        current = queue.pop(0)
        visited.add(current)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            next_pos = (current[0] + neighbor[0], current[1] + neighbor[1])
            if next_pos[0] < 0 or next_pos[0] >= GRID_SIZE or next_pos[1] < 0 or next_pos[1] >= GRID_SIZE:
                continue
            if next_pos in snake.positions or next_pos in obstacles or next_pos in visited:
                continue

            queue.append(next_pos)
            visited.add(next_pos)
            came_from[next_pos] = current

    return []

# Game loop
def game_loop():
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Dual Snake Game")
    clock = pygame.time.Clock()

    # Initialize snakes
    start_pos = (GRID_SIZE // 2, GRID_SIZE // 2)
    red_snake = Snake(RED, start_pos)
    blue_snake = Snake(BLUE, start_pos)

    # Initialize start positions
    red_start_pos = start_pos
    blue_start_pos = start_pos

    # Generate obstacles
    num_obstacles = random.randint(5, 10)
    obstacles = set()
    while len(obstacles) < num_obstacles:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) != start_pos:
            obstacles.add((x, y))

    # Generate initial apple
    apple = None
    while apple is None:
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        if (x, y) != start_pos and (x, y) not in obstacles:
            apple = (x, y)

    # Initialize game data
    game_start_time = datetime.now().strftime("%y%m%d%H%M%S%f")[:15]
    game_time = round(datetime.now().timestamp() * 1000,0)
    red_turns = 0
    blue_turns = 0

    running = True
    while running:


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move snakes
        red_path = astar(red_snake, apple, obstacles)
        if red_path:
            red_direction = (red_path[0][0] - red_snake.positions[0][0], red_path[0][1] - red_snake.positions[0][1])
            red_snake.move(red_direction)
            red_turns += 1

        blue_path = bfs(blue_snake, apple, obstacles)
        if blue_path:
            blue_direction = (blue_path[0][0] - blue_snake.positions[0][0], blue_path[0][1] - blue_snake.positions[0][1])
            blue_snake.move(blue_direction)
            blue_turns += 1

        # Check if snakes reached the apple
        red_reached_apple = red_snake.positions[0] == apple
        blue_reached_apple = blue_snake.positions[0] == apple

        if red_reached_apple or blue_reached_apple:

            next_time = round(datetime.now().timestamp()*1000,0)
            eat_time = next_time - game_time  #datetime.now().strftime("%y%m%d%H%M%S%f")[:15]
            #print(next_time, game_time)
            game_time = next_time

            if red_reached_apple:
                red_snake.grow()
                red_data = [game_start_time, "astar", eat_time, red_turns, red_start_pos[0], red_start_pos[1], apple[0], apple[1]]
                with open("game_data.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(red_data)
                red_turns = 0
                red_start_pos = red_snake.positions[0]  # Update red start position

            if blue_reached_apple:
                blue_snake.grow()
                blue_data = [game_start_time, "bfs", eat_time, blue_turns, blue_start_pos[0], blue_start_pos[1], apple[0], apple[1]]
                with open("game_data.csv", "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(blue_data)
                blue_turns = 0
                blue_start_pos = blue_snake.positions[0]  # Update blue start position

            apple = None

        # Generate new apple if needed
        if apple is None:
            while apple is None:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                if (x, y) not in red_snake.positions and (x, y) not in blue_snake.positions and (x, y) not in obstacles:
                    apple = (x, y)

        # Check for collisions
        if red_snake.positions[0] in obstacles or red_snake.positions[0] in red_snake.positions[1:]:
            running = False
        if blue_snake.positions[0] in obstacles or blue_snake.positions[0] in blue_snake.positions[1:]:
            running = False

        # Draw game objects
        screen.fill(BLACK)
        red_snake.draw(screen)
        blue_snake.draw(screen)
        for obstacle in obstacles:
            pygame.draw.rect(screen, WHITE, (obstacle[0] * BLOCK_SIZE, obstacle[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(screen, GREEN, (apple[0] * BLOCK_SIZE, apple[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        # Draw scores
        font = pygame.font.Font(None, 36)
        red_score_text = font.render(f"Red: {red_snake.score}", True, RED)
        blue_score_text = font.render(f"Blue: {blue_snake.score}", True, BLUE)
        screen.blit(red_score_text, (WINDOW_SIZE[0] - 100, 10))
        screen.blit(blue_score_text, (10, 10))

        pygame.display.flip()

        if red_reached_apple and not blue_reached_apple:
            clock.tick(1)
        if not red_reached_apple and blue_reached_apple:
            clock.tick(1)
        else:
            clock.tick(2000)

    pygame.quit()

# Run the game
game_loop()