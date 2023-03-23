import psutil
import time
import os
import signal

def get_rw_speed(sample_time:float,device_id:int)->tuple:
    start_time = time.time()
    disk_io_counter = psutil.disk_io_counters(True)
    drive = "PhysicalDrive"+str(device_id)
    if drive not in disk_io_counter:
        return (0,0,"NOO")
    disk_io_counter = disk_io_counter[drive]
    if disk_io_counter is None:return (0,0,"NOO")
    start_read_bytes = disk_io_counter[2]
    start_write_bytes = disk_io_counter[3]
    time.sleep(sample_time)
    disk_io_counter = psutil.disk_io_counters(True)
    if drive not in disk_io_counter:
        return (0,0,"NOO")
    disk_io_counter = disk_io_counter[drive]
    if disk_io_counter is None:return (0,0,"NOO")
    end_read_bytes = disk_io_counter[2]
    end_write_bytes = disk_io_counter[3]
    end_time = time.time()
    time_diff = end_time - start_time
    read_speed = (end_read_bytes - start_read_bytes)/time_diff
    write_speed = (end_write_bytes - start_write_bytes)/time_diff
    # Convert to Mb/s
    read_mega_bytes_sec = round(read_speed / (1024**2), 2)
    write_mega_bytes_sec = round(write_speed / (1024**2), 2)
    return read_mega_bytes_sec, write_mega_bytes_sec, ""

def clear_n_banner():
    #clear screen and print banner
    os.system('cls' if os.name == 'nt' else 'clear')
    print(" "*20,"-"*30)
    print(" "*20,"|"," "*26,"|")
    print(" "*20,"|"," "*5,"Disk Speed Test"," "*4,"|")
    print(" "*20,"|"," "*5,"by NotTrueFalse"," "*4,"|")
    print(" "*20,"|"," "*26,"|")
    print(" "*20,"-"*30)

def signal_handler(sig, frame):
    global saved
    if save_for_latter:
        file = open("disk_speed.csv","a")
        file.write("Read speed,Write speed,Time\n")
        for i in saved:
            file.write(f"{i[0]},{i[1]},{i[2]}\n")
        file.close()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("[+] Saved to disk_speed.csv")
    os.abort()

signal.signal(signal.SIGINT, signal_handler)
saved = []
if __name__ == '__main__':
    clear_n_banner()
    physical_disk = list(psutil.disk_partitions())
    print("List of physical disks:")
    for i in range(len(physical_disk)):
        print(f"{i+1}. {physical_disk[i].device}")
    print("99. Exit")
    letter_name = input("[?] Choose a disk: ")
    if letter_name == 99:
        print("GoodBye!")
        exit()
    id_disk = int(letter_name)-1
    letter_name = physical_disk[id_disk].device
    try:
        hdd=psutil.disk_usage(letter_name)
        print ("Total:", round(hdd.total / (2**30),2),"GB")
        print ("Used:", round(hdd.used / (2**30),2),"GB")
        print ("Free:", round(hdd.free / (2**30),2),"GB")
        print ("Percentage:", hdd.percent,"%")
    except Exception as e:
        print("An error occured: ",e)
    save_for_latter = input("[?] Do you want to save the results? (by pressing Ctrl-C) (y/n): ").lower() == "y"
    while True:
        read_speed, write_speed, err = get_rw_speed(1,id_disk+1) #remove the +1 if it doesn't work
        if err == "NOO":
            print("[-] Disk not found")
            break
        print(f"Read speed: {read_speed} Mb/s, Write speed: {write_speed} Mb/s"," "*100,end="\r")
        if save_for_latter:
            current_time = time.strftime("%H:%M:%S", time.localtime())
            saved.append((read_speed,write_speed,current_time))
        if read_speed == 0 and write_speed == 0:
            break
