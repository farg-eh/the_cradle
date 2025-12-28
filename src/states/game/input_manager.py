from dataclasses import dataclass, field
import pygame.key
from src.settings import GAME_CTRLS
from src.utils import Pos

@dataclass()
class Input:
    attack: bool = False
    attack_hold: bool = False
    attack_up: bool = False
    interact: bool = False
    cycle_items: bool = False
    inventory: bool = False # implement later
    start_menu: bool = False # implement later
    move_dir: Pos = field(default_factory=lambda: Pos(0, 0))
    aim_dir: Pos = field(default_factory=lambda: Pos(0, 0))


# TODO allow it to manage multiple inputs not just one
class InputManger:
    def __init__(self, game):
        self.game = game
        self.mouse = game.mouse
        self.joy_mgr = game.core.joy_mgr
        self.input = Input()
        self.input2 = Input()
        self.input_method = "keyboard"
        print(self.input.__dict__)

        # okay lets do this 
        self.single_keys = []

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            self.single_keys.append(event.key)

    def update_entity_input(self, entity, p=1):
        if p == 1:
            entity.input = self.input
        elif p == 2:
            entity.input = self.input2

    def manage_input(self):
        # for now we will handle only one joystick because we are handling only one input
        # if controller is active disable keyboard
        # JOYSTICK ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if len(self.joy_mgr.joys) > 0:
            joystick = self.joy_mgr.joys[0]
            self.input.move_dir = joystick['move_dir']
            self.input.aim_dir = Pos(joystick['aim_dir'][0], joystick['aim_dir'][1] * -1)
            self.input.attack = joystick['attack'] or joystick['R1']
            self.input.attack_hold = joystick['attack_hold']
            self.input.attack_up = joystick['attack_up']
            self.input.interact = joystick['interact']
            self.input.cycle_items = joystick['L1']
            self.input.start_menu = joystick['start']
            self.input.inventory = joystick['dash']
            self.input_method = 'joystick'
            if len(self.joy_mgr.joys) >1:
                joystick = self.joy_mgr.joys[1]
                self.input2.move_dir = joystick['move_dir']
                self.input2.aim_dir = Pos(joystick['aim_dir'][0], joystick['aim_dir'][1] * -1)
                self.input2.attack = joystick['attack'] or joystick['R1']
                self.input2.attack_hold = joystick['attack_hold']
                self.input2.attack_up = joystick['attack_up']
                self.input2.interact = joystick['interact']
                self.input2.cycle_items = joystick['L1']
                self.input2.start_menu = joystick['start']
                self.input.inventory = joystick['dash']
                self.input_method = 'joystick'
            return

        self.input_method = 'keyboard'
        # KEYBOARD ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # keys
        keys = pygame.key.get_pressed()
        up_keys = pygame.key.get_just_released()
        single_keys = pygame.key.get_just_pressed()

        # movement
        # vertical
        if any([keys[x] for x in GAME_CTRLS['mvup']]):
            self.input.move_dir.y = -1
        elif any([keys[x] for x in GAME_CTRLS['mvdown']]):
            self.input.move_dir.y = 1

        # horizontal
        if any([keys[x] for x in GAME_CTRLS['mvleft']]):
            self.input.move_dir.x = -1
        elif any([keys[x] for x in GAME_CTRLS['mvright']]):
            self.input.move_dir.x = 1

        # normalize
        if self.input.move_dir.magnitude() > 0:
            self.input.move_dir.normalize()

        # aim
        if self.mouse.r_down:
            player_pos = Pos(*self.game.player.hitbox.center)
            mouse_world_pos = self.game.camera.get_cam_mouse_pos(self.mouse.pos)
            self.input.aim_dir = (mouse_world_pos - player_pos).normalize()
            print(f'\033[94mmouse aim dir: {self.input.aim_dir}\033[0m')


        # btn actions
        self.input.attack_hold = any([keys[x] for x in GAME_CTRLS['attack']])
        self.input.attack_up = any([up_keys[x] for x in GAME_CTRLS['attack']])
        self.input.attack = any([x  in self.single_keys for x in GAME_CTRLS['attack']])
        self.input.interact = any([x  in self.single_keys for x in GAME_CTRLS['interact']])
        self.input.inventory = any([x in self.single_keys for x in GAME_CTRLS['inventory']])
        self.input.cycle_items = any([x  in self.single_keys for x in GAME_CTRLS['cycle_items']])
        self.input.start_menu = any([x in self.single_keys for x in GAME_CTRLS['start']])

    def update(self, tick_dt):
        self.manage_input()
        # reset the input
        self.input = Input()
        self.input2 = Input()
        self.joy_mgr.clear()
        print(self.single_keys)
        self.single_keys.clear()



