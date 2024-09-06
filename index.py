import pygame
import sys
import random

# Inicializa o pygame
pygame.init()

# Configurações da tela
screen_width = 600
screen_height = 450
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pacman")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Configurações do Pacman
pacman_size = 30
pacman_speed = 5

# Configurações dos Fantasmas
ghost_size = 25  # Tamanho ajustado dos fantasmas
ghost_speed = 4

# Tamanho dos blocos do labirinto
block_size = 30

def generate_maze(width, height):
    maze = [[1] * width for _ in range(height)]
    stack = [(1, 1)]
    maze[1][1] = 0

    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                if maze[y + dy // 2][x + dx // 2] == 1:
                    neighbors.append((nx, ny))
        
        if neighbors:
            nx, ny = random.choice(neighbors)
            maze[ny][nx] = 0
            maze[ny - (ny - y) // 2][nx - (nx - x) // 2] = 0
            stack.append((nx, ny))
        else:
            stack.pop()

    for x in range(width):
        maze[0][x] = 1
        maze[height-1][x] = 1
    for y in range(height):
        maze[y][0] = 1
        maze[y][width-1] = 1

    return maze

def ensure_accessibility(maze):
    width = len(maze[0])
    height = len(maze)
    
    def is_accessible(start_x, start_y):
        visited = [[False] * width for _ in range(height)]
        stack = [(start_x, start_y)]
        while stack:
            x, y = stack.pop()
            if not (0 <= x < width and 0 <= y < height):
                continue
            if visited[y][x] or maze[y][x] == 1:
                continue
            visited[y][x] = True
            stack.extend([(x + dx, y + dy) for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]])
        return visited
    
    start_x, start_y = 1, 1
    accessible = is_accessible(start_x, start_y)
    
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 0 and not accessible[y][x]:
                maze[y][x] = 1

    return maze

def get_valid_position(exclude_positions=[]):
    while True:
        x = random.randint(1, maze_width - 2) * block_size
        y = random.randint(1, maze_height - 2) * block_size
        if (x, y) not in exclude_positions and labirinto[y // block_size][x // block_size] == 0:
            return x, y

def get_spawn_position():
    while True:
        x = random.randint(1, maze_width - 2) * block_size
        y = random.randint(1, maze_height - 2) * block_size
        if labirinto[y // block_size][x // block_size] == 0:
            return x, y

def check_ghost_collision(pacman_rect):
    for ghost in fantasmas:
        ghost_rect = pygame.Rect(ghost['x'], ghost['y'], ghost_size, ghost_size)
        if pacman_rect.colliderect(ghost_rect):
            return True
    return False

def check_bolinha_collision(pacman_rect):
    global bolinhas
    bolinhas = [bolinha for bolinha in bolinhas if not pacman_rect.colliderect(pygame.Rect(bolinha[0] * block_size, bolinha[1] * block_size, block_size, block_size))]

def check_collision(rect, dx, dy):
    future_rect = rect.move(dx, dy)
    for y, row in enumerate(labirinto):
        for x, cell in enumerate(row):
            if cell == 1:
                wall_rect = pygame.Rect(x * block_size, y * block_size, block_size, block_size)
                if future_rect.colliderect(wall_rect):
                    return True
    return False

def draw_pacman(x, y, size, direction):
    if direction == 'right':
        pacman_image = pygame.image.load('imagens/pacman_right.png')
    elif direction == 'left':
        pacman_image = pygame.image.load('imagens/pacman_left.png')
    elif direction == 'up':
        pacman_image = pygame.image.load('imagens/pacman_up.png')
    elif direction == 'down':
        pacman_image = pygame.image.load('imagens/pacman_down.png')

    pacman_image = pygame.transform.scale(pacman_image, (size, size))
    screen.blit(pacman_image, (x, y))

def draw_ghost(x, y, image):
    ghost_image = pygame.image.load(image)
    ghost_image = pygame.transform.scale(ghost_image, (ghost_size, ghost_size))
    screen.blit(ghost_image, (x, y))

def draw_lives(lives):
    heart_image = pygame.image.load('imagens/heart.png')
    heart_image = pygame.transform.scale(heart_image, (pacman_size, pacman_size))
    
    for i in range(lives):
        screen.blit(heart_image, (10 + i * (pacman_size + 5), 10))

def move_ghost(ghost, pacman_rect):
    directions = ['left', 'right', 'up', 'down']
    
    # Move o fantasma em uma direção aleatória, mas evita mudar para uma direção oposta
    if random.random() < 0.1:
        move = random.choice(directions)
    else:
        pacman_x, pacman_y = pacman_rect.x, pacman_rect.y
        ghost_x, ghost_y = ghost['x'], ghost['y']
        
        if abs(pacman_x - ghost_x) > abs(pacman_y - ghost_y):
            move = 'right' if pacman_x > ghost_x else 'left'
        else:
            move = 'down' if pacman_y > ghost_y else 'up'
    
    new_x, new_y = ghost['x'], ghost['y']
    
    if move == 'left':
        new_x -= ghost_speed
    elif move == 'right':
        new_x += ghost_speed
    elif move == 'up':
        new_y -= ghost_speed
    elif move == 'down':
        new_y += ghost_speed

    # Verifica colisões com paredes
    future_rect = pygame.Rect(new_x, new_y, ghost_size, ghost_size)
    if not check_collision(future_rect, new_x - ghost['x'], new_y - ghost['y']):
        ghost['x'] = new_x
        ghost['y'] = new_y
    else:
        # Tenta uma nova direção se houver colisão com uma parede
        ghost['direction'] = random.choice(directions)

    # Garante que os fantasmas não saiam da tela
    ghost['x'] = max(0, min(screen_width - ghost_size, ghost['x']))
    ghost['y'] = max(0, min(screen_height - ghost_size, ghost['y']))

maze_width = screen_width // block_size
maze_height = screen_height // block_size
labirinto = generate_maze(maze_width, maze_height)
labirinto = ensure_accessibility(labirinto)

bolinhas = [(x, y) for y, row in enumerate(labirinto) for x, cell in enumerate(row) if cell == 0]

ghost_spawn_points = [(2, 2), (maze_width - 3, 2), (2, maze_height - 3), (maze_width - 3, maze_height - 3)]
ghost_images = ['imagens/ghost1.png', 'imagens/ghost2.png', 'imagens/ghost3.png', 'imagens/ghost4.png']
fantasmas = []

for i, spawn in enumerate(ghost_spawn_points):
    x, y = spawn[0] * block_size, spawn[1] * block_size
    while labirinto[y // block_size][x // block_size] != 0:
        x, y = get_spawn_position()
    fantasmas.append({'x': x, 'y': y, 'image': ghost_images[i], 'direction': random.choice(['left', 'right', 'up', 'down'])})

pacman_x, pacman_y = 1 * block_size, 1 * block_size
pacman_direction = 'right'
pacman_rect = pygame.Rect(pacman_x, pacman_y, pacman_size, pacman_size)
lives = 3

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and not check_collision(pacman_rect, -pacman_speed, 0):
        pacman_x -= pacman_speed
        pacman_direction = 'left'
    if keys[pygame.K_RIGHT] and not check_collision(pacman_rect, pacman_speed, 0):
        pacman_x += pacman_speed
        pacman_direction = 'right'
    if keys[pygame.K_UP] and not check_collision(pacman_rect, 0, -pacman_speed):
        pacman_y -= pacman_speed
        pacman_direction = 'up'
    if keys[pygame.K_DOWN] and not check_collision(pacman_rect, 0, pacman_speed):
        pacman_y += pacman_speed
        pacman_direction = 'down'

    pacman_rect.topleft = (pacman_x, pacman_y)
    check_bolinha_collision(pacman_rect)

    if check_ghost_collision(pacman_rect):
        lives -= 1
        if lives <= 0:
            print("Game Over")
            pygame.quit()
            sys.exit()
        pacman_x, pacman_y = 1 * block_size, 1 * block_size
        pacman_rect.topleft = (pacman_x, pacman_y)

    screen.fill(BLACK)
    
    # Desenha o labirinto
    for y, row in enumerate(labirinto):
        for x, cell in enumerate(row):
            if cell == 1:
                pygame.draw.rect(screen, BLUE, (x * block_size, y * block_size, block_size, block_size))

    # Desenha as bolinhas
    for bolinha in bolinhas:
        pygame.draw.circle(screen, WHITE, (bolinha[0] * block_size + block_size // 2, bolinha[1] * block_size + block_size // 2), block_size // 4)

    # Desenha o Pacman
    draw_pacman(pacman_x, pacman_y, pacman_size, pacman_direction)

    # Desenha os fantasmas
    for ghost in fantasmas:
        move_ghost(ghost, pacman_rect)
        draw_ghost(ghost['x'], ghost['y'], ghost['image'])

    # Desenha as vidas
    draw_lives(lives)

    pygame.display.flip()
    clock.tick(30)
