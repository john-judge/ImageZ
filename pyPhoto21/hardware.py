import ctypes
import os
import numpy as np

# https://medium.com/@stephenscotttucker/interfacing-python-with-c-using-ctypes-classes-and-arrays-42534d562ce7


class Hardware:
    
    def __init__(self, dll_path='./x64/Release/'):
        self.lib = None
        self.load_dll(dll_path=dll_path)
        self.define_c_types()
        self.controller = self.lib.createController()

    def __del__(self):
        try:
            self.lib.destroyController(self.controller)
        except AttributeError:
            pass

    def record(self, **kwargs):
        imgs_orig_shape = kwargs['images'].shape
        fp_orig_shape = kwargs['fp_data'].shape
        imgs = kwargs['images'].reshape(-1)
        fp_data = kwargs['fp_data'].reshape(-1)
        try:
            self.lib.acqui(self.controller, imgs, fp_data)
        except Exception as e:
            print("Could not record. Are the camera and NI-USB connected?")
            print(e)
        imgs = imgs.reshape(imgs_orig_shape)
        fp_data = fp_data.reshape(fp_orig_shape)

    def take_rli(self, **kwargs):
        orig_shape = kwargs['images'].shape
        imgs = kwargs['images'].reshape(-1)
        try:
            self.lib.takeRli(self.controller, imgs)
        except Exception as e:
            print("Could not take RLI. Are the camera and NI-USB connected?")
            print(e)
        imgs = imgs.reshape(orig_shape)

    # choose programs 0-7 (inclusive)
    def set_camera_program(self, **kwargs):
        if 'program' not in kwargs:
            return
        p = kwargs['program']
        if type(p) != int or p < 0 or p > 7:
            return
        print('setting hardware to camera program', kwargs['program'])
        self.lib.setCameraProgram(self.controller, kwargs['program'])

    def get_camera_program(self):
        return self.lib.getCameraProgram(self.controller)

    # set the number of points acquired during recording
    def set_num_pts(self, **kwargs):
        self.lib.setNumPts(self.controller, kwargs['num_pts'])

    def get_num_pts(self):
        return self.lib.getNumPts(self.controller)

    # set the interval between points acquired during recording
    def set_int_pts(self, **kwargs):
        self.lib.setIntPts(self.controller, kwargs['interval'])

    def get_int_pts(self):
        return self.lib.getIntPts(self.controller)

    # set the number of pulses during acquisition
    def set_num_pulses(self, **kwargs):
        self.lib.setNumPulses(self.controller, kwargs['num_pulses'], kwargs['channel'])

    def get_num_pulses(self, **kwargs):
        return self.lib.getNumPulses(self.controller, kwargs['channel'])

    # set the interval between pulses during acquisition
    def set_int_pulses(self, **kwargs):
        self.lib.setIntPulses(self.controller, kwargs['interval_pulses'], kwargs['channel'])

    def get_int_pulses(self, **kwargs):
        return self.lib.getIntPulses(self.controller, kwargs['channel'])

    # set the number of bursts during acquisition
    def set_num_bursts(self, **kwargs):
        self.lib.setNumBursts(self.controller, kwargs['num_bursts'], kwargs['channel'])

    def get_num_bursts(self, **kwargs):
        return self.lib.getNumBursts(self.controller, kwargs['channel'])

    # set the interval between bursts during acquisition
    def set_int_bursts(self, **kwargs):
        self.lib.setIntBursts(self.controller, kwargs['interval_bursts'], kwargs['channel'])

    def get_int_bursts(self, **kwargs):
        return self.lib.getIntBursts(self.controller, kwargs['channel'])

    def set_schedule_rli_flag(self, **kwargs):
        self.lib.setScheduleRliFlag(self.controller, kwargs['schedule_rli_flag'])

    # get total acquisition OR stimulation duration, whichever is longer
    def get_duration(self):
        return self.lib.getDuration(self.controller)

    # set acqui onset
    def set_acqui_onset(self, **kwargs):
        self.lib.setAcquiOnset(self.controller, kwargs['acqui_onset'])

    def get_acqui_onset(self):
        return self.lib.getAcquiOnset(self.controller)

    def ni_error_dump(self):
        self.lib.NiErrorDump(self.controller)

    #  get total acquisition duration
    def get_acqui_duration(self):
        return self.lib.getAcquiDuration(self.controller)

    # set num dark RLI frames
    def set_num_dark_rli(self, **kwargs):
        self.lib.setNumDarkRLI(self.controller, kwargs['dark_rli'])

    def get_num_dark_rli(self):
        return self.lib.getNumDarkRLI(self.controller)

    # set num light RLI frames
    def set_num_light_rli(self, **kwargs):
        self.lib.setNumLightRLI(self.controller, kwargs['light_rli'])

    def get_num_light_rli(self):
        return self.lib.getNumLightRLI(self.controller)

    def get_display_width(self):
        return self.lib.getDisplayWidth(self.controller)

    def get_display_height(self):
        return self.lib.getDisplayHeight(self.controller)

    def define_c_types(self):
        controller_handle = ctypes.POINTER(ctypes.c_char)
        c_uint_array = np.ctypeslib.ndpointer(dtype=np.uint16, ndim=1, flags='C_CONTIGUOUS')
        c_float_array = np.ctypeslib.ndpointer(dtype=np.float64, ndim=1, flags='C_CONTIGUOUS')

        self.lib.createController.argtypes = []  # argument types
        self.lib.createController.restype = controller_handle  # return type
        
        self.lib.destroyController.argtypes = [controller_handle]
        
        self.lib.takeRli.argtypes = [controller_handle, c_uint_array]
        
        self.lib.acqui.argtypes = [controller_handle, c_uint_array, c_float_array]
        
        self.lib.setCameraProgram.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getCameraProgram.argtypes = [controller_handle]
        self.lib.getCameraProgram.restype = ctypes.c_int
        
        self.lib.setNumPts.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getNumPts.argtypes = [controller_handle]
        self.lib.getNumPts.restype = ctypes.c_int
        
        self.lib.setIntPts.argtypes = [controller_handle, ctypes.c_double]
        
        self.lib.getIntPts.argtypes = [controller_handle]
        self.lib.getIntPts.restype = ctypes.c_float
        
        self.lib.setNumPulses.argtypes = [controller_handle, ctypes.c_int, ctypes.c_int]
        
        self.lib.getNumPulses.argtypes = [controller_handle, ctypes.c_int]
        self.lib.getNumPulses.restype = ctypes.c_int
        
        self.lib.setIntPulses.argtypes = [controller_handle, ctypes.c_int, ctypes.c_int]
        
        self.lib.getIntPulses.argtypes = [controller_handle, ctypes.c_int]
        self.lib.getIntPulses.restype = ctypes.c_int
        
        self.lib.setNumBursts.argtypes = [controller_handle, ctypes.c_int, ctypes.c_int]
        
        self.lib.getNumBursts.argtypes = [controller_handle, ctypes.c_int]
        self.lib.getNumBursts.restype = ctypes.c_int
        
        self.lib.setIntBursts.argtypes = [controller_handle, ctypes.c_int, ctypes.c_int]
        
        self.lib.getIntBursts.argtypes = [controller_handle, ctypes.c_int]
        self.lib.getIntBursts.restype = ctypes.c_int
        
        self.lib.setScheduleRliFlag.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getScheduleRliFlag.argtypes = [controller_handle]
        self.lib.getScheduleRliFlag.restype = ctypes.c_int

        self.lib.getDuration.argtypes = [controller_handle]
        self.lib.getDuration.restype = ctypes.c_int
        
        self.lib.setAcquiOnset.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getAcquiOnset.argtypes = [controller_handle]
        self.lib.getAcquiOnset.restype = ctypes.c_int
        
        self.lib.getAcquiDuration.argtypes = [controller_handle]
        self.lib.getAcquiDuration.restype = ctypes.c_float
        
        self.lib.NiErrorDump.argtypes = [controller_handle]
        
        self.lib.setNumDarkRLI.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getNumDarkRLI.argtypes = [controller_handle]
        self.lib.getNumDarkRLI.restype = ctypes.c_int
        
        self.lib.setNumLightRLI.argtypes = [controller_handle, ctypes.c_int]
        
        self.lib.getNumLightRLI.argtypes = [controller_handle]
        self.lib.getNumLightRLI.restype = ctypes.c_int

        self.lib.getDisplayWidth.restype = ctypes.c_int
        self.lib.getDisplayHeight.restype = ctypes.c_int


    def load_dll(self, dll_path='./x64/Release/', verbose=False):
        dll_path = os.path.abspath(dll_path)
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(os.getcwd())
            os.add_dll_directory(os.path.dirname(dll_path + os.path.sep + "PhotoLib.dll"))
            os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib/Include/EDT')))
            os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib/Include')))
            os.add_dll_directory(os.path.dirname(os.path.abspath('./PhotoLib')))
            env_paths = os.environ['PATH'].split(';')
            for path in env_paths:
                try:
                    os.add_dll_directory(path)
                    if verbose:
                        print('added DLL dependency path:', path)
                except:
                    if verbose:
                        print('Failed to add DLL dependency path:', path)
            self.lib = ctypes.cdll.LoadLibrary(dll_path + os.path.sep  + 'PhotoLib.dll')
            #self.lib = ctypes.CDLL(dll_path + os.path.sep + "PhotoLib.dll")
        else:
            os.environ['PATH'] = os.path.dirname(dll_path + os.path.sep + "PhotoLib.dll") + ';'\
                                 + os.path.dirname(os.path.abspath('./PhotoLib/Include/EDT')) + ';' \
                                 + os.path.dirname(os.path.abspath('./PhotoLib/Include')) + ';' \
                                 + os.path.dirname(os.path.abspath('./PhotoLib')) + ';' \
                                 + os.environ['PATH']
            self.lib = ctypes.cdll.LoadLibrary(dll_path + 'PhotoLib.dll')

