#!/usr/bin/env python

import random
import math
import pygame as pg
import os

tile_width = 12
tile_height = 12
scale = 4

up = 0
left = 1
down = 2
right = 3
empty = 4
vert = 5
horiz = 6

tiles = [
    pg.image.load(os.path.join('tiles', 'up.png')),
    pg.image.load(os.path.join('tiles', 'left.png')),
    pg.image.load(os.path.join('tiles', 'down.png')),
    pg.image.load(os.path.join('tiles', 'right.png')),
    pg.image.load(os.path.join('tiles', 'empty.png')),
    pg.image.load(os.path.join('tiles', 'vert.png')),
    pg.image.load(os.path.join('tiles', 'horiz.png')),
]
for i in range(len(tiles)):
    tiles[i] = pg.transform.scale(tiles[i], (tile_width * scale, tile_height * scale))

adj = [[]] * 7

adj[up] = [[]] * 4
adj[up][up] = (right, down, left, vert)
adj[up][left] = (right, down, up, horiz)
adj[up][down] = (down, empty, horiz)
adj[up][right] = (down, left, up, horiz)

adj[left] = [[]] * 4
adj[left][up] = (right, down, left, vert)
adj[left][left] = (right, up, down, horiz)
adj[left][down] = (up, left, right, vert)
adj[left][right] = (right, empty, vert)

adj[down] = [[]] * 4
adj[down][up] = (up, empty, horiz)
adj[down][left] = (down, up, right, horiz)
adj[down][down] = (right, left, up, vert)
adj[down][right] = (down, up, left, horiz)

adj[right] = [[]] * 4
adj[right][up] = (right, down, left, vert)
adj[right][left] = (left, empty, vert)
adj[right][down] = (up, left, right, vert)
adj[right][right] = (up, down, left, horiz)

adj[empty] = [[]] * 4
adj[empty][up] = (up, empty, horiz)
adj[empty][left] = (left, empty, vert)
adj[empty][down] = (down, empty, horiz)
adj[empty][right] = (right, empty, vert)

adj[vert] = [[]] * 4
adj[vert][up] = (down, left, right, vert)
adj[vert][left] = (empty, left)
adj[vert][down] = (up, left, right, vert)
adj[vert][right] = (empty, right)

adj[horiz] = [[]] * 4
adj[horiz][up] = (empty, up)
adj[horiz][left] = (up, down, right)
adj[horiz][down] = (empty, down)
adj[horiz][right] = (up, down, left)

width = 10
height = 10

WINSIZE = [
    width * tile_width * scale,
    height * tile_height * scale,
]

def main():
    random.seed()
    clock = pg.time.Clock()
    pg.init()
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("wave function collapse")

    black = 20, 20, 40
    screen.fill(black)

    grid = init_grid()
    print_grid(grid)

    finished = False

    done = False
    while not done:
        if not finished:
            screen.fill(black)

        finished = not collapse(grid)

        # render grid
        for x in range(width):
            for y in range(height):
                tile = get_tile(grid[x][y])
                if tile != -1:
                    screen.blit(tiles[tile], (x * tile_width * scale, y * tile_height * scale))

        pg.display.update()

        for e in pg.event.get():
            if e.type == pg.QUIT or (e.type == pg.KEYUP and (e.key == pg.K_ESCAPE or e.key == pg.K_q)):
                done = True
                break
            elif e.type == pg.KEYUP and e.key == pg.K_p:
                print_grid(grid)
            elif e.type == pg.KEYUP and e.key == pg.K_c:
                collapse(grid)
            elif e.type == pg.KEYUP and e.key == pg.K_r:
                grid = init_grid()
                finished = False

        if finished:
            clock.tick(10)
    pg.quit()

def get_tile(tile):
    index = -1
    for (i, t) in enumerate(tile):
        if t and index != -1:
            return -1
        elif t:
            index = i
    return index

def find_lowest_entropy(grid):
    lcoords = []
    le = 2 ** 32
    for x in range(width):
        for y in range(height):
            e = sum(grid[x][y])
            if e <= 1:
                continue

            if e < le:
                le = e
                lcoords.clear()

            if e <= le:
                lcoords.append((x, y))

    if le == 2 ** 32:
        return None
    return (*random.choice(lcoords), le)

def get_valid_tiles(tile):
    tiles = []
    for (i, t) in enumerate(tile):
        if t:
            tiles.append(i)
    return tiles

def collapse_random_tile(tile):
    return random.choice(get_valid_tiles(tile))

def set_tiles(*indices):
    return [i in indices for i in range(len(tiles))]

def collapse(grid):
    tile = find_lowest_entropy(grid)
    if tile is None:
        return False

    x, y, entropy = tile
    collapsed = collapse_random_tile(grid[x][y])
    print(f"Collapsing {x}-{y} to {collapsed} e={entropy}")
    print(set_tiles(collapsed))
    grid[x][y] = set_tiles(collapsed)
    propagate(grid)

    return True

def init_grid():
    # init
    grid = []
    for i in range(width):
        grid.append([])
        for j in range(height):
            grid[i].append([True] * len(tiles))

    print(grid)

    start_x = random.randrange(width)
    start_y = random.randrange(height)

    # collapse random tile
    grid[start_x][start_y] = [True] + [False] * (len(tiles) - 1)
    propagate(grid)
    return grid

def propagate(grid):
    #old_grid = copy.deepcopy(grid)
    old_grid = grid

    # propagate changes
    while True:
        prop = False
        for x in range(width):
            for y in range(height):
                valid_tiles = get_valid_tiles(old_grid[x][y])
                if len(valid_tiles) > 1:
                    continue
                if len(valid_tiles) == 0:
                    print("warn: Zero entropy")
                    continue

                tile = valid_tiles[0]

                # up
                if y - 1 >= 0 and sum(old_grid[x][y - 1]) > 1:
                    for i in range(len(tiles)):
                        if i not in adj[tile][up] and grid[x][y - 1][i]:
                            grid[x][y - 1][i] = False
                            prop = True
                # left
                if x - 1 >= 0 and sum(old_grid[x - 1][y]) > 1:
                    for i in range(len(tiles)):
                        if i not in adj[tile][left] and grid[x - 1][y][i]:
                            grid[x - 1][y][i] = False
                            prop = True
                # down
                if y + 1 < height and sum(old_grid[x][y + 1]) > 1:
                    for i in range(len(tiles)):
                        if i not in adj[tile][down] and grid[x][y + 1][i]:
                            grid[x][y + 1][i] = False
                            prop = True
                # right
                if x + 1 < width and sum(old_grid[x + 1][y]) > 1:
                    for i in range(len(tiles)):
                        if i not in adj[tile][right] and grid[x + 1][y][i]:
                            grid[x + 1][y][i] = False
                            prop = True

        if not prop:
            break

def print_grid(grid):
    print()
    print()
    print()
    print("---" + "----------" * width)
    for y in range(height):
        print(" | ", end="")
        for x in range(width):
            print(*map(int, grid[x][y]), end=" | ")
        print()
        print("---" + "----------" * width)

if __name__ == "__main__":
    main()
