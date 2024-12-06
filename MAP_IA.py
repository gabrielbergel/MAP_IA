import pygame
import random
import numpy as np
import math

pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 800  
GRID_SIZE = 40  
ROWS = (HEIGHT // GRID_SIZE) - 1  
COLS = (WIDTH // GRID_SIZE) - 1 

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mapa")

WHITE = (255, 255, 255)  # Rua (atualizada pra cores por conta do trafego)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)  # Tráfego leve
ORANGE = (255, 165, 0)  # Tráfego médio
RED = (255, 0, 0)  # Tráfego pesado
BLACK = (0, 0, 0)
CAR_COLOR = (BLUE) 
INTERSECTION_YELLOW = (255, 255, 0)  
INTERSECTION_GRAY = (169, 169, 169) 

NUM_CARS = 5
CAR_SIZE = GRID_SIZE // 2 

map_grid = [[1 for _ in range(COLS)] for _ in range(ROWS)]
traffic_grid = [[WHITE for _ in range(COLS)] for _ in range(ROWS)] 

def generate_blocks():
    for y in range(1, ROWS - 1, 3):  
        for x in range(1, COLS - 1, 3): 
            # Marca as células da quadra como 0 (bloqueadas)
            map_grid[y][x] = 0
            map_grid[y][x + 1] = 0
            map_grid[y + 1][x] = 0
            map_grid[y + 1][x + 1] = 0

    for i in range(COLS):  
        map_grid[ROWS - 1][i] = 1
    for i in range(ROWS):
        map_grid[i][COLS - 1] = 1

    map_grid[ROWS - 1][COLS - 1] = 1

generate_blocks()

def generate_traffic():
    for y in range(ROWS):
        for x in range(COLS):
            if map_grid[y][x] == 1:  # Apenas nas ruas
                rand = random.randint(1, 100)
                if rand <= 70:
                    traffic_grid[y][x] = GREEN
                elif rand <= 90:
                    traffic_grid[y][x] = ORANGE
                else:
                    traffic_grid[y][x] = RED

generate_traffic()

def create_car():
    return {
        "x": 0,
        "y": 0,
        "dir": "RIGHT",
        "color": CAR_COLOR,
        "prev_pos": None,
        "path": [],
        "q_table": np.random.uniform(size=(ROWS, COLS, 4)),
        "epsilon": 0.1,
        "alpha": 0.1,
        "gamma": 0.9,
        "score": 0,
        "last_distance": float('inf'),
        "wait_time": 0 
    }

cars = [create_car() for _ in range(NUM_CARS)]

start_point = None
end_point = None
car_moving = False

def draw_map():
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            if is_intersection(x, y):
                draw_gray_stripes(x, y)
            else:
                color = traffic_grid[y][x] if map_grid[y][x] == 1 else BLACK
                pygame.draw.rect(screen, color, rect)

            pygame.draw.rect(screen, BLACK, rect, 1)

            if start_point and (x, y) == start_point:
                pygame.draw.rect(screen, (0, 255, 0), rect)
            if end_point and (x, y) == end_point:
                pygame.draw.rect(screen, (255, 0, 255), rect)

def is_intersection(x, y):
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    road_count = 0

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS and map_grid[ny][nx] == 1:
            road_count += 1

    return road_count >= 3

def draw_gray_stripes(x, y):
    num_lines = 4 
    line_thickness = GRID_SIZE // (num_lines * 2)  

    for i in range(num_lines):
        stripe_y = y * GRID_SIZE + (i * line_thickness * 2) + line_thickness // 2
        if i % 2 == 0:
            pygame.draw.rect(screen, INTERSECTION_YELLOW, (x * GRID_SIZE, stripe_y, GRID_SIZE, line_thickness))
        else:
            pygame.draw.rect(screen, INTERSECTION_GRAY, (x * GRID_SIZE, stripe_y, GRID_SIZE, line_thickness))

def calcular_distancia(car):
    return math.sqrt((end_point[0] - car["x"])**2 + (end_point[1] - car["y"])**2)

def move_car(car):
    if car["wait_time"] > 0:
        car["wait_time"] -= 1
        return

    # Verifique se end_point está definido
    if end_point is None:
        return  # Não faça nada se não houver um ponto final

    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    state = (car["y"], car["x"])
    action = actions[np.argmax(car["q_table"][state])]

    dx, dy = 0, 0
    if action == "UP":
        dy = -1
    elif action == "DOWN":
        dy = 1
    elif action == "LEFT":
        dx = -1
    elif action == "RIGHT":
        dx = 1

    new_x = car["x"] + dx
    new_y = car["y"] + dy

    if 0 <= new_x < COLS and 0 <= new_y < ROWS and map_grid[new_y][new_x] == 1 and (new_x, new_y) != car["prev_pos"]:
        car["prev_pos"] = (car["x"], car["y"])
        car["x"], car["y"] = new_x, new_y
        car["path"].append((new_x, new_y))

        current_distance = calcular_distancia(car)
        reward = 0

        # Recompensa por se mover em direção ao ponto final
        if current_distance < car["last_distance"]:
            reward = 1  # Recompensa positiva
        elif current_distance > car["last_distance"]:
            reward = -1  # Penalidade por se afastar

        if traffic_grid[new_y][new_x] == ORANGE:
            car["wait_time"] = 30  # Espera 1 segundo
            reward = -5  # Penalidade vermelho
        elif traffic_grid[new_y][new_x] == RED:
            car["wait_time"] = 60  # Espera 2 segundos
            reward = -10  # Penalidade laranja

        car["last_distance"] = current_distance
        update_q_table(car, state, action, reward)
        choose_new_direction(car)
    else:
        reward = -1
        update_q_table(car, state, action, reward)
        choose_new_direction(car)

def update_q_table(car, state, action, reward):
    actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    action_index = actions.index(action)
    next_state = (car["y"], car["x"])
    best_next_action = np.max(car["q_table"][next_state])
    
    car["q_table"][state][action_index] += car["alpha"] * (reward + car["gamma"] * best_next_action - car["q_table"][state][action_index])

def choose_new_direction(car):
    directions = ["UP", "DOWN", "LEFT", "RIGHT"]
    random.shuffle(directions)

    valid_directions = []
    for dir in directions:
        dx, dy = 0, 0
        if dir == "UP":
            dy = -1
        elif dir == "DOWN":
            dy = 1
        elif dir == "LEFT":
            dx = -1
        elif dir == "RIGHT":
            dx = 1

        new_x = car["x"] + dx
        new_y = car["y"] + dy

        if 0 <= new_x < COLS and 0 <= new_y < ROWS and map_grid[new_y][new_x] == 1 and (new_x, new_y) != car["prev_pos"]:
            valid_directions.append(dir)

    if len(valid_directions) >= 3:
        valid_directions = [dir for dir in valid_directions if dir != opposite_direction(car["dir"])]
        if valid_directions:
            car["dir"] = random.choice(valid_directions)
    elif valid_directions:
        car["dir"] = valid_directions[0]

def opposite_direction(direction):
    opposites = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT"
    }
    return opposites[direction]

def draw_cars():
    for car in cars:
        x = car["x"] * GRID_SIZE + GRID_SIZE // 4
        y = car["y"] * GRID_SIZE + GRID_SIZE // 4
        pygame.draw.rect(screen, car["color"], pygame.Rect(x, y, CAR_SIZE, CAR_SIZE))

def run_game():
    global start_point, end_point, car_moving
    
    running = True
    while running:
        screen.fill(BLACK)
        draw_map()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                grid_x, grid_y = x // GRID_SIZE, y // GRID_SIZE

                if not start_point:
                    start_point = (grid_x, grid_y)
                    for car in cars:
                        car["x"], car["y"] = grid_x, grid_y
                elif not end_point:
                    end_point = (grid_x, grid_y)
                    car_moving = True

        if car_moving and start_point and end_point:
            for car in cars:
                move_car(car)

                if (car["x"], car["y"]) == end_point:
                    print("Caminho encontrado:", car["path"])
                    car["score"] += 1
                    start_point = None
                    end_point = None
                    car_moving = False
                    reset_cars()

        draw_cars()
        pygame.display.flip()
        pygame.time.Clock().tick(30)

def reset_cars():
    for car in cars:
        car["x"] = 0
        car["y"] = 0
        car["dir"] = "RIGHT"
        car["prev_pos"] = None
        car["path"] = []
        car["last_distance"] = float('inf')
        car["wait_time"] = 0

run_game()
pygame.quit()
