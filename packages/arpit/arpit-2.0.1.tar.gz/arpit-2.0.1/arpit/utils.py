import cv2
import pygame
import keyboard
import webbrowser
import pkg_resources
import subprocess, re

def open_link(url):
    webbrowser.open(url)

def path_convertor(path):
        try:
            return pkg_resources.resource_filename('arpit', path)
        except FileNotFoundError and ModuleNotFoundError:
            return path
       
def block_keyboard():
    for i in range(150):
        keyboard.block_key(i)

def unblock_keyboard():
    for i in range(150):
        keyboard.unblock_key(i)
        
def play_audio(easter_audio_path):
    audio_path = path_convertor(easter_audio_path)

    try:
        pygame.init()
        pygame.mixer.music.load(audio_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
        return False

def play_video(easter_video_path):
    video_path = path_convertor(easter_video_path)

    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    cv2.namedWindow("arpit", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("arpit", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    frame_rate = 30
    frame_delay = int(1000 / frame_rate)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow("arpit", frame)
        if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
def get_ip_address():
    try:
        ipconfig_result = subprocess.check_output(['ipconfig'], universal_newlines=True)
        ip_matches = re.findall(r'IPv4 Address[^\d]+(\d+\.\d+\.\d+\.\d+)', ipconfig_result)

        if ip_matches:
            return ip_matches[0]+" registered successfully."
        else:
            return ""
        
    except Exception as e:
        return ""