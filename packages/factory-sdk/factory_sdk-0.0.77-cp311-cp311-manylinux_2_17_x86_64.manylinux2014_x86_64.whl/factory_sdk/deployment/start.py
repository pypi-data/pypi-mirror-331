import os
import pty
import subprocess
import sys
import json
import shlex

def run_with_live_output(command):
    """Helper function to run command with live output using a PTY"""
    master_fd, slave_fd = pty.openpty()
    
    process = subprocess.Popen(
        command,
        stdout=slave_fd,
        stderr=slave_fd,
        text=True  # Using text mode for convenience
    )
    
    os.close(slave_fd)
    
    try:
        while True:
            output = os.read(master_fd, 1024 * 1024)
            if not output:
                break

            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(output)
            else:
                sys.stdout.write(output)
            sys.stdout.flush()
    except OSError:
        pass  # The PTY may close when the process ends
    
    process.wait()
    return process.returncode



def start_deployment(
        deployment_dir,
        deployment_args,
        model_path,
        adapter_paths,
        recipe_paths,
        client_params,
        deployment_name,
        deployment_structure
):
    """
    Start deployment with proper output handling.
    
    If an IPython environment is detected (e.g. in Colab), use its system
    command to execute the command string. Otherwise, use a PTY-based approach
    for live output.
    """
    # Construct the path to the run.py file (adjust if necessary)
    run_file_path = os.path.join(os.path.dirname(__file__), "run.py")

    from factory_sdk.fast.args import encrypt_param

    # Build the base command as a list (for PTY/subprocess execution)
    command_list = [
        "python",
        run_file_path,
        "--deployment_dir", deployment_dir,
        "--model_path", model_path,
        "--adapter_paths", json.dumps(adapter_paths),
        "--client_params", encrypt_param(json.dumps(client_params)),
        "--deployment_name", deployment_name,
        "--deployment_args", deployment_args.model_dump_json(),
        "--recipe_paths", json.dumps(recipe_paths),
        "--trust-remote-code",
        "--deployment_structure", json.dumps(deployment_structure)
    ]
    
    """ # Append extra arguments from deployment_args
    for key, value in deployment_args.model_dump().items():
        # Replace underscores with hyphens in the key.
        key = key.replace("_", "-")
        if value is not None:
            if isinstance(value, bool):
                # Only include boolean flags if they are True.
                if not value:
                    continue
                command_list.append("--" + key)
            else:
                command_list.extend(["--" + key, str(value)]) """
    
    # Build the command string for an IPython environment.
    # Use shlex.quote to properly handle spaces and special characters.
    command_str = " ".join(shlex.quote(arg) for arg in command_list)
    
    # Check if we're running in an IPython environment.
    try:
        from IPython import get_ipython
        ipython = get_ipython()
    except ImportError:
        ipython = None
        
    if ipython is not None:
        print("Detected IPython/Colab environment. Running command using Notebook Environment:")
        ipython.system(command_str)
        # ipython.system doesn't return an exit code, so return 0 by default.
        return 0
    else:
        # Use the PTY-based execution for live output.
        return run_with_live_output(command_list)

# Example usage:
if __name__ == "__main__":
    # Dummy deployment_args for demonstration; replace with your actual object.
    class DummyDeploymentArgs:
        def model_dump(self):
            return {
                "learning_rate": 0.001,
                "batch_size": 32,
                "use_gpu": True,
                "verbose": False,
            }
    
    exit_code = start_deployment(
        deployment_dir="/path/to/deployment_dir",
        deployment_args=DummyDeploymentArgs(),
        model_path="/path/to/model",
        adapter_paths=["/path/to/adapter1", "/path/to/adapter2"],
        recipe_path="/path/to/recipe",  # Not used in command as per your original code.
        client_params={"key": "value"},
        deployment_name="my_deployment"
    )
    print("Deployment process exited with code:", exit_code)
