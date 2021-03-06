class EventMapping:

    def __init__(self, gui):
        self.event_mapping = {
            'Save': {
                'function': gui.data.save_metadata_to_json,
                'args': {}
            },
            'Launch Hyperslicer': {
                'function': gui.launch_hyperslicer,
                'args': {},
            },
            "Select Background": {
                'function': gui.set_background_option_index,
                'args': {},
            },
            "Show RLI": {
                'function': gui.toggle_show_rli,
                'args': {},
            },
            "Open": {
                'function': gui.load_data_file,
                'args': {},
            },
            '-github-': {
                'function': gui.launch_github_page,
                'args': {'kind': "technical"},
            },
            'Help': {
                'function': gui.launch_github_page,
                'args': {'kind': "user"},
            },
            '-psg-': {
                'function': gui.launch_github_page,
                'args': {'kind': "issue"},
            },
            '-timer-': {
                'function': gui.launch_little_dave_calendar,
                'args': {'kind': "issue"},
            },
            'Digital Binning': {
                'function': gui.set_digital_binning,
                'args': {},
            },
            'Choose Load Directory': {
                'function': gui.choose_load_dir,
                'args': {},
            },
            'Save As': {
                'function': gui.save_as_current_file,
                'args': {}
            },
            "Load Directory File List": {
                'function': gui.autoload_file,
                'args': {},
            },
            "ROI Identifier Config": {
                'function': gui.launch_roi_settings,
                'args': {},
            },
            "Identify ROI": {
                'function': gui.enable_roi_identification,
                'args': {}
            },
            'Pixel-wise SNR cutoff Raw': {
                'function': gui.set_cutoff,
                'args': {'form': 'raw',
                         'kind': 'pixel'}
            },
            'Pixel-wise SNR cutoff Percentile': {
                'function': gui.set_cutoff,
                'args': {'form': 'percentile',
                         'kind': 'pixel'}
            },
            'Cluster-wise SNR cutoff Raw': {
                'function': gui.set_cutoff,
                'args': {'form': 'raw',
                         'kind': 'cluster'}
            },
            'Cluster-wise SNR cutoff Percentile': {
                'function': gui.set_cutoff,
                'args': {'form': 'percentile',
                         'kind': 'cluster'}
            },
            'ROI-wise SNR cutoff Raw': {
                'function': gui.set_cutoff,
                'args': {'form': 'raw',
                         'kind': 'roi_snr'}
            },
            'ROI-wise SNR cutoff Percentile': {
                'function': gui.set_cutoff,
                'args': {'form': 'percentile',
                         'kind': 'roi_snr'}
            },
            'ROI-wise Amplitude cutoff Raw': {
                'function': gui.set_cutoff,
                'args': {'form': 'raw',
                         'kind': 'roi_amplitude'}
            },
            'ROI-wise Amplitude cutoff Percentile': {
                'function': gui.set_cutoff,
                'args': {'form': 'percentile',
                         'kind': 'roi_amplitude'}
            },
            "Time Window Start frames pre_stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 0,
                         'kind': 'pre_stim',
                         'form': 'frames'}
            },
            "Time Window Start (ms) pre_stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 0,
                         'kind': 'pre_stim',
                         'form': 'ms'}
            },
            "Time Window End frames pre_stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 1,
                         'kind': 'pre_stim',
                         'form': 'frames'}
            },
            "Time Window End (ms) pre_stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 1,
                         'kind': 'pre_stim',
                         'form': 'ms'}
            },
            "Time Window Start frames stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 0,
                         'kind': 'stim',
                         'form': 'frames'}
            },
            "Time Window Start (ms) stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 0,
                         'kind': 'stim',
                         'form': 'ms'}
            },
            "Time Window End frames stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 1,
                         'kind': 'stim',
                         'form': 'frames'}
            },
            "Time Window End (ms) stim": {
                'function': gui.set_roi_time_window,
                'args': {'index': 1,
                         'kind': 'stim',
                         'form': 'ms'}
            },
            "roi.k_clusters": {
                'function': gui.set_roi_k_clusters,
                'args': {}
            },
            "View Silhouette Plot": {
                'function': gui.view_roi_plot,
                'args': {'type': 'silhouette'}
            },
            "View Elbow Plot": {
                'function': gui.view_roi_plot,
                'args': {'type': 'elbow'}
            },
            "Load ROI Data from File": {
                'function': gui.load_roi_file,
                'args': {'type': 'elbow'}
            },
            "Save ROI Data to File": {
                'function': gui.save_roi_file,
                'args': {'type': 'elbow'}
            },
            "Increment Trial": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.data.increment_current_trial_index,
                         'call2': gui.update_tracking_num_fields}
            },
            "Decrement Trial": {
                'function': gui.pass_no_arg_calls,
                'args': {'call': gui.data.decrement_current_trial_index,
                         'call2': gui.update_tracking_num_fields}
            },
            "Trial Number": {
                'function': gui.validate_and_pass_int,
                'args': {'call': gui.set_current_trial_index,
                         'call2': gui.update_tracking_num_fields}
            },
            "Temporal Filter Radius": {
                'function': gui.set_t_filter_radius,
                'args': {}
            },
            "Spatial Filter Sigma": {
                'function': gui.set_s_filter_sigma,
                'args': {}
            },
            "Select Temporal Filter": {
                'function': gui.set_temporal_filter_index,
                'args': {},
            },
            'T-Filter': {
                'function': gui.set_is_t_filter_enabled,
                'args': {}
            },
            'S-Filter': {
                'function': gui.set_is_s_filter_enabled,
                'args': {}
            },
            "Select Baseline Correction": {
                'function': gui.set_baseline_correction,
                'args': {}
            },
            'RLI Division': {
                'function': gui.set_rli_division,
                'args': {}
            },
            'Data Inverse': {
                'function': gui.set_data_inverse,
                'args': {}
            },
            "Select Display Value": {
                'function': gui.set_display_value_option_index,
                'args': {},
            },
            "Baseline Skip Window": {
                'function': gui.select_baseline_skip_window,
                'args': {}
            },
            "Baseline Skip Window Start (ms)": {
                'function': gui.set_baseline_skip_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'ms'}
            },
            "Baseline Skip Window End (ms)": {
                'function': gui.set_baseline_skip_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'ms'}
            },
            "Baseline Skip Window Start frames": {
                'function': gui.set_baseline_skip_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'frames'}
            },
            "Baseline Skip Window End frames": {
                'function': gui.set_baseline_skip_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'frames'}
            },
            "Save Preference": {
                'function': gui.save_preference,
                'args': {}
            },
            "Load Preference": {
                'function': gui.load_preference,
                'args': {}
            },
            'Average Trials': {
                'function': gui.toggle_average_trials,
                'args': {}
            },
            "About": {
                'function': gui.introduction,
                'args': {}
            },
            'Selected Frame to TSV': {
                'function': gui.export_data,
                'args': {'kind': 'frame', 'form': 'tsv'}
            },
            'Selected Regions to TSV': {
                'function': gui.export_data,
                'args': {'kind': 'regions', 'form': 'tsv'}
            },
            'Selected Traces to TSV': {
                'function': gui.export_data,
                'args': {'kind': 'traces', 'form': 'tsv'}
            },
            'Selected Frame to PNG': {
                'function': gui.export_data,
                'args': {'kind': 'frame', 'form': 'png'}
            },
            'Selected Traces to PNG': {
                'function': gui.export_data,
                'args': {'kind': 'traces', 'form': 'png'}
            },
            'Save Analysis': {
                'function': gui.export_all_data,
                'args': {}
            },
            'Export all of the above': {
                'function': gui.export_all_data,
                'args': {}
            },
            'Import Regions from TSV(s)': {
                'function': gui.import_regions_from_tsv,
                'args': {}
            },
            "Measure Window Start frames": {
                'function': gui.set_measure_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'frames'}
            },
            "Measure Window End frames": {
                'function': gui.set_measure_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'frames'}
            },
            "Measure Window Start (ms)": {
                'function': gui.set_measure_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'ms'}
            },
            "Measure Window End (ms)": {
                'function': gui.set_measure_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'ms'}
            },
            "Notepad": {
                'function': gui.data.set_notepad_text,
                'args': {}
            },
            "Select Colormap": {
                'function': gui.fv.set_color_map_option_name,
                'args': {}
            },
            "Camera Artifact Exclusion Window Start frames": {
                'function': gui.set_artifact_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'frames'}
            },
            "Camera Artifact Exclusion Window End frames": {
                'function': gui.set_artifact_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'frames'}
            },
            "Camera Artifact Exclusion Window Start (ms)": {
                'function': gui.set_artifact_window,
                'args': {'index': 0,
                         'kind': None,
                         'form': 'ms'}
            },
            "Camera Artifact Exclusion Window End (ms)": {
                'function': gui.set_artifact_window,
                'args': {'index': 1,
                         'kind': None,
                         'form': 'ms'}
            },
            "Contrast Scaling": {
                'function': gui.set_contrast_scaling,
                'args': {}
            },
            "Time Course File Selector": {
                'function': gui.tcv.update_file_list,
                'args': {}
            },
            "Frame X-Cropping Window Start": {
                'function': gui.set_frame_crop_window,
                'args': {'index': 0,
                         'kind': 'x'}
            },
            "Frame X-Cropping Window End": {
                'function': gui.set_frame_crop_window,
                'args': {'index': 1,
                         'kind': 'x'}
            },
            "Frame Y-Cropping Window Start": {
                'function': gui.set_frame_crop_window,
                'args': {'index': 0,
                         'kind': 'y'}
            },
            "Frame Y-Cropping Window End": {
                'function': gui.set_frame_crop_window,
                'args': {'index': 1,
                         'kind': 'y'}
            }

        }

    def get_event_mapping(self):
        return self.event_mapping
