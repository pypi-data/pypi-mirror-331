import tkinter as tk
from PIL import ImageTk

def center_win(window: tk.Tk, width: int, height: int):
    window_width = width
    window_height = height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    window.geometry(f'{window_width}x{window_height}+{position_right}+{position_top}')

def start_move(event, parent: tk.Tk):
    parent.x=event.x
    parent.y=event.y

def move_window(event, parent: tk.Tk):
    x=event.x_root-parent.x
    y=event.y_root-parent.y
    parent.geometry(f'+{x}+{y}')
            
def close_window(parent: tk.Tk):
    parent.destroy()
            
def toggle_winsize(parent: tk.Tk, widget: tk.Label | tk.Button,
                   maximg: ImageTk.PhotoImage, resimg: ImageTk.PhotoImage):
    win_state=parent.state()
    if win_state=='normal':
        parent.state('zoomed')
        widget.config(image=resimg)
        widget.image=resimg
    else:
        parent.state('normal')
        widget.config(image=maximg)
        widget.image=maximg