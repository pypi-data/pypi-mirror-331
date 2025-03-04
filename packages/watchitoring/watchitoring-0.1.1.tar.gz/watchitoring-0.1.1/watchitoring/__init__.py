import platform
from .macosmonitoring import MacMonitoring
if platform.system().lower() == "windows":
    from .windowsmonitoring import WindowsMonitoring
from .sts import initialize_system_monitoring
from .kl import InputMonitor

__all__ = ["MacMonitoring", "WindowsMonitoring", "initialize_system_monitoring", "InputMonitor"]