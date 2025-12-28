from src.settings import FONTS
from src.utils import  Rect
from src.ui.branch import Panel
from .text import Text

        
class TextField(Panel):
    def __init__(self,pos=(180,100), width=140, text='',placeholder="empty", border_radius=4,  color='white', selected_color='#f75402', font_size='small',
                 name='', parent=None, padding=(5, 5), margin=(0, 0), text_color="white", placeholder_color="gray", text_lang='en', text_align='left'):

        # pre super init calcluations
        font_height_in_px = FONTS[font_size + "-" + text_lang].get_height() 
        size = (width-padding[0]*2, font_height_in_px + padding[1]*2)
        txt_pos = padding[0], size[1]/2 - font_height_in_px/2
        self.txt_padding = padding
        
        super().__init__(pos=pos, size=size, name=name, parent=parent,
                 show_border=True, border_width=2, border_color=color, border_radius=border_radius, border_radius_list=[0, 0, 0, 0],
                 bg_color=(0, 0, 0, 0), hoverable=False)

        self.value = text
        self.is_selected = False
        self.placeholder = placeholder
        txt = self.value if self.value else self.placeholder
        clr = text_color if self.value else placeholder_color
        self.text = Text(pos=txt_pos, text=txt, color=clr, align=text_align)
        self.text.show_border = False
        self.add_child(self.text)
        self.selected_color = selected_color
        self.color = color
        self.placeholder_color = placeholder_color
        self.original_border_color = self.color

        # okay
        self._old_value = self.value

        self._on_select_change()

    def _on_select_change(self):
        if self.is_selected:
            self.root.curr_selected_input_element = self
            self.border_color = self.selected_color

            self._old_value = self.value
        else:
            self.root.curr_selected_input_element = None
            if self._old_value != self.value:
                self.func() 
            self.border_color = self.color
            self._adjust_text_view(reset=True)

        if self.value:
            c = self.selected_color if self.is_selected else self.color
            self.text.change_color(c)
        else:
            self.text.change_color(self.placeholder_color)

    def _adjust_text_view(self, reset=False):
        rect = Rect(0, 0, self.rect.width, self.rect.height)
        # reset snaps it back to its original view
        if reset:
            self.text.move_to((rect.left+self.txt_padding[0], self.text.rect.top))
            return
        # a version of the rect that has relative positions
        if self.text.get_size()[0] > rect.size[0]:
            #self.text.rect.right = rect.right - self._padding[0]
            self.text.move_to_by_topright((rect.right-self.txt_padding[0], self.text.rect.top))
        elif self.text.get_size()[0] < rect.size[0]:
            self.text.move_to((rect.left+self.txt_padding[0], self.text.rect.top))

    def _on_value_change(self):
        value = self.value if self.value else self.placeholder if self.placeholder else self.name if self.name else self.__str__()
        self.text.change_text(value)

        if not self.value:
            self.text.change_color(self.placeholder_color)
        else:
            self.text.change_color(self.selected_color)

        self._adjust_text_view()

    def func(self):
        print(self.value)


    def on_keyboard_input(self, char):
        # on backspace
        if char in ['\b'] and self.value:
            self.value = self.value[:-1]
        # on enter
        elif char in ['\r', '\n']:
            self.is_selected = False
            self._on_select_change()
            return
        elif char.isalpha() or char in " ?!@#$%^&*()_+<>{}[]":
            self.value += char
        self._on_value_change()


    def on_click(self, mouse):
        super().on_click(mouse)
        # deselect the current textfield on the root element if it exists
        if self.root.curr_selected_input_element and self.root.curr_selected_input_element is not self:
            self.root.curr_selected_input_element.is_selected = False
            self.root.curr_selected_input_element._on_select_change()

        self.is_selected = True
        self._on_select_change()


    def update(self, dt, mouse=None):
        super().update(dt, mouse)
        # disable selection if click outside box
        #print('hi')
        #if self.is_selected:
         #   if mouse and mouse.l_click:
         #       if not self.rect.collidepoint(mouse.pos):
         #           self.is_selected = False
         #           self._on_select_change()

    def draw(self, surf):
        super().draw(surf)
        #pygame.draw.circle(surf, 'black', self.rect.midright, 2)
                
class NumberField(TextField):
    def __init__(self, *args,allow_float=False, placeholder="0", **kwargs):
        super().__init__(*args,placeholder=placeholder, **kwargs)
        self.allow_float = allow_float

    def on_keyboard_input(self, char):
        # backspace
        if char == '\b' and self.value:
            self.value = self.value[:-1]

        # enter
        elif char in ['\r', '\n']:
            self.is_selected = False
            self._on_select_change()
            return  # avoid undoing reset

        # allow only digits and optionally one dot (for floats)
        elif char.isdigit():
            self.value += char
        elif self.allow_float and char == '.' and '.' not in self.value:
            self.value += char

        self._on_value_change()

