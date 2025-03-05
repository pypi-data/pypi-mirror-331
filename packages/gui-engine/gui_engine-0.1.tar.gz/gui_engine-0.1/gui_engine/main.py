import tkinter as tk
import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image, ImageTk
import wmi
import os
from window_functions import *

white='#FFFFFF'
lightgray='#848484'
gray='#333333'
darkgray='#171717'
darkgray2='#1C1C1C'
darkgray3='#1F1F1F'
black='#000000'
green='#048C34'
red='#FF0000'
orange='#FF8C00'
brightred='#EE1E1E'
darkred='#9F0000'
lightred='#FFAAAA'
gold='#FFD700'
blue='#33B8F0'

TOP=tk.TOP
BOTTOM=tk.BOTTOM
LEFT=tk.LEFT
RIGHT=tk.RIGHT
CENTER=tk.CENTER
X=tk.X
Y=tk.Y
BOTH=tk.BOTH
N=tk.N
NE=tk.NE
NW=tk.NW
S=tk.S
SE=tk.SE
SW=tk.SW
E=tk.E
W=tk.W
END=tk.END

class UI(tk.Tk):
    def __init__(self,
                 bg_color: str | None = 'transparent',
                 title: str | None = 'UI',
                 width: int | None = 400,
                 height: int | None = 300):
        super().__init__()
        self.bg_color = bg_color
        self.title = title
        self.width = width
        self.height = height

    def _title(self, title: str):
        super().title(title)
        self.title = title

    def _close(self):
        self.destroy()

    def _res(self, width: int, height: int):
        self.geometry('{}x{}'.format(width, height))
    
    def _bg(self, color: str):
        super().configure(bg=color)
        self.bg_color = color
    
    def _ico(self, path: str):
        super().iconbitmap(path)
        self.ico = path

    def _center(self):
        center_win(self, self.width, self.height)

    def _run(self):
        self.mainloop()

class UIAppBase(UI):
    def __init__(self,
                 maximg: str,
                 restimg: str,
                 closeimg: str,
                 bg_color: str | None = darkgray,
                 width: int | None = 400,
                 height: int | None = 300,
                 titlbr_title: str | None = 'UI',
                 titlbr_color: str | None = black,
                 titlbr_hover_color: str | None = gray,
                 titlbr_text_color: str | None = white,
                 titlbr_action_color: str | None = lightgray,
                 titlbr_bdwidth: int | None = 0,
                 titlbr_bdcolor: str | None = black,
                 resizable: bool | None = True):
        super().__init__()

        self.geometry(f'{width}x{height}')
        self.configure(bg=bg_color)

        title_bar=UITitlebar(parent=self, parent_width=width, parent_height=height,
                             bg_color=titlbr_color, bd_width=titlbr_bdwidth, bd_color=titlbr_bdcolor,
                             title=titlbr_title, text_color=titlbr_text_color, resizable=resizable,
                             hover_color=titlbr_hover_color, action_color=titlbr_action_color,
                             maximg=maximg, restimg=restimg, closeimg=closeimg)
        title_bar._pack(side=tk.TOP, fill=tk.X)

        center_win(self, width, height)

        self.overrideredirect(True)
    
    def set_img_bg(self, path: str):
        img=Image.open(path)
        img=img.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)
        img=ImageTk.PhotoImage(img)
        label=tk.Label(self, image=img)
        label.image=img
        label.place(relx=0.5, rely=0.5, anchor=CENTER)
    
    def _close(self):
        self.destroy()
    
    def _run(self):
        self.mainloop()

class UIFrame(ctk.CTkFrame):
    def __init__(self,
                 parent: UI,
                 width: int | None = 100,
                 height: int | None = 100,
                 rad: int | None = 15,
                 bg_color: str | None = black,
                 bd_width: int | None = 0,
                 bd_color: str | None = black):
        super().__init__(parent, width, height, corner_radius=rad, fg_color=bg_color,
                         border_width=bd_width, border_color=bd_color)

        self._propagate(False)

    def _get(self, resc):
        if resc=='rad':
            return self.cget('corner_radius')
        elif resc=='bg_color':
            return self.cget('fg_color')
        elif resc=='bd_width':
            return self.cget('border_width')
        elif resc=='bd_color':
            return self.cget('border_color')
    
    def _config(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'width':
                self.configure(width=value)
            elif key == 'height':
                self.configure(height=value)
            elif key == 'rad':
                self.configure(corner_radius=value)
            elif key == 'bg_color':
                self.configure(fg_color=value)
            elif key == 'bd_width':
                self.configure(border_width=value)
            elif key == 'bd_color':
                self.configure(border_color=value)
    
    def _propagate(self, value: bool):
        self.pack_propagate(value)

    def _custom_bind(self, event: str, func: Callable):
        self.bind(event, func)
    
    def _update_idletasks(self):
        self.update_idletasks()

    def _pack(self,
              side: str | None = None,
              anchor: str | None = None,
              fill: str | None = None,
              expand: bool | None = None,
              padx: int | None = None,
              pady: int | None = None):
        self.pack(side=side, anchor=anchor, fill=fill, expand=expand,padx=padx, pady=pady)
    
    def _place(self,
               relx: float | None = None,
               rely: float | None = None,
               anchor: str | None = None,
               x: int | None = None,
               y: int | None = None):
        self.place(relx=relx, rely=rely, anchor=anchor, x=x, y=y)
    
    def _close(self):
        self.destroy()

class UIEntry:
    def __init__(self,
                 parent: UI | UIFrame,
                 bg_color: str | None = darkgray,
                 width: int | None = 150,
                 height: int | None = 30,
                 rad: int | None = 15,
                 bd_width: int | None = 0,
                 bd_color: str | None = None,
                 text_color: str | None = white,
                 select_bg: str | None = gray,
                 select_fg: str | None = white,
                 placeholder_text: str | None = '',
                 placeholder_color: str | None = gray):
        frame=ctk.CTkFrame(parent, corner_radius=rad, fg_color=bg_color,
                           border_width=bd_width, border_color=bd_color,
                           width=width, height=height)
        frame.pack_propagate(False)

        entry=tk.Entry(frame, bg=bg_color, fg=text_color, bd=0,
                       insertbackground=text_color, selectbackground=select_bg,
                       selectforeground=select_fg)
        entry.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.frame=frame
        self.entry=entry

        self._set_placeholder(self.entry, placeholder_text, placeholder_color, text_color)

    def _set_placeholder(self, entry, placeholder, placeholder_color, text_color):
        entry.config(fg=placeholder_color)
        entry.insert(0, placeholder)
        entry.bind("<FocusIn>", lambda event: self._clear_placeholder(event, placeholder, text_color))
        entry.bind("<FocusOut>", lambda event: self._add_placeholder(event, placeholder, placeholder_color))

    def _clear_placeholder(self, event, placeholder, text_color):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(fg=text_color)

    def _add_placeholder(self, event, placeholder, placeholder_color):
        if not event.widget.get():
            event.widget.insert(0, placeholder)
            event.widget.config(fg=placeholder_color)
    
    def _get(self):
        return self.entry.get()

    def _clear(self):
        self.entry.delete(0, tk.END)
        self._set_placeholder(self.entry, self.entry.get(), lightgray, white)

    def _config(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'bg_color':
                self.entry.config(bg=value)
                self.frame.configure(fg_color=value)
            elif key == 'text_color':
                self.entry.config(fg=value, insertbackground=value)
            elif key == 'select_bg':
                self.entry.config(selectbackground=value)
            elif key == 'select_fg':
                self.entry.config(selectforeground=value)
            elif key == 'placeholder_text':
                self._set_placeholder(self.entry, value, kwargs.get('placeholder_color', lightgray), kwargs.get('text_color', white))
            elif key == 'placeholder_color':
                self._set_placeholder(self.entry, kwargs.get('placeholder_text', ''), value, kwargs.get('text_color', white))
            elif key == 'width':
                self.frame.configure(width=value)
            elif key == 'height':
                self.frame.configure(height=value)
            elif key == 'rad':
                self.frame.configure(corner_radius=value)
            elif key == 'bd_width':
                self.frame.configure(border_width=value)
            elif key == 'bd_color':
                self.frame.configure(border_color=value)

    def _pack(self,
              side: str | None = None,
              anchor: str | None = None,
              fill: str | None = None,
              expand: bool | None = None,
              padx: int | None = None,
              pady: int | None = None):
        self.frame.pack(side=side, anchor=anchor, fill=fill, expand=expand,padx=padx, pady=pady)
    
    def _place(self,
               relx: float | None = None,
               rely: float | None = None,
               anchor: str | None = None,
               x: int | None = None,
               y: int | None = None):
        self.frame.place(relx=relx, rely=rely, anchor=anchor, x=x, y=y)

class UIImage:
    def __init__(self, path: str, size: int):
        image=Image.open(path)
        image=image.resize((size, size), Image.LANCZOS)
        image=ImageTk.PhotoImage(image)
        self._image=image
        self._size=size

    def _get_image(self):
        return self._image
    
    def _get_size(self):
        return self._size

class UILabel:
    def __init__(self,
                 parent: UI | UIFrame,
                 base_width: int | None = 30,
                 base_height: int | None = 30,
                 bg_color: str | None = '#2B2B2B',
                 bd_width: int | None = 0,
                 bd_color: str | None = '#2B2B2B',
                 corner_rad: int | None = 15,
                 image: UIImage | None = None,
                 text: str | None = None,
                 text_color: str | None = 'white',
                 padding: int | None = 6,
                 hover_color: str | None = None):
        base_frame=ctk.CTkFrame(parent, fg_color=bg_color, border_width=bd_width, border_color=bd_color,
                                corner_radius=corner_rad, width=base_width, height=base_height)
        
        self.base_width=base_width
        self.base_height=base_height

        width=base_width - padding
        height=base_height - padding

        frame=tk.Frame(base_frame, bg=bg_color, bd=0, width=width, height=height)
        frame.pack_propagate(False)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        self.text=None
        self.image=None
        
        if text != None:
            _text=tk.Label(frame, bg=bg_color, text=text, fg=text_color)
            self.text=_text
            if hover_color != None:
                _text.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
                _text.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            # get text length in pixels
            text_len=_text.winfo_reqwidth()
            # configure frame and base frame
            frame.configure(width=text_len, height=height - padding)
            base_frame.configure(width=text_len + padding, height=height + padding)
            _text.pack(side=tk.RIGHT)

        if image != None:
            self.image=_image
            _image=tk.Label(frame, bg=bg_color, image=image._get_image())
            if hover_color != None:
                _image.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
                _image.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            # get image size in pixels
            image_size=image._get_size()
            # configure frame and base frame
            frame.configure(width=image_size, height=image_size)
            base_frame.configure(width=image_size + padding, height=image_size + padding)
            _image.pack(side=tk.LEFT)

        if text != None and image != None:
            frame.configure(width=text_len + image_size, height=image_size)
            base_frame.configure(width=text_len + image_size + padding, height=image_size + padding)
        
        # Adjust frame size based on content
        if text is not None and image is not None:
            base_width = text_len + image_size + padding
            base_height = max(image_size, base_height) + padding
        elif text is not None:
            base_width = text_len + padding
            base_height = base_height
        elif image is not None:
            base_width = image_size + padding
            base_height = image_size + padding
        else:
            base_width = base_width
            base_height = base_height

        frame.update_idletasks()

        self.base=base_frame
        self.frame=frame

        self._propagate(False)

        if hover_color != None:
            self.frame.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
            self.frame.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            self.base.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
            self.base.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
    
    def _config(self, **kwargs):
        if 'base_width' in kwargs:
            self.base_width = kwargs['base_width']
            self.base.configure(width=self.base_width)
        
        if 'base_height' in kwargs:
            self.base_height = kwargs['base_height']
            self.base.configure(height=self.base_height)
        
        if 'bg_color' in kwargs:
            self.base.configure(fg_color=kwargs['bg_color'])
            self.frame.configure(bg=kwargs['bg_color'])
        
        if 'bd_width' in kwargs:
            self.base.configure(border_width=kwargs['bd_width'])
        
        if 'bd_color' in kwargs:
            self.base.configure(border_color=kwargs['bd_color'])
        
        if 'corner_rad' in kwargs:
            self.base.configure(corner_radius=kwargs['corner_rad'])
        
        if 'text' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text"):
                    widget.configure(text=kwargs['text'])
                    text_len = widget.winfo_reqwidth()
                    self.frame.configure(width=text_len)
                    self.base.configure(width=text_len + 10)
        
        if 'text_color' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text"):
                    widget.configure(fg=kwargs['text_color'])
        
        if 'image' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("image"):
                    widget.configure(image=kwargs['image']._get_image())
                    image_size = kwargs['image']._get_size()
                    self.frame.configure(width=image_size, height=image_size)
                    self.base.configure(width=image_size + 10, height=image_size + 10)

    def _on_enter(self, event, hover_color):
        self.frame.configure(bg=hover_color)
        self.base.configure(fg_color=hover_color)
        if self.text != None:
            self.text.configure(bg=hover_color)
        if self.image != None:
            self.image.configure(bg=hover_color)

    def _on_leave(self, event, bg_color):
        self.frame.configure(bg=bg_color)
        self.base.configure(fg_color=bg_color)
        if self.text != None:
            self.text.configure(bg=bg_color)
        if self.image != None:
            self.image.configure(bg=bg_color)
    
    def _propagate(self, bool: bool | None = False):
        self.base.pack_propagate(bool)

    def _pack(self,
              side: str | None = None,
              fill: str | None = None,
              expand: bool | None = None,
              anchor: str | None = None,
              padx: int | None = None,
              pady: int | None = None):
        self.base.pack(side=side, fill=fill, expand=expand, anchor=anchor, padx=padx, pady=pady)
    
    def _place(self,
               x: int | None = None,
               y: int | None = None,
               relx: float | None = None,
               rely: float | None = None,
               anchor: str | None = None):
        self.base.place(x=x, y=y, relx=relx, rely=rely, anchor=anchor)

class UIButton:
    def __init__(self,
                 parent: UI | UIFrame,
                 base_width: int | None = 30,
                 base_height: int | None = 30,
                 bg_color: str | None = '#2B2B2B',
                 bd_width: int | None = 0,
                 bd_color: str | None = '#2B2B2B',
                 corner_rad: int | None = 15,
                 image: UIImage | None = None,
                 text: str | None = None,
                 text_color: str | None = 'white',
                 action: Callable | None = None,
                 action_color: str | None = None,
                 hover_color: str | None = None,
                 padding: int | None = 6):
        base_frame=ctk.CTkFrame(parent, fg_color=bg_color, border_width=bd_width, border_color=bd_color,
                                corner_radius=corner_rad, width=base_width, height=base_height)
        
        self.base_width=base_width
        self.base_height=base_height

        width=base_width - padding
        height=base_height - padding

        frame=tk.Frame(base_frame, bg=bg_color, bd=0, width=width, height=height)
        frame.pack_propagate(False)
        frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
        self.text=None
        self.image=None
        
        if text != None:
            _text=tk.Label(frame, bg=bg_color, text=text, fg=text_color)
            self.text=_text
            if action != None:
                _text.bind("<Button-1>", lambda event: action())
            if action_color != None:
                _text.bind("<Button-1>", lambda event: self._on_click(event, action_color))
                _text.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))
            if hover_color != None:
                _text.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
                _text.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            # get text length in pixels
            text_len=_text.winfo_reqwidth()
            # configure frame and base frame
            frame.configure(width=text_len, height=height - padding)
            base_frame.configure(height=height + padding)
            _text.pack(side=tk.RIGHT)

        if image != None:
            _image=tk.Label(frame, bg=bg_color, image=image._get_image())
            self.image=_image
            if action != None:
                _image.bind("<Button-1>", lambda event: action())
            if action_color != None:
                _image.bind("<Button-1>", lambda event: self._on_click(event, action_color))
                _image.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))
            if hover_color != None:
                _image.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
                _image.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            # get image size in pixels
            image_size=image._get_size()
            # configure frame and base frame
            frame.configure(width=image_size, height=image_size)
            base_frame.configure(width=image_size + padding, height=image_size + padding)
            _image.pack(side=tk.LEFT)

        if text != None and image != None:
            frame.configure(width=text_len + image_size, height=image_size)
            base_frame.configure(width=text_len + image_size + padding, height=image_size + padding)
        
        # Adjust frame size based on content
        if text is not None and image is not None:
            base_width = text_len + image_size + padding
            base_height = max(image_size, base_height) + padding
        elif text is not None:
            base_width = text_len + padding
            base_height = base_height
        elif image is not None:
            base_width = image_size + padding
            base_height = image_size + padding
        else:
            base_width = base_width
            base_height = base_height

        frame.update_idletasks()

        self.base=base_frame
        self.frame=frame

        self._propagate(False)

        if action != None:
            self.frame.bind("<Button-1>", lambda event: action())
            self.base.bind("<Button-1>", lambda event: action())
            if text != None:
                self.text.bind("<Button-1>", lambda event: action())
            if image != None:
                self.image.bind("<Button-1>", lambda event: action())

        if action_color != None:
            self.frame.bind("<Button-1>", lambda event: self._on_click(event, action_color, action))
            self.base.bind("<Button-1>", lambda event: self._on_click(event, action_color, action))
            self.frame.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))
            self.base.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))
            if image != None:
                self.image.bind("<Button-1>", lambda event: self._on_click(event, action_color, action))
                self.image.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))
            if text != None:
                self.text.bind("<Button-1>", lambda event: self._on_click(event, action_color, action))
                self.text.bind("<ButtonRelease-1>", lambda event: self._on_release(event, hover_color))

        if hover_color != None:
            self.frame.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
            self.frame.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
            self.base.bind("<Enter>", lambda event: self._on_enter(event, hover_color))
            self.base.bind("<Leave>", lambda event: self._on_leave(event, bg_color))
    
    def _config(self, **kwargs):
        if 'base_width' in kwargs:
            self.base_width = kwargs['base_width']
            self.base.configure(width=self.base_width)
        
        if 'base_height' in kwargs:
            self.base_height = kwargs['base_height']
            self.base.configure(height=self.base_height)
        
        if 'bg_color' in kwargs:
            self.base.configure(fg_color=kwargs['bg_color'])
            self.frame.configure(bg=kwargs['bg_color'])
        
        if 'bd_width' in kwargs:
            self.base.configure(border_width=kwargs['bd_width'])
        
        if 'bd_color' in kwargs:
            self.base.configure(border_color=kwargs['bd_color'])
        
        if 'corner_rad' in kwargs:
            self.base.configure(corner_radius=kwargs['corner_rad'])
        
        if 'text' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text"):
                    widget.configure(text=kwargs['text'])
                    text_len = widget.winfo_reqwidth()
                    self.frame.configure(width=text_len)
                    self.base.configure(width=text_len + 10)
        
        if 'text_color' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("text"):
                    widget.configure(fg=kwargs['text_color'])
        
        if 'image' in kwargs:
            for widget in self.frame.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget("image"):
                    widget.configure(image=kwargs['image']._get_image())
                    image_size = kwargs['image']._get_size()
                    self.frame.configure(width=image_size, height=image_size)
                    self.base.configure(width=image_size + 10, height=image_size + 10)

        if 'action' in kwargs:
            self.frame.bind("<Button-1>", lambda event: kwargs['action']())
            self.base.bind("<Button-1>", lambda event: kwargs['action']())
        
        if 'action_color' in kwargs and 'hover_color' in kwargs:
            self.frame.bind("<Enter>", lambda event: self._on_enter(event, kwargs['hover_color']))
            self.frame.bind("<Leave>", lambda event: self._on_leave(event, kwargs['bg_color']))
            self.base.bind("<Enter>", lambda event: self._on_enter(event, kwargs['hover_color']))
            self.base.bind("<Leave>", lambda event: self._on_leave(event, kwargs['bg_color']))

        if 'hover_color' in kwargs:
            self.frame.bind("<Enter>", lambda event: self._on_enter(event, kwargs['hover_color']))
            self.frame.bind("<Leave>", lambda event: self._on_leave(event, kwargs['bg_color']))
            self.base.bind("<Enter>", lambda event: self._on_enter(event, kwargs['hover_color']))
            self.base.bind("<Leave>", lambda event: self._on_leave(event, kwargs['bg_color']))
    
    def _on_enter(self, event, hover_color):
        self.frame.configure(bg=hover_color)
        self.base.configure(fg_color=hover_color)
        if self.text != None:
            self.text.configure(bg=hover_color)
        if self.image != None:
            self.image.configure(bg=hover_color)
    
    def _on_leave(self, event, bg_color):
        self.frame.configure(bg=bg_color)
        self.base.configure(fg_color=bg_color)
        if self.text != None:
            self.text.configure(bg=bg_color)
        if self.image != None:
            self.image.configure(bg=bg_color)

    def _on_click(self, event, action_color, action: Callable | None = None):
        action()
        self.frame.configure(bg=action_color)
        self.base.configure(fg_color=action_color)
        if self.text != None:
            self.text.configure(bg=action_color)
        if self.image != None:
            self.image.configure(bg=action_color)
        
    def _on_release(self, event, hover_color):
        self.frame.configure(bg=hover_color)
        self.base.configure(fg_color=hover_color)
        if self.text != None:
            self.text.configure(bg=hover_color)
        if self.image != None:
            self.image.configure(bg=hover_color)
    
    def _propagate(self, bool: bool | None = False):
        self.base.pack_propagate(bool)

    def _pack(self,
              side: str | None = None,
              fill: str | None = None,
              expand: bool | None = None,
              anchor: str | None = None,
              padx: int | None = None,
              pady: int | None = None):
        self.base.pack(side=side, fill=fill, expand=expand, anchor=anchor, padx=padx, pady=pady)
    
    def _place(self,
               x: int | None = None,
               y: int | None = None,
               relx: float | None = None,
               rely: float | None = None,
               anchor: str | None = None):
        self.base.place(x=x, y=y, relx=relx, rely=rely, anchor=anchor)

class UITitlebar:
    def __init__(self,
                 parent: UI | UIFrame | UIAppBase,
                 parent_width: int,
                 parent_height: int,
                 maximg: str,
                 restimg: str,
                 closeimg: str,
                 bg_color: str | None = black,
                 bd_width: int | None = 0,
                 bd_color: str | None = black,
                 title: str | None = 'UI',
                 text_color: str | None = white,
                 resizable: bool | None = True,
                 hover_color: str | None = black,
                 action_color: str | None = black):
        base=tk.Frame(parent, bg=bg_color, height=30,
                      highlightthickness=bd_width, highlightbackground=bd_color)
        base.pack_propagate(False)

        maximize=UIImage(maximg, 18)
        restore=UIImage(restimg, 18)
        close=UIImage(closeimg, 20)

        _title=tk.Label(base, text=title, bg=bg_color, fg=text_color)
        _title.pack(side=tk.LEFT, padx=5, pady=5)

        close_frame=tk.Frame(base, bg=bg_color, height=30, width=45)
        close_frame.pack_propagate(False)
        close_frame.pack(side=tk.RIGHT)

        close_btn=tk.Label(close_frame, image=close._get_image(), bg=bg_color, bd=0)
        close_btn.image=close._get_image()
        close_btn.place(relx=0.5, rely=0.5, anchor=CENTER)

        close_frame.bind('<Enter>', lambda event: self._on_enter(event, close_frame, hover_color))
        close_frame.bind('<Leave>', lambda event: self._on_leave(event, close_frame, bg_color))
        close_btn.bind('<Enter>', lambda event: self._on_enter(event, close_frame, hover_color))
        close_btn.bind('<Leave>', lambda event: self._on_leave(event, close_frame, bg_color))

        if resizable:
            winsize_frame=tk.Frame(base, bg=bg_color, height=30, width=45)
            winsize_frame.pack_propagate(False)
            winsize_frame.pack(side=RIGHT)

            winsize_btn=tk.Label(winsize_frame, image=maximize._get_image(), bg=bg_color, bd=0)
            winsize_btn.image=maximize._get_image()
            winsize_btn.place(relx=0.5, rely=0.5, anchor=CENTER)
            winsize_btn.bind('<Button-1>', lambda event: self._on_click(event, winsize_frame, action_color, action=lambda: toggle_winsize(event, parent, winsize_btn, maximize._get_image(), restore._get_image())))
            winsize_btn.bind('<ButtonRelease-1>', lambda event: self._on_release(event, winsize_frame, hover_color))
            winsize_frame.bind('<Enter>', lambda event: self._on_enter(event, winsize_frame, hover_color))
            winsize_frame.bind('<Leave>', lambda event: self._on_leave(event, winsize_frame, bg_color))
            winsize_frame.bind('<Button-1>', lambda event: self._on_click(event, winsize_frame, action_color, action=lambda: toggle_winsize(event, parent, winsize_btn, maximize._get_image(), restore._get_image())))
            winsize_frame.bind('<ButtonRelease-1>', lambda event: self._on_release(event, winsize_frame, hover_color))

        base.bind('<ButtonPress-1>', lambda event: start_move(event, parent))
        base.bind('<B1-Motion>', lambda event: move_window(event, parent))
        _title.bind('<ButtonPress-1>', lambda event: start_move(event, parent))
        _title.bind('<B1-Motion>', lambda event: move_window(event, parent))
        close_frame.bind('<ButtonPress-1>', lambda event: close_window(parent))
        close_btn.bind('<ButtonPress-1>', lambda event: close_window(parent))

        parent.overrideredirect(True)

        center_win(parent, parent_width, parent_height)

        self.base=base

    def _on_click(self, event, widget_frame, action_color: str, action: Callable | None = None):
        if action != None:
            action()
        widget_frame.config(bg=action_color)
        for widget in widget_frame.winfo_children():
            widget.config(bg=action_color)

    def _on_release(self, event, widget_frame, hover_color: str):
        widget_frame.config(bg=hover_color)
        for widget in widget_frame.winfo_children():
            widget.config(bg=hover_color)

    def _on_enter(self, event, widget_frame, hover_color: str):
        widget_frame.config(bg=hover_color)
        for widget in widget_frame.winfo_children():
            widget.config(bg=hover_color)

    def _on_leave(self, event, widget_frame, bg_color: str):
        widget_frame.config(bg=bg_color)
        for widget in widget_frame.winfo_children():
            widget.config(bg=bg_color)

    def _pack(self,
              side: str | None = TOP,
              fill: str | None = X,
              anchor: str | None = N,
              expand: bool | None = False,
              padx: int | None = 0,
              pady: int | None = 0):
        self.base.pack(side=side, fill=fill, anchor=anchor, expand=expand, padx=padx, pady=pady)
    
    def _place(self,
               x: int | None = None,
               y: int | None = None,
               relx: float | None = None,
               rely: float | None = None,
               anchor: str | None = None):
        self.base.place(x=x, y=y, relx=relx, rely=rely, anchor=anchor)

class UIBrightnessBar:
    def __init__(self,
                 parent: UI | UIAppBase | UIFrame,
                 bg_color: str | None = darkgray,
                 fg_color: str | None = gray,
                 brightness_color: str | None = white,
                 corner_rad: int | None = 15):
        base=ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=corner_rad, height=30)
        base.pack_propagate(0)

        frame=tk.Frame(base, bg=bg_color)
        frame.pack(fill=X, padx=10, pady=5)

        brightness=UIImage('icon/brightness.png', 20)

        _brightness=tk.Label(frame, image=brightness._get_image(), bg=bg_color)
        _brightness.image=brightness._get_image()
        _brightness.pack(side=RIGHT)

        _brightness_bar=ctk.CTkProgressBar(frame, fg_color=fg_color, progress_color=brightness_color,
                                        height=10, corner_radius=corner_rad)
        _brightness_bar.pack(fill=X, padx=5, pady=5)

        self.parent=parent
        
        self.base=base
        self._brightness_bar=_brightness_bar

        self.update_brightness()

    def _winfo_width(self) -> int:
        return self.base.winfo_width()
    
    def _winfo_height(self) -> int:
        return self.base.winfo_height()

    def get_brightness(self):
        w = wmi.WMI(namespace='wmi')
        brightness = w.WmiMonitorBrightness()[0]
        return brightness.CurrentBrightness

    def set_brightness(self, level):
        # Ensure the level is between 0 and 100
        level = max(0, min(100, level))
        # Convert the level to a value between 0 and 1 for the progress bar
        self._brightness_bar.set(level / 100)

    def update_brightness(self):
        current_brightness = self.get_brightness()
        self.set_brightness(current_brightness)
        # Schedule the function to run again after 1000 milliseconds (1 second)
        self.parent.after(100, self.update_brightness)

    def _place(self,
               x: int | None = None,
               y: int | None = None,
               anchor: str | None = None,
               relx: float | None = None,
                rely: float | None = None) -> None:
        self.base.place(x=x, y=y, anchor=anchor, relx=relx, rely=rely)

    def _pack(self,
              side: str | None = None,
              fill: str | None = None,
              anchor: str | None = None,
              padx: int | None = None,
              pady: int | None = None,
              expand: bool = False) -> None:
        self.base.pack(side=side, fill=fill, anchor=anchor, padx=padx, pady=pady, expand=expand)

class UIShell:
    def __init__(self, parent: UI | UIAppBase | UIFrame,
                 bg_color: Optional[str] = 'black',
                 text_color: Optional[str] = 'white',
                 font: Optional[str] = 'Arial',
                 font_size: Optional[int] = 10,
                 bar_color: Optional[str] = 'white',
                 bar_hover_color: Optional[str] = 'white',
                 insert_color: Optional[str] = 'white',
                 selectfg_color: Optional[str] = 'white',
                 selectbg_color: Optional[str] = 'blue',
                 shell_tag: Optional[str] = 'shell>: '):
        textboxbg = tk.Frame(parent, bg=bg_color)
        textboxbg.pack(side=LEFT, fill=BOTH, expand=True)
        textboxbg.pack_propagate(False)

        scrollbarbg = tk.Frame(parent, bg=bg_color, width=15)
        scrollbarbg.pack(side=RIGHT, fill=Y)
        scrollbarbg.pack_propagate(False)
        
        textbox = tk.Text(textboxbg, bg=bg_color, fg=text_color, font=(font, font_size), bd=0,
                          insertbackground=insert_color, selectbackground=selectbg_color,
                          selectforeground=selectfg_color)
        textbox.pack(side=LEFT, fill=BOTH, expand=True)
        textbox.pack_propagate(False)
        textbox.focus_set()

        scrollbar = ctk.CTkScrollbar(scrollbarbg, command=textbox.yview,
                                     button_color=bar_color, fg_color=bg_color,
                                     button_hover_color=bar_hover_color)
        scrollbar.pack(side=RIGHT, fill=Y)
        textbox.config(yscrollcommand=scrollbar.set)

        self.textbox = textbox
        self.text_color = text_color
        self.shell_tag = shell_tag

        def_cmdz = {
            'ls': self.ls
        }

        self.cmdz = def_cmdz

        self.textbox.bind('<Return>', self.process_input)
        self.shelltag()
    
    def ls(self):
        _path = os.getcwd()
        _dir = os.listdir(_path)
        _dir.sort()
        _dir = [f'{i}\n' for i in _dir]
        _dir = ''.join(_dir)
        _dir = f'[{_path}]\n{_dir}'
        self.write(f'\n{_dir}')
        file_count = len(_dir.split('\n'))
        dir_count = len([i for i in _dir.split('\n') if os.path.isdir(os.path.join(_path, i))])
        self.write(f'\n{file_count} files, {dir_count} directories\n')
        used_size = sum(os.path.getsize(os.path.join(_path, i)) for i in _dir.split('\n') if os.path.isfile(os.path.join(_path, i)))
        used_size = used_size / (1024 * 1024)
        used_size = round(used_size, 2)
        used_size = f'{used_size} MB'
        self.write(f'Used space: {used_size}\n')
        total_size = sum(os.path.getsize(os.path.join(_path, i)) for i in _dir.split('\n') if os.path.isfile(os.path.join(_path, i)))
        total_size = total_size / (1024 * 1024)
        total_size = round(total_size, 2)
        total_size = f'{total_size} MB'
        self.write(f'Total space: {total_size}\n')

    def config_tagz(self, tagz: dict):
        for tag, color in tagz.items():
            self.textbox.tag_config(tag, foreground=color)
        
    def config_cmdz(self, cmdz: dict):
        for cmd, func in cmdz.items():
            self.handle_command(cmd, func)

    def add_cmdz(self, cmdz: dict):
        self.cmdz.update(cmdz)

    def write(self, text: str, tag: Optional[str] = None):
        if tag:
            self.textbox.insert(END, text, tag)
        else:
            self.textbox.insert(END, text)
        self.textbox.see(END)
    
    def shelltag(self):
        self.textbox.insert(END, self.shell_tag)
        self.textbox.see(END)

    def process_input(self, event):
        input_text = self.textbox.get("end-2l linestart", "end-1c").strip()
        command = input_text.split(f'{self.shell_tag}')[-1]
        self.handle_command(command, cmdz = self.cmdz)
        self.write('\n')
        self.shelltag()
        return "break"

    def handle_command(self, command: str, cmdz: dict):
        for cmd, func in cmdz.items():
            if command == cmd:
                func()