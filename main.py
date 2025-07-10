import pygame
import sys
from src.settings import SW, SH, FRAMERATE
from src.states.state import State


class Core:
    def __init__(self):
        # basic pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((SW, SH))
        self.clock = pygame.time.Clock()
        self.dt = 0 

        self.current_state = State(self, 'menu')
    def switch_state(self, new_state):
        pass

    def run(self):
        while True:
            for event in pygame.event.get():
                # ~~~~~ general event handling ~~~~~
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # ~~~~~ state event handling ~~~~~
                self.current_state.handle_input(event)

            # calculate delta time
            self.dt = self.clock.tick(FRAMERATE)

            # update
            self.current_state.update(self.dt)
            
            # draw
            self.current_state.draw()
            pygame.display.update()
if __name__ == '__main__':
    Core().run()
