import configparser
import os

# Functions:

def fetch_profile_path():
    """
    Fetch the profile path.
    Source: https://stackoverflow.com/a/71111512
    """
    # Get the Mozilla folder set in %APPDATA%
    mozilla_profile = os.path.join(os.getenv('APPDATA'), r'Mozilla\Firefox')

    # Read the profiles.ini file in to determine which folder to use
    mozilla_profile_ini = os.path.join(mozilla_profile, r'profiles.ini')
    profile = configparser.ConfigParser()
    profile.read(mozilla_profile_ini)

    # Normalise the path
    for section in profile.sections():
        if section.startswith("Install"):
            # Get the current default profile
            path = os.path.normpath(os.path.join(mozilla_profile, profile.get(section, "Default")))
            break

    return path