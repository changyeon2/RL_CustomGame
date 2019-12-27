import pygame, random, sys, math, gym

width, height = 1000, 600

class Env:
    global width, height

    def random_coordinate(self):
        return random.randrange(100, width - 100), random.randrange(100, height - 100)

    def __init__(self):
        self.stage = 1
        self.stage_clear = True
        self.enemies_num = 2
        self.pikachu_num = 0
        self.pingu_num = 0
        self.Step = 1
        self.size = width, height
        self.action_space = gym.spaces.Discrete(4)
        #self.screen = pygame.display.set_mode(self.size)
        self.screen = pygame.Surface(self.size)
        self.color = 255, 255, 255
        xcor, ycor = self.random_coordinate()
        self.hero = archer(xcor, ycor)
        self.enemies_list = pygame.sprite.Group()
        self.done = False
        self.info = "continuing"

        pygame.init()
        pygame.display.set_caption("Legend of Archer")

        print("################### Game Start ###################")

    def draw(self):
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(self.color)
        #self.screen.blit(pygame.transform.scale(pygame.image.load("mountain.png").convert(), (width, height))
        self.screen.blit(self.hero.image, (self.hero.rect.centerx, self.hero.rect.centery))

        for arrow in self.hero.arrow:
            self.screen.blit(arrow.image, (arrow.rect.centerx, arrow.rect.centery))

        for enemy in self.enemies_list:
            if enemy.hp <= 0:
                continue
            self.screen.blit(enemy.image, (enemy.rect.centerx, enemy.rect.centery))
            for weapon in enemy.weapon_list:
                self.screen.blit(weapon.image, (weapon.rect.centerx, weapon.rect.centery))
        return

    def render(self):
        pygame.display.flip()
        self.screen = pygame.Surface(self.size)

    def get_reward(self):
        if (self.enemies_num == 0):
            return 30
        elif self.hero.hp <= 0:
            return -10
        else:
            return 0.05

    def update(self, action):
        # len(enemies_list) == 0 <=> stage_clear
        if self.stage_clear == True:
            self.hero.arrow = pygame.sprite.Group()
            self.pikachu_num = random.randrange(0, self.enemies_num)
            self.pingu_num = self.enemies_num - self.pikachu_num

            for i in range(0, self.pikachu_num):
                xcor, ycor = self.random_coordinate()
                self.enemies_list.add(enemies(xcor, ycor, "pikachu"))

            for j in range(0, self.pingu_num):
                xcor, ycor = self.random_coordinate()
                self.enemies_list.add(enemies(xcor, ycor, "pingu"))

            self.stage_clear = False

        for arrow in self.hero.arrow:
            if len(self.enemies_list) != 0:
                arrow.move(find_closest(self.hero, self.enemies_list))

        if self.Step % 20 == 0:
            for enemy in self.enemies_list:
                enemy.get_speed()

        if self.Step % 5 == 0:
            self.hero.add_Arrow()

        if self.Step % 20 == 0:
            for enemy in self.enemies_list:
                enemy.add_Weapons()

        if self.Step % 30 == 0:
            for enemy in self.enemies_list:
                for weapon in enemy.weapon_list:
                    weapon.get_speed(self.hero)

        for enemy in self.enemies_list:
            if enemy.rect.centerx + enemy.speed[0] < 50 or enemy.rect.centerx + enemy.speed[0] > width - 50:
                enemy.speed[0] *= -1
                enemy.rect = enemy.rect.move(enemy.speed)
            if enemy.rect.centery + enemy.speed[1] < 50 or enemy.rect.centery + enemy.speed[1] > height - 50:
                enemy.speed[1] *= -1
                enemy.rect = enemy.rect.move(enemy.speed)
            enemy.rect = enemy.rect.move(enemy.speed)
            for weapon in enemy.weapon_list:
                weapon.move(self.hero)

        self.hero.move(action)

        # check collision
        for enemy in self.enemies_list:
            for weapon in enemy.weapon_list:
                if pygame.sprite.collide_rect(weapon, self.hero):
                    self.hero.hp -= weapon.damage
                    enemy.weapon_list.remove(weapon)
                    weapon.kill()
        for arrow in self.hero.arrow:
            for enemy in self.enemies_list:
                if pygame.sprite.collide_rect(enemy, arrow):
                    enemy.hp -= arrow.damage
                    self.enemies_list.remove(arrow)
                    arrow.kill()

        if len(self.enemies_list) == 0:
            print("\t    Stage " + str(self.stage) + " Clear!" + " (Archer's HP : " + str(self.hero.hp) + ")")
            self.stage += 1
            self.stage_clear = True
            self.enemies_num += 2

        # check valid
        for arrow in self.hero.arrow:
            if arrow.isOut() == True:
                self.hero.arrow.remove(arrow)
                arrow.kill()
        for enemy in self.enemies_list:
            for weapon in enemy.weapon_list:
                if weapon.isOut() == True:
                    enemy.weapon_list.remove(weapon)
                    weapon.kill()
            if enemy.isDead() == True:
                self.enemies_list.remove(enemy)
                enemy.kill()

        if self.hero.isDead():
            print("\t\t\t      Archer is DEAD")
            self.done = True
            self.info = "HP became zero."

        self.Step += 1

        if len(self.enemies_list) == 0:
            return 10, self.done, self.info
        else:
            return self.get_reward(), self.done, self.info

    def step(self, action):
        reward, done, info = self.update(action)
        self.draw()
        obs = pygame.surfarray.array3d(self.screen)

        return obs, reward, done, info

    def reset(self):
        self.stage = 1
        self.stage_clear = True
        self.enemies_list = pygame.sprite.Group()
        self.enemies_num = 2
        self.pikachu_num = 0
        self.pingu_num = 0
        self.done = False
        self.info = "continuing"
        self.Step = 0
        xcor, ycor = self.random_coordinate()
        self.hero = archer(xcor, ycor)
        self.draw()
        obs = pygame.surfarray.array3d(self.screen)

        return obs

    def close(self):
        sys.exit()

class weapons(pygame.sprite.Sprite):
    def __init__(self, x, y, id, num=0):
        pygame.sprite.Sprite.__init__(self)
        self.speed = None
        self.num = num

        if id == "bolt":
            self.id = "bolt"
            self.image = pygame.transform.scale(pygame.image.load("../images/fire_rb.png"), (30, 30))
            self.rect = self.image.get_rect(center=(x,y))
            self.damage = 60
        elif id == "ice":
            self.id = "ice"
            self.image = pygame.transform.scale(pygame.image.load("../images/iceball_rb.png"), (30, 30))
            self.rect = self.image.get_rect(center=(x,y))
            self.damage = 80
        else :
            self.id = "arrow"
            self.image = pygame.transform.scale(pygame.image.load("../images/arrow_rb.png"), (40, 40))
            self.rect = self.image.get_rect(center=(x, y))
            self.damage = 50

    def get_speed(self, target):
        if self.id == "bolt":
            dir_dict = {0: (1, 0), 1: (-1, 0), 2: (0, 1), 3: (0, -1)}
            self.speed = dir_dict[self.num]
        else:
            if self.speed != None:
                return
            else:
                diff_x = target.rect.centerx - self.rect.centerx
                diff_y = target.rect.centery - self.rect.centery
                dis = math.sqrt(diff_x ** 2 + diff_y ** 2)
                if dis == 0:
                    dis = 0.0000000001
                if self.id == "ice":
                    self.speed = [2 * diff_x / dis, 2 * diff_y / dis]
                elif self.id == "arrow":
                    self.speed = [70 * diff_x / dis, 70 * diff_y / dis]
                else:
                    self.speed = [5 * diff_x / dis, 5 * diff_y / dis]

    def move(self, target):
        self.get_speed(target)
        self.rect = self.rect.move(self.speed)

        return

    def isOut(self):
        return self.rect.left < 0 or self.rect.right > width \
                or self.rect.top < 0 or self.rect.bottom > height

class enemies(pygame.sprite.Sprite):
    def __init__(self, x, y, id):
        pygame.sprite.Sprite.__init__(self)
        self.speed = [0, 0]

        if id == "pikachu":
            self.id = "pikachu"
            self.image = pygame.transform.scale(pygame.image.load("../images/pikachu_rb.png"), (60, 60))
            self.rect = self.image.get_rect(center=(x,y))
            self.hp = 150
            self.weapon_list = pygame.sprite.Group()
        else :
            self.id = "pingu"
            self.image = pygame.transform.scale(pygame.image.load("../images/pingu_rb.png"), (60, 60))
            self.rect = self.image.get_rect(center=(x, y))
            self.hp = 100
            self.weapon_list = pygame.sprite.Group()

        return

    def get_speed(self):
        diagonal_vec = (10*math.cos(math.pi/4), 10*math.sin(math.pi/4))
        speed_dict = {0: [10, 0], 1: [-10, 0], 2: [0, 10], 3: [0, -10],
                      4: [diagonal_vec[0], diagonal_vec[1]],
                      5: [diagonal_vec[0]*(-1), diagonal_vec[1]],
                      6: [diagonal_vec[0]*(-1), diagonal_vec[1]*(-1)],
                      7: [diagonal_vec[0], diagonal_vec[1]*(-1)]
                      }
        self.speed = speed_dict[random.randrange(0,8)]

        return

    def add_Weapons(self):
        if self.id == "pikachu":
            for i in range (0, 4) :
                self.weapon_list.add(weapons(self.rect.centerx, self.rect.centery, "bolt", i))
        else :
            self.weapon_list.add(weapons(self.rect.centerx, self.rect.centery, "ice"))

    def move(self):
        self.get_speed()
        if self.rect.centerx + self.rect.speed[0] < 50 or self.rect.centerx + self.rect.speed[0]> width - 50:
            self.speed[0] *= -1
            self.rect = self.rect.move(self.speed)
        if self.rect.centery + self.rect.speed[1] < 50 or self.rect.centery + self.rect.speed[1] > height - 50:
            self.speed[1] *= -1
            self.rect = self.rect.move(self.speed)

        self.rect = self.rect.move(self.speed)

        return

    def isDead(self):
        return self.hp <= 0

class archer(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("../images/hero_rb.png"), (90, 90))
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = 500
        self.arrow = pygame.sprite.Group()
        self.speed = [0,0]

    def move(self, action):
        # up
        if action == 0:
            if self.speed[1] == 20:
                self.speed[1] = 0
            else:
                self.speed[0] = 0
                self.speed[1] = -20
        # down
        elif action == 1:
            if self.speed[1] == -20:
                self.speed[1] = 0
            else:
                self.speed[0] = 0
                self.speed[1] = 20
        # left
        elif action == 2:
            if self.speed[0] == 20:
                self.speed[0] = 0
            else:
                self.speed[0] = -20
                self.speed[1] = 0
        # right
        elif action == 3:
            if self.speed[0] == -20:
                self.speed[0] = 0
            else:
                self.speed[0] = 20
                self.speed[1] = 0


        if self.rect.centerx + self.speed[0] < 50 or self.rect.centerx + self.speed[0] > width - 50:
            self.speed[0] *= -1
            self.rect = self.rect.move(self.speed)
        if self.rect.centery + self.speed[1] < 50 or self.rect.centery + self.speed[1] > height - 50:
            self.speed[1] *= -1
            self.rect = self.rect.move(self.speed)

        self.rect = self.rect.move(self.speed)

    def isDead(self):
        return self.hp <= 0

    def add_Arrow(self):
        self.arrow.add(weapons(self.rect.centerx, self.rect.centery, "arrow"))

# only for archer
def find_closest(hero, enemies_list):
    shortest_dis = sys.maxsize
    arrow_target = None
    for enemy in enemies_list:
        diff_x = hero.rect.centerx - enemy.rect.centerx
        diff_y = hero.rect.centery - enemy.rect.centery
        dis = math.sqrt(diff_x ** 2 + diff_y ** 2)

        if shortest_dis >= dis:
            shortest_dis = dis
            arrow_target = enemy

    return arrow_target