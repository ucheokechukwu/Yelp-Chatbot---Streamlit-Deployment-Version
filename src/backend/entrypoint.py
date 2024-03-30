import subprocess
launch_command = "uvicorn src.backend.main:app --host 0.0.0.0 --port 8000"
process = subprocess.Popen(launch_command.split(), stdout=subprocess.PIPE)