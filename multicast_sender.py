'''
import socket
import asyncio

multicast_group = '239.0.0.1'
multicast_port = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

# default value 1 works
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

############### POPULATE SCOREBOARD WITH 10 RACERS ###############
# for x in range(1, 11):
#     test = [x, 2, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0]
#     test2 = 'JohnnyDepp'
#     test3 = [0, 1]

#     data = bytes(test) + bytes(test2, 'utf-8') + bytes(test3)
#     sock.sendto(data, (multicast_group, multicast_port))

async def main():
    # tasks = []
    for x in range(1, 11):
        asyncio.get_event_loop().create_task(start_kart(x, x))
        # task = asyncio.get_event_loop().create_task(start_kart(x, x))
        # tasks.append(task)

    # for task in tasks:
    #     await task

async def start_kart(delay, kart):
    # await asyncio.sleep(delay)
    prevLap = 0
    elapsed = 0
    while True:
        data_part_1 = [kart, 2, 1, 3] # kartNO, status, currLap, totalLaps
        data_part_2 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # prevLap
        data_part_3 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # bestLap
        data_part_4 = ('Racer ' + str(kart) + '   ')[0:10] # name
        data_part_5 = [0, 1] # checkSum, mode
        data = bytes(data_part_1) + bytes(data_part_2) + bytes(data_part_3) + bytes(data_part_4, 'utf-8') + bytes(data_part_5)
        sock.sendto(data, (multicast_group, multicast_port))
        elapsed += 100
        if(elapsed % 5000):
            prevLap = 5000 - elapsed // 5000
        # await asyncio.sleep(0.1)

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
loop.close()
'''

'''
from multiprocessing import Process
from time import sleep
import socket

def start_kart(delay, kart):
    multicast_group = '239.0.0.1'
    multicast_port = 8888
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    prevLap = 0
    elapsed = 0
    while True:
        data_part_1 = [kart, 2, 1, 3] # kartNO, status, currLap, totalLaps
        data_part_2 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # prevLap
        data_part_3 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # bestLap
        data_part_4 = ('Racer ' + str(kart) + '   ')[0:10] # name
        data_part_5 = [0, 1] # checkSum, mode
        data = bytes(data_part_1) + bytes(data_part_2) + bytes(data_part_3) + bytes(data_part_4, 'utf-8') + bytes(data_part_5)
        sock.sendto(data, (multicast_group, multicast_port))
        elapsed += 100
        if(elapsed % 5000):
            prevLap = 5000 - elapsed // 5000
        sleep(1)

if __name__ == '__main__':
    for x in range(1, 11):
        Process(target=start_kart, args=(x, x)).start()
'''

from threading import Thread
from time import sleep
import socket

multicast_group = '239.0.0.1'
multicast_port = 8888
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

def start_kart(delay, kart):
    prevLap = 0
    elapsed = 0
    lap = 1
    # sleep(delay)
    while True:
        data_part_1 = [kart, 2, lap, 3] # kartNO, status, currLap, totalLaps
        # data_part_2 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # prevLap
        # data_part_3 = [0, ((prevLap // 256) // 256) % 256, (prevLap // 256) % 256, prevLap % 256] # bestLap
        data_part_2 = prevLap.to_bytes(4, 'big') # prevLap
        data_part_3 = elapsed.to_bytes(4, 'big') # timeSpent
        data_part_4 = (1000*(60*5+11)+888).to_bytes(4, 'big') # totalTime
        data_part_5 = ('Racer ' + str(kart) + '   ')[0:10] # name
        data_part_6 = [0, kart%2] # checkSum, mode
        data = bytes(data_part_1) + data_part_2 + data_part_3 + data_part_4 + bytes(data_part_5, 'utf-8') + bytes(data_part_6)
        sock.sendto(data, (multicast_group, multicast_port))
        elapsed += 100
        if(elapsed % 5000):
            prevLap = 5000 - elapsed // 5000
        lap = elapsed // 5000 + 1
        sleep(0.1)

def main():
    for x in range(1, 11):
        Thread(target=start_kart, args=(x,x)).start()

if __name__ == '__main__':
    main()
