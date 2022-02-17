import numpy as np
import threading
import time
import string
import PySimpleGUI as sg
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from webbrowser import open as open_browser

from pyPhoto21.viewers.frame import FrameViewer
from pyPhoto21.viewers.trace import TraceViewer
from pyPhoto21.viewers.time_course import TimeCourseViewer
from pyPhoto21.analysis.roi import ROI
from pyPhoto21.gui_elements.layouts import *
from pyPhoto21.gui_elements.event_mapping import EventMapping
from pyPhoto21.export import Exporter


# from mpl_interactions import image_segmenter


# import io


class GUI:

    def __init__(self, data, production_mode=True):
        matplotlib.use("TkAgg")
        sg.theme('DarkBlue12')
        self.data = data
        data.gui = self
        self.production_mode = production_mode
        self.tv = TraceViewer(self)
        self.fv = FrameViewer(self.data, self.tv)
        self.tcv = TimeCourseViewer(self)
        self.roi = ROI(self.data)
        self.exporter = Exporter(self.tv, self.fv)
        self.layouts = Layouts(data)
        self.window = None

        # general state/settings
        self.title = "Photo21"
        self.freeze_input = False  # whether to allow fields to be updated. Frozen during acquire (how about during file loaded?)
        self.event_mapping = None
        self.define_event_mapping()  # event callbacks used in event loops
        self.cached_num_pts = 600  # number of points to restore to whenever not 200 Hz cam program
        self.cached_num_trials = 5
        # kickoff workflow
        if self.production_mode:
            self.introduction()
        self.main_workflow()

    def introduction(self):
        layout = [[
            sg.Column([[sg.Image(key="-IMAGE-")]]),
            [sg.Text("Welcome to Photo21! \n\tCheck that your camera and \n\tNI-USB are turned on.")],
            [sg.Button("OK")]
        ]]
        intro_window = sg.Window(self.title, layout, finalize=True)
        self.intro_event_loop(intro_window)
        intro_window.close()

    @staticmethod
    def intro_event_loop(window, filename='art/meyer.png'):
        window["-IMAGE-"].update(filename=filename)
        while True:
            event, values = window.read()
            # End intro when user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break

    def main_workflow(self):
        right_col = self.layouts.create_right_column(self)
        left_col = self.layouts.create_left_column(self)
        toolbar_menu = self.layouts.create_menu()

        layout = [[toolbar_menu],
                  [sg.Column(left_col),
                   sg.VSeperator(),
                   sg.Column(right_col)]]

        self.window = sg.Window(self.title,
                                layout,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        self.window.Maximize()
        self.plot_trace()
        self.plot_frame()
        self.plot_time_course()
        self.main_workflow_loop()
        self.window.close()

    def main_workflow_loop(self, history_debug=False, window=None, exit_event="Exit"):
        if window is None:
            window = self.window
        events = ''
        while True:
            event, values = window.read()
            if history_debug and event is not None and not self.production_mode:
                events += str(event) + '\n'
            if event == exit_event or event == sg.WIN_CLOSED or event == '-close-':
                if self.is_recording():
                    self.data.save_metadata_to_json()
                break
            elif event not in self.event_mapping or self.event_mapping[event] is None:
                print("Not Implemented:", event)
            else:
                ev = self.event_mapping[event]
                if event in values:
                    ev['args']['window'] = window
                    ev['args']['values'] = values[event]
                    ev['args']['event'] = event
                ev['function'](**ev['args'])
        if history_debug and not self.production_mode:
            print("**** History of Events ****\n", events)

    def plot_time_course(self):
        fig = self.tcv.get_fig()
        figure_canvas_agg = self.draw_figure(self.window['time_course_canvas'].TKCanvas, fig)
        figure_canvas_agg.mpl_connect('scroll_event', self.tcv.onscroll)
        figure_canvas_agg.mpl_connect('button_press_event', self.tcv.onpress)
        figure_canvas_agg.mpl_connect('motion_notify_event', self.tcv.onmove)
        self.tcv.update()

    def plot_trace(self):
        fig = self.tv.get_fig()
        figure_canvas_agg = self.draw_figure(self.window['trace_canvas'].TKCanvas, fig)
        figure_canvas_agg.mpl_connect('scroll_event', self.tv.onscroll)
        figure_canvas_agg.mpl_connect('button_press_event', self.tv.onpress)
        figure_canvas_agg.mpl_connect('motion_notify_event', self.tv.onmove)

    def plot_frame(self):
        fig = self.fv.get_fig()

        figure_canvas_agg = self.draw_figure(self.window['frame_canvas'].TKCanvas, fig)
        figure_canvas_agg.mpl_connect('button_release_event', self.fv.onrelease)
        figure_canvas_agg.mpl_connect('button_press_event', self.fv.onpress)
        figure_canvas_agg.mpl_connect('key_press_event', self.fv.onkeypress)
        figure_canvas_agg.mpl_connect('key_release_event', self.fv.onkeyrelease)
        figure_canvas_agg.mpl_connect('motion_notify_event', self.fv.onmove)
        figure_canvas_agg.mpl_connect('scroll_event', self.fv.onscroll)
        self.window['frame_canvas'].TKCanvas.focus_force()
        s_max = self.fv.get_slider_max()
        if s_max is not None:
            s_max.on_changed(self.fv.change_frame)

    @staticmethod
    def draw_figure(canvas, fig):
        if canvas.children:
            for child in canvas.winfo_children():
                child.destroy()
        figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
        figure_canvas_agg.draw_idle()
        figure_canvas_agg.get_tk_widget().pack(fill='none', expand=True)
        return figure_canvas_agg

    def get_trial_sleep_time(self):
        sleep_sec = self.data.get_int_trials()
        if self.data.get_is_schedule_rli_enabled():
            sleep_sec = max(0, sleep_sec - .12)  # attempt to shorten by 120 ms, rough lower bound on time to take RLI
        return sleep_sec

    def get_record_sleep_time(self):
        sleep_sec = self.data.get_int_records()
        return max(0, sleep_sec - self.get_trial_sleep_time())

    def launch_hyperslicer(self):
        self.fv.launch_hyperslicer()

    def toggle_show_rli(self, **kwargs):
        v = bool(kwargs['values'])
        self.data.meta.show_rli = v
        if v:
            self.fv.slider_enabled = False
            self.window["Select Background"].update(disabled=True)
        else:
            self.fv.enable_disable_slider()
            self.window["Select Background"].update(disabled=False)
        self.fv.set_show_rli_flag(v, update=True)

    @staticmethod
    def notify_window(title, message):
        layout = [[sg.Column([
            [sg.Text(message)],
            [sg.Button("OK")]])]]
        wind = sg.Window(title, layout, finalize=True)
        while True:
            event, values = wind.read()
            # End intro when user closes window or
            # presses the OK button
            if event == "OK" or event == sg.WIN_CLOSED:
                break
        wind.close()

    def choose_save_dir(self, **kwargs):
        folder = self.browse_for_folder()
        if folder is not None:
            self.data.set_save_dir(folder)
            self.data.db.set_save_dir(folder)
            self.exporter.set_save_dir(folder)
            self.window["Time Course File Selector"].update(self.data.get_data_filenames_in_folder())
            print("New save location:", folder)

    def browse_for_file(self, file_extensions, multi_file=False, tsv_only=False):
        layout_choice = None
        if not multi_file:
            layout_choice = self.layouts.create_file_browser()
        else:
            layout_choice = self.layouts.create_files_browser()
        file_window = sg.Window('File Browser',
                                layout_choice,
                                finalize=True,
                                element_justification='center',
                                resizable=True,
                                font='Helvetica 18')
        file = None
        # file browser event loop
        while True:
            event, values = file_window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                file_window.close()
                return
            elif event == "file_window.open":
                file = values["file_window.browse"]
                file_ext = file.split('.')
                if len(file_ext) > 0:
                    file_ext = file_ext[-1]
                else:
                    file_ext = ''
                if file_ext not in file_extensions:
                    supported_file_str = " ".join(file_extensions)
                    self.notify_window("File Type",
                                       "Unsupported file type.\nSupported: " + supported_file_str)
                else:
                    break
        if self.freeze_input and not self.data.get_is_loaded_from_file():
            file = None
            self.notify_window("File Input Error",
                               "Cannot load file during acquisition")
        file_window.close()
        return file

    def browse_for_save_as_file(self, file_types=(("Tab-Separated Value file", "*.tsv"),)):
        w = sg.Window('Save As',
                      self.layouts.create_save_as_browser(file_types),
                      finalize=True,
                      element_justification='center',
                      resizable=True,
                      font='Helvetica 18')
        new_file = None
        # file browser event loop
        while True:
            event, values = w.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                w.close()
                return
            elif event == "save_as_window.open":
                new_file = values["save_as_window.browse"]
                break
        if self.is_recording():
            new_file = self.data.get_save_dir()
            self.notify_window("Warning",
                               "Please stop recording before exporting data.")
            new_file = None
        w.close()
        if new_file is None or len(new_file) < 1:
            return None
        return new_file

    def browse_for_folder(self, recording_notif=True):
        folder_window = sg.Window('Folder Browser',
                                  self.layouts.create_folder_browser(),
                                  finalize=True,
                                  element_justification='center',
                                  resizable=True,
                                  font='Helvetica 18')
        folder = None
        # file browser event loop
        while True:
            event, values = folder_window.read()
            if event == sg.WIN_CLOSED or event == "Exit":
                folder_window.close()
                return
            elif event == "folder_window.open":
                folder = values["folder_window.browse"]
                break
        if recording_notif and self.is_recording():
            folder = self.data.get_save_dir()
            self.notify_window("Warning",
                               "You are changing the save location during acquisition." +
                               "I don't recommend scattering your files. " +
                               "Keeping this save directory:\n" +
                               folder)
        folder_window.close()
        if len(folder) < 1:
            return None
        return folder

    def load_roi_file(self, **kwargs):
        filename = self.browse_for_file(['roi'])
        data_obj = self.data.retrieve_python_object_from_json(filename)
        self.roi.load_roi_data(data_obj)

    def save_roi_file(self, **kwargs):
        data_obj, filename = self.roi.dump_roi_data()
        self.data.dump_python_object_to_json(filename,
                                             data_obj,
                                             extension='roi')

    def load_preference(self):
        file = self.browse_for_file(['json'])
        if file is not None:
            print("Loading from preference file:", file)
            self.data.load_preference_file(file)
            self.sync_gui_fields_from_meta()
            self.fv.update_new_image()
            self.tv.update_new_traces()

    def save_preference(self):
        file = self.browse_for_save_as_file(('JSON', "*" + self.data.metadata_extension))
        if file is not None:
            self.data.save_preference_file(file)

    def load_data_file(self):
        file = self.browse_for_file(['npy', 'json', 'zda', 'tsm', 'fits'])
        if file is not None:
            self.freeze_hardware_settings(include_buttons=False, freeze_file_flip=False)
            print("Loading from file:", file, "\nThis will take a few seconds...")
            self.data.load_from_file(file)
            # Sync GUI
            self.sync_gui_fields_from_meta()
            # Freeze input fields to hardware

            print("File Loaded.")
            self.fv.update_new_image()
            self.tv.update_new_traces()

    # Pull all file-based data from Data and sync GUI fields
    def sync_gui_fields_from_meta(self):
        w = self.window
        base_skip = self.data.core.get_baseline_skip_window()
        int_pts = self.data.get_int_pts()

        # Analysis Settings
        w["Select Baseline Correction"].update(self.data.core.get_baseline_correction_options()[
                                                   self.data.core.get_baseline_correction_type_index()])
        w["Baseline Skip Window Start frames"].update(base_skip[0])
        w["Baseline Skip Window End frames"].update(base_skip[1])
        w["Baseline Skip Window Start (ms)"].update(base_skip[0] * int_pts)
        w["Baseline Skip Window End (ms)"].update(base_skip[1] * int_pts)
        w['T-Filter'].update(self.data.core.get_is_temporal_filter_enabled())
        w['Select Temporal Filter'].update(self.data.core.get_temporal_filter_options()[self.data.core.get_temporal_filter_index()])
        w['Temporal Filter Radius'].update(self.data.core.get_temporal_filter_radius())
        w['S-Filter'].update(self.data.core.get_is_spatial_filter_enabled())
        w['Spatial Filter Sigma'].update(self.data.core.get_spatial_filter_sigma())
        w['RLI Division'].update(self.data.get_is_rli_division_enabled())
        w['Data Inverse'].update(self.data.get_is_data_inverse_enabled())
        w['Digital Binning'].update(self.data.meta.binning)
        w['Data Inverse'].update(self.data.get_is_data_inverse_enabled())
        w['Average Trials'].update(self.data.get_is_trial_averaging_enabled())

        t_measure = self.data.get_measure_window()
        if t_measure[1] == -1:
            t_measure[1] = self.data.get_num_pts()
        w['Measure Window End (ms)'].update(str(t_measure[1] * int_pts)[:6])
        w['Measure Window Start (ms)'].update(str(t_measure[0] * int_pts)[:6])
        w['Measure Window End frames'].update(str(t_measure[1])[:6])
        w['Measure Window Start frames'].update(str(t_measure[0])[:6])

        t_art = self.data.get_artifact_exclusion_window()
        if t_art[1] == -1:
            t_art[1] = self.data.get_num_pts()
        w['Camera Artifact Exclusion Window Start (ms)'].update(str(t_art[0] * int_pts)[:6])
        w['Camera Artifact Exclusion Window End (ms)'].update(str(t_art[1] * int_pts)[:6])
        w['Camera Artifact Exclusion Window Start frames'].update(str(t_art[0])[:6])
        w['Camera Artifact Exclusion Window End frames'].update(str(t_art[1])[:6])

        # ROI Settings
        t_pre_stim = self.roi.get_time_window('pre_stim')
        t_stim = self.roi.get_time_window('stim')
        if t_pre_stim[1] == -1:
            t_pre_stim[1] = self.data.get_num_pts()
        if t_stim[1] == -1:
            t_stim[1] = self.data.get_num_pts()
        w['Identify ROI'].update(self.data.meta.is_roi_enabled)
        w['Time Window End (ms) stim'].update(str(t_stim[1] * int_pts)[:6])
        w['Time Window Start (ms) stim'].update(str(t_stim[0] * int_pts)[:6])
        w['Time Window End frames stim'].update(str(t_stim[1])[:6])
        w['Time Window Start frames stim'].update(str(t_stim[0])[:6])
        w['Time Window End (ms) pre_stim'].update(str(t_pre_stim[1] * int_pts)[:6])
        w['Time Window Start (ms) pre_stim'].update(str(t_pre_stim[0] * int_pts)[:6])
        w['Time Window End frames pre_stim'].update(str(t_pre_stim[1])[:6])
        w['Time Window Start frames pre_stim'].update(str(t_pre_stim[0])[:6])

        w['Notepad'].update(self.data.meta.notepad_text)
        display_value_options = self.tv.get_display_value_options()
        w["Select Display Value"].update(display_value_options[self.get_display_value_option_index()])

        self.update_tracking_num_fields()

    # disable file-viewing mode, allowing acquisition to resume
    def unload_file(self):
        if self.data.get_is_loaded_from_file():
            self.unfreeze_hardware_settings()
            self.data.set_is_loaded_from_file(False)
            self.fv.update_new_image()

    @staticmethod
    def launch_github_page(**kwargs):
        urls = {
            'technical': 'https://github.com/john-judge/PhotoLib#photolib',
            'user': 'https://github.com/john-judge/PhotoLib/blob/master/'
                    'TUTORIAL.md#users-manual-for-pyphoto21-little-dave',  # Update this to user tutorial link
            'issue': 'https://github.com/john-judge/PhotoLib/issues/new'
        }
        if 'kind' in kwargs and kwargs['kind'] in urls:
            open_browser(urls[kwargs['kind']], new=2)

    @staticmethod
    def launch_youtube_tutorial():
        pass

    @staticmethod
    def launch_little_dave_calendar(**kwargs):
        open_browser('https://calendar.google.com/calendar'
                     '/render?cid=24tfud764rqbe4tcdgvqmi6pdc@'
                     'group.calendar.google.com')

    # Returns True if string s is a valid numeric input
    @staticmethod
    def validate_numeric_input(s, non_zero=False, max_digits=None, min_val=None, max_val=None, decimal=False):
        if decimal:  # decimals: allow removing at most one decimal anywhere
            if len(s) > 0 and s[0] == '.':
                s = s[1:]
            elif len(s) > 0 and s[-1] == '.':
                s = s[:-1]
            elif '.' in s:
                s = s.replace('.', '')
        return type(s) == str \
               and s.isnumeric() \
               and (max_digits is None or len(s) <= max_digits) \
               and (not non_zero or int(s) != 0) \
               and (min_val is None or int(s) >= min_val) \
               and (max_val is None or int(s) <= max_val)

    def set_digital_binning(self, **kwargs):
        binning = kwargs['values']
        while len(binning) > 0 and \
                (not self.validate_numeric_input(binning, max_val=min(self.data.get_display_width(),
                                                                      self.data.get_display_height()) // 4)
                 or len(binning) > 3):
            binning = binning[:-1]
        if not self.validate_numeric_input(binning, non_zero=True):
            self.window['Digital Binning'].update('')
            return
        else:
            self.window['Digital Binning'].update(binning)
        binning = int(binning)
        self.fv.set_digital_binning(binning)

    def toggle_average_trials(self, **kwargs):
        v = bool(kwargs['values'])
        new_index = 0
        if v:
            new_index = None
        self.data.set_is_trial_averaging_enabled(v)
        self.set_current_trial_index(value=new_index)
        self.window["Trial Number"].update(str(self.data.get_current_trial_index()))

    @staticmethod
    def pass_no_arg_calls(**kwargs):
        for key in kwargs:
            if key.startswith('call'):
                kwargs[key]()

    def validate_and_pass_int(self, **kwargs):
        max_val = None
        if 'max_val' in kwargs:
            max_val = kwargs['max_val']
        fn_to_call = kwargs['call']
        v = kwargs['values']
        window = kwargs['window']
        while len(v) > 0 and not self.validate_numeric_input(v, max_digits=5, max_val=max_val):
            v = v[:-1]
        if len(v) > 0 and self.validate_numeric_input(v, max_digits=5, max_val=max_val):
            fn_to_call(value=int(v))
            window[kwargs['event']].update(v)
            if not self.production_mode:
                print("called:", fn_to_call)
            if 'call2' in kwargs:
                kwargs['call2'](value=int(v))
                if not self.production_mode:
                    print("called:", kwargs['call2'])
        else:
            fn_to_call(value=None)
            window[kwargs['event']].update('')

    # for passing to channel-based setters
    def validate_and_pass_channel(self, **kwargs):
        fns_to_call = []
        for k in kwargs:
            if k.startswith('call'):
                fns_to_call.append(kwargs[k])
        v = kwargs['values']
        ch = kwargs['channel']
        window = kwargs['window']
        while len(v) > 0 and not self.validate_numeric_input(v, max_digits=6):
            v = v[:-1]
        if len(v) > 0 and self.validate_numeric_input(v, max_digits=6):
            for fn in fns_to_call:
                fn(value=int(v), channel=ch)
            window[kwargs['event']].update(v)
            if not self.production_mode:
                print("called:", fns_to_call)
        else:
            for fn in fns_to_call:
                fn(value=0, channel=ch)
            window[kwargs['event']].update('')

    def launch_roi_settings(self, **kwargs):
        w = sg.Window('ROI Identification Settings',
                      self.layouts.create_roi_settings_form(self),
                      finalize=True,
                      element_justification='center',
                      resizable=True,
                      font='Helvetica 18')
        # roi settings event loop
        self.main_workflow_loop(window=w, exit_event="Exit ROI")
        w.close()

    def enable_roi_identification(self, **kwargs):
        if kwargs['values']:
            self.roi.enable_roi_identification()
        else:
            self.roi.disable_roi_identification()
        self.fv.update_new_image()

    def set_cutoff(self, **kwargs):
        form = kwargs['form']
        v = kwargs['values']
        window = kwargs['window']
        max_val = None
        min_val = None
        if form == 'percentile':
            max_val = 100.0
            min_val = 0.0
        while len(v) > 0 and not self.validate_numeric_input(v, min_val=min_val, max_val=max_val, decimal=True):
            v = v[:-1]

        if len(v) > 0 and form == 'percentile' and float(v) > max_val:
            v = str(max_val)

        partner_field = None
        partner_form = None
        if form == 'Raw':
            partner_form = 'Percentile'
            partner_field = kwargs['event'].replace('Raw', 'Percentile')
        else:
            partner_form = 'Raw'
            partner_field = kwargs['event'].replace('Percentile', 'Raw')

        self.roi.set_cutoff(kwargs['kind'],
                            form,
                            v)
        partner_v = self.roi.get_cutoff(kwargs['kind'], partner_form)
        window[partner_field].update(str(partner_v))
        if len(v) == 0 or float(v) != kwargs['values']:
            window[kwargs['event']].update(v)

    # generic setter that links together 2 ms / frame linked fields
    def set_time_window_generic(self, setter_function, arg_dict):
        v = arg_dict['values']
        form = arg_dict['form']
        kind = arg_dict['kind']
        index = arg_dict['index']
        partner_field = None
        partner_v = None
        if form == 'ms':
            partner_field = arg_dict['event'].replace('(ms)', 'frames')
        else:
            partner_field = arg_dict['event'].replace('frames', '(ms)')

        # if possible, trim input of invalid characters
        while len(v) > 0 and not self.validate_numeric_input(v,
                                                             non_zero=True,
                                                             min_val=0,
                                                             max_val=self.data.get_num_pts()):
            v = v[:-1]

        if len(v) > 0 and self.validate_numeric_input(v,
                                                      non_zero=True,
                                                      min_val=0,
                                                      max_val=self.data.get_num_pts()):
            if form == 'ms':
                v = float(v)
                partner_v = int(v / self.data.get_int_pts())
            else:
                v = int(v)
                partner_v = float(v * self.data.get_int_pts())

            self.window[partner_field].update(str(partner_v)[:6])
            self.window[arg_dict['event']].update(str(v)[:6])
            setter_function(kind, index, v)
        else:
            v = None
            if index == 0:
                v = 0
            elif index == 1:
                v = self.data.get_num_pts()
            setter_function(kind, index, v)
            self.window[partner_field].update('')
            self.window[arg_dict['event']].update('')

    def set_baseline_skip_window(self, **kwargs):
        self.set_time_window_generic(self.data.core.set_baseline_skip_window, kwargs)
        self.tv.update_new_traces()

    def set_roi_time_window(self, **kwargs):
        self.set_time_window_generic(self.roi.set_time_window, kwargs)

    def set_measure_window(self, **kwargs):
        self.set_time_window_generic(self.data.set_measure_window, kwargs)
        self.fv.update_new_image()
        self.tv.update_new_traces()

    def set_artifact_window(self, **kwargs):
        self.set_time_window_generic(self.data.set_artifact_exclusion_window, kwargs)
        self.fv.update_new_image()
        self.tv.update_new_traces()

    def select_baseline_skip_window(self):
        print("select_baseline_skip_window (graphical method) not implemented")

    def select_time_window_workflow_generic(self):
        # to be a generic method for helping graphically choose a time window
        pass

    def set_roi_k_clusters(self, **kwargs):
        k = kwargs['values']
        while len(k) > 0 and not self.validate_numeric_input(k,
                                                             non_zero=True,
                                                             max_digits=3,
                                                             min_val=0,
                                                             max_val=None,
                                                             decimal=False):
            k = k[:-1]
        if kwargs['values'] != k:
            kwargs['window'][kwargs['event']].update(k)
        if len(k) == 0:
            k = None
        else:
            k = int(k)
        self.roi.set_k_clusters(k)

    def view_roi_plot(self, **kwargs):
        plot_type = kwargs['type']
        self.roi.launch_cluster_score_plot(plot_type)

    def define_event_mapping(self):
        if self.event_mapping is None:
            self.event_mapping = EventMapping(self).get_event_mapping()

    def update_tracking_num_fields(self, no_plot_update=False, **kwargs):
        self.window["Slice Number"].update(self.data.get_slice_num())
        self.window["Location Number"].update(self.data.get_location_num())
        self.window["Record Number"].update(self.data.get_record_num())
        self.window["Trial Number"].update(self.data.get_current_trial_index())
        self.window["File Name"].update(self.data.db.get_current_filename(no_path=True,
                                                                          extension=self.data.db.extension))
        if not no_plot_update:
            self.fv.update_new_image()
            self.tv.update_new_traces()

    def set_current_trial_index(self, **kwargs):
        if 'value' in kwargs:
            if kwargs['value'] is None:
                value = None
            else:
                value = int(kwargs['value'])
            self.data.set_current_trial_index(value)
            self.fv.update_new_image()
            self.tv.update_new_traces()

    def set_slice(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_slice(value)
        self.fv.update_new_image()

    def set_record(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_record(value)
        self.fv.update_new_image()

    def set_location(self, **kwargs):
        value = int(kwargs['value'])
        self.data.set_location(value)
        self.fv.update_new_image()

    def set_background_option_index(self, **kwargs):
        bg_name = kwargs['values']
        bg_index = self.data.get_background_options().index(bg_name)
        self.data.db.meta.background_option_index = bg_index
        self.fv.enable_disable_slider()
        self.tv.update_new_traces()

    # value to display in trace viewer
    def get_display_value_option_index(self):
        return self.data.get_display_value_option_index()

    # value to display in trace viewer
    def set_display_value_option_index(self, **kwargs):
        name = kwargs['values']
        ind = self.tv.get_display_value_options().index(name)
        self.data.set_display_value_option_index(ind)
        self.tv.update_new_traces()

    def set_temporal_filter_index(self, **kwargs):
        tf_name = kwargs['values']
        tf_index = self.data.core.get_temporal_filter_options().index(tf_name)
        self.data.core.set_temporal_filter_index(tf_index)
        self.tv.update_new_traces()
        self.data.full_data_processor.update_full_processed_data()

    def set_t_filter_radius(self, **kwargs):
        v = int(kwargs['values'])
        self.data.core.set_temporal_filter_radius(v)
        self.tv.update_new_traces()
        self.data.full_data_processor.update_full_processed_data()

    def set_s_filter_sigma(self, **kwargs):
        v = float(kwargs['values'])
        self.data.core.set_spatial_filter_sigma(v)
        self.fv.update_new_image()
        self.data.full_data_processor.update_full_processed_data()

    def set_is_t_filter_enabled(self, **kwargs):
        v = bool(kwargs['values'])
        self.data.core.set_is_temporal_filter_enabled(v)
        self.tv.update_new_traces()
        self.data.full_data_processor.update_full_processed_data()
        if self.data.core.get_is_temporal_filter_enabled():
            filter_type = self.data.core.get_temporal_filter_options()[
                self.data.core.get_temporal_filter_index()]
            sigma_t = self.data.core.get_temporal_filter_radius()
            if not self.data.validate_filter_size(filter_type, sigma_t):
                self.notify_window("Invalid Settings",
                                   "Measure window is too small for the"
                                   " default cropping needed for the temporal filter"
                                   " settings. \nUntil measure window is widened or "
                                   " filtering radius is decreased, temporal filtering will"
                                   " not be applied to traces.")

    def set_is_s_filter_enabled(self, **kwargs):
        v = bool(kwargs['values'])
        self.data.core.set_is_spatial_filter_enabled(v)
        self.fv.update_new_image()
        self.data.full_data_processor.update_full_processed_data()

    def set_baseline_correction(self, **kwargs):
        v = kwargs['values']
        v = self.data.core.get_baseline_correction_options().index(v)
        self.data.core.set_baseline_correction_type_index(v)
        self.tv.update_new_traces()
        self.fv.update_new_image()
        self.data.full_data_processor.update_full_processed_data()

    def set_rli_division(self, **kwargs):
        v = bool(kwargs['values'])
        self.data.set_is_rli_division_enabled(v)
        self.tv.update_new_traces()
        self.fv.update_new_image()
        self.data.full_data_processor.update_full_processed_data()

    def set_data_inverse(self, **kwargs):
        v = bool(kwargs['values'])
        self.data.set_is_data_inverse_enabled(v)
        self.tv.update_new_traces()
        self.fv.update_new_image()
        self.data.full_data_processor.update_full_processed_data()

    def export_data(self, **kwargs):
        kind = kwargs['kind']
        form = kwargs['form']
        file = None
        if form == 'tsv':
            file = self.browse_for_save_as_file()
            if file is None or len(file) < 1:
                return
            if kind == 'traces':
                self.exporter.export_traces_to_tsv(file)
            elif kind == 'frame':
                self.exporter.export_frame_to_tsv(file)
            elif kind == 'regions':
                self.exporter.export_regions_to_tsv(file)
        elif form == 'png':
            file = self.browse_for_save_as_file(file_types=(("Portable Network Graphics file", "*.png"),))
            if file is None or len(file) < 1:
                return
            if kind == 'traces':
                self.exporter.export_traces_to_png(file)
            elif kind == 'frame':
                self.exporter.export_frame_to_png(file)
        self.notify_window("Export successful",
                           "Exported " + kind + " to file:\n"
                           + file)

    def export_all_data(self, **kwargs):
        folder = self.browse_for_folder(recording_notif=False)
        if folder is None:
            return

        file_prefix = folder + "\\" + self.data.db.get_current_filename(no_path=True, extension='')
        self.exporter.export_traces_to_tsv(file_prefix + '_traces.tsv')
        self.exporter.export_frame_to_tsv(file_prefix + '_frame.tsv')
        self.exporter.export_traces_to_png(file_prefix + '_traces.png')
        self.exporter.export_frame_to_png(file_prefix + '_frame.png')
        self.exporter.export_regions_to_tsv(file_prefix + '_regions.tsv')
        self.notify_window("Export successful",
                           "Exported to .png/.tsv files with prefix:\n"
                           + file_prefix + '_*')

    def import_regions_from_tsv(self, **kwargs):
        files = self.browse_for_file(['tsv'], multi_file=True, tsv_only=True)
        if files is None:
            return
        files = files.split(';')
        for f in files:
            self.exporter.import_regions_from_tsv(f)

    def set_contrast_scaling(self, **kwargs):
        v = kwargs['values']
        self.data.set_contrast_scaling(v)
        self.fv.update_new_image()
