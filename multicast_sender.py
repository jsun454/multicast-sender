from threading import Thread
from time import sleep
import socket

# kart status
STATUS_IDLE = 0
STATUS_PREP = 1
STATUS_DRIVE = 2

# race modes
DISTANCE_MODE = 0
TIME_MODE = 1

RACE_TIME_LENGTH = 1000*60*1 # 1 minute race
RACE_TOTAL_LAPS = 10 # 10 lap race

multicast_group = '239.0.0.1'
multicast_port = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# TODO: implement realistic checkSum
# TODO: vary racer lap times to test scoreboard reordering

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
    lap_times = [0, 1000*8, 1000*15, 1000*21, 1000*26, 1000*30, 1000*38, 1000*45, 1000*51, 1000*56, 1000*60, 1000*660] # element at position i stores the total time needed to complete i laps
    lap_time_offset = 10*kart*(1 if kart%2==0 else -1) # modify how long it takes each kart to complete a lap
    race_is_done = False

    sleep(delay/10) # initial delay before starting this kart

    # main loop for sending multicast packets for this kart
    while True:
        if status == STATUS_IDLE:
            if idle_time >= max_idle_time:
                if race_is_done:
                    race_is_done = False
                    race_mode = not race_mode
                    driver_name = ('Person ' + str(kart) + '  ')[0:10]
                    elapsed_time = 0
                    prev_lap_time = 0
                    lap = 1
                    idle_time = 0
                else:
                    status = STATUS_PREP
                    idle_time = 0

            if race_is_done:
                # kart number, status, current lap number, total number of laps
                data_part_1 = [kart, STATUS_IDLE, lap, total_laps]
                # previous lap time
                data_part_2 = prev_lap_time.to_bytes(4, 'big')
                # time spent so far
                data_part_3 = elapsed_time.to_bytes(4, 'big')
                # total race duration
                data_part_4 = total_time.to_bytes(4, 'big')
                # driver name
                data_part_5 = driver_name
                # check sum, racing mode (0 for distance mode, 1 for time mode)
                data_part_6 = [0, race_mode]

                data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
                sock.sendto(data, (multicast_group, multicast_port))
            else:
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
        elif status == STATUS_PREP:
            if prep_time >= max_prep_time:
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
        elif status == STATUS_DRIVE:
            # if the race is finished already then ignore this
            if not race_is_done:
                # racer finishes another lap
                if elapsed_time > lap_times[lap] + lap_time_offset:
                    # record lap time
                    prev_lap_time = lap_times[lap] - lap_times[lap-1] + lap_time_offset
                    if race_mode == DISTANCE_MODE and lap == total_laps:
                        # race is finished if this was the last lap in distance mode
                        race_is_done = True
                        status = STATUS_IDLE

                    # reverse the offset
                    lap_time_offset = -lap_time_offset

                    # increment the current lap number
                    lap += 1

                # race is finished if the elapsed time surpasses the total race duration
                if race_mode == TIME_MODE and elapsed_time >= total_time:
                    race_is_done = True
                    status = STATUS_IDLE

            # kart number, status, current lap number, total number of laps
            data_part_1 = [kart, STATUS_DRIVE, lap, total_laps]
            # previous lap time
            data_part_2 = prev_lap_time.to_bytes(4, 'big')
            # time spent so far
            data_part_3 = elapsed_time.to_bytes(4, 'big')
            # total race duration
            data_part_4 = total_time.to_bytes(4, 'big')
            # driver name
            data_part_5 = driver_name
            # check sum, racing mode (0 for distance mode, 1 for time mode)
            data_part_6 = [0, race_mode]

            data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
            sock.sendto(data, (multicast_group, multicast_port))

            if not race_is_done:
                elapsed_time += 100
            sleep(0.1)
        else:
            break

def main():
    for x in range(1, 11):
        Thread(target=start_kart, args=(x,x)).start()

if __name__ == '__main__':
    main()
