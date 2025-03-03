import sys
import pygame
import tkinter as tk
from tkinter import messagebox
from .utils import path_convertor, block_keyboard, open_link

def show_error():
    pygame.init()
    
    pygame.mouse.set_visible(False)

    audio_path = path_convertor("assets/audio/error_audio.mp3")
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()

    image_path = path_convertor("assets/misc/error_image.png")
    image = pygame.image.load(image_path)
    image_width, image_height = image.get_size()

    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.SWSURFACE)
    screen_width, screen_height = pygame.display.get_surface().get_size()

    scale_factor = min(screen_width / image_width, screen_height / image_height)
    scaled_width = int(image_width * scale_factor)
    scaled_height = int(image_height * scale_factor)

    x = (screen_width - scaled_width) // 2
    y = (screen_height - scaled_height) // 2

    image = pygame.transform.smoothscale(image, (scaled_width, scaled_height))


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))
        screen.blit(image, (x, y))
        pygame.display.flip()
    
    print("Damn, you figured it out")
    
    pygame.quit()
    sys.exit()
    

def error_main():
    block_keyboard()
    show_error()
    
def message_box():
    root = tk.Tk()
    root.withdraw()
    result = messagebox.askquestion("Friend Request", "Will you be my friend?")

    if result.lower()=="yes":
        open_link("https://linktr.ee/arpy8")
    
    elif result.lower()=="no":
        error_main()