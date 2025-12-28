from src.settings import SW, SH
from .panel import Panel, ScrollablePanel
from .list import HList, VList
from src.ui.leaf import Button, Text


# page color   : #eec39a
# page shadow  : #d19f71
# font color 1 : #b96d4a 
# font color 2 : #bb3736
# font color 3 : #dd936e
# font color 4 : #e06363
def empty_popup_gen(size=(300, 200), bg_color="#eec39a", scroll=False, **kwargs):

    panel_cls = Panel if not scroll else ScrollablePanel
    panel = panel_cls(size=size, bg_color=bg_color, border_radius=0, show_border=True, border_color="#d19f71", border_width=2, **kwargs)
    panel.hover_border_color = '#b96d4a'
    panel.move_to_by_center((SW/2, SH/2))
    vlist = VList(pos=(0,0),size=(260, 180), h_gap=0, v_gap=4)
    vlist.show_border = False
    vlist.move_to_by_center((panel.rect.width/2, panel.rect.height/2))
    
    panel.add_child(vlist)
    return panel, vlist

def confirm_popup_gen(title , confirmation_text, on_confirm_func=None, on_cancel_func=None):
    panel, vlist = empty_popup_gen()
    vlist.v_gap = 12
    vlist.add_child(Text(title, font_size='xxbig', wrap_width=vlist.rect.width, align='mid', color="#bb3736"))
    vlist.add_child(Text(confirmation_text, font_size='mid', wrap_width=vlist.rect.width, align='mid', color="#b96d4a"))
    hlist = HList(h_gap=40)
    hlist.show_border = False
    s = (60, 25)
    btn_yes = Button(text='Yes', size=s, back_color="#00000000",fore_color="#bb3736", border_color="#bb3736", func=on_confirm_func)
    btn_no = Button(text='No', size=s, back_color="#00000000", fore_color="#b96d4a", border_color="#b96d4a", func=on_cancel_func)
    hlist.add_child(btn_yes)
    hlist.add_child(btn_no)
    vlist.add_child(hlist)
    hlist.move_to_by_center((vlist.rect.width/2, hlist.rect.centery + 20))
    return panel
    

class PopPanel(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,pos=(0, 0), size=(SW, SH), bg_color="#000000e2",**kwargs)

    @classmethod
    def with_confirm_popup(cls, title="Title" , confirmation_text="confirmation text..", on_confirm_func=None,
                           on_cancel_func=None, **kwargs):
        pop_panel = PopPanel(**kwargs)
        if not on_cancel_func:
            on_cancel_func=lambda: pop_panel.func() or pop_panel.on_click(None)
        else:
            # without this i get a recursion error cuz lambda keeps calling themselves
            og_on_cancel_func = on_cancel_func
            on_cancel_func=lambda: og_on_cancel_func() or pop_panel.on_click(None)
        if not on_confirm_func:
            on_confirm_func=lambda: print('confirm') or pop_panel.on_click(None)
        else:
            og_on_confirm_func = on_confirm_func
            on_confirm_func=lambda: og_on_confirm_func() or pop_panel.on_click(None)


        popup = confirm_popup_gen(title , confirmation_text, on_confirm_func, on_cancel_func)
        pop_panel.add_child(popup)
        return pop_panel

    @classmethod
    def with_empty_panel(cls, *children, size=(300, 200), **kwargs):
        panel, vlist = empty_popup_gen(size=size, **kwargs)
        for child in children:
            vlist.add_child(child)
        # incase u wanna add them ur self
        pop_panel = PopPanel()
        pop_panel.add_child(panel)
        return pop_panel, panel, vlist
    
    def func(self):
        pass
        #print('im destroied')

    def handle_mouse(self, mouse, _mouse_offset=(0, 0)):
        #print(f"\033[94m mouse pos {mouse.pos} mouse offset {_mouse_offset}\033[0m")
        returned = super().handle_mouse(mouse, _mouse_offset)
        
        return returned

    def on_click(self, mouse):
        self.func()
        self.die()
