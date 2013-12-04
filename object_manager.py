import pygame

import game_objects

_all = pygame.sprite.RenderPlain()
_enemies = pygame.sprite.RenderPlain()

def add(obj):
    global _all
    _all.add(obj)
    if type(obj) == game_objects.Enemy:
        _enemies.add(obj)

def update():
    global _all
    _all.update()

def draw(screen):
    global _all
    _all.draw(screen)

def collide(obj):
    global _all
    return pygame.sprite.spritecollide(obj, _all, False)

def has(obj):
    global _all
    return _all.has(obj)

def enemies():
    global _enemies
    return _enemies.sprites()

def get():
    global _all
    return _all.sprites()
