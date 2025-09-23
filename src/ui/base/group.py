from .ui_element import UiElement


class Group(UiElement):
    def __init__(self, pos=(0, 0), size=(0, 0), name='', parent=None, 
                 clickable=True, hoverable=True, scrollable=False, padding=(0, 0), margin=(0, 0),
                 show_border=False, hidden=False, border_width=1, border_color='white' ):
        super().__init__( pos=pos, size=size, name=name, parent=parent, 
                 clickable=clickable, hoverable=hoverable, scrollable=scrollable, padding=padding, margin=margin,
                 show_border=show_border, hidden=hidden, border_width=border_width, border_color=border_color )

        self.root = self

        self.mouse_stack = []
        self.children = []
        self.named_children = {}

    def add_child(self, ui_element):
        self.children.append(ui_element)
        ui_element.parent = self
        ui_element.root = self.root
        # add it to named children for easy access later
        if ui_element.name:
            if self.root.named_children.get(ui_element.name):
                self.root.named_children[ui_element.name].append(ui_element)
            else:
                self.root.named_children[ui_element.name] = [ui_element]

        # TODO
        # now i should check if what i added is a group
        # if its a group imma check if the children know the correct root
        # if they do they we skip if not
        # we traverse all of them and correct that 
        # any named_children should be move to the new root named_children
        if hasattr(ui_element, 'children'):
            if ui_element.children:
                if ui_element.children[0].root != self.root:
                    for child in ui_element:
                        child.root = self.root
                    if ui_element.named_children:
                        self.root.named_children |= ui_element.named_children
                        ui_element.named_children = {}

        
    def remove_child(self, ui_element):
        self.children.remove(ui_element)
    
    def get_children_by_name(self, name):
        """returns a list of children that have the name if found else returns None"""
        return self.root.named_children.get(name)

    def get_child_by_name(self, name):
        kids = self.get_children_by_name(name)
        return kids[0] if kids else None

    def _porcess_mouse_events(self, mouse):
        # handle on hover
        self.on_hover(mouse)

        # if this is the root element
        if self == self.root and self.mouse_stack:
            top_element = self.mouse_stack[-1]
            # handle on_click
            if mouse.l_up_once:
                click_winner = top_element
                while click_winner != None:
                    if click_winner.clickable:
                        click_winner.on_click(mouse)
                        break
                    else:
                        click_winner = click_winner.parent
            # hanlde on_scroll
            if mouse.wheel_dir != 0:
                scroll_winner = top_element
                while scroll_winner != None:
                    if scroll_winner.scrollable:
                        scroll_winner.on_scroll(mouse)
                        break
                    else:
                        scroll_winner = scroll_winner.parent

    def handle_mouse(self, mouse):
        # clear the mouse stack each loop 
        if self == self.root:
            self.root.mouse_stack.clear()
        # if mouse is inside this
        if self.rect.collidepoint(mouse.pos):
            self.mouse_inside = True
            # if the mouse stack is empty or this is not the top element
            if not self.root.mouse_stack or self.root.mouse_stack[-1] != self:
                # add this to the top of the stack
                self.root.mouse_stack.append(self)

            if self.root.mouse_stack[-1] == self:
                # loop through kids in reverse order (last added is first to be checked)
                for child in reversed(self.children):
                    if child.hidden: continue
                    # TODO: what if the child is a group that is not clickable or hoverable or scrollable but has children
                    if (hasattr(child, 'children') and child.children) or child.clickable or child.hoverable or child.scrollable:
                        # if mouse is in that child then there is no need to check the others
                        mouse_in = child.handle_mouse(mouse)
                        if mouse_in:
                            break

        # handle mouse events for the element
        self._porcess_mouse_events(mouse)
        
        m_in = self.mouse_inside
        self.mouse_inside = False
        return m_in
            
    def draw(self, surf):
        if self.hidden: return
        super().draw(surf) # will draw the border if show_border enabled
        for child in self.children:
                child.draw(surf)

    def update(self, dt, mouse=None):
        if self.hidden: return
        if self.root == self:
            self.handle_mouse(mouse)

        for child in self.children:
            child.update(dt, mouse)


    def __iter__(self):
        yield self
        for child in self.children:
            if isinstance(child, Group):
                yield from child
            else:
                yield child
