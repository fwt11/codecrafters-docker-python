import subprocess
import sys
import os
import tempfile
import shutil


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    #print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #

    command = sys.argv[3]
    args = sys.argv[4:]
    



    with tempfile.TemporaryDirectory() as temp_dir:
        print(temp_dir)
        os.chdir(temp_dir)
        os.makedirs("usr/bin")
        os.makedirs("usr/local/bin")
        shutil.copy("/usr/bin/ls", "usr/bin/")
        shutil.copy("/usr/local/bin/docker-explorer", "usr/local/bin/")
        os.chroot(".")
        completed_process = subprocess.run([command, *args], capture_output=True)
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end='')
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end='')


    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
