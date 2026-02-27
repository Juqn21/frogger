class State:
    def __init__(self, game):
        self.game = game

    def on_enter(self): pass
    def update(self, dt): pass
    def render(self, surface): pass
    def handle_events(self, events): pass