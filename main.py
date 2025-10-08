import pygame
import sys, os, psutil
from src.settings import SW, SH, FRAMERATE, DEBUG, FONTS
from src.ui.custom.notify import NotificationManager
from src.utils import Timer, import_font
from src.states import Menu, Game, Editor, TestYard
import gc
from src.ui.custom import gen_debug_panel
from src.ui import ScrollablePanel
from src.utils.lerp import oscilating_lerp
from src.settings import conf
from src.joystick import JoysMgr

# this class share global info between all other game states and is responsible
# for state swtiching 
class Core:
    def __init__(self):
        # start pygame 
        pygame.init()

    
        # load fonts (this can be moved to different states if i try having different fonts for diffrent states)
        self.load_fonts()

        # display settings
        self.screen = None
        self._fullscreen = False
        self._scaled = True
        self._show_fps = False
        self.update_screen()
        self.display = pygame.Surface((SW//2, SH//2), pygame.SRCALPHA)
        # swich state effect
        self.effect_surface = pygame.Surface((SW, SH), flags=pygame.SRCALPHA)
        self.effect_surface.fill((1, 1, 1))
        self.effect_timer = Timer(1000)

        self.effect_timer_func = None
        # sound settings
        self._sfx_vol = 1.0
        self._music_vol = 0.33333
        # framerate & delta time
        self.clock = pygame.time.Clock()
        self.dt = 0 

        self.current_state = Menu(self)

        self.PERFORMANCE_INFO = {'ram_usage': '0 MB',
                                 'fps': '0',
                                 'fps_avg': '0',
                                 # system
                                 'system_cpu_usage': '0%',
                                 'system_disk_usage': '0%',
                                 'system_available_ram': '0 MB'

                     }

        # stuff for measuring game performance info
        self.process = psutil.Process(os.getpid())
        self.fps_avg = 0
        self.avg_timer = Timer(500, False, True)
        self.frames = [] # for measuring fps average every 500ms
        self.cpu_usages = [] # same thing but for cpu

        # state shared debug panel ui
        self.debug_panel: ScrollablePanel = gen_debug_panel()
        self.prepare_debug_panel(self.debug_panel)

        # notification card test
        #self.nc = NotificationCard()

        # modifier keys
        self.K_CTRL = False

        # joysticks manager
        self.joy_mgr = JoysMgr(self)

        # notifications manager
        self.notifier = NotificationManager()
        


        # delete
        self.meme_msgs = ["i", "love", "you\n meme sOOOoOOOOooooo much !!!", "<3 "*17, 'love you '*9, "hehe", "hugs", ":)", "mwah"*40 ] 
        self.ind = 0

    def load_fonts(self):
        path = 'assets/fonts/regular.ttf'
        FONTS['small-en'] = import_font(path, 10)
        FONTS['mid-en'] = import_font(path, 14)
        FONTS['big-en'] = import_font(path, 17)
        FONTS['xbig-en'] = import_font(path, 20)
        FONTS['xxbig-en'] = import_font(path, 24)
        FONTS['small-ar'] = import_font(path, 10)
        FONTS['mid-ar'] = import_font(path, 14)
        FONTS['big-ar'] = import_font(path, 17)
        FONTS['xbig-ar'] = import_font(path, 20)
        FONTS['xxbig-ar'] = import_font(path, 24)
        for f in ['small-ar', 'mid-ar', 'big-ar', 'xbig-ar', 'xxbig-ar']:
            font = FONTS[f]
            font.set_script("Arab")
            font.set_direction(pygame.DIRECTION_RTL)
            #font.align = pygame.FONT_RIGHT




    def prepare_debug_panel(self, debug_panel):
        fullscreen_cbox = debug_panel.get_child_by_name('fullscreen')
        fullscreen_cbox.value = self._fullscreen
        fullscreen_cbox.func = self.switch_fullscreen

        scaled_cbox = debug_panel.get_child_by_name('scaled')
        scaled_cbox.value = self._scaled
        scaled_cbox.func = self.switch_scaled

        panel_opacity_slider = debug_panel.get_child_by_name('dpanel_opacity')
        panel_opacity_slider.value = 1
        panel_opacity_slider.min_v = 0.15
        self.debug_panel.set_opacity(panel_opacity_slider.value)
        panel_opacity_slider.func = self.change_dpanel_opacity


        self.debug_panel.hidden = not DEBUG
        print(pygame.display.list_modes(flags=pygame.FULLSCREEN))

    def update_screen(self):
        if self._fullscreen and self._scaled:
            self.screen = pygame.display.set_mode((SW, SH), flags=pygame.FULLSCREEN|pygame.SCALED)
        elif self._fullscreen:
            self.screen = pygame.display.set_mode((SW, SH), flags=pygame.FULLSCREEN)
        elif self._scaled:
            self.screen = pygame.display.set_mode((SW, SH), flags=pygame.SCALED)
        else:
            self.screen = pygame.display.set_mode((SW, SH))

    def _switch_state(self, new_state):
        pygame.mixer.music.unload()
        match new_state:
            case 'menu':
                self.current_state = Menu(self)
            case 'game':
                self.current_state = Game(self)
            case 'editor':
                self.current_state = Editor(self)
            case 'testyard':
                self.current_state = TestYard(self)
            case _:
                raise ValueError(f"you tried to switch to an unknow game state : {new_state}")

    def switch_state(self, new_state):
        self.effect_timer_func = lambda: self._switch_state(new_state)
        self.effect_timer.activate()

    def run(self):
        while True:
            for event in pygame.event.get():
                # ~~~~~ general event handling ~~~~~
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11: # fullscreen switch
                        self._fullscreen = not self._fullscreen 
                        self.update_screen()

                    if event.key == pygame.K_F12: # scaled window switch
                        self._scaled = not self._scaled
                        self.update_screen()

                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL: # ctrl buttons tracking
                        self.K_CTRL = True

                    if event.key == pygame.K_d and self.K_CTRL: # debug mode 
                        global DEBUG
                        DEBUG = not DEBUG
                        self.debug_panel.hidden = not DEBUG

                    if event.key == pygame.K_0: # force grabage collection
                        gc.collect()
                        self.notifier.notify(self.meme_msgs[self.ind])
                        self.ind +=1
                        self.ind %= len(self.meme_msgs)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        self.K_CTRL = False

                # ~~~~~ state event handling ~~~~~
                self.joy_mgr.handle_event(event)
                self.current_state.handle_input(event)

            # calculate delta time
            self.dt = self.clock.tick(FRAMERATE) / 1000

            # update
            self.debug_panel.update(self.dt, self.current_state.mouse)

            self.current_state.update(self.dt)
            
            self.effect_timer.update()
            if self.effect_timer.get_progress() > 0.5 and self.effect_timer_func != None:
                self.effect_timer_func()
                self.effect_timer_func = None

            self.joy_mgr.update()

            #self.nc.update(self.dt, self.current_state.mouse)
            self.notifier.update(self.dt, self.current_state.mouse)


            
            # draw
            self.current_state.draw()

            self.debug_panel.draw(self.screen)

            #self.nc.draw(self.screen)
            self.notifier.draw(self.screen)
            #print(self.notifier.children)

            if self.effect_timer:
                self.effect_surface.set_alpha(int(oscilating_lerp(0, 255, 1 - self.effect_timer.get_progress())))
                self.screen.blit(self.effect_surface)

            if self._show_fps:
                self.screen.blit(FONTS['mid-en'].render(self.PERFORMANCE_INFO['fps_avg'], False, 'lightyellow'), (SW - 30, 10))

            pygame.display.update()

            # ~~~~~ calculate game performance info ~~~~~ 
            # cpu & fps
            fps = self.clock.get_fps()
            self.frames.append(fps)
            if DEBUG:
                self.cpu_usages.append(psutil.cpu_percent())
            self.avg_timer.update()
            if self.avg_timer.done:
                self.PERFORMANCE_INFO['fps_avg'] = str(int(sum(self.frames)/len(self.frames)))
                self.frames.clear()
                if DEBUG:
                    self.PERFORMANCE_INFO['system_cpu_usage'] = f"{(sum(self.cpu_usages)/len(self.cpu_usages)):.1f} %"
                    self.cpu_usages.clear()
                self.avg_timer.activate()
            self.PERFORMANCE_INFO['fps'] = str(int(fps))
            if DEBUG:
                # ram
                self.PERFORMANCE_INFO['ram_usage'] = f"{self.process.memory_info().rss / (1024 * 1024):.2f} MB"
                self.PERFORMANCE_INFO['system_available_ram'] = f"{psutil.virtual_memory().available // (1024 * 1024)} MB" 

                # disk
                self.PERFORMANCE_INFO['system_disk_usage'] = f"{psutil.disk_usage('/')[3]}%"
                #print("\033[95m" + "~"*22 + "\033[0m")
                #for key, item in self.PERFORMANCE_INFO.items():
                    #print(f"{key} -> \033[93m{item}\033[0m")



            # ~~~~~ update debug panel info ~~~~~ 
            if not self.debug_panel.hidden:
                info = self.PERFORMANCE_INFO
                self.debug_panel.get_child_by_name('fps').change_text(info['fps_avg'])
                self.debug_panel.get_child_by_name('cpu_usage').change_text(info['system_cpu_usage'])
                self.debug_panel.get_child_by_name('ram_usage').change_text(info['ram_usage']) 
                self.debug_panel.get_child_by_name('system_available_ram').change_text(info['system_available_ram'])        
                self.debug_panel.get_child_by_name('system_disk_usage').change_text(info['system_disk_usage'])        
                self.debug_panel.get_child_by_name('mouse_abs_pos').change_text(f">{self.current_state.mouse.pos}<")        

                m_path_txt = self.debug_panel.get_child_by_name('mouse_path')        
                if self.debug_panel.rect.collidepoint(self.current_state.mouse.pos):
                    m_path_txt.change_text(" > ".join([kid.name if kid.name else str(kid) for kid in self.debug_panel.mouse_stack]))
                else:
                    m_path_txt.change_text(" > ".join([kid.name if kid.name else str(kid) for kid in self.current_state.root.mouse_stack]))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ throw away methods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def switch_fullscreen(self, value):
        self._fullscreen = value
        self.update_screen()

    def switch_scaled(self, value):
        self._scaled = value
        self.update_screen()

    def change_dpanel_opacity(self, value, mouse=None):
        self.debug_panel.set_opacity(value)


                
if __name__ == '__main__':
    Core().run()



