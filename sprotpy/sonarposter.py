import multiprocessing
import time

def child_process(ns):

    while(1):
        time.sleep(0.5)

        # Child process can read from pipe
        print ns.arr
        print "Child Process"

if __name__ == '__main__':

    # Pipe Manager
    manager = multiprocessing.Manager()
    ns = manager.Namespace()

    # Start child process
    p1 = multiprocessing.Process(target=child_process, args=(ns,))
    p1.start()

    # Local var
    local_arr = []

    # Pipe var
    ns.arr = []

    # Parent Process
    while(1):
        time.sleep(0.5)

        # Write local arr to pipe
        local_arr.append(1)
        ns.arr = local_arr

        print "Parent Process"


    #Join
    p1.join()