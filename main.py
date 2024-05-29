# import dependencies
from os import path, kill, remove
from sys import executable, argv, exit
from win32api import EnumDisplayMonitors, GetMonitorInfo
from win32gui import IsWindowVisible, ShowWindow, EnumWindows, GetWindowRect, MoveWindow
from win32con import SW_HIDE
from win32process import GetWindowThreadProcessId
from ctypes import windll, c_void_p
from math import ceil
from time import sleep
from psutil import Process
from subprocess import Popen
from threading import Thread
import customtkinter
from CTkMessagebox import CTkMessagebox
from pynput.mouse import Controller
from re import findall

# restart as admin if not admin
# if not windll.shell32.IsUserAnAdmin():
#     windll.shell32.ShellExecuteW(None, "runas", executable, " ".join(argv), None, 0x0400)
#     exit()

# setup paths
directory = path.dirname(path.abspath(__file__))
save_path = path.join(directory, "advanced_settings.txt")
exe_path = path.join(directory, "start.exe")
update_path = path.join(directory, ".Stellaria-launcher.exe")
config_path = path.join(directory, "settings.cfg")
crash_path = path.join(directory, "CrashSender1500.exe")

# set to previously set scale if exists
if path.exists(save_path):
    with open(save_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        values = eval(line.strip())
        if values[0] == -3:
            scale = round((int(values[1].replace("%", "")) / 100), 1)
            customtkinter.set_widget_scaling(scale)
            customtkinter.set_window_scaling(scale)

# set app theme
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("blue")

# main GUI app
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # configure window
        self.title("Stellaria Advanced Launcher")
        if path.exists(update_path):
            self.wm_iconbitmap(update_path)

        # window size and position
        window_width = 720
        window_height = 500
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        scale_factor = self._get_window_scaling()
        x = int(((screen_width/2) - (window_width/2)) * scale_factor)
        y = int(((screen_height/2) - (window_height/2)) * scale_factor)
        
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # configure grid layout (3 rows x 2 columns)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # setup text fonts
        self.title_font = customtkinter.CTkFont(size=20, weight="bold")
        self.subtitle_font = customtkinter.CTkFont(size=15, weight="bold", underline=True)
        self.label_font = customtkinter.CTkFont(size=15)

        # create sidebar frame
        self.sidebar_frame = customtkinter.CTkScrollableFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.columnconfigure(2, weight=1)
        self.windows_label = customtkinter.CTkLabel(self.sidebar_frame, text="Windows", font=self.title_font)
        self.windows_label.grid(row=0, column=0, columnspan=4, sticky="nsew", padx=20, pady=(20, 10))
        self.sidebar_button_add = customtkinter.CTkButton(self.sidebar_frame, text="Add", command=self.sidebar_add_window)
        self.sidebar_button_add.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # create start frame
        self.start_frame = customtkinter.CTkFrame(self, width=220, corner_radius=0)
        self.start_frame.grid(row=2, column=0, sticky="nsew")
        self.start_frame.columnconfigure(0, weight=1)
        self.update_checkbox = customtkinter.CTkCheckBox(self.start_frame, text="Check for Update?", fg_color="green", hover_color="green")
        self.update_checkbox.grid(row=0, column=0, sticky="w", padx=(10,0))
        self.start_button = customtkinter.CTkButton(self.start_frame, text="START", fg_color="green", hover_color="#006400", font=self.title_font, command=self.start)
        self.start_button.grid(row=1, column=0, sticky="nsew", padx=(10,25), pady=10)

        # create settings frame
        self.settings_frame = customtkinter.CTkFrame(self, fg_color=["gray92", "gray14"])
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.settings_frame.columnconfigure(3, weight=1)
        self.settings_label = customtkinter.CTkLabel(self.settings_frame, text="Settings", font=self.title_font)
        self.settings_label.grid(row=0, column=1, columnspan=5, sticky="nsew", padx=20,pady=(20,3))
        self.scale_label = customtkinter.CTkLabel(self.settings_frame, text="Scale:", font=self.label_font)
        self.scale_label.grid(row=0, column=1, sticky="w", padx=(10,0), pady=(20,3))
        self.scale_optionmenu = customtkinter.CTkOptionMenu(self.settings_frame, values=["40%", "60%", "80%", "100%", "120%", "140%", "160%"], width=100, command=self.set_scale)
        self.scale_optionmenu.grid(row=0, column=2, sticky="w", padx=(5,25), pady=(20,3))
        self.load_defaults_button = customtkinter.CTkButton(self.settings_frame, text="Paste", width=20, command=self.load_defaults)
        self.load_defaults_button.grid(row=0, column=4, padx=(0,10), sticky="e", pady=(20,3))
        self.save_defaults_button = customtkinter.CTkButton(self.settings_frame, text="Copy", width=20, command=self.save_defaults)
        self.save_defaults_button.grid(row=0, column=5, padx=(0,20), sticky="e", pady=(20,3))

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

        ### VIDEO TAB ###
        self.video_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Video", font=self.title_font)
        self.video_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # monitor selection
        self.monitor_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Monitor", font=self.label_font)
        self.monitor_label.grid(row=1, column=0, sticky="nw", padx=2, pady=2)
        self.display_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Video"), values=self.get_monitor_values(), command=self.check_screens)
        self.display_optionmenu.grid(row=1, column=1, sticky="nw", padx=2, pady=2)

        # validation for size fields
        size_validation = (self.register(self.size_val), "%P")

        # width_start
        self.width_start_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Width Start (0-100%)", font=self.label_font)
        self.width_start_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)
        self.width_start_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.width_start_entry.grid(row=2, column=1, sticky="nw", padx=2, pady=2)

        # width_end
        self.width_end_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Width End (0-100%)", font=self.label_font)
        self.width_end_label.grid(row=3, column=0, sticky="nw", padx=2, pady=2)
        self.width_end_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.width_end_entry.grid(row=3, column=1, sticky="nw", padx=2, pady=2)

        # height_start
        self.height_start_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Height Start (0-100%)", font=self.label_font)
        self.height_start_label.grid(row=4, column=0, sticky="nw", padx=2, pady=2)
        self.height_start_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.height_start_entry.grid(row=4, column=1, sticky="nw", padx=2, pady=2)

        # height_end
        self.height_end_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Height End (0-100%)", font=self.label_font)
        self.height_end_label.grid(row=5, column=0, sticky="nw", padx=2, pady=2)
        self.height_end_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=size_validation)
        self.height_end_entry.grid(row=5, column=1, sticky="nw", padx=2, pady=2)
        
        # validation for fps field
        fps_validation = (self.register(self.fps_val), "%P")

        # fps
        self.fps_label = customtkinter.CTkLabel(self.tabview.tab("Video"), text="Max FPS (1-360)", font=self.label_font)
        self.fps_label.grid(row=6, column=0, sticky="nw", padx=2, pady=2)
        self.fps_entry = customtkinter.CTkEntry(self.tabview.tab("Video"), validate="key", validatecommand=fps_validation)
        self.fps_entry.grid(row=6, column=1, sticky="nw", padx=2, pady=2)

        # fullscreen
        self.fullscreen_switch = customtkinter.CTkSwitch(self.tabview.tab("Video"), text="Fullscreen")
        self.fullscreen_switch.grid(row=7, column=0, sticky="nw", padx=2, pady=2)

        ### AUDTIO TAB ###
        self.audio_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Audio", font=self.title_font)
        self.audio_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # sfx
        self.sfx_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Sound Effects", font=self.label_font)
        self.sfx_label.grid(row=1, column=0, sticky="nw", padx=2, pady=2)
        self.sfx_number = customtkinter.IntVar(value=0)
        self.sfx_slider = customtkinter.CTkSlider(self.tabview.tab("Audio"), from_=0, to=5, number_of_steps=5, command=self.set_sfx)
        self.sfx_slider.grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        self.sfx_number_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), textvariable=self.sfx_number, font=self.label_font)
        self.sfx_number_label.grid(row=1, column=2, sticky="nw", padx=2, pady=2)

        # bgm
        self.bgm_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), text="Background Music", font=self.label_font)
        self.bgm_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)
        self.bgm_number = customtkinter.DoubleVar()
        self.bgm_number_str = customtkinter.StringVar()
        self.bgm_number.trace_add("write", self.update_bgm_number_str)
        self.bgm_slider = customtkinter.CTkSlider(self.tabview.tab("Audio"), from_=0, to=1, number_of_steps=20, command=self.set_bgm)
        self.bgm_slider.grid(row=2, column=1, sticky="ew", padx=2, pady=2)
        self.bgm_number_label = customtkinter.CTkLabel(self.tabview.tab("Audio"), textvariable=self.bgm_number_str, font=self.label_font)
        self.bgm_number_label.grid(row=2, column=2, sticky="nw", padx=2, pady=2)

        ### EFFECTS TAB ###
        self.effects_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Effects", font=self.title_font)
        self.effects_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # effects
        self.effects_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Effects")
        self.effects_switch.grid(row=1, column=0, sticky="nw", padx=2, pady=2,)

        # names
        self.names_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Names")
        self.names_switch.grid(row=2, column=0, sticky="nw", padx=2, pady=2)

        # chat
        self.chat_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Chat")
        self.chat_switch.grid(row=3, column=0, sticky="nw", padx=2, pady=2)

        # glow + glitter
        self.glow_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Glow + Glitter")
        self.glow_switch.grid(row=4, column=0, sticky="nw", padx=2, pady=2)

        # model preview
        self.model_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Show Model Preview")
        self.model_switch.grid(row=5, column=0, sticky="nw", padx=2, pady=2)

        # metin2 cursor
        self.cursor_switch = customtkinter.CTkSwitch(self.tabview.tab("Effects"), text="Use Stellaria Cursor")
        self.cursor_switch.grid(row=6, column=0, sticky="nw", padx=2, pady=2)

        # fov
        self.fov_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="FOV", font=self.label_font)
        self.fov_label.grid(row=7, column=0, sticky="nw", padx=2, pady=2)
        self.fov_number = customtkinter.IntVar(value=0)
        self.fov_slider = customtkinter.CTkSlider(self.tabview.tab("Effects"), from_=0, to=90, number_of_steps=90, command=self.set_fov)
        self.fov_slider.grid(row=7, column=1, sticky="ew", padx=2, pady=2)
        self.fov_number_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), textvariable=self.fov_number, font=self.label_font)
        self.fov_number_label.grid(row=7, column=2, sticky="nw", padx=2, pady=2)

        # transparent
        self.transparent_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Transparency", font=self.label_font)
        self.transparent_label.grid(row=8, column=0, sticky="nw", padx=2, pady=2)
        self.transparent_number = customtkinter.DoubleVar()
        self.transparent_number_str = customtkinter.StringVar()
        self.transparent_number.trace_add("write", self.update_transparent_number_str)
        self.transparent_slider = customtkinter.CTkSlider(self.tabview.tab("Effects"), from_=0, to=1, number_of_steps=20, command=self.set_transparent)
        self.transparent_slider.grid(row=8, column=1, sticky="ew", padx=2, pady=2)
        self.transparent_number_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), textvariable=self.transparent_number_str, font=self.label_font)
        self.transparent_number_label.grid(row=8, column=2, sticky="nw", padx=2, pady=2)

        # shadows
        self.shadow_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Shadows", font=self.label_font)
        self.shadow_label.grid(row=9, column=0, sticky="nw", padx=2, pady=2)
        self.shadow_options = ["None", "Background", "Background + Player", "All - low", "All - Medium", "All - High"]
        self.shadow_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Effects"), width=175, values=self.shadow_options)
        self.shadow_optionmenu.grid(row=9, column=1, sticky="nw", padx=2, pady=2)

        # skybox
        self.skybox_label = customtkinter.CTkLabel(self.tabview.tab("Effects"), text="Skybox", font=self.label_font)
        self.skybox_label.grid(row=10, column=0, sticky="nw", padx=2, pady=2)
        self.skybox_options = ["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "Original"]
        self.skybox_optionmenu = customtkinter.CTkOptionMenu(self.tabview.tab("Effects"), width=175, values=self.skybox_options)
        self.skybox_optionmenu.grid(row=10, column=1, sticky="nw", padx=2, pady=2)

        ### COMBAT TAB ###
        self.combat_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Combat", font=self.title_font)
        self.combat_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # pet skill used in chat
        self.petskill_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Pet's Skill Message")
        self.petskill_switch.grid(row=1, column=0, sticky="nw", padx=2, pady=2)

        self.monsters_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Monsters", font=self.subtitle_font)
        self.monsters_label.grid(row=2, column=0, sticky="nw", padx=2, pady=2)

        # dogmode
        self.dogmode_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Use Dog-mode")
        self.dogmode_switch.grid(row=3, column=0, sticky="nw", padx=2, pady=2)

        # mob level
        self.moblvl_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Monster's Level")
        self.moblvl_switch.grid(row=4, column=0, sticky="nw", padx=2, pady=2)

        # aggresive mob indicator
        self.agromob_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Aggresive Indicator (*)")
        self.agromob_switch.grid(row=5, column=0, sticky="nw", padx=2, pady=2)

        self.damage_label = customtkinter.CTkLabel(self.tabview.tab("Combat"), text="Damage", font=self.subtitle_font)
        self.damage_label.grid(row=6, column=0, sticky="nw", padx=2, pady=2)

        # damage
        self.damage_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Damage")
        self.damage_switch.grid(row=7, column=0, sticky="nw", padx=2, pady=2,)

        # multiple targets damage
        self.multidmg_switch = customtkinter.CTkSwitch(self.tabview.tab("Combat"), text="Show Multi-target Damage")
        self.multidmg_switch.grid(row=8, column=0, sticky="nw", padx=2, pady=2)

        ### FUNCTIONAL TAB ###
        self.functional_label = customtkinter.CTkLabel(self.tabview.tab("Functional"), text="Functional", font=self.title_font)
        self.functional_label.grid(row=0, column=0, sticky="nw", padx=2, pady=2)

        # IME
        self.ime_switch = customtkinter.CTkSwitch(self.tabview.tab("Functional"), text="Use Stellaria IME")
        self.ime_switch.grid(row=1, column=0, sticky="nw", padx=2, pady=2,)

        # pickup
        self.pickup_switch = customtkinter.CTkSwitch(self.tabview.tab("Functional"), text="Pickup Everything")
        self.pickup_switch.grid(row=2, column=0, sticky="nw", padx=2, pady=2)

        # prepare loading screen
        self.loading = customtkinter.CTkLabel(self, text="Starting... Please Wait", font=customtkinter.CTkFont(size=50))

        # initialize values
        self.current_window = 1
        self.row_counter = 0
        self.buttons = []
        self.checkboxes = []
        self.delete_buttons = []
        self.edit_buttons = []
        self.settings = []
        self.to_start = []
        self.minfo = []

        # set default values
        self.defaults = ['0','100','0','100','60',0,0,0.000,1,1,1,1,1,1,90,1.000,5,9,1,0,1,1,1,1,1,1,self.get_monitor_values()[0]]
        self.scale_optionmenu.set("100%")

        # configure custom events
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<<BackgroundTaskFinished>>", lambda event: self.show_all())

        # load values from file
        self.get_saved_values()

    def get_saved_values(self):
        if path.exists(save_path):
            with open(save_path, 'r') as file:
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

        with open(save_path, 'w') as file:
            file.write(str([0,self.defaults]) + "\n")
            for window in self.settings:
                file.write(str(window) + "\n")   
            file.write(str([-1,states]) + "\n")
            file.write(str([-2,names]) + "\n")
            file.write(str([-3,self.scale_optionmenu.get(),self.update_checkbox.get()]))

    def open_stellaria(self):
        windll.user32.SetThreadDpiAwarenessContext(c_void_p(-1))
        minfo = []
        for monitor in EnumDisplayMonitors():
            m_info = GetMonitorInfo(monitor[0])
            minfo.append(m_info)
        self.minfo = minfo.copy()

        windows_to_start = []
        for window, start in zip(self.settings, self.to_start):
            if start == 1:
                if window[1][5] == 1:
                    x = -8
                    y = 0
                else:
                    work_area = []
                    for item in self.minfo:
                        if item['Device'].split("\\")[-1] == window[1][26].split()[0]:
                            work_area = item['Work']
                            break
                    x = int((int(window[1][0]) / 100) * (work_area[2]-work_area[0])) -8 + work_area[0]
                    y = int((int(window[1][2]) / 100) * (work_area[3]-work_area[1])) + work_area[1]
                windows_to_start.append([x,y,self.combine_values(window[1])])

        if self.update_checkbox.get() == 1 or not exe_path:
            uphwnds = []
            def updateEnumHandler(uphwnd, ctx):
                if IsWindowVisible(uphwnd):
                    _, process_id = GetWindowThreadProcessId(uphwnd)
                    if process_id == ctx:
                        ShowWindow(uphwnd, SW_HIDE)
                        uphwnds.append(uphwnd)

            process = Popen([update_path])
            pidd = process.pid
            p = Process(pidd)
            while True:
                EnumWindows(updateEnumHandler, pidd)
                if len(uphwnds) > 0:
                    break

            while True:
                io_counters = p.io_counters() 
                read = io_counters[2]
                write = io_counters[3]
                sleep(10)
                io_counters_new = p.io_counters() 
                read_new = io_counters_new[2]
                write_new = io_counters_new[3]
                if read == read_new and write == write_new:
                    sleep(1)
                    kill(pidd,15)
                    if path.exists(crash_path):
                        remove(crash_path)
                    break

        key_lines = []
        if path.exists(config_path): 
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
        access_time_timestamp = path.getatime(config_path)
        process = Popen([exe_path])
        pids.append(process.pid)

        if len(windows_to_start) > 1:
            for window in windows_to_start[1:]:
                while True:
                    access_time_timestamp_new = path.getatime(config_path)
                    if access_time_timestamp_new > access_time_timestamp:
                        sleep(0.1)
                        with open(config_path, 'w') as file:
                            for value in window[2]:
                                file.write((value) + "\n")
                            for key in key_lines:
                                file.write((key) + "\n")
                        access_time_timestamp = path.getatime(config_path)
                        process = Popen([exe_path])
                        pids.append(process.pid)
                        break

        hwnds = []
        com = []
        for win, pid in zip(windows_to_start,pids):
            fsc = findall(r'\d+', win[2][3])
            com.append([win[0],win[1],pid,int(fsc[0])])

        def winEnumHandler(hwnd, ctx):
            if IsWindowVisible(hwnd):
                _, process_id = GetWindowThreadProcessId(hwnd)
                if process_id == ctx[2]:
                    if ctx[3] != 0:
                        rect = GetWindowRect(hwnd)
                        w = rect[2] - rect[0]
                        h = rect[3] - rect[1]
                        MoveWindow(hwnd, ctx[0], ctx[1], w, h, True)
                    hwnds.append(hwnd)
                    com.remove(ctx)

        while True:
            for vals in com:
                EnumWindows(winEnumHandler, vals)
            if len(pids) == len(hwnds):
                break

        self.event_generate("<<BackgroundTaskFinished>>", when="tail")
    def start(self):
        self.start_button.configure(state="disabled")
        self.save_file()
        self.get_selected_windows()

        # check if at least one window exists
        if len(self.settings) == 0:
            CTkMessagebox(master=self, title="Warning Message!", message=f"Please create and select at least one window", icon="warning")
            self.start_button.configure(state="normal")
            return
        
        # check if at least one window is selected
        if sum(self.to_start) == 0:
            CTkMessagebox(master=self, title="Warning Message!", message=f"Please select at least one window to start", icon="warning")
            self.start_button.configure(state="normal")
            return
        
        # check if patcher exists
        if self.update_checkbox.get() == 1:
            if not path.exists(update_path):
                CTkMessagebox(master=self, title="Warning Message!", message=f"Cannot find .Stellaria-launcher.exe, please rename your launcher", icon="warning")
                self.start_button.configure(state="normal")
                return
        
        # check for empty fields and valid monitor selection
        for window, start, but in zip(self.settings,self.to_start,self.buttons):
            if start == 1:
                if window[1][0] == "" or window[1][1] == "" or window[1][2] == "" or window[1][3] == "" or window[1][4] == "":
                    CTkMessagebox(master=self, title="Warning Message!", message=f"Please fill out all Video fields in {but[1].cget("text")}", icon="warning")
                    self.start_button.configure(state="normal")
                    return
                elif window[1][5] == "":
                    CTkMessagebox(master=self, title="Warning Message!", message=f"Please fill out the FPS field in {but[1].cget("text")}", icon="warning")
                    self.start_button.configure(state="normal")
                    return
                device = self.get_monitor_values()
                if window[1][26] not in device:
                    CTkMessagebox(master=self, title="Warning Message!", message=f"Please select a valid monitor in {but[1].cget("text")}", icon="warning")
                    self.display_optionmenu.configure(values=device.copy())
                    self.start_button.configure(state="normal")
                    return
        
        # start opening windows
        self.hide_all()
        open_met = Thread(target=self.open_stellaria)
        open_met.start()



    def get_selected_windows(self):
        to_start = []
        for checkbox in self.checkboxes:
            if checkbox[1].get() == 1:
                to_start.append(1)
            else:
                to_start.append(0)
        self.to_start = to_start.copy()
    def get_monitor_values(self):
        device = []
        for monitor in EnumDisplayMonitors():
            m_info = GetMonitorInfo(monitor[0])
            if m_info.get('Flags') == 1:
                device.append(m_info.get('Device').split("\\")[-1]+" (Main)")
            else:
                device.append(m_info.get('Device').split("\\")[-1])
        return device
    def check_screens(self,value):
        device = self.get_monitor_values()
        if value not in device:
            self.display_optionmenu.set(device[0])
        self.display_optionmenu.configure(values=device.copy())

    def hide_all(self):
        self.start_frame.grid_forget()
        self.sidebar_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.tabview.grid_forget()

        self.loading.grid(row=0, column=0, rowspan=50, columnspan=50, sticky="nsew", padx=20, pady=20)
    def show_all(self):
        self.loading.grid_forget()

        self.start_frame.grid(row=2, column=0, sticky="nsew")
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.settings_frame.grid(row=0, column=1, sticky="nsew")
        self.tabview.grid(row=1, column=1, rowspan=2, padx=20, pady=(0,20), sticky="nsew")
        self.start_button.configure(state="normal")

    def combine_values(self, values):
        # get the working area
        work_area = []
        for item in self.minfo:
            if item['Device'].split("\\")[-1] == values[26].split()[0]:
                work_area = item['Work']
                break
        
        # calculate width and height
        width = ceil(((abs(int(values[1])-int(values[0]))) / 100) * (work_area[2] - work_area[0]))
        height = ceil((((abs(int(values[3])-int(values[2]))) / 100) * (work_area[3] - work_area[1])) - windll.user32.GetSystemMetrics(4) - 8)

        # prepare settings.cfg file
        settings = ["WIDTH "+str(width),
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
        return settings   
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
        self.display_optionmenu.set(values[26])
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
                   self.pickup_switch.get(),
                   self.display_optionmenu.get()]
        return values
    
    def sidebar_button_event(self, b_id):
        # save values of previous window
        for list in self.settings:
            if int(list[0]) == int(self.current_window):
                list[1] = self.get_values()
                break

        # set the pressed window to current
        for button in self.buttons:
            if button[0] == b_id:
                button[1].configure(fg_color=["#325882", "#14375e"])
                self.current_window = button[0]
            else:
                button[1].configure(fg_color=["#3B8ED0", "#1F6AA5"])
                
        # show values for current window
        for list in self.settings:
            if int(list[0]) == int(self.current_window):
                self.set_values(list[1])
                break
    def sidebar_add_window(self, settings=[]):
        self.row_counter += 1
        button_id = self.row_counter

        # add delete button
        delete_button = customtkinter.CTkButton(self.sidebar_frame, text="X", fg_color="red", width=28, hover_color="#8B0000", font=customtkinter.CTkFont(size=15, weight="bold"), command=lambda b_id=button_id: self.sidebar_delete_window(b_id))
        delete_button.grid(row=self.row_counter, column=0, padx=5, pady=5, sticky="nws")

        # add edit button
        edit_name_button = customtkinter.CTkButton(self.sidebar_frame, text="E", fg_color="#ff7900", width=28, hover_color="#b35500", font=customtkinter.CTkFont(size=15, weight="bold"), command=lambda b_id=button_id: self.rename_window(b_id))
        edit_name_button.grid(row=self.row_counter, column=1, padx=(0,5), pady=5, sticky="nws")

        # add window button
        sidebar_button = customtkinter.CTkButton(self.sidebar_frame, text=(f'Window{button_id}'), command=lambda b_id=button_id: self.sidebar_button_event(b_id))
        sidebar_button.grid(row=self.row_counter, column=2, padx=(0,5), pady=5,sticky="nsew")

        # add checkbox
        checkbox = customtkinter.CTkCheckBox(self.sidebar_frame, text="", hover_color="green",fg_color="green", width=24)
        checkbox.grid(row=self.row_counter, column=3, pady=5, sticky="nws")

        # move add button down
        self.sidebar_button_add.grid(row=self.row_counter+1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)

        # save widgets
        if settings == []:
            self.settings.append([button_id,self.defaults])
        else:
            self.settings.append([button_id,settings])   
        self.delete_buttons.append([button_id,delete_button])
        self.buttons.append([button_id,sidebar_button])
        self.checkboxes.append([button_id,checkbox])
        self.edit_buttons.append([button_id,edit_name_button])
        self.sidebar_button_event(button_id)
        
        # show settings if hidden (1 or more windows exists)
        if not self.tabview.winfo_ismapped():
            self.tabview.grid(row=1, column=1, rowspan=2, padx=20, pady=15, sticky="nsew")
            self.load_defaults_button.grid(row=0, column=4, padx=(0,10), pady=(20,3), sticky="e")
            self.save_defaults_button.grid(row=0, column=5, padx=(0,20), pady=(20,3), sticky="e")
    def sidebar_delete_window(self, id):
        # delete the delete button
        for delete_button in self.delete_buttons:
            if delete_button[0] == id:
                delete_button[1].grid_forget()
                delete_button[1].destroy()
                self.delete_buttons.remove(delete_button)
                break

        # delete the edit button
        for edit_button in self.edit_buttons:
            if edit_button[0] == id:
                edit_button[1].grid_forget()
                edit_button[1].destroy()
                self.edit_buttons.remove(edit_button)
                break

        # delete the window button
        for button in self.buttons:
            if button[0] == id:
                button[1].grid_forget()
                button[1].destroy()
                self.buttons.remove(button)
                break

        # delete the checkbox
        for checkbox in self.checkboxes:
            if checkbox[0] == id:
                checkbox[1].grid_forget()
                checkbox[1].destroy()
                self.checkboxes.remove(checkbox)
                break
        
        # delete the settings
        for setting in self.settings:
            if setting[0] == id:
                self.settings.remove(setting)
                break
        
        # hide settings if no button
        if len(self.buttons) == 0:
            self.hide_settings()
        else:
            # if active button was delete
            if id == self.current_window:

                # select the last button
                self.buttons[-1][1].configure(fg_color=["#325882", "#14375e"])
                self.current_window = self.buttons[-1][0]

                #get settings for last button
                for list in self.settings:
                    if int(list[0]) == int(self.current_window):
                        self.set_values(list[1])
                        break    
    def rename_window(self, id):
        for button in self.buttons:
            if button[0] == id:
                previous_name = button[1].cget("text")
                dialog = customtkinter.CTkInputDialog(text="Type in a new name:", title=f"Rename {previous_name}",)
                mouse = Controller()
                position = mouse.position
                dialog.geometry("+"+str(position[0])+"+"+str(position[1]))
                out = dialog.get_input()
                if out != None:
                    button[1].configure(text=out)
                break

    def hide_settings(self):
        self.tabview.grid_forget()
        self.save_defaults_button.grid_forget()
        self.load_defaults_button.grid_forget()       
    def show_settings(self):
        self.tabview.grid(row=1, column=1, rowspan=2, columnspan = 3, padx=20, pady=(0,20), sticky="nsew")
        self.load_defaults_button.grid(row=0, column=2, padx=(0,10), pady=(20,0), sticky="nsew")
        self.save_defaults_button.grid(row=0, column=3, padx=(0,20), pady=(20,0), sticky="nsew")       

    def save_defaults(self):
        self.defaults = self.get_values()
    def load_defaults(self):
        self.set_values(self.defaults)

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

    def update_bgm_number_str(self, *args):
        self.bgm_number_str.set(f"{self.bgm_number.get():.3f}")
    def update_transparent_number_str(self, *args):
        self.transparent_number_str.set(f"{self.transparent_number.get():.3f}")

    def size_val(self, P):
        if P == "":
            return True
        if P.isdigit():
            if (0 <= int(P) <= 100):
                if int(P[0]) == 0 and len(P) > 1:
                    return False
                return True
            return False
        return False
    def fps_val(self, P):
        if P == "":
            return True
        if P.isdigit():
            if (1 <= int(P) <= 360):
                return True
            return False
        return False

    def close(self):
        self.save_file()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()