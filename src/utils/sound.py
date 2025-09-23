import pygame
import random
from src.utils import import_sound


# NOTE : the implementation of this class is beta it should be changed later but the design should remain the same
class SoundManager:
    def __init__(self, sound_paths_to_load: list, vol=1.0):
        """you just need a list of paths each path  will start from the sounds directory"""
        self._vol = vol
        self.sounds = {x[0]: x[1] for x in [import_sound('assets/sound/'+path) for path in sound_paths_to_load]}
        self.seq = {}
        self.rand = {}

    def _set_vol_and_play(self, sound):
        sound.set_volume(self._vol)
        sound.play()

    def play(self, sound_name, sound_list_method='random'):
        """
        sound_name: the name the sound u wanna play without the extention
        if the sound_name exist in the assets it will be played 
        if the name is a key for a list of sounds sound_list_method will be used to specify what to play 
        available methods
        - random
        - index;i
        - random-no-repeat
        - seq

        """
        sound = self.sounds[sound_name]

        # if the sound is a list of sounds
        if isinstance(sound, list):
            
            method = sound_list_method.split(';')
            method_type = method[0]
            method_value = method[1] if len(method) > 1 else None
            
            match method_type:
                case 'random':
                     s = random.choice(sound)
                     self._set_vol_and_play(s)
                case 'index':
                    s = sound[method_value] if method_value != None else None
                    if s:
                     self._set_vol_and_play(s)
                case 'random-no-repeat':
                    # entry format is (sound_name : {history: [], }

                    # when there is no entry for the sound name in self.rand
                    if not self.rand.get(sound_name):
                        self.rand[sound_name] = {'history':[]}

                    # when an entry exists
                    if len(self.rand[sound_name]['history']) == len(sound): 
                        self.rand[sound_name]['history'].clear() # reset the history if it has all the sound
                    drawing_pool = [x for x in sound if x not in self.rand[sound_name]['history']] 
                    rand_sound = random.choice(drawing_pool)
                    self.rand[sound_name]['history'].append(rand_sound)
                    # play
                    self._set_vol_and_play(rand_sound)

                case 'seq':
                    # entry format is (sound_name: {curr_index: int})
                    # if no entry make one
                    if not self.seq.get(sound_name):
                        self.seq[sound_name] = {'curr_index': 0}

                    # when we have an entry
                    # index clamp
                    if self.seq[sound_name]['curr_index'] >= len(sound):
                        self.seq[sound_name]['curr_index'] = 0
                    # play 
                    index = self.seq[sound_name]['curr_index']
                    seq_sound = sound[index]
                    self._set_vol_and_play(seq_sound)

                    # index increment
                    self.seq[sound_name]['curr_index'] += 1

                    # debug
                    print(f"- snd\033[92m {sound_name}:[{index}]\033[0m len: \033[93m{seq_sound.get_length():.3f}s\033[0m vol: \033[94m{seq_sound.get_volume()}\033[0m")



                case _:
                    raise ValueError
        else: # if its a single sound
            sound.play()


        

        
