import pygame as pg
import multiprocessing

pg.init()
FONT = pg.font.SysFont("Arial", 20)
WHITE = (255, 255, 255)
GRAY = (48, 48, 48)
LIGHT_GRAY = (80, 80, 80)
DARK_GRAY = (30, 30, 30)
GREEN = (0, 200, 0)

_widgets = {}
_scroll_offset = 0

_shared = None  # <--- Store shared dict globally

class TextInput:
    def __init__(self, x, y, w=120, h=30, text=''):
        self.rect = pg.Rect(x, y, w, h)
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pg.K_RETURN:
                self.active = False
            else:
                self.text += event.unicode

    def draw(self, screen, offset):
        rect = self.rect.move(0, offset)
        color = WHITE if self.active else LIGHT_GRAY
        pg.draw.rect(screen, color, rect, 2)
        txt = FONT.render(self.text, True, WHITE)
        screen.blit(txt, (rect.x + 5, rect.y + 5))

class SliderWidget:
    def __init__(self, name, x, y, shared):
        self.name = name
        self.shared = shared
        self.label = FONT.render(name, True, WHITE)
        self.rect = pg.Rect(x + 120, y, 200, 20)
        self.slider_rect = pg.Rect(self.rect.x, y, 10, 20)
        self.dragging = False
        self.input = TextInput(self.rect.right + 100, y, 120, 30, name)

    def draw(self, screen, offset):
        screen.blit(self.label, (20, self.rect.y + offset))
        base = self.rect.move(0, offset)
        pg.draw.rect(screen, LIGHT_GRAY, base)
        slider = self.slider_rect.move(0, offset)
        pg.draw.rect(screen, GREEN, slider)
        val_txt = FONT.render(str(self.shared[self.name]), True, WHITE)
        screen.blit(val_txt, (base.right + 10, base.y))
        self.input.draw(screen, offset)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and self.slider_rect.collidepoint(event.pos[0], event.pos[1] - _scroll_offset):
            self.dragging = True
        elif event.type == pg.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pg.MOUSEMOTION and self.dragging:
            new_x = event.pos[0]
            self.slider_rect.x = max(self.rect.x, min(new_x, self.rect.right - self.slider_rect.width))
            value = int(((self.slider_rect.x - self.rect.x) / (self.rect.width - self.slider_rect.width)) * 1000)
            self.shared[self.name] = value
        self.input.handle_event(event)

class CheckboxWidget:
    def __init__(self, name, x, y, shared):
        self.name = name
        self.shared = shared
        self.label = FONT.render(name, True, WHITE)
        self.rect = pg.Rect(x + 120, y, 20, 20)
        self.input = TextInput(self.rect.right + 100, y - 2, 120, 30, name)

    def draw(self, screen, offset):
        screen.blit(self.label, (20, self.rect.y + offset))
        box = self.rect.move(0, offset)
        pg.draw.rect(screen, WHITE, box, 2)
        if self.shared[self.name]:
            pg.draw.line(screen, GREEN, box.topleft, box.bottomright, 3)
            pg.draw.line(screen, GREEN, box.topright, box.bottomleft, 3)
        self.input.draw(screen, offset)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            box = self.rect.move(0, _scroll_offset)
            if box.collidepoint(event.pos):
                self.shared[self.name] = not self.shared[self.name]
        self.input.handle_event(event)

class InputWidget:
    def __init__(self, name, x, y, shared):
        self.name = name
        self.shared = shared
        self.label = FONT.render(name, True, WHITE)
        self.input = TextInput(x + 120, y, 200, 30, '')

    def draw(self, screen, offset):
        screen.blit(self.label, (20, self.input.rect.y + offset))
        self.input.draw(screen, offset)

    def handle_event(self, event):
        self.input.handle_event(event)
        self.shared[self.name] = self.input.text

def gui_process(shared, config):
    global FONT
    pg.init()
    FONT = pg.font.SysFont("Arial", 20)
    screen = pg.display.set_mode((600, 800))
    pg.display.set_caption("pygui Control Panel")
    clock = pg.time.Clock()

    y = 50
    for name, typ in config.items():
        if typ == "slider":
            _widgets[name] = SliderWidget(name, 50, y, shared)
            shared[name] = 0
        elif typ == "bool":
            _widgets[name] = CheckboxWidget(name, 50, y, shared)
            shared[name] = False
        elif typ == "input":
            _widgets[name] = InputWidget(name, 50, y, shared)
            shared[name] = ''
        y += 60

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return
            if event.type == pg.MOUSEWHEEL:
                global _scroll_offset
                _scroll_offset += event.y * 30
            for widget in _widgets.values():
                widget.handle_event(event)

        screen.fill(GRAY)
        for widget in _widgets.values():
            widget.draw(screen, _scroll_offset)
        pg.display.flip()
        clock.tick(60)

def create(vars: dict):
    global _shared
    manager = multiprocessing.Manager()
    _shared = manager.dict()
    p = multiprocessing.Process(target=gui_process, args=(_shared, vars), daemon=True)
    p.start()
    return _shared

def get_value(name, default=None):
    if _shared is None:
        return default
    return _shared.get(name, default)
