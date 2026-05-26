import time

class Console:        
    def log(text, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {text}")
    