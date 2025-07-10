class State:
    def __init__(self, core,  state_name):
        self.state_name = state_name
        self.core = core
        self.switch_state = core.switch_state
    def handle_input(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self):
        pass
