import time
import threading
from .error import message_box
from .utils import play_audio, play_video, block_keyboard, unblock_keyboard
    

def execute_video():
    easter_video_path='assets/video/easter_video.mp4' 
    easter_audio_path='assets/audio/easter_audio.mp3'
    
    video_thread = threading.Thread(target=play_video, args=[easter_video_path])
    audio_thread = threading.Thread(target=play_audio, args=[easter_audio_path])

    block_keyboard()

    audio_thread.start()
    video_thread.start()
    
    time.sleep(14.3)
    
    message_box()

    unblock_keyboard()