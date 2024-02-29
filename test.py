import random

def initialize_layout(width, height):
    return [[' ' for _ in range(width)] for _ in range(height)]

def set_boundaries(layout, width, height):
    for i in range(width):
        layout[0][i] = layout[height - 1][i] = '#'
    for i in range(height):
        layout[i][0] = layout[i][width - 1] = '#'

def set_player(layout, width, height):
    player = next((i, j) for i in range(height - 1, 0, -1) for j in range(width) if layout[i][j] == ' ' and layout[i][j + 1] == ' ')
    layout[player[0]][player[1]] = 'P'

def set_random_elements(layout, width, height):
    for _ in range(random.randint(5, 7)):
        while True:
            i, j = random.randint(0, width - 1), random.randint(0, height - 1)
            if layout[i][j] == ' ' and layout[i - 1][j] == '#' and layout[i][j - 2] != 'P':
                layout[i][j] = random.choice(['1', '2', '3'])
                break

def print_layout(layout):
    for row in layout:
        print(''.join(row))

def main():
    width, height = 17, 17
    layout = initialize_layout(width, height)

    for i in range(height - 1, 0, -1):
        if i % 2 == 0:
            for j in range(width):
                layout[i][j] = '#'
            while True:
                vertical = random.randint(1, width - 2)
                if layout[i - 1][vertical] == ' ':
                    layout[i][vertical] = ' '
                    break
        else:
            for j in range(random.randint(0, int(width/4))):
                if layout[i - 1][j] == ' ':
                    break
                layout[i][j] = '#'
            for j in range(random.randint(int(width/(4/3)), width), width):
                if layout[i - 1][j] == ' ':
                    break
                layout[i][j] = '#'

    set_boundaries(layout, width, height)
    set_player(layout, width, height)
    set_random_elements(layout, width, height)
    print_layout(layout)

if __name__ == "__main__":
    main()

