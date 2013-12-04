import argparse
import os
import sys

import pygame
from pygame.locals import *

import game_objects
import object_manager

LEVELS_DIR = 'levels'
RESOLUTION = 800, 600
BACKGROUND_COLOR = 180, 180, 180
CAPTION = 'Tanks'
FPS = 60

class Tanks:

    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.init()
        self.screen = pygame.display.set_mode(RESOLUTION)
        pygame.mouse.set_visible(False)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background.fill(BACKGROUND_COLOR)
        self.fps = FPS
        self.player = None

    def _load_level(self, level):
        level = os.path.join(LEVELS_DIR, level)
        level_file = open(level, 'r')
        for line in level_file:
            try:
                object_type, x, y = line.split()
                object_type = int(object_type)
                coords = (int(x), int(y))
            except:
                sys.exit('Wrong file format')
            if object_type == game_objects.STONE:
                obj = game_objects.Stone(coords)
            elif object_type == game_objects.PLAYER:
                if self.player is None:
                    obj = game_objects.Player(coords)
                    self.player = obj
                else:
                    sys.exit('More then one player')
            elif object_type == game_objects.ENEMY:
                obj = game_objects.Enemy(coords)
            else:
                sys.exit('Wrong file format')
            obj.type = object_type
        level_file.close()

    def _write_level(self, level):
        level = os.path.join(LEVELS_DIR, level)
        try:
            level_file = open(level, 'w')
            objects = object_manager.get()
            for obj in objects:
                x, y = obj.rect.center
                level_file.write("%d %d %d\n" % (obj.type, x, y))
        except:
            sys.exit('Unknown error')
        finally:
            level_file.close()

    def game(self, level):
        try:
            self._load_level(level)
        except IOError:
            sys.exit('No such file: %s' % level)
        running = True
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_UP:
                        self.player.turn_up()
                        self.player.move()
                    elif event.key == K_LEFT:
                        self.player.turn_left()
                        self.player.move()
                    elif event.key == K_DOWN:
                        self.player.turn_down()
                        self.player.move()
                    elif event.key == K_RIGHT:
                        self.player.turn_right()
                        self.player.move()
                    elif event.key == K_SPACE:
                        self.player.stop()
                        self.player.shoot()
                elif event.type == KEYUP:
                    if event.key == K_UP \
                    or event.key == K_LEFT \
                    or event.key == K_DOWN \
                    or event.key == K_RIGHT:
                        self.player.stop()
            object_manager.update()
            if not object_manager.has(self.player):
                running = False
            if not object_manager.enemies():
                running = False
            self.screen.blit(self.background, (0, 0))
            object_manager.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

    def level_editor(self, level):
        try:
            self._load_level(level)
        except IOError:
            print('New file')
        cursor = game_objects.Cursor(self.player is not None)
        cursor_surface = pygame.sprite.RenderPlain()
        cursor_surface.add(cursor)
        running = True
        while running:
            self.clock.tick(self.fps)
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        cursor.next()
                elif event.type == MOUSEBUTTONDOWN:
                    if cursor.current == game_objects.DELETE:
                        cursor.delete()
                    else:
                        cursor.create()

            cursor_surface.update()
            self.screen.blit(self.background, (0, 0))
            object_manager.draw(self.screen)
            cursor_surface.draw(self.screen)
            pygame.display.flip()
        self._write_level(level)
        pygame.quit()


def main():
    parser = argparse.ArgumentParser(
            description='Simple game written in Python 3 using pygame library')
    parser.add_argument('level', help='name of level file')
    parser.add_argument('-e', '--editor', 
            action='store_true', help='run level editor')
    args = parser.parse_args()
    tanks = Tanks()
    if args.editor:
        tanks.level_editor(args.level)
    else:
        tanks.game(args.level)

if __name__ == '__main__' :
    main()
