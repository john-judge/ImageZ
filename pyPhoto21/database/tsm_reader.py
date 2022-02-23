import os
import struct
import numpy as np

from pyPhoto21.database.file import File
from pyPhoto21.database.metadata import Metadata


# RedshirtImaging website says it works with ImageJ, which supports:
#   https://imagej.nih.gov/ij/docs/guide/146-7.html#sub:Native-Formats
class TSM_Reader(File):

    def __init__(self):
        super().__init__(Metadata())

    # def load_tsm(self, filename, db, meta):
    #     raw_data, metadata_dict, rli, fp_data = self.read_tsm_to_variables(filename)
    #     self.populate_meta(meta, metadata_dict)
    #     db.meta = meta
    #     self.create_npy_file(db, raw_data, rli, fp_data)

    # side-effect is to create .npy file and populate meta object
    def load_tsm(self, filename, db):
        print(filename, "to be treated as TSM file to open")

        width = self.meta.width
        height = self.meta.height
        num_pts = self.meta.num_pts

        file = open(filename, 'rb')
        header = str(file.read(2880))

        # header parsing
        header = [x.strip() for x in header.split(" ") if x != "=" and len(x) > 0]
        for i in range(len(header)):
            if header[i] == "NAXIS1":
                width = int(header[i+1])
            if header[i] == "NAXIS2":
                height = int(header[i+1])
            if header[i] == "NAXIS3":
                num_pts = int(header[i+1])

        print("Reading file as", num_pts, "images of size", width, "x", height)

        images = np.zeros((num_pts, height, width), dtype=np.int16)

        for k in range(num_pts):
            for i in range(height):
                for j in range(width):
                    images[k, i, j] = int.from_bytes(file.read(2), byteorder='little')

        dark_frame = np.zeros((height, width), dtype=np.int16)

        for i in range(height):
            for j in range(width):
                dark_frame[i, j] = int.from_bytes(file.read(2), byteorder='little')
        file.close()

        # set metadata in preparation for file creation
        self.meta.num_pts, self.meta.height, self.meta.width = num_pts, height, width
        self.meta.num_trials = 1

        # create npy file from image data
        db.clear_or_resize_mmap_file()  # loads correct dimensions since we already set meta
        arr = db.load_data_raw()
        arr[0, :, :, :] = images[:, :, :]  # only 1 trial per FITS file
        print(arr.shape)
        tbn_filename = filename.split(".tsm")[0] + ".tbn"
        self.load_tbn(tbn_filename, db, num_pts)

    # read NI data from .tbn file
    def load_tbn(self, filename, db, num_pts, trial=0):

        if db.file_exists_in_own_path(filename):
            print("Found file to load FP data from:", filename)
        else:
            print("Could not find a matching .tbn file:", filename)
            return

        file = open(filename, 'rb')

        num_channels = int.from_bytes(file.read(2), byteorder='little', signed=True)
        if num_channels < 0:
            print("TBN file designates origin as NI for this data.")
            num_channels *= -1
        BNC_ratio = int.from_bytes(file.read(2), byteorder='little')
        num_channels = min(self.meta.num_fp, num_channels)
        num_fp_pts = BNC_ratio * num_pts
        print("Found", num_channels, "channels in BNC ratio:", BNC_ratio)

        fp_arr = np.fromfile(file, dtype=np.float64, count=num_channels * num_fp_pts).reshape(num_channels, num_fp_pts)
        fp_arr_dst = db.load_trial_fp_data(trial)
        fp_arr_dst[:, :] = np.transpose(fp_arr)[:, :]

        file.close()

    def populate_meta(self, meta, metadata_dict):
        pass

    def create_npy_file(self, db, raw_data, rli, fp_data):
        pass

