# tmseegpy/cli.py

import sys
import threading
from tmseegpy.run import process_subjects, setup_qt_plugin_path
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication


def main():
    """Main entry point for tmseegpy"""
    # Setup Qt plugin path first
    setup_qt_plugin_path()
    app = QApplication.instance()
    if app is None:
        app = QApplication([])


    # Parse arguments
    parser = argparse.ArgumentParser(description='TMSeegpy: TMS-EEG Processing Pipeline')
    subparsers = parser.add_subparsers(dest='command', help='Commands')



    process_parser = subparsers.add_parser('process', help='Process TMS-EEG data')


    process_parser.add_argument('--data_dir', type=str, default=str(Path.cwd() / 'data'),
                        help='Path to the data directory (default: ./data)')

    process_parser.add_argument('--output_dir', type=str, default=str(Path.cwd() / 'output'),
                        help='Path to the output directory (default: ./output)')

    process_parser.add_argument('--data_format', type=str, default='neurone',
                        choices=['neurone', 'brainvision', 'edf', 'cnt', 'eeglab', 'auto'],
                        help='Format of input data (default: neurone)')

    process_parser.add_argument('--no_preproc_output', action='store_true', default=False,
                        help='Skip saving preprocessed epochs (default: False)')

    process_parser.add_argument('--no_pcist', action='store_true', default=False,
                        help='Skip PCIst calculation and only preprocess (default: False)')

    process_parser.add_argument('--eeglab_montage_units', type=str, default='auto',
                        help='Units for EEGLAB channel positions (default: auto)')

    process_parser.add_argument('--stim_channel', type=str, default='STI 014',
                        help='Name of the stimulus channel (default: STI 014)')

    process_parser.add_argument('--save_preproc', action='store_true', default=False,
                        help='Save plots between preprocessing steps (default: False)')

    process_parser.add_argument('--random_seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')

    process_parser.add_argument('--substitute_zero_events_with', type=int, default=10,
                        help='Value to substitute zero events with (default: 10)')


    process_parser.add_argument('--auto_detect_artifacts', action='store_true', default=False,
                        help='Use automatic artifact detection instead of triggers (default: False)')

    process_parser.add_argument('--artifact_threshold_std', type=float, default=10,
                        help='Standard deviations above mean for artifact detection (default: 10)')

    process_parser.add_argument('--min_artifact_distance_ms', type=float, default=50,
                        help='Minimum distance between artifacts in ms (default: 50)')

    process_parser.add_argument('--final_sfreq', type=float, default=725,
                        help='Final downsampling frequency (default: 725)')

    # Trying to match TESA
    process_parser.add_argument('--initial_window_start', type=float, default=-2,

                        help='Initial TMS artifact window start (TESA default: -2)')

    process_parser.add_argument('--initial_window_end', type=float, default=10,
                        help='Initial TMS artifact window end (TESA default: 10)')

    process_parser.add_argument('--extended_window_start', type=float, default=-2,
                        help='Extended TMS artifact window start (TESA default: -2)')

    process_parser.add_argument('--extended_window_end', type=float, default=15,
                        help='Extended TMS artifact window end (TESA default: 15)')

    process_parser.add_argument('--initial_interp_window', type=float, default=1.0,
                        help='Initial interpolation window (TESA default: 1.0)')

    process_parser.add_argument('--extended_interp_window', type=float, default=5.0,
                        help='Extended interpolation window (TESA default: 5.0)')

    process_parser.add_argument('--interpolation_method', type=str, default='cubic',
                        choices=['cubic'],
                        help='Interpolation method (TESA requires cubic)')

    process_parser.add_argument('--second_artifact_removal', action='store_true', default=False,
                    help='Skip the second stage of TMS artifact removal (default: False)')

    process_parser.add_argument('--mne_filter_epochs', action='store_true', default=False,
                        help='Use built in filter in mne (default: False)')

    process_parser.add_argument('--scipy_filter_epochs', action='store_true', default=False,
                    help='Use custom filter from scipy (default: False)')

    process_parser.add_argument('--plot_raw', action='store_true',
                        help='Plot raw data (takes time) (default: False)')

    process_parser.add_argument('--filter_raw', action='store_true', default=False,
                        help='Whether to filter raw data instead of epoched (default: False)')

    process_parser.add_argument('--l_freq', type=float, default=1,
                        help='Lower frequency for filtering (default: 1)')

    process_parser.add_argument('--raw_l_freq', type=float, default=1,
                        help='Lower frequency for filtering (default: 1)')

    process_parser.add_argument('--h_freq', type=float, default=45,
                        help='Upper frequency for filtering (default: 45)')

    process_parser.add_argument('--raw_h_freq', type=float, default=250,
                        help='Upper frequency for filtering the raw eeg data (default: 250)')

    process_parser.add_argument('--notch_freq', type=float, default=None,
                        help='Notch filter frequency (default: None)')

    process_parser.add_argument('--notch_width', type=float, default=None,
                        help='Notch filter width (default: None)')

    process_parser.add_argument('--raw_notch_freq', type=float, default=50,
                        help='Notch filter frequency (default: 50)')

    process_parser.add_argument('--raw_notch_width', type=float, default=2,
                        help='Notch filter width (default: 2)')

    process_parser.add_argument('--epochs_tmin', type=float, default=-0.9,
                        help='Start time for epochs (default: -0.8)')

    process_parser.add_argument('--epochs_tmax', type=float, default=0.8,
                        help='End time for epochs (default: 0.8)')

    process_parser.add_argument('--bad_channels_threshold', type=float, default=3,
                        help='Threshold (std) for removing bad channels with mne_faster (default: 3)')

    process_parser.add_argument('--bad_epochs_threshold', type=float, default=3,
                        help='Threshold (std) for removing bad epochs with mne_faster (default: 3)')

    process_parser.add_argument('--ica_method', type=str, default='fastica',
                        help='ICA method (default: fastica)')

    process_parser.add_argument('--blink_thresh', type=float, default=2.5,
                        help='Threshold for blink detection (default: 2.5)')

    process_parser.add_argument('--lat_eye_thresh', type=float, default=2.0,
                        help='Threshold for lateral eye movement detection (default: 2.0)')

    process_parser.add_argument('--noise_thresh', type=float, default=6.0,
                        help='Threshold for noise detection (default: 4.0)')

    process_parser.add_argument('--tms_muscle_thresh', type=float, default=2.0,
                        help='Threshold for TMS muscle artifact (default: 2.0)')

    process_parser.add_argument('--muscle_thresh', type=float, default=1.0,
                        help='Threshold for ongoing muscle contamination (default: 0.6)')

    process_parser.add_argument('--parafac_muscle_artifacts', action='store_true', default=False,
                        help='Enable muscle artifact cleaning (default: False)')

    process_parser.add_argument('--muscle_window_start', type=float, default=0.005,
                        help='Start time for muscle artifact window (default: 0.005)')

    process_parser.add_argument('--muscle_window_end', type=float, default=0.030,
                        help='End time for muscle artifact window (default: 0.030)')

    process_parser.add_argument('--threshold_factor', type=float, default=1.0,
                        help='Threshold factor for muscle artifact cleaning (default: 1.0)')

    process_parser.add_argument('--first_ica_manual', action='store_true', default=True,
                        help='Enable manual component selection for first ICA (default: True)')

    process_parser.add_argument('--second_ica_manual', action='store_true', default=True,
                        help='Enable manual component selection for second ICA (default: True)')

    process_parser.add_argument('--n_components', type=int, default=5,
                        help='Number of components for muscle artifact cleaning (default: 5)')

    process_parser.add_argument('--no_first_ica', action='store_true', default=False,
                        help='Disable first ICA (default: False)')

    process_parser.add_argument('--no_second_ica', action='store_true', default=False,
                        help='Disable seconds ICA ´ (default: False)')

    process_parser.add_argument('--second_ica_method', type=str, default='infomax',
                        help='Second ICA method that can be infomax or fastica (default: infomax)')

    process_parser.add_argument('--ica_topo', action='store_true', default=False,
                        help='Use topography-based automatic ICA component classification (default: False)')

    process_parser.add_argument('--topo_edge_threshold', type=float, default=0.15,
                                help='Distance threshold for edge detection in topography classifier (default: 0.15)')

    process_parser.add_argument('--topo_zscore_threshold', type=float, default=3.5,
                                help='Z-score threshold for focal point detection (default: 3.5)')

    process_parser.add_argument('--topo_peak_threshold', type=float, default=3,
                                help='Peak count threshold for artifact detection (default: 3)')

    process_parser.add_argument('--topo_focal_threshold', type=float, default=0.2,
                                help='Threshold for focal area detection (default: 0.2)')

    process_parser.add_argument('--apply_ssp', action='store_true',
                        help='Apply SSP (default: False)')

    process_parser.add_argument('--ssp_n_eeg', type=int, default=2,
                        help='Number of EEG components for SSP (default: 2)')

    process_parser.add_argument('--apply_csd', action='store_true',
                        help='Apply CSD transformation (default: True)')

    process_parser.add_argument('--lambda2', type=float, default=1e-3,
                        help='Lambda2 parameter for CSD transformation (default: 1e-5)')

    process_parser.add_argument('--stiffness', type=int, default=4,
                        help='Stiffness parameter for CSD transformation (default: 4)')

    process_parser.add_argument('--save_evoked', action='store_true',
                        help='Save evoked plot with TEPs (default: False)')

    process_parser.add_argument('--save_raw_data', action='store_true',
                    help='Save initial raw eeg as .fif (default: False)')

    process_parser.add_argument('--analyze_teps', action='store_true', default=True,
                        help='Find TEPs that normally exist (default: True)')

    process_parser.add_argument('--save_validation', action='store_true',
                        help='Save TEP validation summary (default: False)')

    process_parser.add_argument('--tep_analysis_type', type=str, default='gmfa',
                        choices=['gmfa', 'roi', 'both'],
                        help='Type of TEP analysis to perform (default: gmfa)')

    process_parser.add_argument('--tep_roi_channels', type=str, nargs='+',
                        default=['C3', 'C4'],
                        help='Channels to use for ROI analysis (default: C3 C4)')

    process_parser.add_argument('--peak_mode', type=str, default=None,
                        choices=['pos', 'neg', 'abs'],
                        help='Mode for MNE peak detection (default: abs)')

    process_parser.add_argument('--peak_windows', type=str, nargs='*',
                        help='Time windows for peak detection in format start,end (in ms). Example: --peak_windows 80,140 150,250')

    process_parser.add_argument('--no_channel_peaks', action='store_true', default=False,
                        help='Disable plotting of individual channel peaks using MNE get_peaks (default: False)')

    # Allow overriding the default component windows
    process_parser.add_argument('--manual_windows', action='store_true',
                        help='Use manual peak_windows to override default component windows (default: False)')

    process_parser.add_argument('--tep_method', type=str, default='largest',
                        choices=['largest', 'centre'],
                        help='Method for peak detection (default: largest)')

    process_parser.add_argument('--tep_samples', type=int, default=5,
                        help='Number of samples for peak detection (default: 5)')

    process_parser.add_argument('--baseline_start', type=int, default=-400,
                        help='Start time for baseline in ms (default: -400)')

    process_parser.add_argument('--baseline_end', type=int, default=-50,
                        help='End time for baseline in ms (default: -50)')

    process_parser.add_argument('--response_start', type=int, default=0,
                        help='Start of response window in ms (default: 0)')

    process_parser.add_argument('--response_end', type=int, default=299,
                        help='End of response window in ms (default: 299)')

    process_parser.add_argument('--amplitude_threshold', type=float, default=300.0,
                        help='Threshold for epoch rejection based on peak-to-peak amplitude in µV (default: 300.0)')

    process_parser.add_argument('--k', type=float, default=1.2,
                        help='PCIst parameter k (default: 1.2)')

    process_parser.add_argument('--min_snr', type=float, default=1.1,
                        help='PCIst parameter min_snr (default: 1.1)')

    process_parser.add_argument('--max_var', type=float, default=99.0,

                        help='PCIst parameter max_var (default: 99.0)')
    process_parser.add_argument('--embed', action='store_true',
                        help='PCIst parameter embed (default: False)')

    process_parser.add_argument('--n_steps', type=int, default=100,
                        help='PCIst parameter n_steps (default: 100)')

    process_parser.add_argument('--pre_window_start', type=int, default=-400,
                        help='Start of the pre-TMS window in ms (default: -400)')

    process_parser.add_argument('--pre_window_end', type=int, default=-50,
                        help='End of the pre-TMS window in ms (default: -50)')

    process_parser.add_argument('--post_window_start', type=int, default=0,
                        help='Start of the post-TMS window in ms (default: 0)')

    process_parser.add_argument('--post_window_end', type=int, default=300,
                        help='End of the post-TMS window in ms (default: 300)')

    process_parser.add_argument('--research', action='store_true',
                        help='Output summary statistics of measurements (default: False)')

    args = parser.parse_args()



    if args.command == 'process':

        pcists = process_subjects(args)
        print(f"PCIst values: {pcists}")

        process_parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()