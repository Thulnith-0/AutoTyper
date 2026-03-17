import customtkinter as ctk # type: ignore
import sys
import ctypes
import os
from tkinter import messagebox
from app.core.engine import TypingEngine  # type: ignore

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class AutoTyperApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("AutoTyper")
        
        window_width = 600
        window_height = 650

        # Center perfectly in the usable work area, accounting for DPI scaling.
        # SPI_GETWORKAREA (48) returns physical pixels; Tkinter geometry uses logical pixels.
        # We divide by the DPI scale factor to convert between the two.
        try:
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long),
                             ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            rect = RECT()
            ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(rect), 0)  # type: ignore
            dpi = ctypes.windll.user32.GetDpiForSystem()  # type: ignore
            scale = dpi / 96.0  # 96 DPI = 100% scale
            work_w = int((rect.right - rect.left) / scale)
            work_h = int((rect.bottom - rect.top) / scale)
            x = int(rect.left / scale) + (work_w - window_width) // 2
            y = int(rect.top / scale) + (work_h - window_height) // 2
        except Exception:
            # Fallback: use Tkinter screen size minus a standard taskbar height
            x = (self.winfo_screenwidth() - window_width) // 2
            y = (self.winfo_screenheight() - window_height) // 2 - 24

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.resizable(False, False)

        # Set window icon (works at runtime)
        if getattr(sys, 'frozen', False):
            # Running as compiled PyInstaller executable
            base_path = sys._MEIPASS # type: ignore
        else:
            # Running natively from python source
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

        icon_path = os.path.join(base_path, "assets", "icon.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)

        if sys.platform == "win32":
            try:
                # Force Windows taskbar to treat this as a standalone app, not a Python/Tkinter generic process
                myappid = 'mycompany.autotyper.app.1'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception:
                pass
            
            try:
                hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int(2)))
            except Exception:
                pass

        self.engine = TypingEngine({
            'update_status': self.update_status,
            'update_time_left': self.update_time_left,
            'finish_typing': self.finish_typing
        })

        self.setup_ui()

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=15)

        self._setup_text_area()
        self._setup_settings()
        self._setup_status_and_buttons()

    def _setup_text_area(self):
        self.lbl_header = ctk.CTkLabel(self.main_frame, text="Text to type:", font=("Segoe UI", 16, "bold"))
        self.lbl_header.pack(anchor="w", pady=(0, 5))

        self.text_area = ctk.CTkTextbox(self.main_frame, height=180, font=("Consolas", 13), corner_radius=10, border_width=1)
        self.text_area.pack(fill="x", pady=(0, 15))

    def _setup_settings(self):
        self.settings_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.settings_frame.pack(fill="x", pady=5)
        self.settings_frame.grid_columnconfigure(0, weight=1)
        self.settings_frame.grid_columnconfigure(1, weight=1)

        self._setup_time_settings()
        self._setup_behavior_settings()

    def _setup_time_settings(self):
        self.time_frame = ctk.CTkFrame(self.settings_frame, corner_radius=10)
        self.time_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

        ctk.CTkLabel(self.time_frame, text="Completion Time", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=15, pady=(15, 2))
        ctk.CTkLabel(self.time_frame, text="Set exact time for task:", text_color="gray", font=("Segoe UI", 12)).pack(anchor="w", padx=15, pady=(0, 10))

        self.hms_frame = ctk.CTkFrame(self.time_frame, fg_color="transparent")
        self.hms_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(self.hms_frame, text="H:", font=("Segoe UI", 13, "bold")).pack(side="left", padx=(2, 2))
        self.hours_var = ctk.StringVar(value="0")
        ctk.CTkEntry(self.hms_frame, textvariable=self.hours_var, width=35).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(self.hms_frame, text="M:", font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 2))
        self.mins_var = ctk.StringVar(value="0")
        ctk.CTkEntry(self.hms_frame, textvariable=self.mins_var, width=35).pack(side="left", padx=(0, 5))

        ctk.CTkLabel(self.hms_frame, text="S:", font=("Segoe UI", 13, "bold")).pack(side="left", padx=(0, 2))
        self.secs_var = ctk.StringVar(value="30")
        ctk.CTkEntry(self.hms_frame, textvariable=self.secs_var, width=35).pack(side="left", padx=(0, 0))

        ctk.CTkLabel(self.time_frame, text="Start Delay (seconds):", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
        self.delay_var = ctk.StringVar(value="5")
        ctk.CTkEntry(self.time_frame, textvariable=self.delay_var, width=70).pack(anchor="w", padx=15, pady=(0, 15))

    def _setup_behavior_settings(self):
        self.behavior_frame = ctk.CTkFrame(self.settings_frame, corner_radius=10)
        self.behavior_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        ctk.CTkLabel(self.behavior_frame, text="Human Behaviors", font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=15, pady=(15, 10))

        self.switches = []

        self.var_speed = ctk.BooleanVar(value=True)
        sw_speed = ctk.CTkSwitch(self.behavior_frame, text="Natural Rhythm Speed", variable=self.var_speed, font=("Segoe UI", 12), width=220)
        sw_speed.pack(anchor="w", padx=15, pady=5)
        self.switches.append(sw_speed)

        self.var_pauses = ctk.BooleanVar(value=True)
        sw_pauses = ctk.CTkSwitch(self.behavior_frame, text="Random Reading Pauses", variable=self.var_pauses, font=("Segoe UI", 12), width=220)
        sw_pauses.pack(anchor="w", padx=15, pady=5)
        self.switches.append(sw_pauses)

        self.var_mistakes = ctk.BooleanVar(value=True)
        sw_mistakes = ctk.CTkSwitch(self.behavior_frame, text="Make & Correct Typos", variable=self.var_mistakes, font=("Segoe UI", 12), width=220)
        sw_mistakes.pack(anchor="w", padx=15, pady=5)
        self.switches.append(sw_mistakes)

        self.var_hesitation = ctk.BooleanVar(value=True)
        sw_hesitation = ctk.CTkSwitch(self.behavior_frame, text="Sentence Hesitation", variable=self.var_hesitation, font=("Segoe UI", 12), width=220)
        sw_hesitation.pack(anchor="w", padx=15, pady=(5, 15))
        self.switches.append(sw_hesitation)

        for sw in self.switches:
            sw.bind("<ButtonPress-1>", lambda e, s=sw: self._animate_switch(s, "click"))
            sw.bind("<ButtonRelease-1>", lambda e, s=sw: self._animate_switch(s, "normal"))

    def _setup_status_and_buttons(self):
        self.lbl_info = ctk.CTkLabel(self.main_frame, text="⚠️ Failsafe: Move your mouse to any 4 corners of screen to abort.", text_color="gray", font=("Segoe UI", 12))
        self.lbl_info.pack(pady=(15, 10))

        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=5)
        
        self.status_lbl = ctk.CTkLabel(self.status_frame, text="Ready", font=("Segoe UI", 16, "bold"), text_color="#1f6aa5")
        self.status_lbl.pack(side="left")

        self.time_lbl = ctk.CTkLabel(self.status_frame, text="00:00:00", font=("Consolas", 18, "bold"), text_color="#d35b58")
        self.time_lbl.pack(side="right")

        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent", height=45)
        self.btn_frame.pack(pady=10, fill="x")

        self.btn_start = ctk.CTkButton(self.btn_frame, text="START TYPING", command=self.start_typing_thread, 
                                       font=("Segoe UI", 14, "bold"), height=40, width=140, corner_radius=8, fg_color="#2ba84a", hover_color="#248f3f")
        self.btn_start.place(relx=0.25, rely=0.5, anchor="center")

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="STOP", command=self.stop_execution, 
                                      font=("Segoe UI", 14, "bold"), height=40, width=140, corner_radius=8, fg_color="#d35b58", hover_color="#b54a48", state="disabled")
        self.btn_stop.place(relx=0.75, rely=0.5, anchor="center")

        self.btn_start.bind("<Enter>", lambda e: self._animate_button(self.btn_start, "hover"))
        self.btn_start.bind("<Leave>", lambda e: self._animate_button(self.btn_start, "normal"))
        self.btn_start.bind("<ButtonPress-1>", lambda e: self._animate_button(self.btn_start, "click"))
        self.btn_start.bind("<ButtonRelease-1>", lambda e: self._animate_button(self.btn_start, "hover"))

        self.btn_stop.bind("<Enter>", lambda e: self._animate_button(self.btn_stop, "hover"))
        self.btn_stop.bind("<Leave>", lambda e: self._animate_button(self.btn_stop, "normal"))
        self.btn_stop.bind("<ButtonPress-1>", lambda e: self._animate_button(self.btn_stop, "click"))
        self.btn_stop.bind("<ButtonRelease-1>", lambda e: self._animate_button(self.btn_stop, "hover"))

    def _animate_switch(self, switch: ctk.CTkSwitch, state: str):
        if state == "click":
            target_width, target_height = 32, 16
        else: # "normal"
            target_width, target_height = 36, 18
            
        try:
            current_width = int(switch.cget("switch_width"))
            current_height = int(switch.cget("switch_height"))
        except Exception:
            return
            
        self._step_switch_animation(switch, current_width, target_width, current_height, target_height)

    def _step_switch_animation(self, switch: ctk.CTkSwitch, curr_w, targ_w, curr_h, targ_h):
        step_w = 1 if targ_w > curr_w else -1 if targ_w < curr_w else 0
        step_h = 1 if targ_h > curr_h else -1 if targ_h < curr_h else 0
        
        if curr_w != targ_w or curr_h != targ_h:
            new_w = curr_w + step_w
            new_h = curr_h + step_h
            try:
                switch.configure(switch_width=new_w, switch_height=new_h)
            except Exception:
                return # Destroyed
            self.after(10, lambda: self._step_switch_animation(switch, new_w, targ_w, new_h, targ_h))

    def _animate_button(self, button: ctk.CTkButton, state: str):
        if button.cget("state") == "disabled":
            target_width, target_height = 140, 40
        elif state == "hover":
            target_width, target_height = 145, 42
        elif state == "click":
            target_width, target_height = 135, 38
        else:
            target_width, target_height = 140, 40
        
        try:
            current_width = int(button.cget("width"))
            current_height = int(button.cget("height"))
        except Exception:
            return
        
        self._step_animation(button, current_width, target_width, current_height, target_height)

    def _step_animation(self, button: ctk.CTkButton, curr_w, targ_w, curr_h, targ_h):
        step_w = 1 if targ_w > curr_w else -1 if targ_w < curr_w else 0
        step_h = 1 if targ_h > curr_h else -1 if targ_h < curr_h else 0
        
        if curr_w != targ_w or curr_h != targ_h:
            new_w = curr_w + step_w
            new_h = curr_h + step_h
            try:
                button.configure(width=new_w, height=new_h)
            except Exception:
                return # Button destroyed
            self.after(10, lambda: self._step_animation(button, new_w, targ_w, new_h, targ_h))

    def stop_execution(self):
        if self.engine.is_typing:
            self.engine.abort()
            self.status_lbl.configure(text="Aborting...")

    def update_status(self, msg, color="#1f6aa5"):
        self.after(0, lambda: self.status_lbl.configure(text=msg, text_color=color))

    def update_time_left(self, rem):
        h = int(rem // 3600)
        m = int((rem % 3600) // 60)
        s = int(rem % 60)
        self.after(0, lambda: self.time_lbl.configure(text=f"{h:02d}:{m:02d}:{s:02d}"))

    def toggle_buttons(self, is_running):
        self.after(0, lambda: self.btn_start.configure(state="disabled" if is_running else "normal"))
        self.after(0, lambda: self.btn_stop.configure(state="normal" if is_running else "disabled"))

    def start_typing_thread(self):
        text_to_type = self.text_area.get("1.0", "end-1c")

        if not text_to_type:
            messagebox.showwarning("Empty Text", "Please enter some text to type.")
            return

        try:
            h = int(self.hours_var.get() or "0")
            m = int(self.mins_var.get() or "0")
            s = int(self.secs_var.get() or "0")
            target_time = h * 3600 + m * 60 + s
            if target_time <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Target Time must be a positive number of hours, minutes, and seconds.")
            return

        try:
            start_delay = int(self.delay_var.get() or "0")
            if start_delay < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Input", "Start Delay must be a non-negative integer.")
            return

        self.toggle_buttons(True)
        self.update_time_left(target_time)
        
        use_mistakes = self.var_mistakes.get()
        use_pauses = self.var_pauses.get()
        use_speed = self.var_speed.get()
        use_hesitation = self.var_hesitation.get()

        self.engine.start(
            text=text_to_type, 
            target_time=target_time, 
            start_delay=start_delay, 
            use_mistakes=use_mistakes, 
            use_pauses=use_pauses, 
            use_speed=use_speed, 
            use_hesitation=use_hesitation
        )

    def finish_typing(self, msg, color):
        self.update_status(msg, color)
        self.toggle_buttons(False)
