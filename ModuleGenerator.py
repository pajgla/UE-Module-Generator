import argparse
import json
import os
import packaging.version
import re
import subprocess
import sys
import winreg

#Colors for console output. No need for library
class bcolors:
    HEADER = '\033[95m'
    GREEN = '\033[92m'
    FAIL = '\033[91m'
    END = '\033[0m'
    WARNING   = '\033[93m'

# --- Globals ---
current_dir = os.getcwd()
module_root_dir = None
module_name = None
project_file = None

# --- Defaults ---
    
class defaults:
    #Add or remove default dependencies for new modules. IMPORTANT! This string must not have compile errors. Make sure each dependency is inside double qoutes ("), and
    #each dependency is separated with comma (,). Do not place comma after the last entry
    module_dependencies = ["Core", "CoreUObject", "Engine"]
    module_type = "Runtime"
    module_loading_phase = "Default"

    #Default content of module Build.cs file
    build_file_content = """
using UnrealBuildTool;

public class {0} : ModuleRules
{{
    public {0}(ReadOnlyTargetRules Target) : base(Target)
    {{

        PrivateDependencyModuleNames.AddRange(new string[] {1} );

    }}

}}
"""
    
    #Default content of module .cpp file
    cpp_file_content = """
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, {0});
"""

# ---- Method definitions below ----
def format_build_file():
    """Formats [defaults.build_file_content] to correct C# syntax."""
    
    parsed_output = r"{"
    for id, dep in enumerate(defaults.module_dependencies):
        parsed_output += " " # add space
        parsed_output += '"' + dep + '"'
        if id != len(defaults.module_dependencies) - 1:
            parsed_output += ","

    parsed_output += " }"

    defaults.build_file_content = defaults.build_file_content.format(module_name, parsed_output)


def format_cpp_file():
    """Formats [defaults.cpp_file_content] to correct C++ syntax."""

    defaults.cpp_file_content = defaults.cpp_file_content.format(module_name)


def bprint(msg : str, code : str):
    """Prints string to console with colors"""

    print(code + msg + bcolors.END)


def is_valid_ue_project() -> bool:
    """Checks if the current working directory is a valid Unreal Engine project root
    
    Returns:
        bool: True if current directory is valid UE project root
    """

    #Folders and files that are required for current directory to be considered as valid UE project root
    required_folders = ["Source"]
    required_file_extensions = [".uproject"]

    #Check folders
    folder_check_counter = 0
    for item in required_folders:
        if os.path.exists(item):
            folder_check_counter += 1

    if folder_check_counter < len(required_folders):
        return False
    
    #Check files
    file_check_counter = 0
    for os_file in os.listdir():
        for req_extension in required_file_extensions:
            if os_file.endswith(req_extension):
                file_check_counter += 1

    return file_check_counter == len(required_file_extensions)


def create_module_files():
    """Creates module files: Module root folder named [module_name], Public and Private folders, [module_name].Build.cs file and [module_name]Module.cpp file.
    Note that [module_name]Module.h file is not being creates, as it is not essential.
    
    Args:
        module_name (str): The name of the module to be created.

    Raises:
        OSError: If an error occurs during directory or file creation.
    """
    
    global module_root_dir

    #Source folder path
    source_root = "Source/"
    try:
        #Create module root folder
        module_root_dir = source_root + module_name + "/"
        os.mkdir(module_root_dir)

        #Create Public and Private folders
        os.mkdir(module_root_dir + "Public")
        os.mkdir(module_root_dir + "Private")

        create_module_build_file()
        create_module_cpp_file()
        bprint("Module files successfully created", bcolors.GREEN)
        
    except OSError as error:
        bprint(f"Error: {error}", bcolors.FAIL)
        exit()


def create_module_build_file():
    """Creates [module_name].Build.cs file inside [module_root_dir] folder"""

    build_filename = module_name + ".Build.cs"

    with open(module_root_dir + build_filename, 'w') as file:
        file.write(defaults.build_file_content)
        bprint("Module build file created successfully", bcolors.GREEN)


def create_module_cpp_file():
    """Creates [module_name]Module.cpp file inside [module_root_dir]\\Private folder"""

    #UE Standard for module cpp files is [module_name]Module.cpp (for example, GameplayModule.cpp)
    fileName = module_name + "Module.cpp"

    with open(module_root_dir + "Private/" + fileName, 'w') as file:
        file.write(defaults.cpp_file_content)
        bprint("Module cpp file created successfully", bcolors.GREEN)


def add_module_to_uproject():
    """Adds module entry to .uproject file. .uproject file can be opened with any text editor, and its content is JSON"""

    global project_file

    with open(project_file, "r") as file:
        data = json.load(file)

    new_module_entry = {
        "Name": module_name,
        "Type": defaults.module_type, #'Runtime'
        "LoadingPhase": defaults.module_loading_phase #'Default'
    }

    data["Modules"].append(new_module_entry)

    with open(project_file, 'w') as file:
        json.dump(data, file, indent=4)

    bprint("JSON Module entry succesffully added", bcolors.GREEN)


def find_project_file() -> str:
    """Searches for .uproject file
    
    Returns:
        str: The full path to the .uproject file in current directory, or None if not found
    """

    for os_file in os.listdir():
        if os_file.endswith(".uproject"):
            return os_file

    if not project_file:
        bprint("Couldn't find .uproject file in current directory", bcolors.FAIL)

    return None


def generate_project():
    """Calls UnrealBuildTool.exe to generate project file for default IDE"""

    global project_file

    ue_install_path = get_latest_ue_install_path()
    if not ue_install_path:
        bprint("Couldn't retrieve UE installation path. Project Generation aborted", bcolors.FAIL)
        return
    
    path_to_build_tool = ue_install_path + r"\Engine\Binaries\DotNET\UnrealBuildTool\UnrealBuildTool.exe"
    full_project_path = os.path.abspath(project_file)

    command = [
        path_to_build_tool,
        "-projectfiles", full_project_path,
        "-game",
        "-progress"
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    #Outputs each line from process until it's finished
    while True:
        output_line = process.stdout.readline()
        if not output_line:
            break
        print(output_line.decode('utf-8').strip())

    process.wait()
    
    if process.returncode != 0:
        bprint(('-' * 20) + " ERROR " + ('-' * 20), bcolors.FAIL)
        error = process.stderr.read()
        print(error.decode('utf-8'))
    else:
        bprint('-' * 20 + " Project files generated " + '-' * 20, bcolors.GREEN)


def get_latest_ue_install_path() -> str:
    """Finds all installed UE editors and returns installation path of the latest one
    
    Returns:
        str: installation path of latest UE Editor
    """
    base_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\EpicGames\\Unreal Engine")
    latest_version = None
    latest_version_path = None

    for i in range(0, winreg.QueryInfoKey(base_key)[0]):
        try:
            subkey_name = winreg.EnumKey(base_key, i)
            subkey = winreg.OpenKey(base_key, subkey_name)
            install_path = winreg.QueryValueEx(subkey, "InstalledDirectory")[0]
            version = packaging.version.parse(subkey_name)

            if latest_version is None or version > latest_version:
                latest_version = version
                latest_version_path = install_path

        except (WindowsError, ValueError):
            bprint(WindowsError, bcolors.FAIL)
            continue
    
    return latest_version_path


def create_module():
    """Calls function in order to create a module"""

    format_build_file()
    format_cpp_file()
    create_module_files()
    add_module_to_uproject()



def main_without_args() -> int:
    """Alternative main function. This one is called if no console arguments are provided by the user. Asks for line input in a while loop.
    
    Returns:
        int: 0 if everything was okay, 1 if there was an error
    """

    global project_file
    global module_name

    quit_strings = {"quit", "q", "exit"}
    generate_strings = {"generate", "g", "gen"}

    while True:
        user_input = input("Enter module name (letters only), 'gen' to generate solution or type 'quit' to exit: ")
        user_input_lower = user_input.lower()

        if user_input_lower in quit_strings:
            break
        elif user_input_lower in generate_strings:
            generate_project()
            continue

        #Validate name
        if not re.match("^[a-zA-Z]+$", user_input):
            bprint("Invalid module name. Please use letters only.", bcolors.WARNING)
        else:
            module_name = user_input
            create_module()

    return 0

def set_defaults_from_args(args):
    """Parses command line arguments and sets default values for program"""

    if args.type:
        defaults.module_type = args.type
    if args.phase:
        defaults.module_loading_phase = args.phase
    if args.dependencies:
        defaults.module_dependencies = args.dependencies


# ---- main function ----

def main():
    global module_name
    global project_file

    if not is_valid_ue_project():
        print(f"Error: {current_dir} is not a valid Unreal Engine project root.", bcolors.FAIL)
        #Wait for user input
        input("Press any key to exit...")
        return 1


    program_name = "Module Generator"
    program_description = "Creates a new UE Module and all its corresponding files (build.cs and module.cpp) and adds new module entry in .uproject file. You can also generate solution files directly from here."
    program_epilog = "Remember to always generate solution files after adding or modifying modules."
    parser = argparse.ArgumentParser(prog=program_name, description=program_description, epilog=program_epilog)
    parser.add_argument("module_name", help="Name of the module to create. Use only letters without spaces. Optional if you use -g", type=str, nargs='?', default=None)
    parser.add_argument("-t", "--type", help=f"Choose module type. Default is '{defaults.module_type}'.", nargs="?", default=defaults.module_type)
    parser.add_argument("-p", "--phase", help=f"Module loading phase. Default is '{defaults.module_loading_phase}'.", nargs="?", default=defaults.module_loading_phase)
    parser.add_argument("-d", "--dependencies", help="Dependencies to include in this module.", default=defaults.module_dependencies, nargs='*')
    parser.add_argument('-g', "--generate", help="Generates solution files using UnrealBuildTool.exe. If module_name is provided, the program will start generating solution files after creating a module.", action="store_true")

    args = parser.parse_args()
    project_file = find_project_file()

    if args.module_name:
        module_name = args.module_name
        if not re.match("^[a-zA-Z]+$", module_name):
            bprint("Invalid module name. Please use letters only without spaces.", bcolors.FAIL)
            return 1
        
        if not is_valid_ue_project():
            bprint("Program is not inside valid UE project root folder.", bcolors.FAIL)
            return 1

        set_defaults_from_args(args)
        
        create_module()


    if args.generate:
        generate_project()

    #If module name and -g arguments are both None, start alternative main function
    if not args.module_name and not args.generate:
        main_without_args()

    return 0

#Call main function

if __name__ == '__main__':
    sys.exit(main())