from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import json
import argparse
import webbrowser
import time, random
from .utils import *
from termcolor import colored
from .video import execute_video
from .music import main as music_main


def type_text(text):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(random.uniform(0.13,0.5))

def get_input():
        will_you_text = colored('Will you? ', 'red', attrs=['reverse', 'blink'])
        print(will_you_text, end=" ")
        user_input = input()
        
        if user_input.lower() in ["yes", "y"]:
            play_audio('assets/audio/yes_audio.mp3')
            webbrowser.open('https://www.linktr.ee/arpy8')
            
        elif user_input.lower() in ["no", "n"]:
            ip = get_ip_address()
            colored_ip = colored(ip, 'red') 
            type_text(colored_ip)
        else: get_input()

def main():
    parser = argparse.ArgumentParser(description="Hi, I'm Arpit. This is a library solely based on who I am.")
    # parser.add_argument("-d", "--desc", action="store_true", help="gives a description of me.")    
    parser.add_argument("-d", "--desc", action="store_true", help="gives a description of me.")    
    parser.add_argument("-m", "--music", action="store_true", help="plays my favourite music.")    
    parser.add_argument("-l", "--links", action="store_true", help="redirects to my link tree.")
    parser.add_argument("-w", "--website", action="store_true", help="redirects to my website.")

    args = parser.parse_args()

    if args.desc:
        with open(path_convertor('assets/misc/data.json')) as json_file:
            data = json.load(json_file)
        print(data["desc"])
        
    if args.music:
        music_main()
        
    if args.links:
        webbrowser.open("https://arpy8.com/gallery")
        play_audio("assets/audio/yes_audio.mp3")
        
    if args.website:
        webbrowser.open("https://arpy8.com/")
        play_audio("assets/audio/yes_audio.mp3")
        
    if not any(vars(args).values()):
        execute_video()
        
        
if __name__ == "__main__":
    main()