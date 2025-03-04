import sys
import subprocess
from signal import signal, SIGINT, SIGTERM
import os
import pathlib



def get_version():
    # the directory containing this file
    HERE = pathlib.Path(__file__).parent
    # launch path
    # print("launch path = " + str(HERE))
    # the version in the version file
    if "audiocat" in str(sys.argv):
        __version__ =  (HERE / "version").read_text()[:-1]
    else:
        __version__ =  (HERE / "audiocat_clark/version").read_text()[:-1]
    return __version__

def get_package_installation_path(package_name):
    try:
        result = subprocess.run(['pip', 'show', '-f', package_name], capture_output=True, text=True)
        output = result.stdout.strip()
        if output:
            lines = output.split('\n')
            for line in lines:
                if line.startswith('Location:'):
                    return line.split(':', 1)[1].strip()
        return None
    except FileNotFoundError:
        return None
        
# python wrapper for audiocat shell script
# in order to use PyPi
##########################################
def main():   
    # change path to installation directory
    installation_path = get_package_installation_path("audiocat-clark")
    if installation_path is not None:
        installation_path = installation_path+"/audiocat_clark"
        os.chdir(installation_path)
        # banner
        print("audiocat " + get_version())
        print("configuration parameters can be set in folder " + installation_path+"/cfg")        
    else:
        # banner
        print("audiocat " + get_version()) 
    print("-------------------------------")
    # with the following line, no message or stack trace will be printed when you Ctrl+C this program
    signal(SIGINT, lambda _, __: exit())
    # parse arguments
    #################                    
    if len(sys.argv) > 1:
        try:
            # call audiocat shell script
            ############################
            command = "".join(["./audiocat '", sys.argv[1], "'"])        
            p1 = subprocess.Popen(command, shell=True, stdout=None, text=True)
            '''p1 = subprocess.Popen(command,
                            shell=True,
                            text=True,
                            stdin =subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE # ,
                            # universal_newlines=True,
                            # bufsize=0
                            )'''
            out, err = p1.communicate()
            if p1.returncode == 0:
                p1.terminate()
                p1.kill()
        except:
            # send the SIGTERM signal to all the process groups to terminate processes launched from here
            os.killpg(os.getpgid(p1.pid), SIGTERM)
    else:
        print("audiocat: *** you must specify an option, run audiocat -h for more information ***")
    
if __name__ == '__main__':
    main()
