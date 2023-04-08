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

    dirs = ["usr/bin", "usr/local/bin", "lib/x86_64-linux-gnu", "lib64"]


    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)

        for d in dirs:
            os.makedirs(d)
    
        shutil.copy("/usr/bin/unshare", "usr/bin/")
        shutil.copy("/usr/local/bin/docker-explorer", "usr/local/bin/")
        shutil.copy("/lib/x86_64-linux-gnu/libc.so.6", "lib/x86_64-linux-gnu/")
        shutil.copy("/lib64/ld-linux-x86-64.so.2", "lib64/")
        os.chroot(".")
        completed_process = subprocess.run(["/usr/bin/unshare", "--fork", "--pid", command, *args], capture_output=True)
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end='')
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end='')

    sys.exit(completed_process.returncode)


if __name__ == "__main__":
    main()
