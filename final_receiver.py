#final_receiver.py부터 실행
from multiprocessing import Process, Pipe
import random
import time
import signal
from socket import *

class TimeOutException(Exception):
    pass


def alarm_handler(signum, frame):
    print("Time-out")
    print("send same Frame")
    print("Restart the timer")
    raise TimeOutException()

data=""
ACK=""

def physical(conn):
    print("physical layer 실행")
    receiverSock = socket(AF_INET, SOCK_STREAM)
    receiverSock.bind(('', 8080))
    receiverSock.listen(1)

    connectionSock, addr = receiverSock.accept()

    print(str(addr), 'connection.')

    global data
    data = connectionSock.recv(1024)
    print('Arrival message from sender: ', data.decode())
    data = data.decode()

    bitStream = data
    result = ""

    for i in range(len(bitStream)):
        if i == 0:
            result += '1'
        elif bitStream[i] != bitStream[i - 1]:
            result += '1'
        else:
            result += '0'

    print("physical layer 변환결과:",result)

    conn.send(result)
    conn.close



def Datalink(conn):
    print("Datalink layer 실행")
    bitStream = data
    output = ""
    count = 0

    for i in range(len(bitStream)):
        if count == 5:
            count = 0
            continue
        if bitStream[i] == '1':
            count += 1
        else:
            count = 0
        output += bitStream[i]
    print(output)

    print("Datalink 변환결과:",output)

    conn.send(output)
    conn.close()

def Network(conn):
    print("Network layer 실행")
    #bypass
    conn.send(data)
    conn.close()

def Transport(conn):
    print("Transport layer 실행")
    ACK = "010000010100001101001011"
    print("ACK 생성")
    conn.send(ACK)
    conn.close()


def Application():
    print("Application layer 실행")
    print("message 수신완료")

def Transport2(conn):
    # stop and wait

    print("trasport layer 실행")
    try:
        conn.send(ACK)
        print('message send ok')
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(2)
        conn.close()

    except TimeOutException:
        Transport(conn)

def Network2(conn):
    print("Network layer 실행")
    #bypass
    conn.send(data)
    conn.close()

def Datalink2(conn):
    print("datalink layer 실행")
    Tfr = 1

    K = 0
    while 1:
        # isIdle == 1: idle
        # isIdle == 0: busy
        isIdle = random.randint(0, 1)
        if isIdle == 0:
            print("...Channel is busy")
        else:
            print("...Channel is idle")

        while isIdle == 0:
            isIdle = random.randint(0, 1)
            if isIdle == 0:
                print("...Channel is busy")
            else:
                print("...Channel is idle")

        print("...Transmit and receive")
        # isCollision == 1: Collision 발생
        # isCollision == 0: Collision 발생x
        isCollision = random.randint(0, 1)

        if isCollision == 1:
            print("...Error:Collision 발생")
            K += 1
            if K > 15:
                print("...Error: To much send")
                break
            print("...send a jamming signal")
            R = random.randrange(0, 2 ** K)
            Tb = R * Tfr
            print("...Tb is", Tb)
            print("...wait", Tb, "seconds")
            time.sleep(Tb)
            continue

        else:
            print("...No Collision")
            print("...Success")
            break
    conn.send(ACK)
    conn.close()

def physical2():
    print("physical layer 실행")
    bitStream = ACK
    output = ""
    lastNoneZero = ''

    for i in range(len(bitStream)):
        if i == 0:
            if bitStream[i] == '0':
                output += '0'
            else:
                lastNoneZero = '+'
                output += '+'
        else:
            if bitStream[i] == '0':
                if output[-1] != '0':
                    lastNoneZero = output[-1]
                output += output[-1]
            elif output[-1] != '0':
                output += '0'
            else:
                if lastNoneZero == '':
                    lastNoneZero = '+'
                    output += '+'
                else:
                    if lastNoneZero == '+':
                        lastNoneZero = '-'
                        output += '-'
                    else:
                        lastNoneZero = '+'
                        output += '+'
    print("physical layer 변환결과:", output)
    senderSock = socket(AF_INET, SOCK_STREAM)
    senderSock.connect(('127.0.0.1', 8081))
    time.sleep(1)
    senderSock.send(output.encode())
    print("socket 전송 완료")







if __name__ =='__main__':
    phy_parent, data_child = Pipe()
    p = Process(target=physical, args=(data_child,))
    p.start()
    data = phy_parent.recv()
    p.join()

    data_parent, net_child = Pipe()
    p = Process(target=Datalink, args=(net_child,))
    p.start()
    data = data_parent.recv()
    p.join()

    net_parent, trans_child = Pipe()
    p = Process(target=Network, args=(trans_child,))
    p.start()
    net_parent.recv()
    p.join()

    trans_parent, App_child = Pipe()
    p = Process(target=Transport, args=(App_child,))
    p.start()
    ACK=trans_parent.recv()
    p.join()

    Application()# scenario2 start
    print("scenario 2 start")

    trans_parent, net_child = Pipe()
    p = Process(target=Transport2, args=(net_child,))
    p.start()
    trans_parent.recv()
    p.join()

    net_parent, data_child = Pipe()
    p = Process(target=Network2, args=(data_child,))
    p.start()
    net_parent.recv()
    p.join()

    data_parent, phy_child = Pipe()
    p = Process(target=Datalink2, args=(phy_child,))
    p.start()
    data_parent.recv()
    p.join()

    physical2()# scenario2 end
