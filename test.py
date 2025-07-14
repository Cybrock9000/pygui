import pygame as pg
import pygui

if __name__ == "__main__":
    shared = pygui.create({
        "E": "slider",
        "y": "slider",
        "fullscreen": "bool",
        "username": "input"
    })

    pg.init()
    screen = pg.display.set_mode((800, 600))
    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        # Access variables via helper:
        x_val = pygui.get_value("E", 0)
        y_val = pygui.get_value("y", 0)
        username = pygui.get_value("username", "")
        fullscreen = pygui.get_value("fullscreen", False)

        screen.fill((30, 30, 30))
        pg.display.set_caption(f"x={x_val} y={y_val} user={username} fullscreen={fullscreen}")
        pg.display.flip()
        clock.tick(60)

    pg.quit()
