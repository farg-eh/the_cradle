import pygame
from src.ui.branch import VList, HList
from src.ui.base import UiElement
from .checkbox import CheckBox
from .text import Text


# wrapping the checkboxes to style them a bit differently 
# TODO: change the style 
class CheckCircle(CheckBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, surf):
        super().draw(surf)

class RadioList(UiElement):
    """takes in checkboxes and gives them the radio behavior"""
    def __init__(self, pos=(0, 0), options=[], gap=3, name='', parent=None, oriantation="horizontal",**kwargs):
        super().__init__(pos=pos, name=name, parent=parent, **kwargs)
        self.selected_box = None  # the option instance
        self.on_change_func = None # u will use this to handle click events on the boxes u will be passed the clicked element name

        # to store our elements
        self.list = HList(pos=pos, h_gap=gap) if oriantation == "horizontal" else VList(pos=pos, v_gap=gap)
        if options:
            self.add_list_options(options)

    def add_list_options(self, arr: list[tuple[str, str]] | list[str]):

        # array of option_name, option_text
        if isinstance(arr[0], tuple):
            for option_name, option_text in arr:
                self.add_option(option_name=option_name, option_text=option_text)

        # array of option names
        elif isinstance(arr[0], str):
            for option_name in arr:
                self.add_option(option_name=option_name)

        else:
            raise Exception("invalid array of options")

    def add_option(self, option_name: str, option_text: str|None = None):

        option_text = option_name if option_text == None else option_text
        circle_box = CheckCircle(name=option_name)
        # pass a function to the option object 
        circle_box.func = lambda value, option_box=circle_box: self.on_option_selected(option_box)

        # wrap the box with a container and throw the text with it too 
        text = Text(option_text)
        opt_hlist = HList()
        opt_hlist.add_child(circle_box)
        opt_hlist.add_child(text)
        opt_hlist.show_broder = True
        self.list.add_child(opt_hlist)
        for element in opt_hlist.children:
            element.move_to_by_center((element.rect.centerx, opt_hlist.rect.centery))
        
        # If no option is selected yet select the first one 
        if self.selected_box is None:
            self.select(circle_box)

        # adjust size
        self.size = self.list.rect.size
        self.rect = self.list.rect
        self.margin_rect = self.list.margin_rect
        self.padding_rect = self.list.padding_rect

    def on_option_selected(self,  clicked_option_box):
        # ignore clicks on an already selected element
        if self.selected_box == clicked_option_box:
            clicked_option_box.value = True # if u remove this line it will be possible to deselect the box 
            return

        # deselect the old option 
        if self.selected_box is not None:
            self.selected_box.value = False
        
        # select the new option
        clicked_option_box.value = True
        self.selected_box = clicked_option_box
        
        # call the users callback function if its  set
        if self.on_change_func:
            self.on_change_func(self.selected_box.name)


    def select(self, box_to_select):
        for child in self.list.children:
            if isinstance(box_to_select, CheckBox) and box_to_select in child.children:
                self.on_option_selected(box_to_select)
            else:
                print(f"\033[91mWarning: option box {box_to_select} is not a valid checkbox in this RadioList\033[0m")
            
    def selected_by_name(self, name):
        for child in self.list.children:
            for box in child.children:
                if isinstance(child, CheckBox) and box.name == name:
                    self.select(child)
                    return
        print(f"\03S[91mWarning: no option box with name '{name}' in this RadioList\033[0m")

    def handle_mouse(self, mouse):
        self.list.handle_mouse(mouse)
   
    def draw(self, surf):
        super().draw(surf)
        self.list.draw(surf)

    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        self.list.update(dt, mouse)
