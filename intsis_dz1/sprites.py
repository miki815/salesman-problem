import math
import random

import pygame
import os
import config
import numpy as np


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass


class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]


class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def find_min(self, cur, coin_distance, path):
        min_distance = float('inf')
        for i in range(0, len(coin_distance)):
            if i not in path and coin_distance[cur][i] < min_distance:
                min_distance = coin_distance[cur][i]
        return coin_distance[cur].index(min_distance)

    def get_agent_path(self, coin_distance):
        path = [0]
        next_min = 0
        for i in range(1, len(coin_distance)):
            next_min = self.find_min(next_min, coin_distance, path)
            path.append(next_min)
        return path + [0]


class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)


    def get_agent_path(self, coin_distance):
        pathdict = {"0": 0}
        for i in range(1, len(coin_distance)):
            paths = []
            for path in pathdict:
                paths.append(path)
            for curpath in paths:
                for j in range(1, len(coin_distance)):
                    if not any(int(char) == j for char in curpath):
                        new_key = curpath + str(j)
                        new_cost = pathdict[curpath] + coin_distance[int(curpath[-1])][j]
                        pathdict[new_key] = new_cost
                del pathdict[curpath]
        paths = []
        for path in pathdict:
            paths.append(path)
        for curpath in paths:
            new_key = curpath + str(0)
            new_cost = pathdict[curpath] + coin_distance[int(curpath[-1])][0]
            pathdict[new_key] = new_cost
            del pathdict[curpath]
        mypath = []
        mincost = float('inf')
        for curpath, curcost in pathdict.items():
            if curcost < mincost:
                mincost = curcost
                mypath = curpath
        mypath_array = [int(i) for i in mypath]
        return mypath_array


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def find_candidate(self, pathdict):
        mincost = float('inf')
        minpath = ""
        for path, cost in pathdict.items():
            if cost > mincost:
                continue
            elif cost < mincost or (cost == mincost and len(path) > len(minpath)) or (cost == mincost and len(path) == len(minpath) and int(path[-1]) < int(minpath[-1])):
                mincost = cost
                minpath = path
        return minpath
   

    def get_agent_path(self, coin_distance):
        pathdict = {}
        for i in range(1, len(coin_distance)):
            pathdict["0" + str(i)] = coin_distance[0][i]
        while True:
            candidate = self.find_candidate(pathdict)
            curr = candidate[-1]
            cost = pathdict[candidate]
            if curr == "0":
                mypath = [int(i) for i in candidate]
                return mypath
            elif len(candidate) == len(coin_distance):
                pathdict[candidate + "0"] = cost + coin_distance[0][int(curr)]
            else:
                for i in range(1, len(coin_distance)):
                    if str(i) not in candidate:
                        pathdict[candidate + str(i)] = cost + coin_distance[i][int(curr)]
            del pathdict[candidate]


class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def mst_cost(self, coin_distance):
        in_tree = [0] * len(coin_distance)
        in_tree[0] = 1
        cost = 0
        for iterations in range(0, len(coin_distance) - 1):
            minimum = float('inf')
            selected = 0
            for i in range(0, len(coin_distance)):
                if in_tree[i]:
                    for j in range(0, len(coin_distance)):
                        if(not in_tree[j] and coin_distance[i][j] < minimum):
                            minimum = coin_distance[i][j]
                            selected = j
            cost += minimum
            in_tree[selected] = 1
        return cost


    def find_candidate(self, pathdict):
        mincost = float('inf')
        minpath = ""
        for path, cost in pathdict.items():
            pathcost = cost[0] + cost[1]
            if pathcost > mincost:
                continue
            elif pathcost < mincost or (pathcost == mincost and len(path) > len(minpath)) or (
                    pathcost == mincost and len(path) == len(minpath) and int(path[-1]) < int(minpath[-1])):
                mincost = pathcost
                minpath = path
        return minpath

    def get_agent_path(self, coin_distance):
        pathdict = {}
        mst = self.mst_cost(coin_distance)
        print(mst)
        for i in range(1, len(coin_distance)):
            pathdict["0" + str(i)] = (coin_distance[0][i], mst)
        while True:
            candidate = self.find_candidate(pathdict)
            curr = candidate[-1]
            cost = pathdict[candidate][0]
            if curr == "0":
                mypath = [int(i) for i in candidate]
                return mypath
            elif len(candidate) == len(coin_distance):
                pathdict[candidate + "0"] = (cost + coin_distance[0][int(curr)], 0)
            else:
                mst_matrix = np.array(coin_distance)
                delete_keys = []
                for m in range(1, len(candidate)):
                    delete_keys.append(int(candidate[m]))
                mst_matrix = np.delete(mst_matrix, delete_keys, axis=0)
                mst_matrix = np.delete(mst_matrix, delete_keys, axis=1)
                mst = self.mst_cost(mst_matrix)
                for i in range(1, len(coin_distance)):
                    if str(i) not in candidate:
                        pathdict[candidate + str(i)] = (cost + coin_distance[i][int(curr)], mst)
            del pathdict[candidate]








