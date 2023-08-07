# NAME: Meghana Gopal Soni
# Roll Number: CS20B051
# Course: CS3205 Jan. 2023 semester
# Lab number: 4
# Date of submission: 05-03-2023
# I confirm that the source file is entirely written by me without resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are:
# URL(s): #https://pythontic.com/modules/socket/udp-client-server-example

import socket
import threading
import time
import sys, getopt

def print_time(i):
	return (str(round(i/1000)) + ":" + str(round(i%1000)))


def generatePacket():  #thread that keeps on generating packets every t seconds
	global flag, Buffer, acked, messageAt, transmissions, PACKET_GEN_RATE, packet_generated_at

	initial_time = time.time()
	t = 1/PACKET_GEN_RATE
	sequence_number = 0
	while(flag==True):
		#print("generating packet")
		message = ""
		for i in range(PACKET_LENGTH):
			message+='x'
			
		if len(Buffer) < MAX_BUFFER_SIZE:
			packet_generated_at[sequence_number] = time.time()-initial_time
			Buffer.append((message, sequence_number))
			messageAt[sequence_number] = message
			transmissions[sequence_number]=0
			sequence_number= (sequence_number+1)%256
			acked[sequence_number] = False
			
		time.sleep(t)
	
def sendPacket():
	global flag, stop_timer, bufferSize, acked, debug, window_start, acked_packets, avgRTT, packet_sent_at, ReceiverIP, packet_generated_at, window_end, transmission_count, WINDOW_SIZE, avgRTT, timerThreads, ReceiverPortNum
	while (flag==True and acked_packets <= MAX_PACKETS):
		if(window_end - window_start  < WINDOW_SIZE and len(Buffer) > 0):
			(message, sequence_number) = Buffer.pop(0)
			msg = str(sequence_number) + ":" + message
			window_end = (window_end+1)%256
			transmission_count += 1
			packet_sent_at[sequence_number] = time.time()
			#print("Sending packet with seq no. " + str(sequence_number))
			transmissions[sequence_number] = 1
			acked[sequence_number] = False
			#print("window now has " + str(window_end - window_start) + " elements.")
			UDPClientSocket.sendto(msg.encode(), (ReceiverIP, ReceiverPortNum))    # Send to server using created UDP socket
			stop_timer[sequence_number] = False
			t = 0.1
			if(acked_packets > 10):
				t = 2*avgRTT
			timerThreads[sequence_number] = threading.Thread(target=checkTimeout, args=(sequence_number, t, ))
			timerThreads[sequence_number].start()
	

def acknowledgePacket():
	global flag, stop_timer, bufferSize, acked, debug, window_start, acked_packets, avgRTT, packet_sent_at, packet_generated_at, MAX_PACKETS

	while(flag==True and acked_packets < MAX_PACKETS):
		msgFromServer = UDPClientSocket.recvfrom(bufferSize)
		sequence_num = int(msgFromServer[0].decode())
		if(acked[sequence_num]==True): #duplicate ack
			continue
		
		acked_packets += 1
		
		for i in range(window_start, (sequence_num+1)%256, 1):
			acked[i] = True
			stop_timer[i] = True

		window_start = (sequence_num+1)%256
		RTT = time.time() - packet_sent_at[sequence_num]

		avgRTT = (avgRTT*acked_packets + RTT)/(acked_packets+1)
		
		if(debug == True):
			print("Seq # " + str(sequence_num) + " Time generated: " + str(packet_generated_at[sequence_num]) + " RTT : " + print_time(RTT*1000000) + "ms   Number of attempts : " + str(transmissions[sequence_num]))
		if(acked_packets==MAX_PACKETS):
			retrans_ratio = transmission_count/acked_packets
			print("PktRate = " + str(PACKET_GEN_RATE) + ", Length = " + str(PACKET_LENGTH) + ", Retransmission Ratio = " + str(retrans_ratio) + ", Avg RTT = " + str(avgRTT))

		if(acked_packets > MAX_PACKETS):
			flag = True



def checkTimeout(sequence_number, t):  
	global transmission_count, window_start, messageAt, acked, window_end, transmissions, flag, stop_timer, timerThreads, packet_sent_at, ReceiverPortNum, ReceiverIP
	if(acked[sequence_number]==True or acked_packets >= MAX_PACKETS):
		return
	
	time.sleep(t)

	if(acked[sequence_number] == False):
		lock.acquire()
		if(acked_packets >= MAX_PACKETS):
			return

		for i in range(window_start, window_start + (window_end-window_start+256)%256, 1):
			acked[i] = True   #stop timers for everything present in the window
        
		for i in range(window_start, window_start + (window_end-window_start+256)%256, 1):
			acked[i] = False
			tt = 0.1
			if(transmission_count > 10):
				tt = 2*avgRTT

			timerThreads[i] = threading.Thread(target = checkTimeout, args = (i,tt,))
			timerThreads[i].start()
			transmissions[i]+=1
			if(transmissions[i] >= 6):
				#print("STOP")
				flag = False
			transmission_count+=1
			message = str(i) + ":" + messageAt[i]


			packet_sent_at[i] = time.time()
			UDPClientSocket.sendto(message.encode(), (ReceiverIP, ReceiverPortNum))

		lock.release()

def Exit():
    global flag, acked_packets, MAX_PACKETS
    while(True):
        if(acked_packets < MAX_PACKETS):
            continue
        else:
            flag = False
            break

"""MAIN"""

argumentList = sys.argv[1:]
options = "ds:p:l:r:n:w:b:"
debug = False
PACKET_LENGTH = 100
PACKET_GEN_RATE = 10
MAX_PACKETS = 100
WINDOW_SIZE = 8
MAX_BUFFER_SIZE = 100
avgRTT = 0
bufferSize = 1024
ReceiverIP = "127.0.0.1"
ReceiverPortNum = 20001
window_start = 0
window_end = 0
acked_packets = 0
Buffer = []
Timeout = {}
acked = {}
transmission_count = 0
generation_time = {}
attempts = {}
messageAt = {}
flag = True
transmissions = {}
stop_timer = {}
packet_sent_at = {}
timerThreads = [0]*256
lock = threading.Lock()
packet_generated_at = {}
arguments, values = getopt.getopt(argumentList, options, [])


for currentArgument, currentValue in arguments:
	if currentArgument == "-d":
		debug = True
	elif currentArgument == "-s":
		ReceiverIP = currentValue
	elif currentArgument == "-p":
		ReceiverPortNum = int(currentValue)
	elif currentArgument == "-l":
		PACKET_LENGTH = int(currentValue)
	elif currentArgument == "-r":
		PACKET_GEN_RATE = int(currentValue)
	elif currentArgument == "-n":
		MAX_PACKETS = int(currentValue)
	elif currentArgument == "-w":
		WINDOW_SIZE = int(currentValue)
	elif currentArgument == "-b":
		MAX_BUFFER_SIZE = int(currentValue)



# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
t1 = threading.Thread(target=generatePacket, args=())
t2 = threading.Thread(target=acknowledgePacket, args=())
t3 = threading.Thread(target = sendPacket, args = ())
t4 = threading.Thread(target = Exit, args = ())
t1.start()
t2.start()
t3.start()
t4.start()

while(flag==True):
	if(1==1):
		continue

retrans_ratio = transmission_count/acked_packets
print("PktRate = " + str(PACKET_GEN_RATE) + ", Length = " + str(PACKET_LENGTH) + ", Retransmission Ratio = " + str(retrans_ratio) + ", Avg RTT = " + str(avgRTT))
UDPClientSocket.close()

t1.join()
t2.join()
t3.join()

#print("TERMINATED**************************")
































"""#print("Timer started for seq no " + str(sequence_number) + " at " + str(round(time.time())))
	init_time = time.time()
	while(time.time()-init_time < t and acked[sequence_number]==False and flag==True):
		if(stop_timer[sequence_number]==True):
			#print("Timer stopped for sequence number " + str(sequence_number))
			return
	
	if(acked[sequence_number] == False):
		print("TIMEOUT OCCURED FOR " + str(sequence_number))
		print("WINDOW START = " + str(window_start) + "  WINDOW END = " + str(window_end))
		for i in range(sequence_number, window_end, 1):
			if(acked[i]==False):
				Retransmit(sequence_number)"""

"""def Retransmit(sequence_number):
	global transmission_count, window_start, messageAt, acked, window_end, transmissions, flag, stop_timer, timeoutVal, avgRTT, UDPClientSocket
	if(acked[sequence_number] == True): #if acked, no need for retransmission
		return
	#close current timer thread first
	stop_timer[sequence_number] = True
	transmissions[sequence_number]+=1
	
	if(transmissions[sequence_number] >= 5):
		flag = False
		return
	acked[sequence_number] = False
	t = 0.1
	if(transmission_count > 10):
		t = 2*avgRTT
	temp = threading.Thread(target=checkTimeout, args=(sequence_number, t, ))
	timerThreads.append(temp)
	temp.start()
	return"""
