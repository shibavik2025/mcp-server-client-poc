"""script to setup sonarqube docker container in local"""

import subprocess


def sonar_setup() -> None:
    """function to run shell command which will run the docker container"""
    subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            "sonarqube",
            "-p",
            "9000:9000",
            "-p",
            "9092:9092",
            "sonarqube:10.4.0-community",
        ],
        check=True,
    )
