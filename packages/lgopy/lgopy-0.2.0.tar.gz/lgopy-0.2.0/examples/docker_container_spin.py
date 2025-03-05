import docker
from docker.errors import DockerException


def is_docker_running():
    try:
        # Initialize Docker client
        client = docker.from_env()
        # Perform a simple command to check if Docker is running
        client.ping()

        print("Docker is running.")
        return True
    except DockerException as e:
        print(f"Docker is not running: {e}")
        return False

# Initialize Docker client
# check if the Docker daemon is running
assert is_docker_running(), "Docker is not running."
client = docker.from_env()
# Build the Docker image from the current directory
image = client.images.pull("r-base:latest")
command = "echo Hello from Docker API!"
output = client.containers.run(
            image=image.id,  # Use a lightweight image like Alpine Linux
            command="echo Hello from Docker API!",  # The command to run
            volumes={  # Mount the current directory into the container
                "/": {"bind": "/app", "mode": "rw"}
            },
            remove=True,  # Automatically remove the container after execution
            stdout=True,
            stderr=True
        )
# Print and return the output
print(output.decode("utf-8"))

