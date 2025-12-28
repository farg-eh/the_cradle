import pygame
from src.utils import Pos

joystick_map = {
        "interact": 3,  # X
        "dash": 1,      # B
        "attack": 2,    # A
        "R1": 5,
        "L1": 4,
        "start": 9
        }

class JoysMgr:
    def __init__(self, core):
        self.core = core
        self.joys = {}
        self.sensitivity_threshold = 0.006  # for joystick sensitivity

    def _add_joystick(self, device_index):
        joystick = pygame.joystick.Joystick(device_index)
        self.joys[joystick.get_instance_id()] = {"joy":joystick,
                                                 "move_dir": Pos(0.0, 0.0),
                                                 "aim_dir": Pos(0.0, 0.0),
                                                 "hat": Pos(0, 0),
                                                 "attack": False,
                                                 "attack_hold": False,
                                                 "attack_up": False,
                                                 "interact": False,
                                                 "dash": False,
                                                 "R1": False,
                                                 "L1": False,
                                                 "start": False
                                                 }
        return joystick.get_instance_id()
    def remove_joystick(self, instance_id):
        del self.joys[instance_id]



    def handle_event(self, event):
        if event.type == pygame.JOYDEVICEADDED:
            ins_id = self._add_joystick(event.device_index)
            joystick = self.joys[ins_id]['joy']
            self.core.notifier.notify(f"joystick {ins_id} have been added")
            if joystick.rumble(0, 0.7, 500):
                print(f"Rumble effect played on joystick {event.device_index}")

        if event.type == pygame.JOYDEVICEREMOVED:
            self.remove_joystick(event.instance_id)

        if event.type == pygame.JOYBUTTONDOWN:
            print(f"\033[91m{event}\033[0m")
            print(f"\033[91m{event.button}\033[0m")
            if event.button == joystick_map['interact']:
                self.joys[event.instance_id]['interact'] = True
                self.joys[event.instance_id]['hold_interact'] = True

            if event.button == joystick_map['dash']:
                self.joys[event.instance_id]['dash'] = True

            if event.button == joystick_map['attack']:
                self.joys[event.instance_id]['attack'] = True

            if event.button == joystick_map['start']:
                self.joys[event.instance_id]['start'] = True
                
            if event.button == joystick_map['R1']:
                self.joys[event.instance_id]['R1'] = True

            if event.button == joystick_map['L1']:
                self.joys[event.instance_id]['L1'] = True
                print("wow")

        if event.type == pygame.JOYBUTTONUP:
            #print(f"\033[93m{event}\033[0m")
            if event.button == joystick_map['interact']:
                self.joys[event.instance_id]['interact_up'] = True
                self.joys[event.instance_id]['hold_interact'] = False

        if event.type == pygame.JOYAXISMOTION:
            #print(f"\033[95m{event}\033[0m")
            if event.axis == 0:
                # direction x 
                x = event.value
                self.joys[event.instance_id]['move_dir'][0] = x if abs(x) >= self.sensitivity_threshold else 0.0
            if event.axis == 1:
                # direction y
                self.joys[event.instance_id]['move_dir'][1] = event.value if abs(event.value) >= self.sensitivity_threshold else 0.0

            if event.axis == 3:
                self.joys[event.instance_id]['aim_dir'][0] = event.value if abs(event.value) >= self.sensitivity_threshold else 0.0

            if event.axis == 4:
                self.joys[event.instance_id]['aim_dir'][1] = event.value if abs(event.value) >= self.sensitivity_threshold else 0.0
                
            
        if event.type == pygame.JOYHATMOTION:
            #print(f"\033[96m{event}\033[0m")
            pos = event.value
            self.joys[event.instance_id]['hat'].x = pos[0]
            self.joys[event.instance_id]['hat'].y = pos[1] * -1

            self.joys[event.instance_id]['move_dir'].x = pos[0]
            self.joys[event.instance_id]['move_dir'].y = pos[1] * -1

        

    # should be called at the end of loops in the input manager or in the state update loop
    # TODO clean this
    def clear(self):
       # print(self.joys[0])
        for joy in self.joys.values():
            joy['start'] = False
            joy['R1'] = False
            joy['L1'] = False
            joy['interact'] = False
            joy['attack'] = False
            joy['dash'] = False

