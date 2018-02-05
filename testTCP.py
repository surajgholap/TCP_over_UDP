
import socket
import io
import time
import typing
import struct
import random
from struct import *
import testdata
import testdata.logging
import binascii


def send(sock: socket.socket, data: bytes):
    """
    Implementation of the sending logic for sending data over a slow,
    lossy, constrained network.
    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
        data -- A bytes object, containing the data to send over the network.
    """

   

    seqno = 0
    ackno = 0
    ack = 0
    fin = 0
    timeout_time = 3
    eRtt = 0
    dRtt = 0
    acknowledgement = pack("i", 0)
    total = 0
    data_received = False
    nextAck = 1
    while not data_received:
        if(total == len(data)):
            print("closed")
            sock.close()
            break
        else:
            first_packet = make(seqno, ackno, ack, fin)
            sock.send(first_packet)
            #send_time = time.time()
            logger = testdata.logging.get_logger("hw5-sender")
            chunk_size = testdata.MAX_PACKET
            pause = .1
            
            offsets = range(0, len(data), testdata.MAX_PACKET)
            for chunk in [data[i:i + chunk_size] for i in offsets]:
                try:
                    send_time = time.time()
                    received_data = 0
                    while not received_data:
                        reply1 = listen(sock)
                        total = total + len(chunk)
                        recv_time = time.time()
                        print("Acknowledgement Packet : ", reply1)
                        
                        if reply1[1] == nextAck:
                            sample_rtt = recv_time - send_time
                            print("Sample RTT : ", sample_rtt)
                            eRtt = eRtt * 0.875 + sample_rtt * 0.125
                            dRtt = 0.75 * dRtt + 0.25 * abs(sample_rtt - eRtt)
                            timeout_time = eRtt + 4 * dRtt
                            print(timeout_time)
                            sock.settimeout(timeout_time)
                            print("ackno matched! send the chunk!")
                            checksum = binascii.crc32(chunk)
                            checksum = struct.pack('L', checksum)
                            sock.send(chunk + checksum)
                            print("Chunk sent")
                            nextAck = nextAck + 1
                            print("Next Acknowledgement Number should be", nextAck)
                            break
                except socket.timeout:
                    sock.settimeout(timeout_time * 2)
                    print(timeout_time * 2)
                    print("ackno matched!ljblhjlg Good to send the chunk!")
                    checksum = binascii.crc32(chunk)
                    checksum = struct.pack('L', checksum)
                    sock.send(chunk + checksum)
                    print("Chunk sent")
                    nextAck = nextAck + 1
                    print("Next Acknowledgement Number should be", nextAck)                 

                

def recv(sock: socket.socket, dest: io.BufferedIOBase) -> int:
    """
    Implementation of the receiving logic for receiving data over a slow,
    lossy, constrained network.
    Args:
        sock -- A socket object, constructed and initialized to communicate
                over a simulated lossy network.
    Return:
        The number of bytes written to the destination.
    """
    logger = testdata.logging.get_logger("hw5-receiver")
    
    reply = listen(sock)
    print("SYN Packet : ", reply)
    #sock.send(second_packet)
    acknowledgement = 1
    num_bytes = 0
    reply1 = []
    reply1 = list(reply)
    total = 0
    for x in range(1):
        reply1[0] = random.randint(1,5)
    #reply1[0] = reply1[0] + 1
    reply1[1] = reply1[1] + 1
    reply1[2] = reply1[2] + 1
        
    second_packet = make(reply1[0], reply1[1], reply1[2], reply1[3])
    print("\nNext Acknowledgement is ", reply1[1])
    sock.send(second_packet)
    a = 2
    while(a == 2):
      
        for x in range(1):
            reply1[0] = random.randint(1, 10)
        reply1[1] = reply1[1] + 1
        reply1[2] = reply1[2] + 1
        
        second_packet = make(reply1[0], reply1[1], reply1[2], reply1[3])
        print("\nNext Acknowledgement is ", reply1[1])
        
        print("Acknowledgement sent")
        data1 = sock.recv(5000)
        dlen = len(data1) - 8
        data = data1[:dlen]
        checksum = struct.unpack("L", data1[dlen:])
        
        print(data)
        print("checkssum:", checksum)
        checkchecksum = binascii.crc32(data)
        print("checkchecksum:", checkchecksum)
        if data and checkchecksum in checksum:
            sock.send(second_packet)
            print("Chunk received")
            print("Length of chunk received : ", len(data))
           
            
        else:
            sock.close()
            break
        logger.info("Received %d bytes", len(data))
        dest.write(data)
        num_bytes += len(data)
        dest.flush()
    print("\nThere was no data received")
    return num_bytes

def make(seqno, ackno, ack, fin):
    packet = struct.pack("iiii", seqno, ackno, ack, fin)
    return packet

def listen(sock: socket.socket):
    first_received = False
    while not first_received:
        received_data = sock.recv(testdata.MAX_PACKET)
        received_packet = struct.unpack("iiii", received_data)
        if received_packet:
            break
    return received_packet
    print("The received packet : ", received_packet)

