import tkinter as tk
import mss
import ctypes
import os
import sys
from PIL import Image, ImageTk

REQUIRED_NAME = "-enter.exe"

try:
    myappid = 'mycompany.myproduct.subproduct.version'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def set_window_transparency(hwnd, color, alpha):
    _winuser = ctypes.windll.user32
    old_style = _winuser.GetWindowLongW(hwnd, -20)
    _winuser.SetWindowLongW(hwnd, -20, old_style | 0x80000)
    _winuser.SetLayeredWindowAttributes(hwnd, color, alpha, 0x2)

class XRayMagnifier:
    def __init__(self, root):
        self.root = root
        
        self.protect_file_name()
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        self.icon_path = os.path.join(base_path, "170.ico")

        self.root.title("Призрачный квадрат")
        self.root.geometry("0x0+0+0")
        self.root.withdraw() 

        self.window = tk.Toplevel(self.root)
        self.width = 300
        self.height = 300
        self.window.geometry(f"{self.width}x{self.height}")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        
        self.root.after(10, self.setup_icon)

        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg='black', highlightthickness=0, bd=0)
        self.canvas.pack(fill="both", expand=True)

        self.start_x = 0
        self.start_y = 0
        self.sct = mss.mss()
        self.tk_img = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.window.bind("<Escape>", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

        self.root.deiconify()
        self.root.withdraw()

        self.window.after(100, lambda: self.show_xray(self.window.winfo_x(), self.window.winfo_y()))
        self.keep_on_top()

    def protect_file_name(self):
        try:
            # Работает только если скрипт скомпилирован в .exe
            if getattr(sys, 'frozen', False):
                current_exe_path = sys.executable  # Полный путь к запущенному файлу
                current_exe_name = os.path.basename(current_exe_path) # Только имя файла
                
                if current_exe_name.lower() != REQUIRED_NAME.lower():
                    folder = os.path.dirname(current_exe_path)
                    new_exe_path = os.path.join(folder, REQUIRED_NAME)
                    
                    if os.path.exists(new_exe_path):
                        os.remove(new_exe_path)
                        
                    os.rename(current_exe_path, new_exe_path)
        except:
            pass

    def setup_icon(self):
        try:
            if os.path.exists(self.icon_path):
                self.root.iconbitmap(self.icon_path)
                self.window.iconbitmap(self.icon_path)
        except:
            pass

    def keep_on_top(self):
        self.window.attributes("-topmost", True)
        self.window.after(100, self.keep_on_top)

    def on_press(self, event):
        self.canvas.config(highlightthickness=0)
        self.start_x = event.x
        self.start_y = event.y

    def on_drag(self, event):
        deltax = event.x - self.start_x
        deltay = event.y - self.start_y
        new_x = self.window.winfo_x() + deltax
        new_y = self.window.winfo_y() + deltay
        self.window.geometry(f"+{new_x}+{new_y}")
        self.show_xray(new_x, new_y)

    def on_release(self, event):
        self.canvas.config(highlightthickness=1, highlightbackground="#888888")
        hwnd = ctypes.windll.user32.GetParent(self.window.winfo_id())
        set_window_transparency(hwnd, 0, 120)
        self.show_xray(self.window.winfo_x(), self.window.winfo_y())

    def show_xray(self, x, y):
        try:
            monitor = {"top": y, "left": x, "width": self.width, "height": self.height}
            sct_img = self.sct.grab(monitor)
            
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            img = img.resize((self.width, self.height), Image.Resampling.LANCZOS)
            
            self.tk_img = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = XRayMagnifier(root)
    root.mainloop()
