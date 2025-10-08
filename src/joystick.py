import pygame
from src.utils import Pos

joystick_map = {
        "interact": 0,  # A
        "dash": 1,      # B
        "attack": 3,    # X
        "R1": 7,
        "L1": 6,
        "start": 11
        }

class JoysMgr:
    def __init__(self, core):
        self.joys = {}
        self.sensitivity_threshold = 0.3  # for joystick sensitivity

    def _add_joystick(self, device_index):
        joystick = pygame.joystick.Joystick(device_index)
        self.joys[joystick.get_instance_id()] = {"joy":joystick,
                                                 "move_dir": Pos(0.0, 0.0),
                                                 "hat": Pos(0, 0),
                                                 "interact": False,
                                                 "hold_interact": False,
                                                 "interact_up": False,
                                                 "attack": False,
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
            if joystick.rumble(0, 0.7, 500):
                print(f"Rumble effect played on joystick {event.instance_id}")

        if event.type == pygame.JOYDEVICEREMOVED:
            self.remove_joystick(event.instance_id)

        if event.type == pygame.JOYBUTTONDOWN:
            #print(f"\033[91m{event}\033[0m")
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
            elif event.axis == 1:
                # direction y
                self.joys[event.instance_id]['move_dir'][1] = event.value if abs(event.value) >= self.sensitivity_threshold else 0.0
                
            
        if event.type == pygame.JOYHATMOTION:
            #print(f"\033[96m{event}\033[0m")
            pos = event.value
            self.joys[event.instance_id]['hat'].x = pos[0]
            self.joys[event.instance_id]['hat'].y = pos[1]

            self.joys[event.instance_id]['move_dir'].x = pos[0]
            self.joys[event.instance_id]['move_dir'].y = pos[1]

        

    # should be called at the end of loops like the mouse update method
    def update(self):
       # print(self.joys[0])
        for joy in self.joys.values():
            joy['start'] = False
            joy['R1'] = False
            joy['L1'] = False
            joy['interact'] = False
            joy['attack'] = False
            joy['dash'] = False

