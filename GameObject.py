from Constants import *
import pygame

class GameObject(object):
    def __init__(self, game_class, x, y, w, h):
        self.game_class = game_class

        self.coord = (x,y)  # top left
        self.dimensions = (w,h)
        self.velocity = (0,0)
        self.max_velocity = 1
        self.fear_radius = 50
        self.feared_by = []
        self.fears = []
        self.sprite = None
        self.frameRect = None
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.update_timer = 0
        self.fear_timer = 0

    def update(self):
        self.move()
        self.rect = pygame.Rect(self.coord, self.dimensions)
        self.apply_fear()

    def apply_fear(self):
        for o in self.game_class.objects:
            if o is not self:
                for f in self.fears:
                    if f in o.feared_by:
                        if (o.coord[0] - self.coord[0])**2 + (o.coord[1] - self.coord[1])**2 < self.fear_radius**2:
                            o.fear_timer = 5
                            self.game_class.player1.fear += 100


    def move(self):
        pro_pos = (self.coord[0] + self.velocity[0], self.coord[1] + self.velocity[1])
        if pro_pos[0] >= 0 and pro_pos[0] + self.dimensions[0] <= LEVEL_WIDTH and \
                pro_pos[1] >= 0 and pro_pos[1] + self.dimensions[1] <= LEVEL_HEIGHT:
            self.coord = pro_pos

        # begin collision detection NOTE: assumes largest object w/ collision is 64x64 (i.e. 2x2 tiles)

        if pro_pos[0] > 0 and pro_pos[1] > 0:
            i = pro_pos[0]/TILE_SIZE  # get the index of the upper right tile
            j = pro_pos[1]/TILE_SIZE
        else:
            i = 0
            j = 0

        #check collision against the 9 possible tiles surrounding object
        collision = False

        for ni in range(i, i+2):
            for nj in range(j, j+2):
                if ni > 0 and ni < LEVEL_WIDTH/TILE_SIZE and nj > 0 and nj < LEVEL_HEIGHT/TILE_SIZE:
                    if not self.game_class.map.grid[ni][nj].walkable:
                        if self.rect.colliderect(self.game_class.map.grid[ni][nj].rect):
                            collision = True

        #end collision detection
        if not collision:
            self.coord = pro_pos

        x, y = pro_pos
    
        if self.velocity[0] < 0:
            if self.coord[0] + self.velocity[0] <= 0:
                x = 0
        elif self.velocity[0] > 0:
            if self.coord[0] + self.dimensions[0] + self.velocity[0] >= LEVEL_WIDTH:
                x = LEVEL_WIDTH - self.dimensions[0]
        if self.velocity[1] < 0:
            if self.coord[1] + self.velocity[1] <= 0:
                y = 0
        elif self.velocity[1] > 0:
            if self.coord[1] + self.dimensions[1] + self.velocity[1] >= LEVEL_HEIGHT:
                y = LEVEL_HEIGHT - self.dimensions[1]

        self.coord = x, y