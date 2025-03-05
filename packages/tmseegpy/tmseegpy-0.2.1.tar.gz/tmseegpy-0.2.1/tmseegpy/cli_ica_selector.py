import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import threading
import queue
import matplotlib.pyplot as plt
import mne
from tmseegpy.ica_selector_gui.ica_selector import ICAComponentSelector, ICAComponentSelectorContinuous

class CLIICASelector:
    def __init__(self, is_gui_mode=False):
        self.is_gui_mode = is_gui_mode
        self.qt_app = None
        self.reset_state()

    def reset_state(self):
        """Reset the selector's state for new use"""
        self.result_queue = queue.Queue()
        self.selection_complete = threading.Event()
        self._cleanup_called = False
        self._window = None

    def select_components(self, ica_instance, inst, component_scores=None):
        """Run ICA selection ensuring Qt app exists"""
        selector = None
        try:
            # Reset state before new selection
            self.reset_state()

            # Initialize Qt application if needed
            self.qt_app = QApplication.instance()
            print("CLIICASelector: Starting component selection")
            print(f"Qt application instance: {self.qt_app}")
            if self.qt_app is None and not self.is_gui_mode:
                self.qt_app = QApplication(sys.argv)

            # Create appropriate selector based on data type
            print("Creating selector...")
            if isinstance(inst, mne.io.Raw):
                selector = ICAComponentSelectorContinuous(None)
            else:
                selector = ICAComponentSelector(None)
            print("Selector created")

            # Callback for when selection is complete
            def selection_callback(components):
                self.result_queue.put(components)
                self.selection_complete.set()
                if not self.is_gui_mode and self.qt_app and self.qt_app.activeWindow():
                    self.qt_app.quit()

            # Show selector window
            print("Calling selector.select_components...")
            selector.select_components(
                ica_instance=ica_instance,
                raw=inst if isinstance(inst, mne.io.Raw) else None,
                epochs=inst if isinstance(inst, mne.Epochs) else None,
                title="Select ICA Components",
                callback=selection_callback,
                component_scores=component_scores
            )
            print("select_components called")

            if not self.is_gui_mode:
                # Create a timer to check if window is shown
                def check_window():
                    if selector._window and selector._window.isVisible():
                        timer.stop()
                    else:
                        print("Waiting for window to appear...")

                timer = QTimer()
                timer.timeout.connect(check_window)
                timer.start(100)

                # Start event loop
                self.qt_app.exec()

            # Wait for selection to complete with timeout
            if not self.selection_complete.wait(timeout=300):  # 5 minute timeout
                print("Warning: Selection timed out")
                return []

            # Get selected components
            try:
                selected_components = self.result_queue.get_nowait()
                print(f"Selected components: {selected_components}")
                return selected_components
            except queue.Empty:
                print("No components selected (queue empty)")
                return []

        except Exception as e:
            print(f"Error in select_components: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

        finally:
            # Ensure cleanup
            if not self.is_gui_mode:
                try:
                    plt.close('all')
                    if selector and hasattr(selector, '_window') and selector._window:
                        selector._window.close()
                    if self.qt_app and self.qt_app.activeWindow():
                        self.qt_app.quit()
                except Exception as e:
                    print(f"Error during cleanup: {str(e)}")

def get_cli_ica_callback(is_gui_mode=False):
    """Create a callback function for ICA selection"""
    selector = CLIICASelector(is_gui_mode)
    return selector.select_components