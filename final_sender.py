#final_receiver.py부터 실행

from multiprocessing import Process, Pipe
import random
import time
import signal
from socket import *

ACK = ""
data = "1111000011110000"

class TimeOutException(Exception):
    pass


def alarm_handler(signum, frame):
    print("Time-out")
    print("send same Frame")
    print("Restart the timer")
    raise TimeOutException()

def binTohex(num):
    num = num[::-1]

    result = 0

    for i in range(len(num)):
        if i == 0:
            x = 1 if num[int(i)] == '1' else 0
            result += x
        else:
            if num[i] == '1':
                result = result + (2 ** i)
    return result

def Application(conn):
    if ACK!= "":#수신확인 메세지를 받았다면
        print("ACK 메세지를 받았습니다")
    else:
        print("Application layer 실행")
        data = "1111000011110000"
        print("1111000011110000 data 생성")
        conn.send(data)
        print("data send fin")
        conn.close()

def Transport(conn):
    #stop and wait

    print("trasport layer 실행")
    try:
        conn.send(data)
        print('message send ok')
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(2)
        conn.close()

    except TimeOutException:
        Transport(conn)


def Network(conn):
    print("Network layer 실행")
    #bypass
    conn.send(data)
    conn.close()

def Datalink(conn):
    print("datalink layer 실행")
    bitStream = data
    output = ""
    count = 0

    for i in range(len(bitStream)):
        if bitStream[i] == '1':
            count += 1
        else:
            count = 0
        output += bitStream[i]
        if count == 5:
            output += '0'
            count = 0
    print("bit-stuffing result:",output)


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
    conn.send(output)
    conn.close()

def physical():
    print("physical layer 실행")
    bitStream = data
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
    senderSock = socket(AF_INET, SOCK_STREAM)
    senderSock.connect(('127.0.0.1', 8080))
    senderSock.send(output.encode())

def physical2(conn):
    receiverSock = socket(AF_INET, SOCK_STREAM)
    receiverSock.bind(('', 8081))
    receiverSock.listen(1)

    connectionSock, addr = receiverSock.accept()
    ACK = connectionSock.recv(1024)
    print('Arrival ACK : ', ACK.decode('utf-8'))

    bitStream = ACK.decode()
    result =""

    for i in range(len(bitStream)):
        if i == 0:
            result += '0'
        elif bitStream[i] != bitStream[i - 1]:
            result += '1'
        else:
            result += '0'

    print("physical layer 변환결과:",result)

    conn.send(result)
    conn.close


def Datalink2(conn):
    print("Datalink layer 실행")
    bitStream = ACK
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

    print("Datalink 변환결과:", output)

    conn.send(output)
    conn.close()


def Network2(conn):
    print("Network layer 실행")
    # bypass
    conn.send(data)
    conn.close()


def Transport2(conn):
    print("Transport layer 실행")
    print("ACK 수신확인")
    #0100 0001 0100 0011 0100 1011
    first = binTohex(ACK[:8])
    second = binTohex(ACK[8:16])
    third = binTohex(ACK[16:])

    result = chr(first)+chr(second)+chr(third)


    conn.send(result)
    conn.close()


def Application2():
    print("Application layer 실행")
    print("message 수신완료")
    print("수신확인 메세지:", ACK)

if __name__=='__main__':
    app_parent, trans_child = Pipe()
    p = Process(target=Application, args=(trans_child, ))
    p.start()
    app_parent.recv()
    p.join()

    trans_parent,net_child = Pipe()
    p = Process(target=Transport, args=(net_child,))
    p.start()
    trans_parent.recv()
    p.join()

    net_parent, data_child = Pipe()
    p = Process(target=Network, args=(data_child,))
    p.start()
    net_parent.recv()
    p.join()

    data_parent, phy_child = Pipe()
    p = Process(target=Datalink, args=(phy_child,))
    p.start()
    data=data_parent.recv()
    p.join()

    physical()# scenario2 start
    print("scenario 2 start")

    phy_parent, data_child = Pipe()
    p = Process(target=physical2, args=(data_child,))
    p.start()
    ACK = phy_parent.recv()
    p.join()

    data_parent, net_child = Pipe()
    p = Process(target=Datalink2, args=(net_child,))
    p.start()
    ACK = data_parent.recv()
    p.join()

    net_parent, trans_child = Pipe()
    p = Process(target=Network2, args=(trans_child,))
    p.start()
    net_parent.recv()
    p.join()

    trans_parent, App_child = Pipe()
    p = Process(target=Transport2, args=(App_child,))
    p.start()
    ACK = trans_parent.recv()
    p.join()

    Application2()  # scenario2 end



