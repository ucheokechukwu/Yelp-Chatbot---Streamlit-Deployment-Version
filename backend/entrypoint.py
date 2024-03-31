# import subprocess
# launch_command = "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
# process = subprocess.Popen(launch_command.split(), stdout=subprocess.PIPE)

import subprocess
import threading

def launch_backend():
    launch_command = "uvicorn backend.main:app --host 0.0.0.0 --port 8000"
    process = subprocess.Popen(
        launch_command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    # Print the output of the subprocess
    for line in process.stdout:
        print(line, end='')

    # Wait for the subprocess to complete
    process.wait()

# Start the backend in a separate thread
backend_thread = threading.Thread(target=launch_backend)
backend_thread.start()