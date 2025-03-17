import os
import platform

import subprocess
import time

class CleanupPersistence:
    def __init__(self):
        self.persistence_path = self.get_persistence_path()

    def get_persistence_path(self):
        system = platform.system()
        if system == "Windows":
            return os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
        elif system == "Darwin":  # macOS
            return os.path.expanduser('~/Library/LaunchAgents')
        elif system == "Linux":  # Ubuntu
            return os.path.expanduser('~/.config/autostart')
        else:
            raise NotImplementedError("Unsupported OS")

    def remove_persistence(self):
        system = platform.system()
        success = True

        # Define the persistence file based on OS
        if system == "Windows":
            startup_file = os.path.join(self.persistence_path, 'game.py')
        elif system == "Darwin":  # macOS
            startup_file = os.path.join(self.persistence_path, 'com.game.snake.plist')
        elif system == "Linux":  # Ubuntu
            startup_file = os.path.join(self.persistence_path, 'snakegame.desktop')

        # macOS: Unload the LaunchAgent before removing the file
        if system == "Darwin" and os.path.exists(startup_file):
            try:
                subprocess.run(["launchctl", "unload", startup_file], check=False)
                print(f"Unloaded LaunchAgent: {startup_file}")
            except Exception as e:
                print(f"Failed to unload LaunchAgent: {e}")
                success = False

        # Remove the persistence file
        if os.path.exists(startup_file):
            try:
                os.remove(startup_file)
                print(f"Removed persistence file: {startup_file}")
            except Exception as e:
                print(f"Failed to remove {startup_file}: {e}")
                success = False
        else:
            print(f"No persistence file found at {startup_file}")

        # Terminate all game.py processes
        if system in ["Darwin", "Linux"]:
            try:
                # Forcefully kill all processes matching 'game.py'
                subprocess.run(["pkill", "-9", "-f", "game.py"], check=False)
                print("Forcefully terminated all game.py processes")
                # Wait briefly and check again to ensure they're gone
                time.sleep(1)
                result = subprocess.run(["pgrep", "-f", "game.py"], capture_output=True, text=True)
                if result.stdout.strip():
                    print("Warning: Some game.py processes may still be running")
                    success = False
                else:
                    print("Confirmed: No game.py processes remain")
            except Exception as e:
                print(f"Failed to terminate game.py processes: {e}")
                success = False
        elif system == "Windows":
            try:
                # Kill all Python processes running game.py
                subprocess.run(["taskkill", "/F", "/IM", "python.exe", "/T"], check=False)
                print("Terminated Python processes (may affect other Python apps)")
                time.sleep(1)
                # Check if any python.exe processes are still running game.py (less precise)
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq python.exe"], capture_output=True, text=True)
                if "python.exe" in result.stdout:
                    print("Warning: Some Python processes may still be running")
                    success = False
                else:
                    print("Confirmed: No Python processes remain")
            except Exception as e:
                print(f"Failed to terminate processes: {e}")
                success = False

        return success

    def run(self):
        print("Starting cleanup of persistence established by game.py...")
        if self.remove_persistence():
            print("Cleanup completed successfully! Game should not restart.")
        else:
            print("Cleanup completed with some errors. Check for lingering processes.")

if __name__ == "__main__":
    cleaner = CleanupPersistence()
    cleaner.run()