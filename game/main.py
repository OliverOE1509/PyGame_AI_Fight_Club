from game import GridGame

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
FPS = 60

game = GridGame(window_width = WINDOW_WIDTH, window_height = WINDOW_HEIGHT, fps = FPS, sound = True)

while True:
    game.step()