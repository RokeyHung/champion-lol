import os

# Read the configuration file
config_file = 'build_config.txt'

# Read the lines from the configuration file
with open(config_file, 'r') as file:
    lines = file.readlines()

# Filter out lines that are not comments
config_lines = [line.strip() for line in lines if line.strip() and not line.startswith('#')]

# Build the PyInstaller command from the config parameters
command = "pyinstaller --onefile " + " ".join(config_lines) + " main.py"

# Print the command to check
print("Generated PyInstaller Command:")
print(command)

# You can run this command from the Python script or execute it in the terminal
os.system(command)
