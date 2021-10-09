# import the pygame module, so you can use it
import pygame

def drawGraph(signal, x_zoom, x_offset, y_offset, screen):
    current = 1
    x = 0

    for i in signal:
        x_end = (x + i) * x_zoom
        y = (100 - current * 100)
        pygame.draw.line(screen, (255, 255, 255), (x * x_zoom + x_offset, y + y_offset),
                         (x_end + x_offset, y + y_offset), 5)

        x += i
        current = (current + 1) % 2

# define a main function
def main():

    file = open('signal_sequences/LOWER')
    signal = []
    for i in file:
        signal.append(int(i))

    x_offset = 10
    y_offset = 10
    x_zoom = 0.01

    # initialize the pygame module
    pygame.init()
    # load and set the logo
    #logo = pygame.image.load("logo32x32.png")
    #pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((3000, 120))

    # define a variable to control the main loop
    running = True

    FPS = pygame.time.Clock()

    # main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEWHEEL:
                x_zoom += event.y / 100
                print('Scrollwheel:', event.y, x_zoom)

        screen.fill((1, 1, 1))
        drawGraph(signal, x_zoom, x_offset, y_offset, screen)
        pygame.display.flip()
        FPS.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()