# preproc.py

#### Debug mne_filter epochs after PARAFAC which might not work
from typing import List, Optional, Callable, Dict, Union, Tuple, Any, TypeVar
import warnings
import os
import numpy as np
import matplotlib.pyplot as plt
import threading
import queue
from scipy import stats, signal
from scipy.interpolate import interp1d
from scipy.stats import zscore
from scipy.spatial.distance import pdist, squareform
from scipy import optimize

# MNE imports
import mne
from mne.preprocessing import compute_proj_ecg, compute_proj_eog, compute_current_source_density, ICA
from mne import (compute_raw_covariance,
                read_source_spaces,
                setup_source_space,
                make_bem_model,
                make_bem_solution,
                make_forward_solution,
                read_trans,
                read_bem_solution)
from mne.io.constants import FIFF

# I currently disabled ica_label functionality since it is not used but the references to it are only commented out
from mne.preprocessing import ICA

# Required for FASTER bad channel/epoch detection 
from mne_faster import find_bad_channels, find_bad_epochs, find_bad_channels_in_epochs

# Required for artifact cleaning (if using TMSArtifactCleaner)
from sklearn.preprocessing import StandardScaler
import tensorly as tl
from tensorly.decomposition import parafac, non_negative_parafac, tucker
from tqdm import tqdm


## Custom TMS-artefact removal using PARAFAC decomposition
from .clean import TMSArtifactCleaner


def detect_tms_artifacts(raw, threshold_std=10, min_distance_ms=50, existing_events=None):
    """
    Automatically detect TMS artifacts based on amplitude threshold, considering existing events.

    Parameters
    ----------
    threshold_std : float
        Number of standard deviations above mean for detection
    min_distance_ms : float
        Minimum distance between artifacts in milliseconds
    existing_events : array | None
        Existing event samples to avoid duplicate detection

    Returns
    -------
    additional_events : array
        Array of additional events in MNE format (N x 3)
    """
    if raw is None:
        raise ValueError("Must have raw data to detect artifacts")

    data = raw.get_data()
    sfreq = raw.info['sfreq']
    min_distance_samples = int(min_distance_ms * sfreq / 1000)

    print(
        f"Running automatic artifact detection for {min_distance_samples} ms samples with standard deviation {threshold_std}")

    # Calculate statistics across all channels
    data_flat = data.reshape(-1)
    mean = np.mean(data_flat)
    std = np.std(data_flat)
    threshold = mean + threshold_std * std
    print(f"mean: {mean}, std: {std} for data")

    # Find peaks above threshold
    peaks = []
    for ch in range(data.shape[0]):
        channel_peaks = np.where(np.abs(data[ch, :]) > threshold)[0]
        peaks.extend(channel_peaks.tolist())

    if not peaks:
        print("No peaks detected above threshold")
        return None

    peaks = np.unique(np.array(peaks))

    # If we have existing events, prepare exclusion zones
    excluded_zones = []
    if existing_events is not None and len(existing_events) > 0:
        for event_sample in existing_events[:, 0]:
            excluded_zones.append((event_sample - min_distance_samples,
                                   event_sample + min_distance_samples))

    # Group nearby peaks and enforce minimum distance
    artifact_samples = []
    last_peak = -min_distance_samples

    for peak in sorted(peaks):
        # Check if peak is in any exclusion zone
        should_exclude = False
        for start, end in excluded_zones:
            if start <= peak <= end:
                should_exclude = True
                break

        if should_exclude:
            continue

        if peak - last_peak >= min_distance_samples:
            artifact_samples.append(peak)
            last_peak = peak

    if len(artifact_samples) > 0:
        print(f"Detected {len(artifact_samples)} additional TMS artifacts")

        # Create new events array for the additional artifacts
        additional_events = np.zeros((len(artifact_samples), 3), dtype=int)
        additional_events[:, 0] = artifact_samples  # Sample numbers
        additional_events[:, 1] = 0  # Middle column should be 0
        additional_events[:, 2] = 1  # Event ID/value

        # Sort by time
        additional_events = additional_events[additional_events[:, 0].argsort()]

        return additional_events
    else:
        print("No additional artifacts detected")
        return None


class TMSEEGPreprocessor:
    """
    A class for preprocessing TMS-EEG data.
    
    This class implements a preprocessing pipeline for TMS-EEG data,
    including artifact removal, filtering, and data quality checks.
    
    Parameters
    ----------
    raw : mne.io.Raw
        The raw TMS-EEG data
    montage : str or mne.channels.montage.DigMontage, optional
        The EEG montage to use (default is 'standard_1020')
    ds_sfreq : float, optional
        The desired sampling frequency for resampling (default is 1000 Hz)
        
    Attributes
    ----------
    raw : mne.io.Raw
        The raw TMS-EEG data
    epochs : mne.Epochs
        The epoched TMS-EEG data
    montage : mne.channels.montage.DigMontage
        The EEG montage
    """

    ### currently using easycap-M10 as the standard montage
    ### used standard_1020 before and not sure if it makes a huge difference

    def __init__(self,
                 raw: mne.io.Raw,
                 montage: Union[str, mne.channels.montage.DigMontage] = 'easycap-M1',
                 final_sfreq: float = 725):

        self.raw = raw.copy()
        self.epochs = None
        self.evoked = None
        self.final_sfreq = final_sfreq

        self.first_ica_manual = False
        self.second_ica_manual = False
        self.selected_first_ica_components = []
        self.selected_second_ica_components = []
        self.ica = None
        self.ica2 = None

        self.processing_stage = {
            'initial_removal': False,
            'first_interpolation': False,
            'artifact_cleaning': False,
            'extended_removal': False,
            'final_interpolation': False
        }
        
        # Remove unused EMG channels if present
        for ch in self.raw.info['ch_names']:
            if ch.startswith('EMG'):
                self.raw.drop_channels(ch)
            elif ch.startswith('31'):
                self.raw.drop_channels(ch)
            elif ch.startswith('32'):
                self.raw.drop_channels(ch)
        
        # Channel name standardization
        ch_names = self.raw.ch_names
        rename_dict = {}
        for ch in ch_names:
            # Common naming variations
            if ch in ['31', '32']:
                continue  # Skip non-EEG channels
            if ch.upper() == 'FP1':
                rename_dict[ch] = 'Fp1'
            elif ch.upper() == 'FP2':
                rename_dict[ch] = 'Fp2'
            elif ch.upper() in ['FPZ', 'FPOZ']:
                rename_dict[ch] = 'Fpz'
            elif ch.upper() == 'POZ':
                rename_dict[ch] = 'POz'
            elif ch.upper() == 'PZ':
                rename_dict[ch] = 'Pz'
            elif ch.upper() == 'FCZ':
                rename_dict[ch] = 'FCz'
            elif ch.upper() == 'CPZ':
                rename_dict[ch] = 'CPz'
            elif ch.upper() == 'FZ':
                rename_dict[ch] = 'Fz'
            elif ch.upper() == 'CZ':
                rename_dict[ch] = 'Cz'
            elif ch.upper() == 'OZ':
                rename_dict[ch] = 'Oz'
        
        if rename_dict:
            print("Renaming channels to match standard nomenclature:")
            for old, new in rename_dict.items():
                print(f"  {old} -> {new}")
            self.raw.rename_channels(rename_dict)
        
        '''        # Set montage with error handling
        if isinstance(montage, str):
            try:
                self.montage = mne.channels.make_standard_montage(montage)
                print(f"Using montage: {montage} which seemed to work?")
            except ValueError as e:
                print(f"Warning: Could not create montage '{montage}': {str(e)}")
                print("Falling back to easycap-M10 montage")
                self.montage = mne.channels.make_standard_montage('standard_1020')
        else:
            self.montage = montage
        
        try:
            # First try to set montage normally
            self.raw.set_montage(self.montage)
        except ValueError as e:
            print(f"\nWarning: Could not set montage directly: {str(e)}")
            
            # Get the channel types
            ch_types = {ch: self.raw.get_channel_types(picks=ch)[0] for ch in self.raw.ch_names}
            
            # Identify non-EEG channels
            non_eeg = [ch for ch, type_ in ch_types.items() if type_ not in ['eeg', 'unknown']]
            if non_eeg:
                print(f"\nFound non-EEG channels: {non_eeg}")
                print("Setting their types explicitly...")
                for ch in non_eeg:
                    self.raw.set_channel_types({ch: 'misc'})
            
            # Try setting montage again with on_missing='warn'
            try:
                self.raw.set_montage(self.montage, on_missing='warn')
                print("\nMontage set successfully with warnings for missing channels")
            except Exception as e2:
                print(f"\nWarning: Could not set montage even with warnings: {str(e2)}")
                print("Continuing without montage. Some functionality may be limited.")'''
        
        self.events = None
        self.event_id = None

        # Initialize attributes that will be set later
        self.stc = None
        self.forward = None
        self.inverse_operator = None
        self.source_space = None
        self.bem_solution = None
        self.noise_cov = None

        self.preproc_stats = {
            'n_orig_events': 0,
            'n_final_events': 0,
            'bad_channels': [],
            'n_bad_epochs': 0,
            'muscle_components': [],
            'excluded_ica_components': [],
            'original_sfreq': 0,
            'interpolated_times': [],
        }








######################## TMS ARTIFACT AND EPOCHS ######################################

    def fix_tms_artifact(self,
                         window: Tuple[float, float] = (-0.002, 0.005),
                         smooth_window: Tuple[float, float] = (-0.002, 0.002),
                         span: int = 2,
                         events: Optional[np.ndarray] = None,
                         verbose: bool = True) -> None:
        """
        Remove TMS artifacts using reversed data and boundary smoothing.

        Parameters
        ----------
        window : tuple
            Start and end time of cut window in seconds (default: (-0.002, 0.005))
        smooth_window : tuple
            Start and end time of smoothing window in seconds (default: (-0.002, 0.002))
        span : int
            Number of samples to use for smoothing on each side (default: 2)
        events : array, optional
            Custom events array (n_events × 3). If None, tries to find events
        verbose : bool
            Whether to print progress information
        """
        if hasattr(self, 'epochs') and self.epochs is not None:
            raise NotImplementedError("TMS pulse removal not yet implemented for epoched data")

        raw_out = self.raw.copy()
        sfreq = raw_out.info['sfreq']

        # Convert windows to samples
        window = np.array([w * sfreq for w in window])
        window_len = int(window[1] - window[0])
        smooth_window = np.array([int(sw * sfreq) for sw in smooth_window])

        # Get events if not provided
        if events is None:
            try:
                events = mne.find_events(raw_out, stim_channel='STI 014')
                if verbose:
                    print(f"\nFound {len(events)} events from STI 014 channel")
            except Exception as e:
                try:
                    events, _ = mne.events_from_annotations(raw_out)
                    if verbose:
                        print(f"\nFound {len(events)} events from annotations")
                except Exception as e2:
                    raise ValueError("No events found or provided. Cannot remove artifacts.")

        if len(events) == 0:
            raise ValueError("No events to process. Cannot remove artifacts.")

        events_sample = events[:, 0]  # Get event sample points

        if verbose:
            print(f"Processing {len(events_sample)} event time points")
            print(f"Window in samples: {window[0]} to {window[1]}")

        # Define the removal function with added validation
        def tms_pulse_removal(y):
            for onset in events_sample:
                cut0 = int(onset + window[0])
                cut1 = int(onset + window[1])

                # Add validation to ensure window is valid
                if cut0 >= cut1:
                    if verbose:
                        print(f"Warning: Invalid window at onset {onset}: cut0={cut0}, cut1={cut1}")
                    continue

                # Calculate the actual window length
                actual_window_len = cut1 - cut0

                # Check if there's enough data before the event
                if cut0 - actual_window_len < 0:
                    if verbose:
                        print(f"Warning: Not enough data before event at {onset} to substitute")
                    continue

                # Substitute data with the reverse of previous data (to remove artifact)
                y[cut0:cut1] = y[cut0 - actual_window_len:cut1 - actual_window_len][::-1]

                # Smooth first "cut"
                smooth_start = int(cut0 + smooth_window[0])
                smooth_end = int(cut0 + smooth_window[1])
                if smooth_start < smooth_end and smooth_start >= 0 and smooth_end < len(y):
                    y[smooth_start:smooth_end] = np.array(
                        [np.mean(y[max(0, samp - span):min(len(y), samp + span + 1)])
                         for samp in range(smooth_start, smooth_end)]
                    )

                # Smooth second "cut"
                smooth_start = int(cut1 + smooth_window[0])
                smooth_end = int(cut1 + smooth_window[1])
                if smooth_start < smooth_end and smooth_start >= 0 and smooth_end < len(y):
                    y[smooth_start:smooth_end] = np.array(
                        [np.mean(y[max(0, samp - span):min(len(y), samp + span + 1)])
                         for samp in range(smooth_start, smooth_end)]
                    )

            return y

        # Apply function to all channels
        raw_out.apply_function(tms_pulse_removal, picks='all', verbose=False)

        # Store info about the removal
        if not hasattr(self, 'tmscut'):
            self.tmscut = []

        self.tmscut.append({
            'window': window,
            'smooth_window': smooth_window,
            'sfreq': sfreq,
            'interpolated': 'no'
        })

        self.raw = raw_out

    def remove_tms_artifact(self,
                            cut_times_tms: Tuple[float, float] = (-2, 10),
                            replace_times: Optional[Tuple[float, float]] = None,
                            events: Optional[np.ndarray] = None,
                            event_id: Optional[Dict] = None,
                            verbose: bool = True) -> None:
        """
        Remove TMS artifacts from all marked events.

        Parameters
        ----------
        cut_times_tms : tuple
            Start and end time of cut window in milliseconds
        replace_times : tuple, optional
            Time window for baseline calculation if replacing with mean
        events : array, optional
            Custom events array (n_events × 3). If None, tries to find events
        event_id : dict, optional
            Dictionary mapping event names to event codes
        verbose : bool
            Whether to print progress information
        """
        # Check if we're working with epochs
        if hasattr(self, 'epochs') and self.epochs is not None:
            if verbose:
                print("\nRemoving TMS artifacts from epochs...")

            # Get data from epochs
            data = self.epochs.get_data()
            sfreq = self.epochs.info['sfreq']

            # Convert cut times from ms to samples
            cut_samples = np.round(np.array(cut_times_tms) * sfreq / 1000).astype(int)

            # Calculate sample points relative to epoch start
            start_sample = int(self.epochs.tmin * sfreq) + cut_samples[0]
            end_sample = int(self.epochs.tmin * sfreq) + cut_samples[1]

            # Ensure we're within epoch boundaries
            if start_sample < 0:
                print(f"Warning: Start time {cut_times_tms[0]}ms is before epoch start. Adjusting...")
                start_sample = 0
            if end_sample >= data.shape[2]:
                print(f"Warning: End time {cut_times_tms[1]}ms is after epoch end. Adjusting...")
                end_sample = data.shape[2] - 1

            # Remove artifact from each epoch
            for epoch_idx in range(data.shape[0]):
                if replace_times is None:
                    data[epoch_idx, :, start_sample:end_sample] = 0
                else:
                    # Handle replacement if specified
                    replace_samples = np.round(np.array(replace_times) * sfreq / 1000).astype(int)
                    baseline_start = int(self.epochs.tmin * sfreq) + replace_samples[0]
                    baseline_end = int(self.epochs.tmin * sfreq) + replace_samples[1]

                    if baseline_start >= 0 and baseline_end < data.shape[2]:
                        baseline_mean = np.mean(data[epoch_idx, :, baseline_start:baseline_end], axis=1)
                        data[epoch_idx, :, start_sample:end_sample] = baseline_mean[:, np.newaxis]

            # Update epochs data
            self.epochs._data = data

        else:
            raw_out = self.raw.copy()
            data = raw_out.get_data()
            sfreq = raw_out.info['sfreq']

            if not hasattr(self, 'tmscut'):
                self.tmscut = []

            tmscut_info = {
                'cut_times_tms': cut_times_tms,
                'replace_times': replace_times,
                'sfreq': sfreq,
                'interpolated': 'no'
            }

            cut_samples = np.round(np.array(cut_times_tms) * sfreq / 1000).astype(int)

            # Use provided events or try to find them
            if events is None:
                # First try to get events from stim channel
                if 'STI 014' in raw_out.ch_names:
                    try:
                        events = mne.find_events(raw_out, stim_channel='STI 014')
                        if verbose:
                            print(f"\nFound {len(events)} events from STI 014 channel")
                        # Create event_id from unique event codes if not provided
                        if event_id is None:
                            unique_events = np.unique(events[:, 2])
                            event_id = {str(code): code for code in unique_events}
                            if verbose:
                                print(f"Event IDs: {list(event_id.values())}")
                    except Exception as e:
                        if verbose:
                            print(f"Error finding events from STI 014: {str(e)}")

                # If no events found from stim channel, try annotations
                if events is None or len(events) == 0:
                    try:
                        events, event_id = mne.events_from_annotations(raw_out)
                        if verbose:
                            print(f"\nFound {len(events)} events from annotations")
                    except Exception as e:
                        if verbose:
                            print(f"Error finding events from annotations: {str(e)}")

            if events is None or len(events) == 0:
                raise ValueError("No events found or provided. Cannot remove artifacts.")

            # Store events and event_id for later use
            self._stored_events = events.copy()
            self._stored_event_id = event_id
            self.events = events.copy()
            self.event_id = event_id

            if verbose:
                print(f"\nFound {len(events)} events to process")
                print(f"Removing artifact in window {cut_times_tms} ms")

            processed_count = 0
            skipped_count = 0

            # Sort events by time to ensure consistent processing
            events = events[events[:, 0].argsort()]

            for event_idx in range(len(events)):
                event_sample = events[event_idx, 0]
                start = event_sample + cut_samples[0]
                end = event_sample + cut_samples[1]

                if start < 0 or end >= data.shape[1]:
                    skipped_count += 1
                    continue

                if replace_times is None:
                    data[:, start:end] = 0
                else:
                    replace_samples = np.round(np.array(replace_times) * sfreq / 1000).astype(int)
                    baseline_start = event_sample + replace_samples[0]
                    baseline_end = event_sample + replace_samples[1]
                    if baseline_start >= 0 and baseline_end < data.shape[1]:
                        baseline_mean = np.mean(data[:, baseline_start:baseline_end], axis=1)
                        data[:, start:end] = baseline_mean[:, np.newaxis]
                processed_count += 1

            if verbose:
                print(f"Successfully removed artifacts from {processed_count} events")
                if skipped_count > 0:
                    print(f"Skipped {skipped_count} events due to window constraints")

            raw_out._data = data
            self.raw = raw_out
            self.tmscut.append(tmscut_info)

    def interpolate_tms_artifact(self,
                                 method: str = 'cubic',
                                 interp_window: float = 1.0,
                                 cut_times_tms: Tuple[float, float] = (-2, 10),
                                 events: Optional[np.ndarray] = None,
                                 event_id: Optional[Dict] = None,
                                 verbose: bool = True) -> None:
        """
        Interpolate TMS artifacts for all marked events.

        Parameters
        ----------
        method : str
            Interpolation method ('cubic')
        interp_window : float
            Window size for interpolation in ms
        cut_times_tms : tuple
            Start and end time of cut window in milliseconds
        events : array, optional
            Custom events array (n_events × 3). If None, uses stored events
        event_id : dict, optional
            Dictionary mapping event names to event codes
        verbose : bool
            Whether to print progress information
        """
        if hasattr(self, 'epochs') and self.epochs is not None:
            data = self.epochs.get_data()
            sfreq = self.epochs.info['sfreq']

            # Get the last cut times from tmscut
            if not hasattr(self, 'tmscut') or not self.tmscut:
                raise ValueError("Must run remove_tms_artifact first")

            cut_times_tms = self.tmscut[-1]['cut_times_tms']

            # Convert to samples
            cut_samples = np.round(np.array(cut_times_tms) * sfreq / 1000).astype(int)
            interp_samples = int(round(interp_window * sfreq / 1000))

            # Calculate sample points relative to epoch start
            start_sample = int(self.epochs.tmin * sfreq) + cut_samples[0]
            end_sample = int(self.epochs.tmin * sfreq) + cut_samples[1]

            # Interpolate each epoch
            for epoch_idx in range(data.shape[0]):
                window_start = start_sample - interp_samples
                window_end = end_sample + interp_samples

                if window_start >= 0 and window_end < data.shape[2]:
                    x = np.arange(window_end - window_start + 1)
                    x_fit = np.concatenate([x[:interp_samples], x[-interp_samples:]])
                    x_fit = x_fit - x_fit[0]
                    x_interp = x[interp_samples:-interp_samples] - x_fit[0]

                    for ch in range(data.shape[1]):
                        y_full = data[epoch_idx, ch, window_start:window_end + 1]
                        y_fit = np.concatenate([y_full[:interp_samples], y_full[-interp_samples:]])

                        if method == 'cubic':
                            p = np.polyfit(x_fit, y_fit, 3)
                            data[epoch_idx, ch, start_sample:end_sample + 1] = np.polyval(p, x_interp)

            self.epochs._data = data

        else:
            if not hasattr(self, 'tmscut') or not self.tmscut:
                raise ValueError("Must run remove_tms_artifact first")

            if verbose:
                print(f"\nStarting interpolation with {method} method")
                print(f"Using interpolation window of {interp_window} ms")
                print(f"Processing cut window {cut_times_tms} ms")

            raw_out = self.raw.copy()
            data = raw_out.get_data()
            sfreq = raw_out.info['sfreq']

            # Use provided events, stored events, or try to find events
            if events is not None:
                current_events = events
                if verbose:
                    print(f"\nUsing {len(current_events)} provided events")
            elif hasattr(self, '_stored_events') and self._stored_events is not None:
                current_events = self._stored_events
                if verbose:
                    print(f"\nUsing {len(current_events)} stored events from previous artifact removal")
            else:
                raise ValueError("No events found. Must provide events or run remove_tms_artifact first")

            cut_samples = np.round(np.array(cut_times_tms) * sfreq / 1000).astype(int)
            interp_samples = int(round(interp_window * sfreq / 1000))

            interpolated_count = 0
            warning_count = 0

            for event_idx in range(len(current_events)):
                event_sample = current_events[event_idx, 0]
                start = event_sample + cut_samples[0]
                end = event_sample + cut_samples[1]

                # Calculate fitting windows
                window_start = start - interp_samples
                window_end = end + interp_samples

                if window_start < 0 or window_end >= data.shape[1]:
                    warning_count += 1
                    continue

                # Get time points for fitting
                x = np.arange(window_end - window_start + 1)
                x_fit = np.concatenate([
                    x[:interp_samples],
                    x[-interp_samples:]
                ])

                # Center x values at 0
                x_fit = x_fit - x_fit[0]
                if len(x) <= 2 * interp_samples:
                    if verbose:
                        print(f"Warning: Window too small for interpolation at sample {event_sample}")
                    warning_count += 1
                    continue

                x_interp = x[interp_samples:-interp_samples] - x_fit[0]

                # Interpolate each channel
                for ch in range(data.shape[0]):
                    y_full = data[ch, window_start:window_end + 1]
                    y_fit = np.concatenate([
                        y_full[:interp_samples],
                        y_full[-interp_samples:]
                    ])

                    p = np.polyfit(x_fit, y_fit, 3)
                    data[ch, start:end + 1] = np.polyval(p, x_interp)

                interpolated_count += 1

            if verbose:
                print(f"\nSuccessfully interpolated {interpolated_count} events")
                if warning_count > 0:
                    print(f"Encountered {warning_count} warnings during interpolation")
                print("TMS artifact interpolation complete")

            raw_out._data = data
            self.raw = raw_out

    def mne_fix_tms_artifact(self,
                             window: Tuple[float, float] = (-0.002, 0.015),
                             mode: str = 'window') -> None:
        """
        Interpolate the TMS artifact using MNE's fix_stim_artifact function.

        Parameters
        ----------
        window : tuple
            Time window around TMS pulse to interpolate (start, end) in seconds
        mode : str
            Interpolation mode ('linear', 'cubic', or 'hann')
        """
        if self.raw is None:
            raise ValueError("Must create raw before interpolating TMS artifact")

        events, event_id = mne.events_from_annotations(self.raw)

        try:
            self.raw = mne.preprocessing.fix_stim_artifact(
                self.raw,
                events=events,
                event_id=event_id,
                tmin=window[0],
                tmax=window[1],
                mode=mode
            )
            print(f"Applied TMS artifact interpolation with mode '{mode}'")
        except Exception as e:
            print(f"Error in TMS artifact interpolation: {str(e)}")


######################### EPOCHS AND REJECTION ################### (story of my life)

    def create_epochs(self,
                      tmin: float = -0.5,
                      tmax: float = 1,
                      baseline: Optional[Tuple[float, float]] = None,
                      amplitude_threshold: float = None,
                      events: Optional[np.ndarray] = None,
                      event_id: Optional[Dict] = None) -> None:
        """
        Create epochs from the continuous data with amplitude rejection criteria.

        Parameters
        ----------
        tmin : float
            Start time of epoch in seconds
        tmax : float
            End time of epoch in seconds
        baseline : tuple or None
            Baseline period (start, end) in seconds
        amplitude_threshold : float
            Threshold for rejecting epochs based on peak-to-peak amplitude in µV
        events : array, optional
            Events to create epochs from
        event_id : dict, optional
            Event IDs to use
        """
        # If no events provided, try to find them
        if events is None:
            print("\nNo events provided, attempting to find events...")
            try:
                # First try STI 014
                if 'STI 014' in self.raw.ch_names:
                    events = mne.find_events(self.raw, stim_channel='STI 014')
                    if len(events) > 0:
                        print(f"Found {len(events)} events from STI 014 channel")
                        # Create event_id if not provided
                        if event_id is None:
                            unique_events = np.unique(events[:, 2])
                            event_id = {str(code): code for code in unique_events}

                # If no events found, try other common stim channels
                if events is None or len(events) == 0:
                    common_stim_channels = ['STIM', 'STI101', 'trigger', 'STI 001']
                    for ch in common_stim_channels:
                        if ch in self.raw.ch_names:
                            print(f"Trying channel {ch}...")
                            events = mne.find_events(self.raw, stim_channel=ch)
                            if len(events) > 0:
                                print(f"Found {len(events)} events from {ch} channel")
                                if event_id is None:
                                    unique_events = np.unique(events[:, 2])
                                    event_id = {str(code): code for code in unique_events}
                                break

                # If still no events, try annotations
                if events is None or len(events) == 0:
                    if len(self.raw.annotations) > 0:
                        print("Trying to get events from annotations...")
                        events, event_id = mne.events_from_annotations(self.raw)
                        if len(events) > 0:
                            print(f"Found {len(events)} events from annotations")

            except Exception as e:
                print(f"Error finding events: {str(e)}")

        # Verify we have events
        if events is None or len(events) == 0:
            raise ValueError("No events found in the data. Cannot create epochs.")

        # Verify we have event_id
        if event_id is None:
            print("No event_id provided, creating from unique event codes...")
            unique_events = np.unique(events[:, 2])
            event_id = {str(code): code for code in unique_events}

        print(f"\nCreating epochs with:")
        print(f"Number of events: {len(events)}")
        print(f"Event IDs: {event_id}")
        print(f"Time window: {tmin} to {tmax} seconds")
        if baseline:
            print(f"Baseline period: {baseline}")

        # Store events and event_id
        self.events = events
        self.event_id = event_id

        if amplitude_threshold is not None:
            print(f"Amplitude rejection threshold: {amplitude_threshold}")
            reject = dict(eeg=amplitude_threshold)
            reject_tmin = 0.15
            reject_tmax = 0.3

        else:
            reject = None
            reject_tmin = None
            reject_tmax = None

        # Create epochs
        self.epochs = mne.Epochs(
            self.raw,
            events=self.events,
            event_id=self.event_id,
            tmin=tmin,
            tmax=tmax,
            baseline=baseline,
            reject_by_annotation=True,
            detrend=0,
            preload=True,
            reject=reject,
            reject_tmin=reject_tmin,
            reject_tmax=reject_tmax,
            verbose=True
        )

        print(f"\nCreated {len(self.epochs)} epochs")

        # Store preprocessing stats
        self.preproc_stats['n_orig_events'] = len(events)
        self.preproc_stats['n_final_events'] = len(self.epochs)

    def _get_events(self, raw_eve):
        """Get events from epochs or raw data."""
        if self.epochs is not None:
            return self.epochs.events
        elif hasattr(self, 'raw'):
            return mne.find_events(raw_eve, stim_channel='STI 014')
        return None

    def _get_event_ids(self, raw_eve):
        """Get event IDs from epochs or raw data."""
        if self.epochs is not None:
            return self.epochs.event_id
        elif hasattr(self, 'raw'):
            _, event_id = mne.events_from_annotations(raw_eve, event_id='auto')
            return event_id
        return None

    def remove_bad_channels(self, interpolate: bool = False, threshold: int = 2) -> None:
        """
        Remove and interpolate bad channels using FASTER algorithm.

        Parameters
        ----------
        threshold : float
            Threshold for bad channel detection (default = 2)
        """
        if self.epochs is None:
            raise ValueError("Must create epochs before removing bad channels")

        bad_channels = find_bad_channels(self.epochs, thres=threshold)

        if bad_channels:
            print(f"Detected bad channels: {bad_channels}")
            self.epochs.info['bads'] = list(set(self.epochs.info['bads']).union(set(bad_channels)))

            try:
                # First try normal interpolation
                if interpolate:
                    # Try interpolation again
                    self.epochs.interpolate_bads(reset_bads=True)
                    print("Successfully interpolated bad channels using default montage")
                else:
                    self.epochs.drop_channels(self.epochs.info['bads'])
                self.epochs.interpolate_bads(reset_bads=True)
                print("Interpolated bad channels")

            except ValueError as e:
                print(f"Warning: Standard interpolation failed: {str(e)}")
                print("Attempting alternative interpolation method...")

                try:
                    # Try setting montage again with default positions
                    temp_montage = mne.channels.make_standard_montage(
                        'easycap-M10')  ## standard_1020 was tried before not sure if it makes u huge difference
                    self.epochs.set_montage(temp_montage, match_case=False, on_missing='warn')

                    if interpolate:
                    # Try interpolation again
                        self.epochs.interpolate_bads(reset_bads=True)
                        print("Successfully interpolated bad channels using default montage")
                    else:
                        self.epochs.drop_channels(self.epochs.info['bads'])

                except Exception as e2:
                    print(f"Warning: Alternative interpolation also failed: {str(e2)}")
                    print("Dropping bad channels instead of interpolating")
                    self.epochs.drop_channels(bad_channels)
                    print(f"Dropped channels: {bad_channels}")

            self.preproc_stats['bad_channels'] = bad_channels
        else:
            print("No bad channels detected")

    def remove_bad_epochs(self, threshold: int = 3) -> None:
        """
        Remove bad epochs using FASTER algorithm.

        Parameters
        ----------
        threshold : float
            Threshold for bad epoch detection
        """
        if self.epochs is None:
            raise ValueError("Must create epochs before removing bad epochs")

        bad_epochs = find_bad_epochs(self.epochs, thres=threshold)

        if bad_epochs:
            print(f"Dropping {len(bad_epochs)} bad epochs")
            self.epochs.drop(bad_epochs)
            self.preproc_stats['n_bad_epochs'] = len(bad_epochs)
        else:
            print("No bad epochs detected")

    ######################## TMS ARTIFACT AND EPOCHS ######################################















######################## ICA AND PARAFAC ############################


    from typing import Optional, List
    import threading
    import tkinter as tk

    def run_ica(self ,
                output_dir: str,
                session_name: str,
                n_components: int = None,
                method: str = "fastica",
                tms_muscle_thresh: float = 2.0,
                blink_thresh: float = 2.5,
                lat_eye_thresh: float = 2.0,
                muscle_thresh: float = 0.6,
                noise_thresh: float = 4.0,
                manual_mode: bool = False,
                use_topo: bool = False,
                topo_edge_threshold: float = 0.15,
                topo_zscore_threshold: float = 3.5,  # Changed name
                topo_peak_threshold: float = 3,  # Added
                topo_focal_threshold: float = 0.2,
                ica_callback: Optional[Callable] = None,) -> None:
        """
        Run first ICA decomposition with TESA artifact detection.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        output_dir : str
            Directory to save outputs
        session_name : str
            Name of the current session
        method : str
            ICA method ('fastica' or 'infomax')
        n_components : int
            Number of components to use
        tms_muscle_thresh : float
            Threshold for TMS-muscle artifact detection
        blink_thresh : float
            Threshold for blink detection
        lat_eye_thresh : float
            Threshold for lateral eye movement detection
        muscle_thresh : float
            Threshold for muscle artifact detection
        noise_thresh : float
            Threshold for noise detection
        plot_components : bool
            Whether to plot ICA components
        manual_mode : bool
            Whether to use manual component selection
        ica_callback : callable, optional
            Callback function for GUI-based component selection
        use_topo : bool
            Whether to use topography-based component selection
        """
        # Store copy of data before ICA
        if hasattr(self, 'epochs') and self.epochs is not None:
            inst = self.epochs
            self.epochs_pre_ica = self.epochs.copy()
            is_epochs = True
        else:
            inst = self.raw
            self.raw_pre_ica = self.raw.copy()
            is_epochs = False

        if n_components is None:
            n_channels = len(self.epochs.ch_names)
            n_epochs = len(self.epochs)
            n_components = min(n_channels - 1, n_epochs - 1)

        # Fit ICA
        print("\nFitting ICA...")
        self.ica = ICA(
            n_components=n_components,
            max_iter="auto",
            method=method,
            random_state=42
        )
        self.ica.fit(inst)
        print("ICA fit complete")

        if use_topo:
            print("\nUsing topography-based component classification...")
            from .ica_topo_classifier import ICATopographyClassifier

            classifier = ICATopographyClassifier(self.ica, inst)
            classifier.edge_dist_threshold = topo_edge_threshold
            classifier.zscore_threshold = topo_zscore_threshold
            classifier.peak_count_threshold = topo_peak_threshold
            classifier.focal_area_threshold = topo_focal_threshold

            results = classifier.classify_all_components()
            suggested_exclude = [idx for idx, res in results.items()
                                 if res['classification'] in ['artifact', 'noise']]

            if suggested_exclude:
                print(f"\nExcluding {len(suggested_exclude)} components based on topography")
                self.ica.apply(inst, exclude=suggested_exclude)
                self.selected_first_ica_components = suggested_exclude
                self.preproc_stats['muscle_components'] = suggested_exclude
            else:
                print("\nNo components selected for exclusion by topography analysis")
                self.preproc_stats['muscle_components'] = []

        elif manual_mode:
            self.first_ica_manual = True
            print("\nStarting manual component selection...")
            print("A new window will open for component selection.")

            try:
                # Run all TESA artifact detection methods
                print("\nRunning TESA artifact detection...")
                artifact_results = self.detect_all_artifacts(
                    tms_muscle_thresh=tms_muscle_thresh,
                    blink_thresh=blink_thresh,
                    lat_eye_thresh=lat_eye_thresh,
                    muscle_freq_thresh=muscle_thresh,
                    noise_thresh=noise_thresh,
                    verbose=True
                )

                # Calculate component scores for GUI
                component_scores = {
                    'blink': artifact_results['blink']['scores']['z_scores'],
                    'lat_eye': artifact_results['lateral_eye']['scores']['z_scores'],
                    'muscle': artifact_results['muscle']['scores']['power_ratios'],
                    'noise': artifact_results['noise']['scores']['max_z_scores']
                }

                # Add TMS-muscle scores if using epoched data
                if is_epochs:
                    component_scores['tms_muscle'] = artifact_results['tms_muscle']['scores']['ratios']

                # Print suggested components
                suggested_exclude = []
                for key in artifact_results:
                    if key == 'tms_muscle' and not is_epochs:
                        continue
                    suggested_exclude.extend(artifact_results[key]['components'])
                suggested_exclude = list(set(suggested_exclude))

                if suggested_exclude:
                    print(f"\nSuggested components for removal: {suggested_exclude}")
                    print("(Based on TESA artifact detection)")

            except Exception as e:
                print(f"\nWarning: Error in component analysis: {str(e)}")
                print("Continuing with manual selection without automatic scores")
                component_scores = None

            if ica_callback is not None:
                # Use the provided callback for GUI-based selection
                selected_components = ica_callback(self.ica, inst, component_scores)

                if selected_components:
                    print(f"\nExcluding {len(selected_components)} manually selected components: {selected_components}")
                    self.ica.apply(inst, exclude=selected_components)
                    self.selected_first_ica_components = selected_components
                    self.preproc_stats['muscle_components'] = selected_components
                else:
                    print("\nNo components selected for exclusion")
                    self.preproc_stats['muscle_components'] = []
            else:
                print("\nWarning: Manual mode selected but no callback provided")
                self.preproc_stats['muscle_components'] = []

        else:
            # Automatic detection using TESA methods
            artifact_results = self.detect_all_artifacts(
                tms_muscle_thresh=tms_muscle_thresh,
                blink_thresh=blink_thresh,
                lat_eye_thresh=lat_eye_thresh,
                muscle_freq_thresh=muscle_thresh,
                noise_thresh=noise_thresh,
                verbose=True
            )

            # Combine all detected components
            exclude_components = []
            for key in artifact_results:
                if key == 'tms_muscle' and not is_epochs:
                    continue  # Skip TMS-muscle components for raw data
                exclude_components.extend(artifact_results[key]['components'])
            exclude_components = list(set(exclude_components))  # Remove duplicates

            if exclude_components:
                print(f"\nExcluding {len(exclude_components)} components: {exclude_components}")
                self.ica.apply(inst, exclude=exclude_components)
                self.preproc_stats['muscle_components'] = exclude_components
            else:
                print("\nNo components detected to exclude")
                self.preproc_stats['muscle_components'] = []

        # Update the appropriate data instance
        if is_epochs:
            self.epochs = inst
        else:
            self.raw = inst


    def run_second_ica(self,
                       method: str = "infomax",
                       n_components: int = None,
                       blink_thresh: float = 2.5,
                       lat_eye_thresh: float = 2.0,
                       muscle_thresh: float = 0.6,
                       noise_thresh: float = 4.0,
                       manual_mode: bool = False,
                       use_topo: bool = False,
                       topo_edge_threshold: float = 0.15,
                       topo_zscore_threshold: float = 3.5,  # Changed name
                       topo_peak_threshold: float = 3,  # Added
                       topo_focal_threshold: float = 0.2,
                       ica_callback: Optional[Callable] = None) -> None:
        """
        Run second ICA with both TESA and ICLabel detection methods.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        method : str
            ICA method ('fastica' or 'infomax')
        n_components : int
            Number of components to use
        exclude_labels : list of str
            Labels of components to exclude if using ICLabel
        blink_thresh : float
            Threshold for blink detection
        lat_eye_thresh : float
            Threshold for lateral eye movement detection
        muscle_thresh : float
            Threshold for muscle artifact detection
        noise_thresh : float
            Threshold for noise detection
        manual_mode : bool
            Whether to use manual component selection
        ica_callback : callable, optional
            Callback function for GUI-based component selection
        use_topo : bool
            Whether to use topography-based component selection
        """
        # Determine if we're working with epochs or raw data
        if hasattr(self, 'epochs') and self.epochs is not None:
            inst = self.epochs
            is_epochs = True
        else:
            inst = self.raw
            is_epochs = False

        if inst is None:
            raise ValueError("No data available for ICA")

        if n_components is None:
            n_channels = len(self.epochs.ch_names)
            n_epochs = len(self.epochs)
            n_components = min(n_channels - 1, n_epochs - 1)

        print("\nPreparing for second ICA...")
        if is_epochs:
            self.set_average_reference()

        # Initialize and fit ICA
        fit_params = dict(extended=True) if method == "infomax" else None
        self.ica2 = ICA(max_iter="auto", n_components=n_components, method=method, random_state=42, fit_params=fit_params)
        self.ica2.fit(inst)
        print("Second ICA fit complete")

        if use_topo:
            print("\nUsing topography-based component classification...")
            from .ica_topo_classifier import ICATopographyClassifier

            # Update classifier parameters
            classifier = ICATopographyClassifier(self.ica2, inst)  # Note: Changed to ica2
            classifier.edge_dist_threshold = topo_edge_threshold
            classifier.zscore_threshold = topo_zscore_threshold
            classifier.peak_count_threshold = topo_peak_threshold
            classifier.focal_area_threshold = topo_focal_threshold

            results = classifier.classify_all_components()
            suggested_exclude = [idx for idx, res in results.items()
                                 if res['classification'] in ['artifact', 'noise']]

            if suggested_exclude:
                print(f"\nExcluding {len(suggested_exclude)} components based on topography")
                self.ica2.apply(inst, exclude=suggested_exclude)  # Fix: Use self.ica2
                self.selected_second_ica_components = suggested_exclude  # Fix: Use second ICA stats
                self.preproc_stats['excluded_ica_components'] = suggested_exclude
            else:
                print("\nNo components selected for exclusion by topography analysis")
                self.preproc_stats['muscle_components'] = []

        elif manual_mode:
            self.second_ica_manual = True
            print("\nStarting manual component selection for second ICA...")

            try:
                # Run TESA artifact detection (excluding TMS-muscle for continuous data)
                print("\nRunning TESA artifact detection...")
                artifact_results = self.detect_all_artifacts(
                    blink_thresh=blink_thresh,
                    lat_eye_thresh=lat_eye_thresh,
                    muscle_freq_thresh=muscle_thresh,
                    noise_thresh=noise_thresh,
                    verbose=True
                )

                # Calculate component scores
                component_scores = {
                    'blink': artifact_results['blink']['scores']['z_scores'],
                    'lat_eye': artifact_results['lateral_eye']['scores']['z_scores'],
                    'muscle': artifact_results['muscle']['scores']['power_ratios'],
                    'noise': artifact_results['noise']['scores']['max_z_scores']
                }

                # Add TMS-muscle scores if using epoched data
                if is_epochs:
                    component_scores['tms_muscle'] = artifact_results['tms_muscle']['scores']['ratios']

                # Print suggested components
                suggested_exclude = []
                for key in artifact_results:
                    if key == 'tms_muscle' and not is_epochs:
                        continue
                    suggested_exclude.extend(artifact_results[key]['components'])
                suggested_exclude = list(set(suggested_exclude))

                if suggested_exclude:
                    print(f"\nSuggested components for removal: {suggested_exclude}")
                    print("(Based on TESA artifact detection)")

            except Exception as e:
                print(f"\nWarning: Error in component analysis: {str(e)}")
                component_scores = None

            if ica_callback is not None:
                # Use the provided callback for GUI-based selection
                selected_components = ica_callback(self.ica2, inst, component_scores)

                if selected_components:
                    print(f"\nExcluding {len(selected_components)} manually selected components: {selected_components}")
                    self.ica2.apply(inst, exclude=selected_components)
                    self.selected_second_ica_components = selected_components
                    self.preproc_stats['excluded_ica_components'] = selected_components
                else:
                    print("\nNo components selected for exclusion")
                    self.preproc_stats['excluded_ica_components'] = []
            else:
                print("\nWarning: Manual mode selected but no callback provided")
                self.preproc_stats['excluded_ica_components'] = []

        else:
            # Automatic detection using TESA methods
            try:
                artifact_results = self.detect_all_artifacts(
                    blink_thresh=blink_thresh,
                    lat_eye_thresh=lat_eye_thresh,
                    muscle_freq_thresh=muscle_thresh,
                    noise_thresh=noise_thresh,
                    verbose=True,
                    ica_instance=self.ica2,
                )

                # Combine detected components
                exclude_idx = []
                for key in artifact_results:
                    if key == 'tms_muscle' and not is_epochs:
                        continue
                    exclude_idx.extend(artifact_results[key]['components'])
                exclude_idx = list(set(exclude_idx))

                if exclude_idx:
                    print(f"\nExcluding {len(exclude_idx)} components: {exclude_idx}")
                    self.ica2.apply(inst, exclude=exclude_idx)
                    self.preproc_stats['excluded_ica_components'] = exclude_idx
                else:
                    print("\nNo components excluded")
                    self.preproc_stats['excluded_ica_components'] = []

            except Exception as e:
                print(f"Warning: Error in automatic component detection: {str(e)}")
                print("No components will be automatically excluded")
                self.preproc_stats['excluded_ica_components'] = []

        # Update the appropriate data instance
        if is_epochs:
            self.epochs = inst
        else:
            self.raw = inst

        print('Second ICA complete')


    def detect_all_artifacts(self,
                             tms_muscle_window=(11, 30),
                             tms_muscle_thresh=2,
                             blink_thresh=2.5,
                             lat_eye_thresh=2.0,
                             muscle_freq_window=(30, 100),
                             muscle_freq_thresh=1.0,
                             noise_thresh=6.0,
                             verbose=True,
                             ica_instance=None) -> Dict:
        """
        Detect all artifact types following TESA's implementation.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        tms_muscle_window : tuple
            Time window (ms) for detecting TMS-evoked muscle activity
        tms_muscle_thresh : float
            Threshold for TMS-evoked muscle components
        blink_thresh : float
            Threshold for blink components
        lat_eye_thresh : float
            Threshold for lateral eye movement components
        muscle_freq_window : tuple
            Frequency window (Hz) for detecting persistent muscle activity
        muscle_freq_thresh : float
            Threshold for persistent muscle components
        noise_thresh : float
            Threshold for electrode noise components
        verbose : bool
            Whether to print verbose output
        ica_instance : mne.preprocessing.ICA, optional
            Specific ICA instance to use. If None, uses self.ica

        Returns
        -------
        dict
            Dictionary containing detected components and their scores
        """
        # Use provided ICA instance or default to self.ica
        ica = ica_instance if ica_instance is not None else self.ica

        if not hasattr(self, 'ica'):
            raise ValueError("Must run ICA before detecting components")

        # Initialize results dictionary
        results = {
            'tms_muscle': {'components': [], 'scores': {}},
            'blink': {'components': [], 'scores': {}},
            'lateral_eye': {'components': [], 'scores': {}},
            'muscle': {'components': [], 'scores': {}},
            'noise': {'components': [], 'scores': {}}
        }

        # Use provided ICA instance or default to self.ica
        ica = ica_instance if ica_instance is not None else self.ica

        # Get ICA weights
        weights = ica.get_components()
        n_components = ica.n_components_

        # Get ICA components (sources)
        if hasattr(self, 'epochs') and self.epochs is not None:
            inst = self.epochs
            components = ica.get_sources(inst)
            is_epochs = True
        else:
            inst = self.raw
            components = ica.get_sources(inst)
            is_epochs = False

        # 1. Detect TMS-evoked muscle artifacts (if using epoched data)
        if is_epochs:
            muscle_comps, muscle_scores = self._detect_tms_muscle(
                components, tms_muscle_window, tms_muscle_thresh)
            results['tms_muscle']['components'] = muscle_comps
            results['tms_muscle']['scores'] = muscle_scores

            if verbose:
                print(f"\nFound {len(muscle_comps)} TMS-muscle components")

        # 2. Detect eye blink artifacts
        blink_comps, blink_scores = self._detect_blinks(
            weights, inst, blink_thresh)
        results['blink']['components'] = blink_comps
        results['blink']['scores'] = blink_scores

        if verbose:
            print(f"Found {len(blink_comps)} blink components")

        # 3. Detect lateral eye movement artifacts
        lat_eye_comps, lat_eye_scores = self._detect_lateral_eye(
            weights, inst, lat_eye_thresh)
        results['lateral_eye']['components'] = lat_eye_comps
        results['lateral_eye']['scores'] = lat_eye_scores

        if verbose:
            print(f"Found {len(lat_eye_comps)} lateral eye movement components")

        # 4. Detect persistent muscle artifacts
        muscle_comps, muscle_scores = self._detect_muscle_frequency(
            components, inst.info['sfreq'], muscle_freq_window, muscle_freq_thresh)
        results['muscle']['components'] = muscle_comps
        results['muscle']['scores'] = muscle_scores

        if verbose:
            print(f"Found {len(muscle_comps)} persistent muscle components")

        # 5. Detect electrode noise
        noise_comps, noise_scores = self._detect_electrode_noise(
            weights, noise_thresh)
        results['noise']['components'] = noise_comps
        results['noise']['scores'] = noise_scores

        if verbose:
            print(f"Found {len(noise_comps)} noisy electrode components")

        return results

    def _detect_tms_muscle(self, components, window=(11, 30), thresh=2.0):
        """
        Detect TMS-evoked muscle artifacts following Equation 3.
        Only works with epoched data.
        """
        if not hasattr(self, 'epochs'):
            return [], {'ratios': [], 'window_means': [], 'total_means': []}

        # Get time window indices
        sfreq = self.epochs.info['sfreq']
        window_samples = np.array([np.abs(self.epochs.times - w / 1000).argmin()
                                   for w in window])

        # Initialize outputs
        muscle_components = []
        scores = {'ratios': [], 'window_means': [], 'total_means': []}

        # Process each component
        for comp_idx in range(self.ica.n_components_):
            # Get component time course averaged across trials
            comp_data = np.mean(components.get_data()[:, comp_idx, :], axis=0)

            # Take absolute values
            comp_abs = np.abs(comp_data)

            # Calculate means following TESA formula
            window_length = window_samples[1] - window_samples[0]
            window_mean = (1 / window_length) * np.sum(
                comp_abs[window_samples[0]:window_samples[1]])
            total_mean = (1 / len(comp_abs)) * np.sum(comp_abs)

            # Calculate ratio
            muscle_ratio = window_mean / total_mean

            # Store scores
            scores['ratios'].append(muscle_ratio)
            scores['window_means'].append(window_mean)
            scores['total_means'].append(total_mean)

            # Classify component
            if muscle_ratio >= thresh:
                muscle_components.append(comp_idx)

        return muscle_components, scores

    def _detect_blinks(self, weights, inst, thresh=2.5):
        """
        Detect eye blink artifacts following Equation 4.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        weights : array
            ICA weight matrix
        inst : Raw or Epochs
            MNE Raw or Epochs instance
        thresh : float
            Z-score threshold for blink detection
        """
        # Get electrode indices for Fp1 and Fp2
        fp_channels = ['Fp1', 'Fp2']
        fp_idx = [inst.ch_names.index(ch) for ch in fp_channels
                  if ch in inst.ch_names]

        if not fp_idx:
            print("Warning: Could not find Fp1/Fp2 channels for blink detection")
            return [], {'z_scores': []}

        # Initialize outputs
        blink_components = []
        scores = {'z_scores': []}

        # Calculate z-scores for weights
        w_mean = np.mean(weights, axis=0)
        w_std = np.std(weights, axis=0)

        for comp_idx in range(weights.shape[1]):
            # Get average z-score for Fp1/Fp2
            fp_z_scores = [(weights[fp, comp_idx] - w_mean[comp_idx]) / w_std[comp_idx]
                           for fp in fp_idx]
            mean_z = np.abs(np.mean(fp_z_scores))

            scores['z_scores'].append(mean_z)

            # Classify component
            if mean_z > thresh:
                blink_components.append(comp_idx)

        return blink_components, scores

    def _detect_lateral_eye(self, weights, inst, thresh=2.0):
        """
        Detect lateral eye movement artifacts following Equations 5 & 6.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        weights : array
            ICA weight matrix
        inst : Raw or Epochs
            MNE Raw or Epochs instance
        thresh : float
            Z-score threshold for lateral eye movement detection
        """
        # Get electrode indices for F7 and F8
        lat_channels = ['F7', 'F8']
        lat_idx = [inst.ch_names.index(ch) for ch in lat_channels
                   if ch in inst.ch_names]

        if len(lat_idx) < 2:
            print("Warning: Could not find F7/F8 channels for lateral eye detection")
            return [], {'z_scores': []}

        # Initialize outputs
        lat_eye_components = []
        scores = {'z_scores': []}

        # Calculate z-scores for weights
        w_mean = np.mean(weights, axis=0)
        w_std = np.std(weights, axis=0)

        for comp_idx in range(weights.shape[1]):
            # Get z-scores for F7/F8
            z_scores = [(weights[ch, comp_idx] - w_mean[comp_idx]) / w_std[comp_idx]
                        for ch in lat_idx]

            scores['z_scores'].append(z_scores)

            # Check for opposite polarity exceeding threshold
            if ((z_scores[0] > thresh and z_scores[1] < -thresh) or
                    (z_scores[0] < -thresh and z_scores[1] > thresh)):
                lat_eye_components.append(comp_idx)

        return lat_eye_components, scores

    def _detect_muscle_frequency(self, components, sfreq, freq_window=(30, 100), thresh=0.6):
        """
        Detect persistent muscle artifacts following Equation 7.
        Works with both Raw and Epochs data.

        Parameters
        ----------
        components : array
            ICA component data
        sfreq : float
            Sampling frequency
        freq_window : tuple
            Frequency window (Hz) for muscle activity detection
        thresh : float
            Threshold for muscle component detection
        """
        from scipy.signal import welch

        # Initialize outputs
        muscle_components = []
        scores = {'power_ratios': []}

        # Get component data
        if isinstance(components, mne.BaseEpochs):
            comp_data = components.get_data()
        else:  # Raw data
            comp_data = components.get_data()
            # Reshape to match epochs format [n_epochs=1, n_components, n_times]
            comp_data = comp_data.reshape(1, *comp_data.shape)

        # Calculate frequency representation for each component
        for comp_idx in range(self.ica.n_components_):
            # Calculate power spectrum
            freqs, psd = welch(comp_data[:, comp_idx, :], fs=sfreq)

            # Get indices for frequency window
            freq_idx = np.where((freqs >= freq_window[0]) &
                                (freqs <= freq_window[1]))[0]

            # Calculate power ratio
            window_power = np.mean(psd[:, freq_idx])
            total_power = np.mean(psd)
            power_ratio = window_power / total_power

            scores['power_ratios'].append(power_ratio)

            # Classify component
            if power_ratio > thresh:
                muscle_components.append(comp_idx)

        return muscle_components, scores

    def _detect_electrode_noise(self, weights, thresh=4.0):
        """
        Detect electrode noise following Equation 8.
        Works with both Raw and Epochs data as it only uses ICA weights.

        Parameters
        ----------
        weights : array
            ICA weight matrix
        thresh : float
            Z-score threshold for noise detection
        """
        # Initialize outputs
        noise_components = []
        scores = {'max_z_scores': []}

        # Calculate z-scores for weights
        w_mean = np.mean(weights, axis=0)
        w_std = np.std(weights, axis=0)

        for comp_idx in range(weights.shape[1]):
            # Calculate z-scores for all electrodes
            z_scores = (weights[:, comp_idx] - w_mean[comp_idx]) / w_std[comp_idx]
            max_abs_z = np.max(np.abs(z_scores))

            scores['max_z_scores'].append(max_abs_z)

            # Classify component
            if max_abs_z > thresh:
                noise_components.append(comp_idx)

        return noise_components, scores

    def clean_muscle_artifacts(self,
                               muscle_window: Tuple[float, float] = (0.005, 0.05),
                               threshold_factor: float = 5.0,
                               n_components: int = 2,
                               verbose: bool = True) -> None:
        """
        Clean TMS-evoked muscle artifacts using tensor decomposition.

        Parameters
        ----------
        muscle_window : tuple
            Time window for detecting muscle artifacts in seconds [start, end]
        threshold_factor : float
            Threshold for artifact detection
        n_components : int
            Number of components to use in tensor decomposition
        verbose : bool
            Whether to print progress information
        """
        if self.epochs is None:
            raise ValueError("Must create epochs before cleaning muscle artifacts")

        # Create cleaner instance
        cleaner = TMSArtifactCleaner(self.epochs, verbose=verbose)

        # Detect artifacts
        artifact_info = cleaner.detect_muscle_artifacts(
            muscle_window=muscle_window,
            threshold_factor=threshold_factor,
            verbose=verbose
        )

        if verbose:
            print("\nArtifact detection results:")
            print(f"Found {artifact_info['muscle']['stats']['n_detected']} artifacts")
            print(f"Detection rate: {artifact_info['muscle']['stats']['detection_rate'] * 100:.1f}%")

        # Clean artifacts
        cleaned_epochs = cleaner.clean_muscle_artifacts(
            n_components=n_components,
            verbose=verbose
        )

        # Update epochs with cleaned data
        self.epochs = cleaned_epochs

        # Apply baseline correction again
        # self.apply_baseline_correction()

        if verbose:
            print("\nMuscle artifact cleaning complete")

    ######################## ICA AND PARAFAC ############################









    ######################## FILTERS ############################

    def filter_raw(self, l_freq=0.1, h_freq=250, notch_freq=50, notch_width=2):
        """
        Filter raw data using a zero-phase Butterworth filter with improved stability.

        Parameters
        ----------
        l_freq : float or None
            Lower frequency cutoff for bandpass filter (default: 0.1 Hz)
        h_freq : float
            Upper frequency cutoff for bandpass filter (default: 45 Hz)
        notch_freq : float or None
            Frequency for notch filter (default: 50 Hz)
        notch_width : float
            Width of notch filter (default: 2 Hz)
        """
        from scipy.signal import butter, sosfiltfilt, filtfilt, iirnotch
        import numpy as np

        print(f"Applying SciPy filters to raw data with frequency {l_freq}Hz and frequency {h_freq}Hz")

        # Create a copy of the raw data
        filtered_raw = self.raw.copy()

        # Get data and scale it up for better numerical precision
        data = filtered_raw.get_data()
        print(f"Data range before scaling: [{np.min(data)}, {np.max(data)}]")
        #scale_factor = 1e6  # Convert to microvolts
        #data = data * scale_factor

        print(f"Data shape: {data.shape}")
        print(f"Scaled data range: [{np.min(data)}, {np.max(data)}] µV")

        # Ensure data is float64
        data = data.astype(np.float64)

        sfreq = filtered_raw.info['sfreq']
        nyquist = sfreq / 2

        try:
            if l_freq is not None:
                # High-pass filter
                sos_high = butter(3, l_freq / nyquist, btype='high', output='sos')
                data = sosfiltfilt(sos_high, data, axis=-1)
                print(f"After high-pass - Data range: [{np.min(data)}, {np.max(data)}] µV")

            # Low-pass filter
            sos_low = butter(5, h_freq / nyquist, btype='low', output='sos')
            data = sosfiltfilt(sos_low, data, axis=-1)
            print(f"After low-pass - Data range: [{np.min(data)}, {np.max(data)}] µV")

            if notch_freq is not None:
                # Multiple notch filters for harmonics
                for freq in [notch_freq, notch_freq * 2]:  # 50 Hz and 100 Hz
                    # Using iirnotch for sharper notch characteristics
                    b, a = iirnotch(freq / nyquist, 35)  # Q=35 for very narrow notch
                    data = filtfilt(b, a, data, axis=-1)
                print(f"After notch - Data range: [{np.min(data)}, {np.max(data)}] µV")

            # Scale back
            #data = data / scale_factor
            filtered_raw._data = data

        except Exception as e:
            print(f"Error during filtering: {str(e)}")
            raise

        print("Filtering complete")
        self.raw = filtered_raw


    def mne_filter_epochs(self, l_freq=0.1, h_freq=45, notch_freq=50, notch_width=2):
        """
        Filter epoched data using MNE's built-in filtering plus custom notch.

        Parameters
        ----------
        l_freq : float
            Lower frequency bound for bandpass filter
        h_freq : float
            Upper frequency bound for bandpass filter
        notch_freq : float
            Frequency to notch filter (usually power line frequency)
        notch_width : float
            Width of the notch filter

        Returns
        -------
        None
            Updates self.epochs in place
        """
        from scipy.signal import iirnotch, filtfilt
        import numpy as np
        from mne.time_frequency import psd_array_welch

        if self.epochs is None:
            raise ValueError("Must create epochs before filtering")

        # Store original epochs for potential recovery
        original_epochs = self.epochs
        try:
            # Create a deep copy to work with
            filtered_epochs = self.epochs.copy()

            # Get data and sampling frequency
            data = filtered_epochs.get_data()
            sfreq = filtered_epochs.info['sfreq']
            nyquist = sfreq / 2.0

            # Diagnostic before filtering
            psds, freqs = psd_array_welch(data.reshape(-1, data.shape[-1]),
                                          sfreq=sfreq,
                                          fmin=0,
                                          fmax=200,
                                          n_per_seg=256,
                                          n_overlap=128)

            print(f"\nBefore filtering:")
            print(f"Peak frequency: {freqs[np.argmax(psds.mean(0))]} Hz")
            print(f"Frequency range with significant power: {freqs[psds.mean(0) > psds.mean(0).max() * 0.1][0]:.1f} - "
                  f"{freqs[psds.mean(0) > psds.mean(0).max() * 0.1][-1]:.1f} Hz")

            # Apply filters in sequence
            print("\nApplying low-pass filter...")
            filtered_epochs.filter(
                l_freq=None,
                h_freq=h_freq,
                picks='eeg',
                filter_length='auto',
                h_trans_bandwidth=10,
                method='fir',
                fir_window='hamming',
                fir_design='firwin',
                phase='zero',
                verbose=True
            )

            print("\nApplying high-pass filter...")
            filtered_epochs.filter(
                l_freq=l_freq,
                h_freq=None,
                picks='eeg',
                filter_length='auto',
                l_trans_bandwidth=l_freq / 2,
                method='fir',
                fir_window='hamming',
                fir_design='firwin',
                phase='zero',
                verbose=True
            )

            # Get the filtered data for notch filtering
            data = filtered_epochs.get_data()

            print("\nApplying notch filters...")
            for freq in [notch_freq, notch_freq * 2]:
                print(f"Processing {freq} Hz notch...")
                Q = 30.0  # Quality factor
                w0 = freq / nyquist
                b, a = iirnotch(w0, Q)

                # Apply to each epoch and channel
                for epoch_idx in range(data.shape[0]):
                    for ch_idx in range(data.shape[1]):
                        data[epoch_idx, ch_idx, :] = filtfilt(b, a, data[epoch_idx, ch_idx, :])

            # Update the filtered epochs with notch-filtered data
            filtered_epochs._data = data

            # Diagnostic after filtering
            data_filtered = filtered_epochs.get_data()
            psds, freqs = psd_array_welch(data_filtered.reshape(-1, data_filtered.shape[-1]),
                                          sfreq=sfreq,
                                          fmin=0,
                                          fmax=200,
                                          n_per_seg=256,
                                          n_overlap=128)

            print(f"\nAfter filtering:")
            print(f"Peak frequency: {freqs[np.argmax(psds.mean(0))]} Hz")
            print(f"Frequency range with significant power: {freqs[psds.mean(0) > psds.mean(0).max() * 0.1][0]:.1f} - "
                  f"{freqs[psds.mean(0) > psds.mean(0).max() * 0.1][-1]:.1f} Hz")

            # Verify the filtered data
            if np.any(np.isnan(filtered_epochs._data)):
                raise ValueError("Filtering produced NaN values")

            if np.any(np.isinf(filtered_epochs._data)):
                raise ValueError("Filtering produced infinite values")

            # Update the instance's epochs with the filtered version
            self.epochs = filtered_epochs
            print("\nFiltering completed successfully")

        except Exception as e:
            print(f"Error during filtering: {str(e)}")
            print("Reverting to original epochs")
            self.epochs = original_epochs
            raise


    def scipy_filter_epochs(self, l_freq=None, h_freq=45, notch_freq=None, notch_width=2):
        """
        Filter epoched data using a zero-phase Butterworth filter with improved stability.

        Parameters
        ----------
        l_freq : float
            Lower frequency cutoff for bandpass filter (default: 0.1 Hz)
        h_freq : float
            Upper frequency cutoff for bandpass filter (default: 45 Hz)
        notch_freq : float
            Frequency for notch filter (default: 50 Hz)
        notch_width : float
            Width of notch filter (default: 2 Hz)
        """
        from scipy.signal import butter, sosfiltfilt, filtfilt, iirnotch
        import numpy as np

        if self.epochs is None:
            raise ValueError("Must create epochs before filtering")

        # Create a copy of the epochs object
        filtered_epochs = self.epochs.copy()

        # Get data and scale it up for better numerical precision
        data = filtered_epochs.get_data()
       # scale_factor = 1e6  # Convert to microvolts
       # data = data * scale_factor

        print(f"Data shape: {data.shape}")
        print(f"Scaled data range: [{np.min(data)}, {np.max(data)}] µV")

        # Ensure data is float64
        data = data.astype(np.float64)

        sfreq = filtered_epochs.info['sfreq']
        nyquist = sfreq / 2

        try:
            # High-pass filter
            sos_high = butter(3, l_freq / nyquist, btype='high', output='sos')
            data = sosfiltfilt(sos_high, data, axis=-1)
            print(f"After high-pass - Data range: [{np.min(data)}, {np.max(data)}] µV")

            # Low-pass filter
            sos_low = butter(5, h_freq / nyquist, btype='low', output='sos')
            data = sosfiltfilt(sos_low, data, axis=-1)
            print(f"After low-pass - Data range: [{np.min(data)}, {np.max(data)}] µV")
            if notch_freq is not None:
                # Multiple notch filters for harmonics
                for freq in [notch_freq, notch_freq * 2]:  # 50 Hz and 100 Hz
                    # Using iirnotch for sharper notch characteristics
                    b, a = iirnotch(freq / nyquist, 35)  # Q=35 for very narrow notch
                    data = filtfilt(b, a, data, axis=-1)
                print(f"After notch - Data range: [{np.min(data)}, {np.max(data)}] µV")

            # Scale back
            #data = data / scale_factor
            filtered_epochs._data = data

        except Exception as e:
            print(f"Error during filtering: {str(e)}")
            raise

        print("Filtering complete")
        self.epochs = filtered_epochs

    ######################## FILTERS ##############################








    ################# SOME FINAL STEPS #####################

    def set_average_reference(self):
        '''
        - Rereference EEG and apply projections
        '''
        self.epochs.set_eeg_reference('average', projection=True)
        print("Rereferenced epochs to 'average'")

    def apply_baseline_correction(self, baseline: Tuple[float, float] = (-0.1, -0.002)) -> None:
        """
        Apply baseline correction to epochs.
        
        Parameters
        ----------
        baseline : tuple
            Start and end time of baseline period in seconds (start, end)
        """
        if self.epochs is None:
            raise ValueError("Must create epochs before applying baseline")
            
        self.epochs.apply_baseline(baseline=baseline)
        print(f"Applied baseline correction using window {baseline} seconds")

    def downsample(self):
        '''
        - Downsample epochs to desired sfreq if current sfreq > desired sfreq (default 1000 Hz)
        '''

        current_sfreq = self.epochs.info['sfreq']
        if current_sfreq > self.ds_sfreq:
            self.epochs = self.epochs.resample(self.ds_sfreq)
            print(f"Downsampled data to {self.ds_sfreq} Hz")
        else:
            print("Current sfreq < target sfreq")
            pass

    def get_preproc_stats(self):
        """Return current preprocessing statistics"""
        return {
            'Original Events': self.preproc_stats['n_orig_events'],
            'Final Events': self.preproc_stats['n_final_events'],
            'Event Retention Rate': f"{(self.preproc_stats['n_final_events']/self.preproc_stats['n_orig_events'])*100:.1f}%",
            'Bad Channels': ', '.join(self.preproc_stats['bad_channels']) if self.preproc_stats['bad_channels'] else 'None',
            'Bad Epochs Removed': self.preproc_stats['n_bad_epochs'],
            'ICA1 Muscle Components': len(self.preproc_stats['muscle_components']),
            'ICA2 Excluded Components': len(self.preproc_stats['excluded_ica_components']),
            'TMS Interpolation Windows': len(self.preproc_stats['interpolated_times'])
    }


    def apply_ssp(self, n_eeg=2):

        
        projs_epochs = mne.compute_proj_epochs(self.epochs, n_eeg=n_eeg, n_jobs=-1, verbose=True)
        self.epochs.add_proj(projs_epochs)
        self.epochs.apply_proj()
        


    def apply_csd(self, lambda2=1e-5, stiffness=4, n_legendre_terms=50, verbose=True):
        """
        Apply Current Source Density transformation maintaining CSD channel type.
        
        Parameters
        ----------
        lambda2 : float
            Regularization parameter
        stiffness : int
            Stiffness of the spline
        n_legendre_terms : int
            Number of Legendre terms
        verbose : bool
            Print progress information
        """
        if verbose:
            print("Applying Current Source Density transformation...")
        
        # Apply CSD transformation
        self.epochs = compute_current_source_density(
            self.epochs,
            lambda2=lambda2,
            stiffness=stiffness,
            n_legendre_terms=n_legendre_terms,
            copy=True
        )
        
        # The channels are now CSD type, so we leave them as is
        if verbose:
            print("CSD transformation complete")
        
        # Store the fact that we've applied CSD
        self.csd_applied = True
        
        return self.epochs



    def final_downsample(self):
        """
        Perform final downsampling of epochs to final_sfreq (default 725 Hz).
        """
        if self.epochs is None:
            raise ValueError("Must create epochs before final downsampling")

        current_sfreq = self.epochs.info['sfreq']
        if current_sfreq > self.final_sfreq:
            self.epochs = self.epochs.resample(self.final_sfreq)
            print(f"Final downsample to {self.final_sfreq} Hz")
        else:
            print(f"Current sfreq ({current_sfreq} Hz) <= final target sfreq ({self.final_sfreq} Hz); "
                  "no final downsampling performed")
    
    def save_epochs(self, fpath: str = None):
        """
        Save preprocessed epochs
        """
        self.epochs.save(fpath, verbose=True, overwrite=True)

        print(f"Epochs saved at {fpath}")
