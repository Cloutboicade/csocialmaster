import os
import subprocess
import time


def pip_install(package):
    sh = f'''pip install {package}'''
    os.system(sh)


def get_reqs():
    file = open('requirements.txt', 'r')
    lines = file.read().splitlines()
    return lines


def install_packages():
    print("Attempting to install Python libraries...")
    ps = get_reqs()
    for p in ps:
        pip_install(p)


def check_ffmpeg():
    print("Checking ffmpeg...")
    try:
        subprocess.run("ffmpeg")
    except Exception as e:
        write_error(f"ffmpeg not installed correctly {e}")


def make_setup_done_file():
    dirr = os.getcwd() + os.sep + os.pardir
    file_name = "dont_delete.txt"
    file_path = os.path.join(dirr, file_name)
    with open(file_path, "w") as file:
        file.write("first_time_setup_complete")
        file.close()


def write_error(error):
    error = f"ERROR: {error}"#
    print(error)
    with open("error.txt", "w") as file:
        file.write(error)
        file.close()
    quit()


if __name__ == "__main__":
    check_ffmpeg()
    try:
        install_packages()
    except Exception as e:
        write_error(e)
    try:
        make_setup_done_file()
    except Exception as e:
        write_error(e)
    print("Successfully setup SocialMaster, please add your spreadsheet key to the file and read readme.txt if you haven't.")
    print("You may close this.")
    time.sleep(30)
