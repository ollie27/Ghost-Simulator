import json
import os.path

import pygame

from gslib import graphics
from gslib import character
from gslib.constants import *
import gslib.character_objects as character_objects

def test():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((800, 800))
    m = Map(os.path.join(TILE_DIR, 'martin.png'), os.path.join(TILE_DIR, 'martin.json'))

    surf = graphics.draw_map(m)

    screen.blit(surf, (0, 0))

    pygame.display.update()
    raw_input()
    pygame.quit()

def open_map_json(map_filename):
    try:
        f = open(map_filename, 'r')
        data = json.load(f)
        f.close()
    except IOError:
        print "Couldn't open map file \"" + map_filename + "\"."

    return data

def load_map(map_filename): # Load a map and objects from a map file
    data = open_map_json(map_filename)

    width = data['tileswide']
    height = data['tileshigh']

    # Use the last "tiles" layer to get the tile map -- in the future will need to get more layers
    all_layers = [item for item in data['layers'] if "tiles" in item]

    for l in all_layers:
        if l['name'] == 'background':
            tile_map = l['tiles']
        elif l['name'] == 'collision':
            coll_map = l['tiles']

    map_grid = [[0 for i in range(height)] for j in range(width)]
    coll_grid = [[0 for i in range(height)] for j in range(width)]

    for tile in tile_map:
        x = tile['x']
        y = tile['y']
        map_grid[x][y] = tile['tile']

    for tile in coll_map:
        x = tile['x']
        y = tile['y']
        coll_grid[x][y] = tile['tile']

    return map_grid, coll_grid


def load_objects(map_filename):
    data = open_map_json(map_filename)
    try:
        obj_list = data['layers'][1]['objects']
    except:
        obj_list = []
        print "Couldn't load any objects from map file \"" + map_filename + "\"."
    return obj_list


class Tile(object):
    def __init__(self, tile_type_grid, coll_grid, map, pos):
        tile_ref = tile_type_grid[pos[0]][pos[1]]
        if tile_ref != -1:
            self.tileset_coord = (tile_ref % map.tileset_cols, tile_ref / map.tileset_cols)
        else:
            self.tileset_coord = (0, 0)

        self.tileset_area = (self.tileset_coord[0] * TILE_SIZE, self.tileset_coord[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.walkable = True
        self.tile_ref = tile_ref
        self.rect = pygame.Rect((pos[0] * TILE_SIZE, pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

        if coll_grid:
            if coll_grid[pos[0]][pos[1]] == 1330:
                self.walkable = False
        else:
            if self.tile_ref in map.unwalkable:
                self.walkable = False


class Map(object):
    def __init__(self, tileset, map_file, game_class):
        self.tileset = pygame.image.load(tileset).convert()
        self.tileset_cols = self.tileset.get_width() / TILE_SIZE

        tile_type_grid, coll_grid = load_map(map_file)
        self.grid = [[Tile(tile_type_grid, coll_grid, self, (i, j)) for j in range(len(tile_type_grid[0]))] for i in range(len(tile_type_grid))]

        loaded_objects = load_objects(map_file) # gives a list of dicts, each dict associated with an object from the map
        
        self.objects = []

        for i in range(4):
            self.objects.append(character.Character(game_class, 100, 100, 16, 16, character.gen_character()))

        self.objects[0].normal_speed = 0
        self.objects[1].collision_weight = 5
        self.objects[1].coord = (150, 100)
        self.objects[2].collision_weight = 2
        self.objects[2].normal_speed = 0
        self.objects[2].coord = (200, 100)
        self.objects[3].collision_weight = 4
        self.objects[3].normal_speed = 0
        self.objects[3].coord = (250, 100)

        self.objects.append(character_objects.SmallDoor(game_class, TILE_SIZE*7, TILE_SIZE*7, character.gen_character()))

        for o_dict in loaded_objects:
            #if o_dict['object_type']=="hat":
                #self.objects.append(character.Character(game_class, o_dict['x'], o_dict['y'], 16, 16, character.gen_character()))
            self.create_object_from_dict(o_dict, game_class)

    def create_object_from_dict(self, d, game_class):
        if d['object_type'] == "character":
            try:
                self.objects.append(character.Character(game_class, d['x'], d['y'], d['sprite_w'], d['sprite_h'], character.gen_character(), sprite_sheet=d['sprite_sheet']))
            except:
                print "Couldn't create an object from map file"



if __name__ == '__main__':
    test()
