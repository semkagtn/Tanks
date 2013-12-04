import os
import random
import sys

import pygame

import object_manager

DATA_DIR = 'data'
STONE_IMAGE = 'stone.png'
PLAYER_IMAGE = 'player.png'
ENEMY_IMAGE = 'enemy.png'
BULLET_IMAGE = 'bullet.png'
DELETE_IMAGE = 'delete.png'
BANG_IMAGE = 'bang.png'
SHOOT_SOUND = 'shoot.wav'
BANG_SOUND = 'bang.wav'
TANK_SPEED = 2
BULLET_SPEED = 8
ENEMY_ROTATE = 0.006
ENEMY_SHOOT = 0.02
BANG_TIME = 12
STONE, PLAYER, ENEMY, DELETE = range(4)  # DELETE must be last!

class GameObject(pygame.sprite.Sprite):

    def __init__(self, coords, image, indestructible):
        super(GameObject, self).__init__()
        try:
            image = os.path.join(DATA_DIR, image)
            self.image = pygame.image.load(image).convert_alpha()
        except pygame.error:
            sys.exit('Cannot load image: %s' % image)
        self.rect = self.image.get_rect()
        self.rect.center = coords
        self.indestructible = indestructible
        self.area = pygame.display.get_surface().get_rect()
        object_manager.add(self)

    def _obstructions(self):
        if self.rect.top < self.area.top \
        or self.rect.left < self.area.left \
        or self.rect.bottom > self.area.bottom \
        or self.rect.right > self.area.right:
            return True
        return len(object_manager.collide(self)) > 1

    def _load_sound(self, sound):
        sound_file = os.path.join(DATA_DIR, sound)
        try:
            return pygame.mixer.Sound(sound_file)
        except:
            class NoSound:
                def play():
                    pass
            return NoSound()


class Bang(GameObject):

    def __init__(self, coords):
        self.bang_sound = self._load_sound(BANG_SOUND)
        super(Bang, self).__init__(coords, BANG_IMAGE, True)
        self.counter = 0
        self.bang_sound.play()

    def update(self):
        self.counter += 1
        if self.counter >= BANG_TIME:
            self.kill()


class Stone(GameObject):

    def __init__(self, coords):
        super(Stone, self).__init__(coords, STONE_IMAGE, True)


class MovingObject(GameObject):

    def __init__(self, coords, image, indestructible, speed):
        super(MovingObject, self).__init__(coords, image, indestructible)
        self.speed = speed
        self.moving = False
        rotate = pygame.transform.rotate
        self.up = self.image
        self.left = rotate(self.image, 90)
        self.down = rotate(self.image, 180)
        self.right = rotate(self.image, 270)

    def turn_up(self):
        self.dx = 0
        self.dy = -self.speed
        self.image = self.up

    def turn_left(self):
        self.dx = -self.speed
        self.dy = 0
        self.image = self.left

    def turn_down(self):
        self.dx = 0
        self.dy = self.speed
        self.image = self.down

    def turn_right(self):
        self.dx = self.speed
        self.dy = 0
        self.image = self.right

    def move(self):
        self.moving = True
        self.rect.move_ip(self.dx, self.dy)
        return not self._obstructions()

    def stop(self):
        self.moving = False

    def update(self):
        if self.moving:
            self.move()


class Bullet(MovingObject):

    def __init__(self):
        super(Bullet, self).__init__((0, 0), BULLET_IMAGE, False, BULLET_SPEED)

    def _destroy(obj):
        obj.kill()

    def update(self):
        super(Bullet, self).update()

    def move(self):
        if not super(Bullet, self).move():
            collides = object_manager.collide(self)
            if len(collides) > 1:
                for obj in collides:
                    if not obj.indestructible:
                        self._destroy(obj)
            else:
                self.kill()


class PlayerBullet(Bullet):

    def __init__(self):
        super(PlayerBullet, self).__init__()

    def _destroy(self, obj):
        if type(obj) != Player:
            obj.kill()


class EnemyBullet(Bullet):

    def __init__(self):
        super(EnemyBullet, self).__init__()

    def _destroy(self, obj):
        if type(obj) != Enemy:
            obj.kill()


class Tank(MovingObject):

    def __init__(self, coords, image):
        super(Tank, self).__init__(coords, image, False, TANK_SPEED)

    def move(self):
        if not super(Tank, self).move():
            self.rect.move_ip(-self.dx, -self.dy)

    def _shoot(self, bullet):
        if self.image == self.up:
            bullet.rect.midtop = self.rect.midtop
            bullet.turn_up()
        elif self.image == self.left:
            bullet.rect.midleft = self.rect.midleft
            bullet.turn_left()
        elif self.image == self.down:
            bullet.rect.midbottom = self.rect.midbottom
            bullet.turn_down()
        elif self.image == self.right:
            bullet.rect.midright = self.rect.midright
            bullet.turn_right()
        bullet.move()
        
    def kill(self):
        super(Tank, self).kill()
        Bang(self.rect.center)
        

class Player(Tank):

    def __init__(self, coords):
        self.shoot_sound = self._load_sound(SHOOT_SOUND)
        super(Player, self).__init__(coords, PLAYER_IMAGE)

    def shoot(self):
        self.shoot_sound.play()
        self._shoot(PlayerBullet())

    def update(self):
        super(Player, self).update()


class Enemy(Tank):

    def __init__(self, coords):
        super(Enemy, self).__init__(coords, ENEMY_IMAGE)
        
    def shoot(self):
        self._shoot(EnemyBullet())

    def update(self):
        rand = random.uniform(0, 1)
        if rand <= ENEMY_ROTATE:
            self.turn_up()
            self.move()
        elif rand <= 2 * ENEMY_ROTATE:
            self.turn_left()
            self.move()
        elif rand <= 3 * ENEMY_ROTATE:
            self.turn_down()
            self.move()
        elif rand <= 4 * ENEMY_ROTATE:
            self.turn_right()
            self.move()
        elif rand <= 4 * ENEMY_ROTATE + ENEMY_SHOOT:
            self.stop()
            self.shoot()
        else:
            super(Enemy, self).update()


class Cursor(pygame.sprite.Sprite):
    """Class for Level Editor."""
    def __init__(self, is_player):
        super(Cursor, self).__init__()
        stone = os.path.join(DATA_DIR, STONE_IMAGE)
        player = os.path.join(DATA_DIR, PLAYER_IMAGE)
        enemy = os.path.join(DATA_DIR, ENEMY_IMAGE)
        delete = os.path.join(DATA_DIR, DELETE_IMAGE)
        self.images = []
        load = pygame.image.load
        try:
            self.images.append(load(stone).convert_alpha())
            self.images.append(load(player).convert_alpha())
            self.images.append(load(enemy).convert_alpha())
            self.images.append(load(delete).convert_alpha())
        except pygame.error:
            sys.exit('Cannot load images: %s, %s, %s, %s' %
                    (stone, player, enemy, delete))
        self.current = 0
        self.image = self.images[self.current]
        self.rect = self.image.get_rect()
        self.area = pygame.display.get_surface().get_rect()
        self.is_player = is_player

    def next(self):
        if self.current == DELETE:
            self.current = 0
        else:
            self.current += 1
        self.image = self.images[self.current]

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        old_rect = self.rect.copy()
        self.rect.center = mouse_pos
        if self._obstructions():
            self.rect = old_rect

    def _obstructions(self):
        if self.rect.top < self.area.top \
        or self.rect.left < self.area.left \
        or self.rect.bottom > self.area.bottom \
        or self.rect.right > self.area.right:
            return True
        return False

    def create(self):
        if len(object_manager.collide(self)) > 0:
            return
        if self.current == STONE:
            obj = Stone(self.rect.center)
        elif self.current == PLAYER:
            if self.is_player:
                return
            obj = Player(self.rect.center)
            self.is_player = True
        elif self.current == ENEMY:
            obj = Enemy(self.rect.center)
        else:
            sys.exit('Unknown error')
        obj.type = self.current

    def delete(self):
        collides = object_manager.collide(self)
        for obj in collides:
            if obj != self:
                super(GameObject, obj).kill()
                if type(obj) == Player:
                    self.is_player = False

