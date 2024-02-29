import random

# Map dimensions
width, height = 13, 13

# Create an empty map
map = [[' ' for _ in range(width)] for _ in range(height)]

# Add borders
for i in range(width):
    map[0][i] = map[height - 1][i] = '#'
for i in range(height):
    map[i][0] = map[i][width - 1] = '#'

# Add vertical corridors
for i in range(height):
    if random.random() < 0.4 or i % 2 == 0:  # Every other row
        for j in range(width):
            if random.random() < 0.8 and map[i - 1][j] == ' ':
                map[i][j] = '#'

# Add horizontal connections
for i in range(1, width, 2):  # Every other column, starting from the second
    for _ in range(random.randint(1, 3)):  # 1 to 3 connections
        j = random.randint(0, height - 1)
        map[j][i] = ' '

# Add enemies
for _ in range(random.randint(5, 7)):
    while True:
        i, j = random.randint(0, width - 1), random.randint(0, height - 1)
        if map[j][i] == ' ' and (map[j - 1][i] == '#' or map[j + 1][i] == '#'):  # Only place enemies in empty spaces
            map[j][i] = 'E'
            break

# Place the player
player = next((i, j) for i in range(height - 1, 0, -1) for j in range(width) if map[i][j] == ' ')

map[player[0]][player[1]] = 'P'

# Print the map
for row in map:
    print(''.join(row))
