import pygame
import weakref
from src.states.testyard import PopPanel
from src.ui import Panel, Group, UiElement, HList, Button, ScrollablePanel, VList, Text, PopPanel, TextField, ImageBox
from src.settings import SW, SH
from src.ui.branch.list import VList
from src.ui.leaf.radio import RadioList
from src.utils import Pos, Timer, get_abs_pos, get_rel_pos
from src.utils.lerp import smooth_step_lerp

# this class is specifc to the editor and is used to reduce the clutter in the editor.py file
# it will handle the overlay and somem of its functions
class Overlay:
    def __init__(self, editor):
        self.editor = editor

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ toolbar ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # important bits
        self.selected_item = 'pen'  # selectable items are pen, move, seleect, bucket, 
        self.show_layers = True
        self.gray_items = ['select']
        # self.toolbar
        self.toolbar_panel = HidingPanel() # will be replaced later
        self.toolbar_buttons = [['pin', 'layers','grid', 'save'], ['zoom', 'bucket', 'pen', 'select', 'move'], ['i','left', 'right', 'settings_1', 'x']]
        self.toolbar = HList((0, 0), name= 'toolbar', border_color='gray',bg_color=(12, 12, 12, 48), h_gap=20, border_radius_list=[0, 0, 12, 12], border_width=1)
        # fill it 
        for btn_list in self.toolbar_buttons:
            hlist = HList(h_gap=0)
            for btn in btn_list:
                img = self.editor.assets['icons'][f"{btn}.png"]
                name = btn
                icon = Icon(img=img, name=name)
                if name in self.gray_items:
                    icon.change_color('gray36')
                self.set_icon_settings(icon, name)
                hlist.add_child(icon)
            self.toolbar.add_child(hlist)


        # hiding and showing
        to_the_left_offset = 32
        show_pos = SW/2-self.toolbar.margin_rect.width//2-to_the_left_offset, 0
        hide_pos = SW/2-self.toolbar.margin_rect.width//2-to_the_left_offset, -self.toolbar.margin_rect.height-2
        self.toolbar_panel = HidingPanel(pos=show_pos, hide_pos=hide_pos, size=self.toolbar.margin_rect.size)
        self.toolbar_panel.add_child(self.toolbar)
        # add to root 
        self.editor.root.add_child(self.toolbar_panel)
    
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ layers panel ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.temp_thingy_for_closure = None
        self.thingy_list = []

        lpanel_size = (160, 200)
        lpanel_pos = SW - lpanel_size[0], SH/2 - 80
        lpanel_hide_pos = SW-2, lpanel_pos[1]

        self.layers_container = ScrollablePanel(size=(lpanel_size[0]-10, lpanel_size[1]-33), margin=(8, 25), show_border=False, bg_color=(12, 12, 12, 28))
        self.layers_list = VList(show_border=False, padding=(5, 5), v_gap=3)
        # fill layer list
        for layer_name,layer in sorted(list(self.editor.tilemap.layers.items()), key=lambda x: x[1]['index'])[::-1]:
            l = self.gen_layer_element(layer_name, layer)
            self.layers_list.add_child(l)
            

        #layer1 = HList(size=(140, 30), show_border=True)
        opt_con = Icon(pos=Pos(0, 0), img=self.editor.assets['icons']['settings_2.png'], name='options')
        

        # layers panel icons
        self.layers_pin_icon = Icon(pos=Pos(5, 0), img= self.editor.assets['icons']['pin.png'], name='layers_pin')
        settings_icon = Icon(pos=Pos(5+self.layers_pin_icon.margin_rect.width+5, 0),img= self.editor.assets['icons']['settings_1.png'], name='layers_settings')
        add_icon = Icon(pos=Pos(5+(self.layers_pin_icon.margin_rect.width+5)*2, 0),img= self.editor.assets['icons']['add_1.png'], name='layers_add')
        # icon on click funcs
        self.layers_pin_icon.on_click = self.layers_pin_func
        settings_icon.on_click = self.layers_settings_func
        add_icon.on_click = self.layers_add_func


        self.layers_panel = HidingPanel(pos=lpanel_pos, hide_pos=lpanel_hide_pos, size=lpanel_size, bg_color=(12, 12, 12, 48), border_radius_list=[12, 0, 0, 12], transition_duration=400)
        self.layers_panel.add_child(self.layers_container)
        self.layers_panel.add_child(self.layers_pin_icon)
        self.layers_panel.add_child(settings_icon)
        self.layers_panel.add_child(add_icon)
        
        self.layers_container.add_child(self.layers_list)
        #layers_list.add_child(layer1)
        self.editor.root.add_child(self.layers_panel)

        c = 'red' if self.layers_panel.pinned else 'white'
        self.layers_pin_icon.change_color(c)




        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ items panel and other things  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        pp, p, vl = PopPanel.with_empty_panel(bg_color=(12, 12, 12, 48), padding=(2, 2), scroll=True)
        pp.die = lambda : setattr(pp, 'hidden', True)

        img = self.editor.assets[self.editor.tile_list[self.editor.tile_group]][self.editor.tile_variant]
        self.curr_item_box = ImageBox(pos=(5, 5), size=(30, 30), img=img, show_border=True, border_color=(12, 12, 12, 48), border_radius=4, padding=(3, 3), bg_color=(12, 12, 12, 48))
        self.curr_item_box.on_click = lambda mouse: setattr(pp, 'hidden', False)
        self.editor.root.add_child(self.curr_item_box)

        items_list = HList(h_gap=4, max_width=vl.padding_rect.width)
        self.test = items_list
        img_box_kwargs = {'size': (40, 40), "bg_color": "#121212aa"}
        for asset_type in self.editor.tile_list:
            for i, surf in enumerate(self.editor.assets[asset_type]):
                group = self.editor.tile_list.index(asset_type)
                img_b = ImageBox(img=surf, **img_box_kwargs)
                img_b.on_click = lambda mouse, index=i, group=group: setattr(self.editor, "tile_group", group) or setattr(self.editor, 'tile_variant', index)
                img_b.show_border = False
                items_list.add_child(img_b)
        sp = ScrollablePanel()
        sp.add_child(items_list)
        vl.add_child(items_list)
        self.editor.root.add_child(pp)

        self.items_dock = HList(pos=(20, 20), h_gap=4)
        self.dock_values = {}
        self.items_dock_curr_box = None
        for i in range(1,9+1):
            img_b = ImageBox(img=Text(f"{i}").surf, **img_box_kwargs)
            img_b.on_click = self.set_item_dock_func(img_b, i)
            img_b.show_border = False
            self.items_dock.add_child(img_b)
        self.items_dock_curr_box = self.items_dock.children[0]

        pp.add_child(self.items_dock)





        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ other ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def draw(self, surf):
        # pygame.draw.rect(surf, 'brown', self.tbar_hitbox_rect, 1)
        #print(f"{self.test.rect.size} hmm")
        pass

    def update(self, dt, mouse):
        # TODO: find a better way ~~~~~~~~~~~~~~~~~~~~~~~ (1)
        c = 'red' if self.layers_panel.pinned else 'white'
        self.layers_pin_icon.change_color(c)
        # TODO: find a better way ~~~~~~~~~~~~~~~~~~~~~~~ (2)
        for child in self.layers_list:
            child.border_color = 'white'
            if child.name == self.editor.current_layer:
                child.border_color = 'red'


    # FIXME this is causing a memory leak
    def _update_layers_elements(self):
        # clear
        #print("hellooo")
        #self.layers_list.clear()
        self.thingy_list.clear()
        # FIXME: clearing lists doesnt work properly that why im making a whole new object
        self.layers_container.remove_child(self.layers_list)
        self.layers_list.die()
        self.layers_list = VList(show_border=False, padding=(5, 5), v_gap=3)
        self.layers_container.add_child(self.layers_list)
        #print(self.layers_list.children)
        # refill
        for layer_name,layer in sorted(list(self.editor.tilemap.layers.items()), key=lambda x: x[1]['index'])[::-1]:
            l = self.gen_layer_element(layer_name, layer)
            self.layers_list.add_child(l)
       # print(self.layers_list.children)
        #print("thats it")

    def set_curr_tile(self, dock_index):
        if dock_index in self.dock_values:
            tile_group, tile_variant = self.dock_values[dock_index]
            self.editor.tile_group = tile_group
            self.editor.tile_variant = tile_variant
    def set_dock_tile(self, dock_index):
        if dock_index >9: return
        img_box = self.items_dock.children[dock_index]
        self.set_item_dock_func(img_box, dock_index)(mouse=None)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ element generators ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def gen_layer_element(self, layer_name, layer):
        weak_self = weakref.proxy(self)
        l = HList(size=(142, 30), show_border=True, border_radius=5, clickable=True,hoverable=False, name=layer_name)
        l.on_hover = lambda mouse=None: None
        l.hover_border_color = 'yellow' 
        eye_type = 'eye_open.png' if not layer.get('hidden') else 'eye_closed.png'
        eye_con = Icon(pos=Pos(0, 0), img=weak_self.editor.assets['icons'][eye_type], name='eye')
        #eye_con_closed = Icon(pos=Pos(0, 0), img=self.editor.assets['icons']['eye_closed.png'], name='eye')
        opt_con = Icon(pos=Pos(0, 0), img=weak_self.editor.assets['icons']['settings_2.png'], name='options')
        txt = Text(layer_name, font_size='mid', margin=(4, 2))
        eye_con.on_click = weak_self.layer_eye_func(eye_con, layer_name,
                                               [weak_self.editor.assets['icons']['eye_open.png'],
                                                weak_self.editor.assets['icons']['eye_closed.png']])
        opt_con.on_click = weak_self.layer_settings_func(layer_name)  # FIXME this is causing a memory leak
        l.add_child(eye_con)
        l.add_child(opt_con)
        l.add_child(txt)
        l.on_click = weak_self.layer_press_func(layer_name)
        return l


    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ icon throw away functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_icon_settings(self, icon, name):
        if name == self.selected_item:
            icon.change_color('yellow')

        # tools
        if name == 'pen':
            icon.on_click = self.pen_func
        elif name == 'bucket':
            icon.on_click = self.bucket_func
        elif name == 'move':
            icon.on_click = self.move_func

        # toggles
        elif name == 'grid':
            c = 'pink' if self.editor.show_grid else 'white'
            icon.change_color(c)
            icon.on_click = self.grid_func
        elif name == 'layers':
            c = 'pink' if self.show_layers else 'white'
            icon.change_color(c)
            icon.on_click = self.layers_func
        elif name == 'pin':
            c = 'red' if self.toolbar_panel.pinned else 'white'
            icon.change_color(c)
            icon.on_click = self.toolbar_pin_func

        # buttons
        elif name == 'save':
            icon.on_click = self.save_func
        elif name == 'zoom':
            icon.on_click = self.zoom_func

        # not set yet
        elif name == 'x':
            icon.on_click = self.x_func
        
        elif name == 'i':
            icon.on_click = self.i_func

        elif name == 'left':
            icon.on_click = self.left_func

        elif name == 'right':
            icon.on_click = self.right_func

        elif name == 'settings_1':
            icon.on_click = self.settings_func

    # items 
    def pen_func(self, mouse=None):
        self.editor.root.get_child_by_name(self.selected_item).change_color('white')
        self.selected_item = 'pen'
        self.editor.root.get_child_by_name('pen').change_color('yellow')

    def bucket_func(self, mouse=None):
        self.editor.root.get_child_by_name(self.selected_item).change_color('white')
        self.selected_item = 'bucket'
        self.editor.root.get_child_by_name(self.selected_item).change_color('yellow')

    def move_func(self, mouse=None):
        self.editor.root.get_child_by_name(self.selected_item).change_color('white')
        self.selected_item = 'move'
        self.editor.root.get_child_by_name('move').change_color('yellow')

    # toggles
    def grid_func(self, mouse=None):
        self.editor.show_grid = not self.editor.show_grid
        color = 'white' if not self.editor.show_grid else 'pink'
        self.editor.root.get_child_by_name('grid').change_color(color)
    
    def layers_func(self, mouse=None):
        self.show_layers = not self.show_layers
        color = 'white' if not self.show_layers else 'pink'
        self.editor.root.get_child_by_name('layers').change_color(color)

        # not really nessassary since im doing it every frame in the update method right now but might help as a hint in the future 
        layers_pin_icon = self.editor.root.get_child_by_name('layers_pin')
        if layers_pin_icon:
            c = 'white' if not self.layers_panel.pinned else 'red'
            layers_pin_icon.change_color(c)
        # ~~~~~~~~~~~~~~~~~~
        
        if self.show_layers:
            self.layers_panel.show_now()
        else:
            self.layers_panel.hide_now()
        #self.layers_panel.pinned = self.show_layers
        #self.layers_panel.hidden = not self.show_layers
        #if self.layers_panel.hide_state == 'hiding':
        #    self.layers_panel.transition_timer.func = lambda: (self.layers_panel.transition_timer.func, self.layers_pin_func)

    def toolbar_pin_func(self, mouse=None):
        self.toolbar_panel.pinned  = not self.toolbar_panel.pinned
        color = 'white' if not self.toolbar_panel.pinned else 'red'
        self.editor.root.get_child_by_name('pin').change_color(color)

    # btns
    def save_func(self, mouse=None):
        self.editor.tilemap.save(self.editor.map_name)
        self.editor.last_change_saved = True

    def zoom_func(self, mouse=None):
        self.editor.camera.cycle_zoom_level_forward()

    def x_func(self, mouse=None):
        print('X')
        if not self.editor.last_change_saved:
            conf_title = "Warning"
            conf_txt = "are you sure you want to leave without saving ?"
            conf_func = lambda: self.editor.core.switch_state('menu')
            self.editor.root.add_child(PopPanel.with_confirm_popup(title=conf_title, confirmation_text=conf_txt, on_confirm_func=conf_func))
        else:
            self.editor.core.switch_state('menu')

    def i_func(self, mouse=None):
        print('info')

    def settings_func(self, mouse=None):
        print('settings')
        
    def left_func(self, mouse=None):
        print('left')

    def right_func(self, mouse=None):
        print('right')


    # layers panel icons funcs
    def layers_pin_func(self, mouse=None):
        self.layers_panel.pinned  = not self.layers_panel.pinned
        color = 'white' if not self.layers_panel.pinned else 'red'
        self.editor.root.get_child_by_name('layers_pin').change_color(color)

    def layers_settings_func(self, mouse=None):
        print('settings of layers')

    def layers_add_func(self, mouse=None):
        print('add layers')
        pop_panel, panel, vlist = PopPanel.with_empty_panel()
        vlist.v_gap = 10
        centerx = vlist.padding_rect.width/2

        title = Text("add layer", color="#dd936e", font_size="big")
        vlist.add_child(title)

        layer_name = "new_layer"
        layer_name_tf = TextField(text=layer_name, width=100, color="#b96d4a", placeholder="layer_name",text_color="#eec39a", selected_color="#bb3736" )
        layer_name_tf.bg_color = "#de946e"
        layer_name_tf.func=lambda: print(f"haaaaaaaaaaaa2")
        vlist.add_child(layer_name_tf)

        radio = RadioList(options=['tiles', 'meta_info', 'objects'])
        vlist.add_child(radio)


        add_btn = Button(text='add', size=(80, 25), back_color="#00000000",fore_color="#bb3736", border_color="#bb3736",
                         func=lambda:self.editor.add_layer(layer_name_tf.value, radio.selected_box.name+"_layer") or pop_panel.die())
        vlist.add_child(add_btn)

        # center elements
        for child in vlist.children:
            child.move_to_by_center((centerx, child.rect.centery))
        
        self.editor.root.add_child(pop_panel)

    # layer specific funcs
    def layer_press_func(self, layer_name):
        def func(mouse=None):
            self.editor.current_layer = layer_name
        return func

    def layer_eye_func(self, icon,layer_name, eye_imgs):

        def func(mouse=None):
            layer = self.editor.tilemap.layers[layer_name]
            if layer.get('hidden') == None:
                layer['hidden'] = False
            # eye_imgs has [eye_open, eye_closed]
            layer['hidden'] = not layer['hidden']
            icon_img = eye_imgs[0] if not layer['hidden'] else eye_imgs[1]
            icon.change_img(icon_img)
        return func

# page color   : #eec39a
# page shadow  : #d19f71
# font color 1 : #b96d4a 
# font color 2 : #bb3736
# font color 3 : #dd936e
# font color 4 : #e06363
    def layer_settings_func(self, layer_name):
        # to avoid memory leak we will use weakref
        weak_self= weakref.proxy(self)


        # create pop panel and its content
        pop_panel, panel, vlist = PopPanel.with_empty_panel()
        vlist.v_gap = 10
        centerx = vlist.padding_rect.width/2

        self.temp_thingy_for_closure = pop_panel
        self.thingy_list.append(pop_panel)
        weak_pop_panel = weakref.proxy(pop_panel)

        title = Text("Settings", color="#dd936e", font_size="big")
        vlist.add_child(title)


        layer_name_tf = TextField(text=layer_name, width=100, color="#b96d4a", placeholder="layer_name",text_color="#eec39a", selected_color="#bb3736" )
        layer_name_tf.bg_color = "#de946e"
        layer_name_tf.func=lambda: print(f"haaaaaaaaaaaa")
        layer_name_label = Text("name : ", font_size="mid", color="#dd936e")
        layer_name_row = HList()
        layer_name_row.add_child(layer_name_label)
        layer_name_row.add_child(layer_name_tf)
        vlist.add_child(layer_name_row)

        btn_kwargs = {'size': (140, 25), 'border_color': '#b96d4a', 'back_color': "black", 'fore_color': "#b96d4a"}
        mvup_btn = Button(text="move up", func=lambda:print(f"\033[91mokay\033[0m"), **btn_kwargs)
        mvdown_btn = Button(text="move down", func=lambda:print(f"\033[91mokay\033[0m"), **btn_kwargs)
        delete_btn = Button(text="delete", func=lambda:print(f"\033[91mokay\033[0m"), **btn_kwargs)
        
        vlist.add_child(mvup_btn)
        vlist.add_child(mvdown_btn)
        vlist.add_child(delete_btn)
        # TODO i didint add functionality yet
        # TODO add callbacks 

        # center children
        for child in vlist.children:
            child.move_to_by_center((centerx, child.rect.centery))


        delete_btn.func = lambda: print('deleted ' + layer_name) or self.editor.remove_layer(
            layer_name) or pop_panel.die()
        mvup_btn.func = lambda: self.editor.move_layer(layer_name,
                                                            direction='down')  # i reversed them here cuz its easier so this is a FIXME
        mvdown_btn.func = lambda: self.editor.move_layer(layer_name, direction='up')
        layer_name_tf.func = lambda: self.editor.rename_layer(layer_name,
                                                                        layer_name_tf.value) or pop_panel.die()

        def func(mouse=None):
            # layer = self.editor.tilemap.layers[layer_name]
            print('EMPTY FUNC')
            print(self.temp_thingy_for_closure)
            if not self.temp_thingy_for_closure:
                return


            weak_self.editor.root.add_child(weak_pop_panel)
            # print(layer['index'])
        return func

    def set_item_dock_func(self, img_b:ImageBox, index):
        def func(mouse, img_box=img_b, idx=index):
            self.items_dock_curr_box.show_border = False
            self.items_dock_curr_box = img_box
            self.items_dock_curr_box.show_border = True
            img_box.change_image(self.editor.assets[self.editor.tile_list[self.editor.tile_group]][self.editor.tile_variant])
            self.dock_values[idx] = (self.editor.tile_group, self.editor.tile_variant)
        return func



class Icon(UiElement):
    def __init__(self, pos=Pos(0, 0), size=(16, 16), img=None, name="icon", color='white'):
        self._original_img = img
        self.img = img.copy()
        self.color = color
        self.change_color(color)
        self.size = size if not self.img else self.img.size
        super().__init__(pos=pos, size=size, name=name, margin=(4, 6))

    def change_color(self, color):
        self.img = self._original_img.copy()
        self.color = pygame.Color(color)
        self.color.a = 255
        self.img.fill(self.color, special_flags=pygame.BLEND_RGBA_MULT)

    def change_img(self, new_img):
        self._original_img = new_img
        self.img = self._original_img.copy()
        self.change_color(self.color)


    def draw(self, surf):
        super().draw(surf)
        if self.img:
            surf.blit(self.img, self.rect.topleft)

    def update(self, dt, mouse):
        super().update(dt, mouse)



class HidingPanel(Panel):
    def __init__(self, pos=(0, 0), hide_pos=(0, 0), size=(110, 110), name="hiding_panel",  border_color='white',
                 border_radius=0, border_radius_list=[0, 0, 0, 0], bg_color=(0, 0, 0, 0), disable_when_hidden=True, transition_duration=300):
        super().__init__(pos=pos, size=size, name=name, border_color=border_color,
                         border_radius=border_radius, border_radius_list=border_radius_list, bg_color=bg_color)
        # state info
        self.disable_when_hidden = disable_when_hidden
        self.pinned = True
        self.hide_state = 'showing'  # options are 'showing' and 'hiding'
        self.targeted_action = 'show' if self.pinned else 'hide'

        # timer
        transition_duration = transition_duration
        self.transition_timer = Timer(transition_duration)

        # hitbox
        self.hitbox_rect = self.rect.inflate(21, 7)

        # positions
        self.show_pos = self.pos
        self.hide_pos = hide_pos

        # an action i wanna do but i cant 
        self.wannado = None # options are show_now and hide_now

    def draw(self, surf):
        super().draw(surf)
        # for debugging
        # pygame.draw.rect(surf, 'brown', self.hitbox_rect, 1)

    def show_now(self):
        if self.transition_timer:
            self.wannado = 'show_now'
            return
        self.hidden = False
        self._show_now(pin=True)

    def _show_now(self, pin=False):
        if self.hide_state == 'showing':
            return

        self.targeted_action = 'show'
        if not pin:
            self.transition_timer.func = lambda : setattr(self, 'hide_state', 'showing')
        else:
            self.transition_timer.func = lambda : setattr(self, 'hide_state', 'showing') or setattr(self, 'pinned', True)
        self.transition_timer.activate()

    def hide_now(self):
        if self.transition_timer:
            self.wannado = 'hide_now'
            return
        self._hide_now(disable_when_hidden=True)

    def _hide_now(self, unpin=True, disable_when_hidden=False):
        if self.hide_state == 'hiding':
            if disable_when_hidden:
                self.hidden = True
            return

        if self.transition_timer:
            self.wannado = 'show_now'
            return

        if unpin:
            self.pinned = False
        
        self.targeted_action = 'hide'
        if disable_when_hidden: 
            self.transition_timer.func = lambda : setattr(self, 'hide_state', 'hiding') or setattr(self, 'hidden', True)
        else:
            self.transition_timer.func = lambda : setattr(self, 'hide_state', 'hiding') 

        self.transition_timer.activate()

    def handle_hiding_and_showing(self, mouse):
        # updates 
        self.transition_timer.update()
        self.hitbox_rect.center = self.rect.center
        #print(f"name: {self.name} pinned: {self.pinned}")
        # shoulds
        if not self.transition_timer.active:
            if self.hitbox_rect.collidepoint(mouse.pos): 
                if self.hide_state == 'hiding':
                    self._show_now()
            else:
                if self.hide_state == 'showing' and not self.pinned:
                    self._hide_now()
        else: # if the timer is active
            # animating
            if self.hide_state == 'showing' and self.targeted_action == 'hide':
                show_pos = Pos(*self.show_pos)
                hide_pos = Pos(*self.hide_pos)
                t = self.transition_timer.get_progress()
                self.move_to(show_pos.lerp(hide_pos, smooth_step_lerp(0, 1, t)))
            elif self.hide_state == 'hiding' and self.targeted_action == 'show':
                show_pos = Pos(*self.show_pos)
                hide_pos = Pos(*self.hide_pos)
                t = self.transition_timer.get_progress()
                self.move_to(hide_pos.lerp(show_pos, smooth_step_lerp(0, 1, t)))


        if not self.transition_timer and self.hide_state=='hiding' and self.wannado:
            if self.wannado == 'show_now':
                self.show_now()

                self.wannado = None

            

    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        self.handle_hiding_and_showing(mouse)






