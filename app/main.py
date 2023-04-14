import subprocess
import sys
import os
import tempfile
import shutil
from ctypes import *
from urllib import request
from urllib.error import HTTPError
import json
from pprint import pprint
import tarfile

CLONE_NEWPID = 0x20000000




def get_manifest(name, reference):
    url = f'https://registry.hub.docker.com/v2/{name}/manifests/{reference}'
    try:
        r = request.urlopen(url)
        j = json.loads(r.read())
        return j
    except HTTPError as http_error:
        if http_error.reason == 'Unauthorized': 
            req = request.Request(url)
            token = get_token(name, "pull")
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Accept", "application/vnd.oci.image.index.v1+json")
            r = request.urlopen(req)
            j = json.loads(r.read())
            return j
        else:
            print(f"HTTPError: {http_error}")
    except Exception as e:
        print(f"Exception: {e}")

    return j


def pull_layer(name, digest):
    filename = digest.split(":")[1] + ".tar"
    url = f'https://registry.hub.docker.com/v2/{name}/blobs/{digest}'
    try:
        r = request.urlopen(url)
        if r.getcode() == 307:
            url = r.getheader('Location')
            r = request.urlopen(url)
            with open(filename, 'bw') as f:
                f.write(r.read())
            tar = tarfile.open(filename)
            os.remove(filename)
            tar.extractall()
    except HTTPError as http_error:
        if http_error.reason == 'Unauthorized': 
            req = request.Request(url)
            token = get_token(name, "pull")
            req.add_header("Authorization", f"Bearer {token}")
            r = request.urlopen(req)
            with open(filename, 'bw') as f:
                f.write(r.read())
            
            tar = tarfile.open(filename)
            tar.extractall()
            os.remove(filename)
    except Exception as e:
        print(e)



def get_token(name, action):

    name = name.replace("/", "%2F")
    #r = request.urlopen(f"https://auth.docker.io/token?scope=repository%3A{name}%3A{action}&service=registry.docker.io")
    r = request.urlopen(f"https://auth.docker.io/token?scope=repository:{name}:{action}&service=registry.docker.io")
    j = json.loads(r.read())
    return j['token']

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    #print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    #
    image = sys.argv[2]
    try:
        image_name, image_ref = image.split(":")
    except:
        image_name, image_ref = image, "latest"
        
    image_name = f"library/{image_name}"

    command = sys.argv[3]
    args = sys.argv[4:]

    libc = CDLL("libc.so.6")

    dirs = ["usr/bin", "usr/local/bin", "lib/x86_64-linux-gnu", "lib64"]

    r = libc.unshare(CLONE_NEWPID)

    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        for d in dirs:
            os.makedirs(d)
    
        shutil.copy("/usr/local/bin/docker-explorer", "usr/local/bin/")

        manifests = get_manifest(image_name, image_ref)
        if manifests["schemaVersion"] == 2:
            layers = manifests["manifests"]
            for layer in layers:
                digest = layer["digest"]
                pull_layer(image_name, digest)
        else:
            layers = manifests["fsLayers"]
            for layer in layers:
                digest = layer["blobSum"]
                pull_layer(image_name, digest)



        os.chroot(".")
        completed_process = subprocess.run([command, *args], capture_output=True)
        print(completed_process.stdout.decode("utf-8"), file=sys.stdout, end='')
        print(completed_process.stderr.decode("utf-8"), file=sys.stderr, end='')

    sys.exit(completed_process.returncode)




if __name__ == "__main__":
    main()


