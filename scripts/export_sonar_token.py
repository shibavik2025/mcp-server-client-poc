"""script to export sonarqube token and set it to a file in user's home directory"""

import sys
import os

from pathlib import Path


def export_sonar_token() -> None:
    """function to get the sonar token as cli args and write the token in a file in user's home"""
    if len(sys.argv) > 1 and sys.argv[1] is not None:
        sonar_token = sys.argv[1]
        project_name = os.getcwd().split("/")[-1]
        user_home = str(Path.home())
        sonarqube_token_file = user_home + f"/.sonarqube-token-{project_name}"
        if os.path.isfile(sonarqube_token_file):
            print(
                f"{sonarqube_token_file} file already exists. Overwriting sonarqube token"
            )
        with open(sonarqube_token_file, "w", encoding="utf-8") as file:
            file.write(sonar_token)
    else:
        print("Error: No Sonarqube token passed to command line argument")
