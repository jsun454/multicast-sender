from threading import Thread
from time import sleep
import socket

# kart status
STATUS_IDLE = 0
STATUS_PREP = 1
STATUS_DRIVE = 2

RACE_TIME_LENGTH = 1000*60*5 # 5 minute race
RACE_TOTAL_LAPS = 10 # 10 lap race

multicast_group = '239.0.0.1'
multicast_port = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def start_kart(delay, kart):
    status = STATUS_IDLE # kart's current status
    race_mode = (kart//6==1) # race mode (0 for distance mode, fixed number of laps; 1 for time mode, fixed race duration)

    # variables for status: idle
    idle_time = 0 # elapsed time in idle state
    max_idle_time = 1000*5 # how much time the kart will spend idle before transitioning into preparation mode

    # variables for status: preparation
    prep_time = 0 # elapsed time in preparation state
    max_prep_time = 1000*5 # how much time the kart will spend in preparation before transitioning into drive mode

    # variables for status: driving
    driver_name = ('Racer ' + str(kart) + '   ')[0:10]
    elapsed_time = 0 # elapsed time since the start of the race
    prev_lap_time = 0 # previous lap time
    total_time = RACE_TIME_LENGTH # total race duration (time mode)
    lap = 1 # current lap number
    total_laps = RACE_TOTAL_LAPS # total race distance (distance mode)

    sleep(delay/10) # initial delay before starting this kart

    # main loop for sending multicast packets for this kart
    while True:
        if(status == STATUS_IDLE):
            if(idle_time >= max_idle_time):
                status = STATUS_PREP
                idle_time = 0

            # kart number, status, current lap number, total number of laps
            data_part_1 = [kart, STATUS_IDLE, 1, 1]
            # previous lap time
            data_part_2 = (0).to_bytes(4, 'big')
            # time driven so far
            data_part_3 = (0).to_bytes(4, 'big')
            # total race duration
            data_part_4 = (0).to_bytes(4, 'big')
            # driver name
            data_part_5 = 'None      '
            # check sum, racing mode (0 for distance mode, 1 for time mode)
            data_part_6 = [0, race_mode]

            data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
            sock.sendto(data, (multicast_group, multicast_port))

            idle_time += 100
            sleep(0.1)
        elif(status == STATUS_PREP):
            if(prep_time >= max_prep_time):
                status = STATUS_DRIVE
                prep_time = 0

            # kart number, status, current lap number, total number of laps
            data_part_1 = [kart, STATUS_PREP, lap, total_laps]
            # previous lap time
            data_part_2 = prev_lap_time.to_bytes(4, 'big')
            # time driven so far
            data_part_3 = elapsed_time.to_bytes(4, 'big')
            # total race duration
            data_part_4 = total_time.to_bytes(4, 'big')
            # driver name
            data_part_5 = driver_name
            # check sum, racing mode (0 for distance mode, 1 for time mode)
            data_part_6 = [0, race_mode]

            data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
            sock.sendto(data, (multicast_group, multicast_port))

            prep_time += 100
            sleep(0.1)
        elif(status == STATUS_DRIVE):
            # kart number, status, current lap number, total number of laps
            data_part_1 = [kart, STATUS_DRIVE, lap, total_laps]

            # previous lap time
            data_part_2 = prev_lap_time.to_bytes(4, 'big')

            # time spent so far
            data_part_3 = elapsed_time.to_bytes(4, 'big')

            # total race duration
            data_part_4 = (1000*(60*5+11)+888).to_bytes(4, 'big')

            # driver name
            data_part_5 = driver_name

            # check sum, racing mode (0 for distance mode, 1 for time mode)
            data_part_6 = [0, race_mode]

            data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
            sock.sendto(data, (multicast_group, multicast_port))

            elapsed_time += 100
            if(elapsed_time % 5000):
                prev_lap_time = 5000 - elapsed_time // 5000
            lap = elapsed_time // 5000 + 1
            sleep(0.1)
        else:
            break

def main():
    for x in range(1, 11):
        Thread(target=start_kart, args=(x,x)).start()

if __name__ == '__main__':
    main()
