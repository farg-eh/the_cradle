import pygame
from src.ui import Panel, Group, UiElement, HList, Button
from src.settings import SW, SH
from src.utils import Pos

# this class is specifc to the editor and is used to reduce the clutter in the editor.py file
# it will handle the overlay and somem of its functions
class Overlay:
    def __init__(self, editor):
        self.editor = editor

        # self.toolbar
        self.toolbar_buttons = [['pin', 'layers','grid', 'save'], ['zoom', 'bucket', 'pen', 'select', 'move'], ['questionmark','left', 'right', 'settings_1', 'x']]
        self.toolbar = HList((265, 0), name= 'toolbar', border_color='gray',bg_color=(12, 12, 12, 48), h_gap=20, border_radius_list=[0, 0, 0, 8], border_width=1)
        for btn_list in self.toolbar_buttons:
            hlist = HList(h_gap=0)
            for btn in btn_list:
                img = self.editor.assets['icons'][f"{btn}.png"]
                name = btn
                icon = Icon(img=img, name=name)
                self.set_icon_settings(icon, name)
                hlist.add_child(icon)
            self.toolbar.add_child(hlist)

        self.editor.root.add_child(self.toolbar)
        self.toolbar.show_border=False
        #for icon_name, icon_img in self.editor.assets['icons'].items():
        #    self.toolbar.add_child(Icon(img=icon_img, name=icon_name.split('.')[0]))
        


    def draw(self, surf):
        self.screen_panel.draw(surf)

    def update(self, dt, mouse):
        #self.screen_panel.update(dt, mouse)
        print(f'toolbar: {self.toolbar.pos}')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ icon throw away functions ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def set_icon_settings(self, icon, name):
        if name == 'pen':
            icon.on_click = self.pen_func

    def pen_func(self, mouse=None):
        self.selected_item = 'pen'
        self.editor.root.get_child_by_name('pen').change_color('yellow')


class Icon(UiElement):
    def __init__(self, pos=Pos(0, 0), size=(16, 16), img=None, name="icon", color='white'):
        self.img = img.copy()
        self.color = color
        self.change_color(color)
        self.size = size if not self.img else self.img.size
        super().__init__(pos=pos, size=size, name=name, margin=(4, 6))

    def change_color(self, color):
        c = pygame.Color(color)
        c.a = 255
        self.img.fill(c, special_flags=pygame.BLEND_RGBA_MULT)

    def draw(self, surf):
        super().draw(surf)
        if self.img:
            surf.blit(self.img, self.rect.topleft)

    def update(self, dt, mouse):
        super().update(dt, mouse)
