import os
import win32api
import ctypes
import subprocess
import time
import psutil
import win32process
import win32gui
import math
import customtkinter
from CTkMessagebox import CTkMessagebox
from pynput.mouse import Controller
import win32con
import threading
import win32ui
import sys

user32 = ctypes.windll.user32
monitor_info = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
work_area = monitor_info.get("Work")

work_area_width = work_area[2]
work_area_height = work_area[3]
title_bar_height = user32.GetSystemMetrics(4)

directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(directory, "advanced_settings.txt")
exe_path = os.path.join(directory, "start.exe")
config_path = os.path.join(directory, "settings.cfg")
update_path = os.path.join(directory, ".Stellaria-launcher.exe")
icon_path = os.path.join(directory, "icon.ico")

ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

large, small = win32gui.ExtractIconEx(update_path,0)
win32gui.DestroyIcon(small[0])

hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
hbmp = win32ui.CreateBitmap()
hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_x )
hdc = hdc.CreateCompatibleDC()

hdc.SelectObject( hbmp )
hdc.DrawIcon( (0,0), large[0] )

hbmp.SaveBitmapFile( hdc, icon_path) 

if os.path.exists(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    inputted_values = []
    for line in lines:
        inputted_values.append(eval(line.strip()))
    
    for val in inputted_values:
        if val[0] == -3:
            scale = round((int(val[1].replace("%", "")) / 100),1)
            customtkinter.set_widget_scaling(scale)
            customtkinter.set_window_scaling(scale)

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        window_width = 720
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale_factor = self._get_window_scaling()
        x = int(((screen_width/2) - (window_width/2)) * scale_factor)
        y = int(((screen_height/2) - (window_height/2)) * scale_factor)

        # Set the geometry of the window
        self.title("Stellaria Advanced Launcher")
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.wm_iconbitmap(icon_path)

        # configure grid layout (3x3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkScrollableFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.columnconfigure(2, weight=1)
        self.windows_label = customtkinter.CTkLabel(self.sidebar_frame, text="Windows", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.windows_label.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=20, pady=(20, 10))
        self.sidebar_button_add = customtkinter.CTkButton(self.sidebar_frame, text="Add", command=self.sidebar_add_window)
        self.sidebar_button_add.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # create start button
        self.start_frame = customtkinter.CTkFrame(self, width=220, corner_radius=0)
        self.start_frame.grid(row=2, column=0, sticky="nsew")
        self.start_frame.columnconfigure(1, weight=1)
        self.update_checkbox = customtkinter.CTkCheckBox(self.start_frame, text="Check for Update?",hover_color="green",fg_color="green")
        self.update_checkbox.grid(row=0, column=1, sticky="w", padx=(10,0))
        self.start_button = customtkinter.CTkButton(self.start_frame, text="START", fg_color="green", hover_color="#006400", command=self.start, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.start_button.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=(10,25), pady=10)

        # create settings label
        self.settings_frame = customtkinter.CTkFrame(self, fg_color=["gray92", "gray14"])
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.settings_frame.columnconfigure(3, weight=1)
        self.settings_label = customtkinter.CTkLabel(self.settings_frame, text="Settings", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.settings_label.grid(row=0, column=1, columnspan=5, sticky="nsew", padx=20,pady=(20,3))
        self.scale_label = customtkinter.CTkLabel(self.settings_frame, text="Scale:", font=customtkinter.CTkFont(size=15))
        self.scale_label.grid(row=0, column=1, sticky="w", padx=(10,0),pady=(20,3))
        self.scale_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame, values=["40%", "60%", "80%", "100%", "120%", "140%", "160%"], width=100, command=self.set_scale)
        self.scale_optionmenu.grid(row=0, column=2, sticky="w", padx=(5,25),pady=(20,3))
        self.scale_optionmenu.set("100%")
        self.load_defaults_button = customtkinter.CTkButton(self.settings_frame, text="Paste", width=20, command=self.load_defaults)
        self.load_defaults_button.grid(row=0, column=4, padx=(0,10), pady=(20,3), sticky="e")
        self.save_defaults_button = customtkinter.CTkButton(self.settings_frame, text="Copy", width=20, command=self.save_defaults)
        self.save_defaults_button.grid(row=0, column=5, padx=(0,20), pady=(20,3), sticky="e")

        # create tabview
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=1, column=1, rowspan=2, padx=20, pady=(0,20), sticky="nsew")
        self.tabview.add("Video")
        self.tabview.add("Audio")
        self.tabview.add("Effects")
        self.tabview.add("Combat")
        self.tabview.add("Functional")

        self.tabview.tab("Video").grid_columnconfigure(1, weight=1)
        self.tabview.tab("Audio").grid_columnconfigure(2, weight=1)
        self.tabview.tab("Effects").grid_columnconfigure(2, weight=1)
        self.tabview.tab("Combat").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Functional").grid_columnconfigure(0, weight=1)

        self.loading = customtkinter.CTkLabel(self, text="Starting... Please Wait", font=customtkinter.CTkFont(size=50))

        # setup video tab
        self.video_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Video", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.video_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        size_validation = (self.register(self.size_val), "%P")
        fps_validation = (self.register(self.fps_val), "%P")

        # monitor selection
        self.shadow_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Monitor", font=customtkinter.CTkFont(size=15))
        self.shadow_label.grid(row=1, column=0, sticky="nw", padx=2, pady=2)
        self.display_optionas = []
        self.display_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Video"), dynamic_resizing=True, values=self.display_optionas)
        self.display_optionmenu.grid(row=1, column=1, padx=2, pady=2, sticky="nw")

        # width_start
        self.width_start_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Width Start (0-100%)", font=customtkinter.CTkFont(size=15))
        self.width_start_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)
        self.width_start_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.width_start_entry.grid(row=2, column=1, padx=2, pady=2, sticky="nw")

        # width_end
        self.width_end_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Width End (0-100%)", font=customtkinter.CTkFont(size=15))
        self.width_end_label.grid(row=3, column=0, sticky="nw", padx=2, pady=2)
        self.width_end_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.width_end_entry.grid(row=3, column=1, padx=2, pady=2, sticky="nw")

        # height_start
        self.height_start_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Height Start (0-100%)", font=customtkinter.CTkFont(size=15))
        self.height_start_label.grid(row=4, column=0, sticky="nw", padx=2, pady=2)
        self.height_start_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.height_start_entry.grid(row=4, column=1, padx=2, pady=2, sticky="nw")

        # height_end
        self.height_end_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Height End (0-100%)", font=customtkinter.CTkFont(size=15))
        self.height_end_label.grid(row=5, column=0, sticky="nw", padx=2, pady=2)
        self.height_end_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.height_end_entry.grid(row=5, column=1, padx=2, pady=2, sticky="nw")

        # fps
        self.fps_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Max FPS (1-360)", font=customtkinter.CTkFont(size=15))
        self.fps_label.grid(row=6, column=0, sticky="nw", padx=2, pady=2)
        self.fps_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=fps_validation)
        self.fps_entry.grid(row=6, column=1, padx=2, pady=2, sticky="nw")

        # fullscreen
        self.fullscreen_switch = customtkinter.CTkSwitch(self.tabview.tab("Video"), text="Fullscreen")
        self.fullscreen_switch.grid(row=7, column=0, padx=2, pady=2, sticky="nw")

        # setup audio tab
        self.audio_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Audio", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.audio_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # sfx
        self.sfx_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Sound Effects", font=customtkinter.CTkFont(size=15))
        self.sfx_label.grid(row=1, column=0, sticky="nw", padx=2, pady=2)
        self.sfx_number = customtkinter.IntVar(value=0)
        self.sfx_slider = customtkinter.CTkSlider(self.tabview.tab("Audio"), from_=0, to=5, number_of_steps=5, command=self.set_sfx)
        self.sfx_slider.grid(row=1, column=1, padx=2, pady=2, sticky="ew")
        self.sfx_number_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), textvariable=self.sfx_number, font=customtkinter.CTkFont(size=15))
        self.sfx_number_label.grid(row=1, column=2, sticky="nw", padx=2, pady=2)

        # bgm
        self.bgm_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Background Music", font=customtkinter.CTkFont(size=15))
        self.bgm_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)
        self.bgm_number = customtkinter.DoubleVar(value=0.000)
        self.bgm_number_str = customtkinter.StringVar()
        self.update_bgm_number_str()
        self.bgm_number.trace_add("write", self.on_bgm_number_change)
        self.bgm_slider = customtkinter.CTkSlider(self.tabview.tab("Audio"), from_=0, to=1, number_of_steps=20, command=self.set_bgm)
        self.bgm_slider.grid(row=2, column=1, padx=2, pady=2, sticky="ew")
        self.bgm_number_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), textvariable=self.bgm_number_str, font=customtkinter.CTkFont(size=15))
        self.bgm_number_label.grid(row=2, column=2, sticky="nw", padx=2, pady=2)

        # setup effects tab
        self.visual_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Effects", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.visual_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # effects
        self.effects_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Effects")
        self.effects_switch.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

        # names
        self.names_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Names")
        self.names_switch.grid(row=2, column=0, padx=2, pady=2, sticky="nw")

        # chat
        self.chat_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Chat")
        self.chat_switch.grid(row=3, column=0, padx=2, pady=2, sticky="nw")

        # glow + glitter
        self.glow_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Glow + Glitter")
        self.glow_switch.grid(row=4, column=0, padx=2, pady=2, sticky="nw")

        # model preview
        self.model_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Model Preview")
        self.model_switch.grid(row=5, column=0, padx=2, pady=2, sticky="nw")

        # metin2 cursor
        self.cursor_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Use Stellaria Cursor")
        self.cursor_switch.grid(row=6, column=0, padx=2, pady=2, sticky="nw")

        # fov
        self.fov_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="FOV", font=customtkinter.CTkFont(size=15))
        self.fov_label.grid(row=7, column=0, sticky="nw", padx=2, pady=2)
        self.fov_number = customtkinter.IntVar(value=0)
        self.fov_slider = customtkinter.CTkSlider(self.tabview.tab("Effects"), from_=0, to=90, number_of_steps=90, command=self.set_fov)
        self.fov_slider.grid(row=7, column=1, padx=2, pady=2, sticky="ew")
        self.fov_number_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), textvariable=self.fov_number, font=customtkinter.CTkFont(size=15))
        self.fov_number_label.grid(row=7, column=2, sticky="nw", padx=2, pady=2)

        # transparent
        self.transparent_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Transparency", font=customtkinter.CTkFont(size=15))
        self.transparent_label.grid(row=8, column=0, sticky="nw", padx=2, pady=2)
        self.transparent_number = customtkinter.DoubleVar(value=0.000)
        self.transparent_number_str = customtkinter.StringVar()
        self.update_transparent_number_str()
        self.transparent_number.trace_add("write", self.on_transparent_number_change)
        self.transparent_slider = customtkinter.CTkSlider(self.tabview.tab("Effects"), from_=0, to=1, number_of_steps=20, command=self.set_transparent)
        self.transparent_slider.grid(row=8, column=1, padx=2, pady=2, sticky="ew")
        self.transparent_number_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), textvariable=self.transparent_number_str, font=customtkinter.CTkFont(size=15))
        self.transparent_number_label.grid(row=8, column=2, sticky="nw", padx=2, pady=2)

        # shadows
        self.shadow_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Shadows", font=customtkinter.CTkFont(size=15))
        self.shadow_label.grid(row=9, column=0, sticky="nw", padx=2, pady=2)
        self.shadow_options = ["None", "Background", "Background + Player", "All - low", "All - Medium", "All - High"]
        self.shadow_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Effects"), dynamic_resizing=True, values=self.shadow_options)
        self.shadow_optionmenu.grid(row=9, column=1, padx=2, pady=2, sticky="nw")

        # skybox
        self.skybox_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Skybox", font=customtkinter.CTkFont(size=15))
        self.skybox_label.grid(row=10, column=0, sticky="nw", padx=2, pady=2)
        self.skybox_options = ["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "Original"]
        self.skybox_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Effects"), dynamic_resizing=True, values=self.skybox_options)
        self.skybox_optionmenu.grid(row=10, column=1, padx=2, pady=2, sticky="nw")

        # setup monsters tab
        self.mob_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Combat", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.mob_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # pet skill used in chat
        self.petskill_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Pet's Skill Message")
        self.petskill_switch.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

        self.mob_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Monsters", font=customtkinter.CTkFont(size=15, weight="bold", underline=True))
        self.mob_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)

        # dogmode
        self.dogmode_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Use Dog-mode")
        self.dogmode_switch.grid(row=3, column=0, padx=2, pady=2, sticky="nw")

        # mob level
        self.moblvl_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Monster's Level")
        self.moblvl_switch.grid(row=4, column=0, padx=2, pady=2, sticky="nw")

        # aggresive mob indicator
        self.agromob_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Aggresive Indicator (*)")
        self.agromob_switch.grid(row=5, column=0, padx=2, pady=2, sticky="nw")

        self.mob_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Damage", font=customtkinter.CTkFont(size=15, weight="bold", underline=True))
        self.mob_label.grid(row=6, column=0, sticky="nw", padx=2, pady=2)

        # damage
        self.damage_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Damage")
        self.damage_switch.grid(row=7, column=0, padx=2, pady=2, sticky="nw")

        # multiple targets damage
        self.multidmg_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Multi-target Damage")
        self.multidmg_switch.grid(row=8, column=0, padx=2, pady=2, sticky="nw")

        # setup functional tab
        self.visual_label = customtkinter.CTkLabel(self.tabview.tab("Functional"), text="Functional", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.visual_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # IME
        self.ime_switch = customtkinter.CTkSwitch(self.tabview.tab("Functional"), text="Use Stellaria IME")
        self.ime_switch.grid(row=1, column=0, padx=2, pady=2, sticky="nw")

        # Pickup
        self.pickup_switch = customtkinter.CTkSwitch(self.tabview.tab("Functional"), text="Pickup Everything")
        self.pickup_switch.grid(row=2, column=0, padx=2, pady=2, sticky="nw")

        # set default values
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.current_window = 1
        self.row_counter = 0
        self.buttons = []
        self.checkboxes = []
        self.delete_buttons = []
        self.edit_buttons = []
        self.settings = []
        self.to_start = []
        self.defaults = ['0','100','0','100','60',0,0,0.000,1,1,1,1,1,1,90,1.000,5,9,1,0,1,1,1,1,1,1]
        self.get_saved_values()
        self.bind("<<BackgroundTaskFinished>>", lambda event: self.show_all())

    def hide_all(self):
        self.start_frame.grid_forget()
        self.sidebar_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.tabview.grid_forget()

        self.loading.grid(row=0, column=0, rowspan=50, columnspan=50, sticky="nsew", padx=20, pady=20)
    def open_stellarai(self):
        ctypes.windll.user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-1))
        windows_to_start = []
        for window, start in zip(self.settings, self.to_start):
            if start == 1:
                if self.fullscreen_switch.get() == 1:
                    x = 1920
                    y = 1080
                else:    
                    x = int((int(window[1][0]) / 100) * work_area_width) -8
                    y = int((int(window[1][2]) / 100) * work_area_height)
                windows_to_start.append([x,y,self.combine_values(window[1])])

        if self.update_checkbox.get() == 1:
            uphwnds = []
            def updateEnumHandler(uphwnd, ctx):
                if win32gui.IsWindowVisible(uphwnd):
                    _, process_id = win32process.GetWindowThreadProcessId(uphwnd)
                    if process_id == ctx:
                        win32gui.ShowWindow(uphwnd, win32con.SW_HIDE)
                        uphwnds.append(uphwnd)

            process = subprocess.Popen([update_path])
            pidd = process.pid
            p = psutil.Process(pidd)
            while True:
                win32gui.EnumWindows(updateEnumHandler, pidd)
                if len(uphwnds) > 0:
                    break

            while True:
                io_counters = p.io_counters() 
                read = io_counters[2]
                write = io_counters[3]
                time.sleep(10)
                io_counters_new = p.io_counters() 
                read_new = io_counters_new[2]
                write_new = io_counters_new[3]
                if read == read_new and write == write_new:
                    time.sleep(1)
                    os.kill(pidd,15)
                    break
        
        key_lines = []
        with open(config_path, 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('KEY'):
                    key_lines.append(line.strip())

        pids = []        
        with open(config_path, 'w') as file:
            for value in windows_to_start[0][2]:
                file.write((value) + "\n")
            for key in key_lines:
                file.write((key) + "\n")
        access_time_timestamp = os.path.getatime(config_path)
        process = subprocess.Popen([exe_path])
        pids.append(process.pid)

        if len(windows_to_start) > 1:
            for window in windows_to_start[1:]:
                while True:
                    access_time_timestamp_new = os.path.getatime(config_path)
                    if access_time_timestamp_new > access_time_timestamp:
                        time.sleep(0.1)
                        with open(config_path, 'w') as file:
                            for value in window[2]:
                                file.write((value) + "\n")
                            for key in key_lines:
                                file.write((key) + "\n")
                        access_time_timestamp = os.path.getatime(config_path)
                        process = subprocess.Popen([exe_path])
                        pids.append(process.pid)
                        break

        if self.fullscreen_switch.get() == 0:
            hwnds = []
            com = []
            for win, pid in zip(windows_to_start,pids):
                com.append([win[0],win[1],pid])

            def winEnumHandler(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    _, process_id = win32process.GetWindowThreadProcessId(hwnd)
                    if process_id == ctx[2]:
                        rect = win32gui.GetWindowRect(hwnd)
                        w = rect[2] - rect[0]
                        h = rect[3] - rect[1]
                        win32gui.MoveWindow(hwnd, ctx[0], ctx[1], w, h, True)
                        hwnds.append(hwnd)
                        com.remove(ctx)

            while True:
                for vals in com:
                    win32gui.EnumWindows(winEnumHandler, vals)
                if len(pids) == len(hwnds):
                    break

        self.event_generate("<<BackgroundTaskFinished>>", when="tail")
    def show_all(self):
        self.loading.grid_forget()
        self.start_frame.grid(row=2, column=0, sticky="nsew")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.tabview.grid(row=1, column=1, rowspan=2, padx=20, pady=(0,20), sticky="nsew")
        self.start_button.configure(state="normal")
    def close(self):
        self.save_file()
        self.destroy()
    def start(self):
        self.start_button.configure(state="disabled")
        self.save_file()
        if len(self.settings) == 0:
            CTkMessagebox(master=self, title="Warning Message!", message=f"Please create and select at least one window", icon="warning")
            self.start_button.configure(state="normal")
            return
        
        if self.update_checkbox.get() == 1:
            if not os.path.exists(update_path):
                CTkMessagebox(master=self, title="Warning Message!", message=f"Cannot find .Stellaria-launcher.exe, please rename your launcher", icon="warning")
                self.start_button.configure(state="normal")
                return
        
        to_start = []
        total = 0
        for checkbox in self.checkboxes:
            if checkbox[1].get() == 1:
                to_start.append(1)
                total += 1
            else:
                to_start.append(0)
        
        if total == 0:
            CTkMessagebox(master=self, title="Warning Message!", message=f"Please select at least one window to start", icon="warning")
            self.start_button.configure(state="normal")
            return
        
        self.to_start = to_start.copy()

        for window, start in zip(self.settings,self.to_start):
            if start == 1:
                if window[1][0] == "" or window[1][1] == "" or window[1][2] == "" or window[1][3] == "" or window[1][4] == "":
                    for but in self.buttons:
                        if but[0] == window[0]:
                            win = but[1].cget("text")
                    CTkMessagebox(master=self, title="Warning Message!", message=f"Please fill out all Video fields in {win} window", icon="warning")
                    self.start_button.configure(state="normal")
                    return

        self.hide_all()
        open_met = threading.Thread(target=self.open_stellarai)
        open_met.start()
    def combine_values(self, values):

        width = math.ceil(((abs(int(values[1])-int(values[0]))) / 100) * work_area_width)
        height = math.ceil((((abs(int(values[3])-int(values[2])))/ 100) * work_area_height) - title_bar_height - 8)

        mylist = ["WIDTH "+str(width),
                  "HEIGHT "+str(height),
                  "MAX_FPS "+str(values[4]),
                  "WINDOWED "+str(1 if values[5] == 0 else 0),
                  "VOICE_VOLUME "+str(values[6]),
                  "MUSIC_VOLUME "+f"{values[7]:.3f}",
                  "SPECIAL_EFFECT_MODE_OTHER "+str(values[8]),
                  "ALWAYS_VIEW_NAME "+str(values[9]),
                  "VIEW_CHAT "+str(values[10]),
                  "SPECIAL_EFFECT_MODE_ITEM "+str(values[11]),
                  "TARGET_RENDER "+str(values[12]),
                  "SOFTWARE_CURSOR "+str(1 if values[13] == 0 else 0),
                  "FIELD_OF_VIEW "+str(values[14]),
                  "TRANSPARENT "+f"{values[15]:.3f}",
                  "SHADOW_LEVEL "+str(values[16]),
                  "SKYBOX_MODE "+str(values[17]),
                  "PET_SKILL_USE_INFO "+str(values[18]),
                  "DOG_MODE "+str(values[19]),
                  "SHOW_MOBLEVEL "+str(values[20]),
                  "SHOW_MOBAIFLAG "+str(values[21]),
                  "SHOW_DAMAGE "+str(values[22]),
                  "SHOW_MULTIPLE_DAMAGE "+str(values[23]),
                  "USE_DEFAULT_IME "+str(1 if values[24] == 0 else 0),
                  "PICKUP_ALL_ONCE "+str(values[25]),
                  "VISIBILITY 3",
                  "BPP 32",
                  "GAMMA 3",
                  "OBJECT_CULLING 1",
                  "PRELOAD_MOTION 1 ",
                  "DECOMPRESSED_TEXTURE 0 ",
                  "SOFTWARE_TILING 0",
                  "IS_SAVE_ID 0",
                  "SAVE_ID 0",
                  "FREQUENCY "+str(values[4])]
        return mylist   
    def get_saved_values(self):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                lines = file.readlines()

            inputted_values = []
            for line in lines:
                inputted_values.append(eval(line.strip()))

            for windows in inputted_values:
                if windows[0] == -3:
                    self.scale_optionmenu.set(windows[1])
                    self.update_checkbox.select() if windows[2] == 1 else self.update_checkbox.deselect()
                elif windows[0] == -2:
                    for button, name in zip(self.buttons, windows[1]):
                        button[1].configure(text=name)
                elif windows[0] == -1:
                    for checkbox, state in zip(self.checkboxes, windows[1]):
                        checkbox[1].select() if state == 1 else checkbox[1].deselect()
                elif windows[0] == 0:
                    self.defaults = windows[1]
                    if len(inputted_values) < 5:
                        self.hide_settings()
                        self.set_values(self.defaults)
                elif windows == inputted_values[1]:
                    self.set_values(windows[1])
                    self.sidebar_add_window(windows[1])
                else:
                    self.sidebar_add_window(windows[1])
        else:
            self.set_values(self.defaults)
            self.hide_settings()         
    def sidebar_button_event(self, b_id):
        for list in self.settings:
            if int(list[0]) == int(self.current_window):
                list[1] = self.get_values()
                break

        for button in self.buttons:
            if button[0] == b_id:
                button[1].configure(fg_color=["#325882", "#14375e"])
                self.current_window = button[0]
            else:
                button[1].configure(fg_color=["#3B8ED0", "#1F6AA5"])
                
        for list in self.settings:
            if int(list[0]) == int(self.current_window):
                self.set_values(list[1])
                break
    def sidebar_add_window(self, settings=[]):
        self.row_counter += 1
        button_id = self.row_counter

        delete_button = customtkinter.CTkButton(self.sidebar_frame, text="X", fg_color="red", width=28, hover_color="#8B0000", font=customtkinter.CTkFont(size=15, weight="bold"), command=lambda b_id=button_id: self.sidebar_delete_window(b_id))
        delete_button.grid(row=self.row_counter, column=0, padx=5, pady=5, sticky="nws")

        edit_name_button = customtkinter.CTkButton(self.sidebar_frame, text="E", fg_color="#ff7900", width=28, hover_color="#b35500", font=customtkinter.CTkFont(size=15, weight="bold"), command=lambda b_id=button_id: self.open_input_dialog_event(b_id))
        edit_name_button.grid(row=self.row_counter, column=1, padx=(0,5), pady=5, sticky="nws")

        sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text=(f'Window{button_id}'), command=lambda b_id=button_id: self.sidebar_button_event(b_id))
        sidebar_button.grid(row=self.row_counter, column=2, padx=(0,5), pady=5,sticky="nsew")

        checkbox = customtkinter.CTkCheckBox(self.sidebar_frame, text="", hover_color="green",fg_color="green", width=24)
        checkbox.grid(row=self.row_counter, column=3, pady=5, sticky="nws")

        self.sidebar_button_add.grid(row=self.row_counter+1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        if settings == []:
            self.settings.append([button_id,self.defaults])
        else:
            self.settings.append([button_id,settings])
            
        self.delete_buttons.append([button_id,delete_button])
        self.buttons.append([button_id,sidebar_button])
        self.checkboxes.append([button_id,checkbox])
        self.edit_buttons.append([button_id,edit_name_button])
        self.sidebar_button_event(button_id)
        
        if not self.tabview.winfo_ismapped():
            self.tabview.grid(row=1, column=1, rowspan=2, padx=20, pady=15, sticky="nsew")
            self.load_defaults_button.grid(row=0, column=4, padx=(0,10), pady=(20,3), sticky="e")
            self.save_defaults_button.grid(row=0, column=5, padx=(0,20), pady=(20,3), sticky="e")
    def set_values(self, values):
        self.width_start_entry.delete(0, customtkinter.END)
        self.width_start_entry.insert(0, values[0])
        self.width_end_entry.delete(0, customtkinter.END)
        self.width_end_entry.insert(0, values[1])
        self.height_start_entry.delete(0, customtkinter.END)
        self.height_start_entry.insert(0, values[2])
        self.height_end_entry.delete(0, customtkinter.END)
        self.height_end_entry.insert(0, values[3])
        self.fps_entry.delete(0, customtkinter.END)
        self.fps_entry.insert(0, values[4])
        self.fullscreen_switch.select() if values[5] == 1 else self.fullscreen_switch.deselect()
        self.sfx_slider.set(values[6])
        self.sfx_number.set(values[6])
        self.bgm_slider.set(values[7])
        self.bgm_number.set(values[7])
        self.effects_switch.select() if values[8] == 1 else self.effects_switch.deselect()
        self.names_switch.select() if values[9] == 1 else self.names_switch.deselect()
        self.chat_switch.select() if values[10] == 1 else self.chat_switch.deselect()
        self.glow_switch.select() if values[11] == 1 else self.glow_switch.deselect()  
        self.model_switch.select() if values[12] == 1 else self.model_switch.deselect()  
        self.cursor_switch.select() if values[13] == 1 else self.cursor_switch.deselect() 
        self.fov_slider.set(values[14])
        self.fov_number.set(values[14])
        self.transparent_slider.set(values[15])
        self.transparent_number.set(values[15])
        self.shadow_optionmenu.set(self.shadow_options[values[16]])
        self.skybox_optionmenu.set(self.skybox_options[values[17]])
        self.petskill_switch.select() if values[18] == 1 else self.petskill_switch.deselect()
        self.dogmode_switch.select() if values[19] == 1 else self.dogmode_switch.deselect()
        self.moblvl_switch.select() if values[20] == 1 else self.moblvl_switch.deselect()
        self.agromob_switch.select() if values[21] == 1 else self.agromob_switch.deselect()
        self.damage_switch.select() if values[22] == 1 else self.damage_switch.deselect()       
        self.multidmg_switch.select() if values[23] == 1 else self.multidmg_switch.deselect()
        self.ime_switch.select() if values[24] == 1 else self.ime_switch.deselect()
        self.pickup_switch.select() if values[25] == 1 else self.pickup_switch.deselect()
    def get_values(self):
        values = [self.width_start_entry.get(),
                  self.width_end_entry.get(),
                   self.height_start_entry.get(),
                   self.height_end_entry.get(),
                   self.fps_entry.get(),
                   self.fullscreen_switch.get(),
                   self.sfx_number.get(),
                   self.bgm_number.get(),
                   self.effects_switch.get(),
                   self.names_switch.get(),
                   self.chat_switch.get(),
                   self.glow_switch.get(),
                   self.model_switch.get(),
                   self.cursor_switch.get(),
                   self.fov_number.get(),
                   self.transparent_number.get(),
                   self.shadow_options.index(self.shadow_optionmenu.get()),
                   self.skybox_options.index(self.skybox_optionmenu.get()),
                   self.petskill_switch.get(),
                   self.dogmode_switch.get(),
                   self.moblvl_switch.get(),
                   self.agromob_switch.get(),
                   self.damage_switch.get(),
                   self.multidmg_switch.get(),
                   self.ime_switch.get(),
                   self.pickup_switch.get()]
        return values
    def sidebar_delete_window(self, b_id):
        for delete_button in self.delete_buttons:
            if delete_button[0] == b_id:
                delete_button[1].grid_forget()
                delete_button[1].destroy()
                self.delete_buttons.remove(delete_button)

        for edit_button in self.edit_buttons:
            if edit_button[0] == b_id:
                edit_button[1].grid_forget()
                edit_button[1].destroy()
                self.edit_buttons.remove(edit_button)

        for button in self.buttons:
            if button[0] == b_id:
                button[1].grid_forget()
                button[1].destroy()
                self.buttons.remove(button)

        for checkbox in self.checkboxes:
            if checkbox[0] == b_id:
                checkbox[1].grid_forget()
                checkbox[1].destroy()
                self.checkboxes.remove(checkbox)
        
        for setting in self.settings:
            if setting[0] == b_id:
                self.settings.remove(setting)
        
        if len(self.buttons) == 0:
            self.hide_settings()
        else:
            if b_id == self.current_window:
                self.buttons[-1][1].configure(fg_color=["#325882", "#14375e"])
                self.current_window = self.buttons[-1][0]

                for list in self.settings:
                    if int(list[0]) == int(self.current_window):
                        self.set_values(list[1])
                        break    
    def hide_settings(self):
        self.tabview.grid_forget()
        self.save_defaults_button.grid_forget()
        self.load_defaults_button.grid_forget()       
    def show_settings(self):
        self.tabview.grid(row=1, column=1, rowspan=2, columnspan = 3, padx=20, pady=(0,20), sticky="nsew")
        self.load_defaults_button.grid(row=0, column=2, padx=(0,10), pady=(20,0), sticky="nsew")
        self.save_defaults_button.grid(row=0, column=3, padx=(0,20), pady=(20,0), sticky="nsew")       
    def save_file(self):
        for list in self.settings:
            if int(list[0]) == int(self.current_window):
                list[1] = self.get_values()
                break

        states = []
        for checkbox in self.checkboxes:
            if checkbox[1].get() == 1:
                states.append(1)
            else:
                states.append(0)
        
        names = []
        for button in self.buttons:
            names.append(button[1].cget("text"))

        with open(file_path, 'w') as file:
            file.write(str([0,self.defaults]) + "\n")
            for window in self.settings:
                file.write(str(window) + "\n")   
            file.write(str([-1,states]) + "\n")
            file.write(str([-2,names]) + "\n")
            file.write(str([-3,self.scale_optionmenu.get(),self.update_checkbox.get()]))
    def save_defaults(self):
        self.defaults = self.get_values()
    def load_defaults(self):
        self.set_values(self.defaults)
    def open_input_dialog_event(self, id):
        for button in self.buttons:
            if button[0] == id:
                previous = button[1].cget("text")
                dialog = customtkinter.CTkInputDialog(text="Type in a new name:", title=f"Rename {previous}",)
                mouse = Controller()
                position = mouse.position
                dialog.geometry("+"+str(position[0])+"+"+str(position[1]))
                out = dialog.get_input()
                if out is not None:
                    button[1].configure(text=out)
    def set_scale(self, val):
        new_scaling_float = round((int(val.replace("%", "")) / 100),1)
        customtkinter.set_window_scaling(new_scaling_float)
        customtkinter.set_widget_scaling(new_scaling_float)
    def set_sfx(self, val):
        self.sfx_number.set(round(val))
    def set_bgm(self, val):
        self.bgm_number.set(round(val,3))
    def set_fov(self, val):
        self.fov_number.set(round(val))
    def set_transparent(self, val):
        self.transparent_number.set(round(val,2))
    def update_bgm_number_str(self):
        self.bgm_number_str.set(f"{self.bgm_number.get():.3f}")
    def on_bgm_number_change(self, *args):
        self.update_bgm_number_str()
    def update_transparent_number_str(self):
        self.transparent_number_str.set(f"{self.transparent_number.get():.3f}")
    def on_transparent_number_change(self, *args):
        self.update_transparent_number_str()
    def size_val(self, P):
        if P == "":
            return True
        elif P.isdigit():
            if (0 <= int(P) <= 100):
                if int(P[0]) == 0 and len(P) >= 2:
                    return False
                return True
            else:
                return False
        else:
            return False
    def fps_val(self, P):
        if P == "":
            return True
        elif P.isdigit():
            if (1 <= int(P) <= 360):
                return True
            else:
                return False
        else:
            return False

if __name__ == "__main__":
    app = App()
    app.mainloop()

