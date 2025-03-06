import sys
import pathlib
import os
import xml.etree.ElementTree as ET


def get_wwise_datadir() -> pathlib.Path:
    """
    Returns a parent directory path
    where persistent application data can be stored.

    # linux: ~/.local/share
    # macOS: ~/Library/Application Support
    # windows: C:/Users/<USER>/AppData/Roaming
    """

    home = pathlib.Path.home()

    if sys.platform == "win32":
        return home / "AppData/Roaming/Audiokinetic/Wwise"
    elif sys.platform == "linux":
        return home / ".local/share/Audiokinetic/Wwise"
    elif sys.platform == "darwin":
        return home / "Library/Application Support/Audiokinetic/Wwise"
    else:
        return None


def get_wwise_usersetting(settingName=None, DirectoriesToCheck=[]):
    if not settingName:
        return None
    if not DirectoriesToCheck:
        DirectoriesToCheck.append(get_wwise_datadir())

    for Dir in DirectoriesToCheck:
        for file in find_wsettings_files_in_dir(Dir):
            result = parse_setting_file_for_value(settingName, file)
            if result:
                return result
    return None


def parse_setting_file_for_value(settingName=None, settingFile=None):
    if not settingName or not settingFile:
        return None
    if not os.path.exists(settingFile):
        return None
    tree = ET.parse(settingFile)
    root = tree.getroot()
    matches = root.findall(".//Property[@Name='{0}']".format(settingName))
    for match in matches:
        # print(match.attrib)
        return match.attrib
    else:
        matches = root.findall(".//{0}".format(settingName))
        for match in matches:
            # print(match.attrib)
            return match.attrib
        return None


def find_wsettings_files_in_dir(DirectoryToSearch=None):
    results = []
    if not os.path.isdir(DirectoryToSearch):
        return results
    for f in os.listdir(DirectoryToSearch):
        if f.endswith('.wsettings'):
            filepath = os.path.join(DirectoryToSearch, f)
            results.append(filepath)
    return results


def get_wamp_port():
    attrib = get_wwise_usersetting("Waapi\\WampPort", [get_wwise_datadir()])
    if not attrib:
        return None
    return attrib["Value"]


