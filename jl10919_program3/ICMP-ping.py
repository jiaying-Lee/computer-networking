# from socket import *
import os
import sys
import struct
import time
import select
import socket
import binascii

ICMP_ECHO_REQUEST = 8

def checksum(string):

    csum = 0
    countTo = (len(string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = ord(string[count+1]) * 256 + ord(string[count])
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1])
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    # add global variable for rtt calculation
    global rtt_min, rtt_max, rtt_sum, rtt_cnt

    timeLeft = timeout

    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)

        if whatReady[0] == []: # Timeout
            return "Request timed out."

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        #Fill in start
        #Fetch the ICMP header from the IP packet
        type, code, checksum, id, seq = struct.unpack('bbHHh', recPacket[20:28])

        if type != 0:
            return 'type should be 0, not {}'.format(type)
        if code != 0:
            return 'code should be 0, not {}'.format(code)
        if ID != id:
            return 'id should be {}, not {}'.format(ID, id)

        send_time, = struct.unpack('d', recPacket[28:])

        rtt = (timeReceived - send_time) * 1000
        rtt_cnt += 1
        rtt_sum += rtt
        rtt_min = min(rtt_min,rtt)
        rtt_max = max(rtt_max,rtt)

        ip_header = struct.unpack('!BBHHHBBH4s4s', recPacket[:20])
        ttl = ip_header[5]
        saddr = socket.inet_ntoa(ip_header[8])
        length = len(recPacket) - 20

        return 'From {}: icmp_seq={}, ttl={}, rtt={:.3f} ms, size={} bytes'.format(saddr,seq,ttl,rtt,length)
        #Fill in end

        timeLeft = timeLeft - howLongInSelect

        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):

    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(str(header + data))

    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = socket.htons(myChecksum) & 0xffff
    else:
        myChecksum = socket.htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout):
    icmp = socket.getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details: http://sockraw.org/papers/sock_raw

    #create a socket
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)

    mySocket.close()
    return delay

def ping(host, timeout=1):
    global rtt_min, rtt_max, rtt_sum, rtt_cnt
    rtt_min, rtt_max = float('+inf'), float('-inf')
    rtt_sum, rtt_cnt, count = 0, 0, 0

    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = socket.gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    # Send ping requests to a server separated by approximately one second
    try:
        while 1 :
            count += 1
            delay = doOnePing(dest, timeout)
            print(delay)
            time.sleep(1)# one second
    # print out the rtt statistic after the ping is killed by the user
    except KeyboardInterrupt:
        if count != 0:
            print ("-------------- Optinal Exercises Output----------")
            print ("Statistics of pinging" + host)

            print("{} packts sent, {} packets received. Packet loss rate: {:.5f}%".format(count, rtt_cnt, 100.0-rtt_cnt*100.0/count))

            if rtt_cnt != 0:
                print("RTTs min: {:.5f} ms, RTTs max: {:.5f} ms, RTT average: {:.5f} ms".format(rtt_min,rtt_max, rtt_sum/rtt_cnt))


# ping('127.0.0.1')
ping("google.com")
# ping("baidu.com")
# ping("www.bbc.co.uk")
# ping("lornajane.com.au")
# ping("www.gov.za")
# ping("www.ypf.com")
# ping("www.itauprivatebank.com")