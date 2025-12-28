from abc import ABC, abstractmethod
import random
import pygame.transform
from asynckivy import animate

from src.utils import import_img, import_imgs, import_sound, import_imgs_as_dict, Animation, Pos, Rect, Timer, StopWatch
from src.ui import Text
from src.settings import SCALE, DW, DH

class MiniGame(ABC):
    def __init__(self, game,  player):
        self.mini_game_name = ""
        self.core = game.core
        self.game = game
        self.screen = game.screen
        self.display = game.display
        self.mouse = game.mouse
        self.root = game.root

        self.player = player
        self.input = player.input
        self.exit_func = None


    def exit(self):
        self.game.mini_game = None
        if self.exit_func:
            self.exit_func()


    @abstractmethod
    def update(self, dt):
        pass

    # optional
    def fixed_update(self, tick_dt):
        pass

    @abstractmethod
    def draw(self, surf):
        pass


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CARDS GAME ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CardsGame(MiniGame):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.assets = self.load_assets()
        # preparing cards
        offset, spacing = 60, 40
        y_offset, y_spacing = 32, 54
        self.values = [('3', '+', '3'), ('12', '/', '2'), ('20', '-', '9'), ('5', '+', '6'), ('2', '*', '3'), ('3', '+', '3'), ('3', '*', '3'), ('9', '*', '1'), ('8', '/', '2'), ('2', '+', '2'), ('3', '*', '5'), ('20', '-', '5'), ('10', '-', '2'), ('4', '*', '2'), ('5', '-', '2'), ('3', '*', '1'), ('15', '-', '2'), ('9', '+', '4')]
        random.shuffle(self.values)
        self.cards = []
        self.selected_cards = []
        for y in range(3):
            for x in range(6):
               num = 6*y + x # a num from 0 to 18
               self.cards.append(Card(game=self, pos=Pos(x*spacing+offset, y*y_spacing + y_offset), val=self.values[num], num=num+1))
 
        
        self.curr_card = self.cards[0]
        # ~~~~~~~~~~~
        self.pos = Pos(0, 0)


        # timers
        self.input_delay = Timer(140)
        self.decision_delay = Timer(1800, func=self._on_decision)

        # stop watch
        self.watch = StopWatch()
        self.watch_txt = Text("00:00", pos=(20, 20))
        self.game.root.add_child(self.watch_txt)


        # state
        self.game_finished = False
        self.exit_func = self.clear_ui

    def clear_ui(self):
        self.game.root.remove_child(self.watch_txt)

    def _on_decision(self):
        card1 = self.selected_cards[0]
        card2 = self.selected_cards[1]
        if card1.numeric_result == card2.numeric_result:
            card1.effect('tick')
            card2.effect('tick')
        else:
            card1.effect('cross')
            card2.effect('cross')

        self.selected_cards.clear()

    def load_assets(self):
        assets = {}
        path = "assets/imgs/cards_game/"
        assets['board'] = import_img(path+"board.png")
        assets['card_light'] = import_img(path+"card/light.png")
        assets['card_open'] = import_imgs(path+"card/open")
        assets['card_close'] = import_imgs(path+"card/close")
        assets['card_tick'] = import_imgs(path+"card/tick")
        assets['card_cross'] = import_imgs(path+"card/cross")
        #assets['bg'] = import_img
        return assets

    def grid_to_index(self, col, row):
        # not used rows_num = 3
        cols_num = 6
        return row * cols_num + col

    def index_to_grid(self, index):
        rows_num = 3
        cols_num = 6
        row =  index / rows_num
        cols = index % cols_num
        return cols, row

    def handle_input(self):
        #print(self.input)
        if self.input.start_menu:
            print('\033[91m trying to exit minigame\033[0m')
            self.exit()

        old_pos = self.pos.x, self.pos.y
        if not self.input_delay.active:
            # handle card navigation
            card_index = self.grid_to_index(*self.pos)
            self.curr_card = self.cards[int(card_index)%18]

            if self.input.move_dir.x > 0:
                self.pos.x += 1
            elif self.input.move_dir.x < 0:
                self.pos.x -= 1
            elif self.input.move_dir.y > 0:
                self.pos.y += 1
            elif self.input.move_dir.y < 0:
                self.pos.y -= 1

        if self.pos == old_pos:
            if self.input.move_dir.magnitude() == 0:
                self.input_delay.deactivate()
        else:
            self.input_delay.activate()

    def process_selected_cards(self):
        if len(self.selected_cards) >=2 and not self.decision_delay.active:
            print('okay')
            self.decision_delay.activate()

    def fixed_update(self, tick_dt):
        pass

    def update(self, dt):
        self.handle_input()
        self.game.input_mgr.update_entity_input(self, 1)
        self.game.input_mgr.update(dt)
        for card in self.cards:
            card.update(dt)


        # win condition
        if all([card.solved for card in self.cards]):
            print("\033[92myou won !!\033[0m")
            self.game_finished = True

        if not self.game_finished:
            time = self.watch.get_time()
            to_seconds = time//1000
            minutes = to_seconds//60
            remaining_seconds = to_seconds%60
            self.watch_txt.change_text(f"{minutes}:{remaining_seconds}")


        # process
        self.process_selected_cards()

        # timers
        self.input_delay.update()
        self.decision_delay.update()
    def draw(self, surf):
        surf.blit(self.assets['board'])
        for card in self.cards:
            card.draw(surf)


class Card:
    def __init__(self, game, pos=(0, 0), num=0, val=('1', '+', '1')):
        self.game = game
        self.pos = Pos(*pos)
        self.num = num
        self.val: list[tuple[str, str, str]] = val
        self.assets = game.assets
        self.curr_imgs = self.assets['card_open']
        self.img_index = 0
        self.img = self.curr_imgs[self.img_index]
        self.rect = Rect(0, 0, 32*SCALE, 48*SCALE)
        self.rect.center = self.pos

        # state
        self.state = "closed"
        self.open = False
        self.solved = False

        # num
        self.num_surf = Text(str(self.num), font_size="big", color='#a36655').get_surf()
        self.num_surf = pygame.transform.scale_by(self.num_surf, (1.2, 1.6))
        self.num_rect = self.num_surf.get_rect(center=(self.pos.x, self.pos.y + 3))

        # value
        txt = f"{self.val[0]}{self.val[1]}{self.val[2]}"
        self.numeric_result = eval(txt)
        txt = f"{self.val[0]}\n{self.val[1]}\n{self.val[2]}".replace('/', '~')
        self.val_surf = Text(str(txt), font_size="small", align='mid', color='#a36655', line_size=12).get_surf()
        self.val_surf = pygame.transform.scale_by(self.val_surf, (1.3, 1))
        self.val_rect = self.val_surf.get_rect(center=(self.pos.x, self.pos.y + 3))

        # flip
        self.flip_timer = Timer(400)

        # effects
        self.effect_type = ''
        self.effecting = False
        self.tick_animation = Animation(imgs=self.assets['card_tick'], duration=700)
        self.cross_animation = Animation(imgs=self.assets['card_cross'], duration=400)
        self.curr_animation = None
        self.frame_fade_timer = Timer(900, func=self._on_effect_end)

    def _on_effect_end(self):
        # self.curr_animation = None
        if self.effect_type == 'tick':
            self.kill()
        elif self.effect_type == 'cross':
            self.flip()
            self.curr_animation = None
        self.effect_type = ''

    def kill(self):
        self.solved = True

    def effect(self, effect_type='cross'):
        self.effect_type = effect_type
        self.curr_animation = self.tick_animation if self.effect_type == 'tick' else self.cross_animation
        self.curr_animation.timer.func = lambda: self.frame_fade_timer.activate()
        self.curr_animation.play()


    def cross_effect(self):
        pass

    def flip(self):
        if self.flip_timer.active: return
        self.flip_timer.activate()
        self.flip_timer.func = lambda: setattr(self, 'open', not self.open)

    def animate(self):
        if self.flip_timer.active:
            self.curr_imgs = self.assets['card_open'] if not self.open else self.assets['card_close']
            t = self.flip_timer.get_progress()
            frames_range = len(self.curr_imgs) - 1
            anim_index = int(t * frames_range)
            self.img = self.curr_imgs[anim_index]

    def on_click(self):
        print(f"card num: {self.num}, card value: {self.val}, card result: {self.numeric_result}")
        if len(self.game.selected_cards) >= 2 or self.solved:
            return
        if len(self.game.selected_cards)>0 :
            if self.game.selected_cards[0] is not self:
                self.flip()
                self.game.selected_cards.append(self)
        else:
            self.flip()
            self.game.selected_cards.append(self)


    def click(self):
        print('clicked')
        self.on_click()

    def update(self, dt):
        if self is self.game.curr_card:
            if self.game.input.interact:
                self.click()

        self.animate()
        self.flip_timer.update()
        if self.curr_animation:
            self.curr_animation.update()
        self.frame_fade_timer.update()

    def get_center(self):
        return self.pos - Pos(self.img.width/2, self.img.height/2)

    def draw(self, surf):
        # main img
        surf.blit(self.img, self.get_center())

        # num surface
        if not self.open and not self.flip_timer:
            surf.blit(self.num_surf, self.num_rect)

        # value surface
        if self.open and not self.flip_timer:
            surf.blit(self.val_surf, self.val_rect)

        # effects
        if self.curr_animation:
            anim_surf = pygame.transform.scale_by(self.curr_animation.curr_img(), (0.6, 0.6))
            t = 1 if not self.frame_fade_timer.active else 1 - self.frame_fade_timer.get_progress()
            t = t if self.effect_type=='cross' else 1
            anim_surf.set_alpha(int(255*t))
            anim_rect = anim_surf.get_rect(center=self.pos)
            surf.blit(anim_surf, anim_rect)

        # highlight
        if self is self.game.curr_card:
            surf.blit(self.assets['card_light'], self.get_center())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FISHING GAME ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class FishingGame(MiniGame):
    def __init__(self, game, player):
        super().__init__(game, player)
        self.assets = self.load_assets()
        # state
        self.game_finished = False
        self.exit_func = self.clear_ui # will be called on exit

        # lanes
        offset = 60
        lane_height = 25
        x = DW/2
        self.lanes = [Pos(x, offset + (lane_height*y)) for y in range(5)]

        # entities
        self.fish_types = ['small_fish', 'mid_fish', 'big_fish']
        self.trash_types = ['boot', 'seaweed']
        self.fishables = []

        # timers
        self.gen_fishable_timer = Timer(1350, True, True, self.gen_fishable)

        # components
        self.hook = Hook(self)
        self.bar = Bar(self)
        self.tap_hinter = TappingHinter(self)

    def gen_fishable(self):
        lane = random.choice(self.lanes)
        fishable_type = random.choice(self.fish_types + self.trash_types)
        self.fishables.append(Fishable(self, Pos(-50, lane.y), fishable_type))
        

    def clear_ui(self):
        pass


    def load_assets(self):
        assets = {}
        path = "assets/imgs/fishing_game/"
        # background
        assets['bg'] = import_img(path+"bg.png")

        # ui
        assets['fish_icon'] = import_img(path+"fish_icon.png")

        # components
        assets['hook'] = import_img(path+'hook.png')
        assets['bar'] = import_img(path+'bar.png')
        assets['tap1'] = import_img(path+'tap1.png')
        assets['tap2'] = import_img(path+'tap1.png')

        # fishables
        assets['small_fish'] = import_img(path+"small_fish.png")
        assets['mid_fish'] = import_img(path+"mid_fish.png")
        assets['big_fish'] = import_img(path+"big_fish.png")
        assets['boot'] = import_img(path+"boot.png")
        assets['seaweed'] = import_img(path+"seaweed.png")
        return assets

    def handle_input(self):
        #print(self.input)
        if self.input.start_menu:
            print('\033[91m trying to exit minigame\033[0m')
            self.exit()

    def fixed_update(self, tick_dt):
        pass

    def update(self, dt):
        self.handle_input()
        self.game.input_mgr.update_entity_input(self, 1)
        self.game.input_mgr.update(dt)
        for fishable in self.fishables:
            fishable.update(dt)

        # timers update
        self.gen_fishable_timer.update()



    def draw(self, surf):
        surf.blit(self.assets['bg'])
        for lane_point in self.lanes:
            lane_point.draw(surf)

        for fishable in self.fishables:
            fishable.draw(surf)

        self.hook.draw(surf)
        self.bar.draw(surf)
        self.tap_hinter.draw(surf)
        surf.blit(self.assets['fish_icon'], (4, 4))
        surf.blit(Text("X 1", color="#f2eaf1").get_surf(), (26, 5))



class Fishable:
    def __init__(self, game, center_pos, fishable_type):
        self.game = game # referes to the minigame and not the actual main game class
        self.img = self.game.assets[fishable_type]
        self.rect = Rect(0, 0, self.img.width, self.img.height)
        self.rect.center = center_pos

        self.direction = Pos(1, 0)
        self.speed = 45

    def kill(self):
        if self in self.game.fishables:
            self.game.fishables.remove(self)

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if self.rect.left > DW:
            self.kill()

    def draw(self, surf):
        surf.blit(self.img, self.rect)


class Hook:
    def __init__(self, game):
        self.game = game
        self.img = self.game.assets['hook']
        self.rect = self.img.get_rect(center=(DW/2, 10))

    def draw(self, surf):
        surf.blit(self.img, self.rect)

class Bar:
    def __init__(self, game):
        self.game = game
        self.img = self.game.assets['bar']
        self.rect = self.img.get_rect(midright=(DW*0.98, DH/2))

    def draw(self, surf):
        surf.blit(self.img, self.rect)

class TappingHinter:
    def __init__(self, game):
        self.game = game
        self.img = self.game.assets['tap1']
        self.rect = self.img.get_rect(bottomleft=(DW*0.2, DH))

    def draw(self, surf):
        surf.blit(self.img, self.rect)
