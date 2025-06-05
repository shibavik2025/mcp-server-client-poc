"""script to setup sonarqube docker container in local"""

import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path

SLEEP_TIME = 15
PROJECT_DIR = os.getcwd()
PROJECT_KEY = PROJECT_DIR.split("/")[-1]
SONAR_SCANNER_OPTS = f"""-Dproject.settings=/usr/src/sonar-project.properties
-Dsonar.projectKey={PROJECT_KEY} -Dsonar.projectName={PROJECT_KEY} -Dsonar.qualitygate.wait=true"""
SONAR_DOCKER_HOST = "http://0.0.0.0:9000"


def sonar_scan() -> None:
    """function to run shell commands which will run the sonar scan"""
    try:
        # start sonar scan docker container
        print("Starting sonarqube container")
        subprocess.run(
            ["docker", "start", "sonarqube"],
            check=True,
        )
        print("Sonarqube server is starting at http://0.0.0.0:9000")

        # run pytest
        print("Cleanup unit test coverage")
        subprocess.run(
            ["rm", "-rf", ".coverage", "coverage.xml", "htmlcov/"],
            check=True,
        )

        print("Running unit test coverage")
        subprocess.run(
            ["uv", "run", "pytest"],
            check=True,
        )

        # get sonar token from user directory and run docker scan on code
        user_home = str(Path.home())
        sonarqube_token_file = user_home + f"/.sonarqube-token-{PROJECT_KEY}"
        sonar_token = None
        if os.path.isfile(sonarqube_token_file):
            with open(sonarqube_token_file, "r", encoding="utf-8") as f:
                sonar_token = f.read()
                sonar_token = sonar_token.strip()
            print(
                f"Sleeping for {SLEEP_TIME} seconds as Sonarqube server is starting up..."
            )
            time.sleep(SLEEP_TIME)
            cmd_to_run = [
                "docker",
                "run",
                "--rm",
                "--user=1000:1000",
                "--network=host",
                "-e",
                f"SONAR_SCANNER_OPTS={SONAR_SCANNER_OPTS}",
                "-e",
                f"SONAR_TOKEN={sonar_token}",
                "-e",
                f"SONAR_HOST_URL={SONAR_DOCKER_HOST}",
                "-v",
                f"{PROJECT_DIR}:/usr/src",
                "sonarsource/sonar-scanner-cli",
            ]

            print(cmd_to_run)
            # Run sonar scanner
            print("Starting sonarqube scan")
            subprocess.run(cmd_to_run, check=True)
            sys.exit(0)
        else:
            error_msg = """
            Error: Sonarqube token not found!
            >>> Please run `uv run export-sonar-token <token>`
            to set the sonarqube token.
            Existing!
            """
            print(textwrap.dedent(error_msg))
            sys.exit(1)
    except subprocess.CalledProcessError as exc:
        print(f"{exc}")
        sonarqube_docs_url = "https://docs.sonarsource.com/sonarqube/latest/user-guide/user-account/generating-and-using-tokens/"  # pylint: disable=line-too-long
        msg = f"""
        >>>Check if Sonarqube server is running on http://0.0.0.0:9000.
        >>>To start Sonarqube server in local dev run `uv run sonar-setup`
        To generate a sonarqube token follow the instructions check the Sonarqube documentation here - {sonarqube_docs_url}
        Once the sonarqube token is generated run
        >>>`uv run export-sonar-token <sonar token>` to set the sonarqube token in the user directory.
        """  # pylint: disable=line-too-long
        print(textwrap.dedent(msg))
        sys.exit(1)
