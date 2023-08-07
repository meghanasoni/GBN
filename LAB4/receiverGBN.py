# NAME: Meghana Gopal Soni
# Roll Number: CS20B051
# Course: CS3205 Jan. 2023 semester
# Lab number: 4
# Date of submission: 05-03-2023
# I confirm that the source file is entirely written by me without resorting to any dishonest means.
# Website(s) that I used for basic socket programming code are:
# URL(s): #https://pythontic.com/modules/socket/udp-client-server-example


import socket
import random
import sys, getopt
import time
    
def timediff(i, f):
    return str(round((f-i)/1000)) + ":" + str(round((f-i)%1000))
    
initial_time = time.time()*1000000
debug = 0
receiverIP     = "127.0.0.1"
receiverPort   = 20001
bufferSize  = 1024
MAX_PACKETS = 15
RANDOM_DROP_PROB = 0
argumentList = sys.argv[1:]
options = "dp:n:e:"
arguments, values = getopt.getopt(argumentList, options, [])
for currentArgument, currentValue in arguments:
	if currentArgument == "-d":
		debug = 1
	elif currentArgument == "-p":
		receiverPort = int(currentValue)
	elif currentArgument == "-n":
		MAX_PACKETS = int(currentValue)
	elif currentArgument == "-e":
		RANDOM_DROP_PROB = float(currentValue)



# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind(("127.0.0.1", receiverPort))

print("UDP server up and listening")
	
NFE = 0
received = 0
# Listen for incoming datagrams
while (received < MAX_PACKETS):
	bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
	curr_time = time.time()*1000000
	message = bytesAddressPair[0].decode()
	address = bytesAddressPair[1]
	l = message.split(":")
	sequence_num = int(l[0])
	previous_ack = -1
	message = l[1]
	r = random.uniform(0,1)
	
	if(r <= RANDOM_DROP_PROB):
		#print("\n" + "DROPPED " + str(sequence_num) + "\n")
		continue
		
	if(sequence_num != NFE and previous_ack!=-1):
		#print("ACK sent for ", previous_ack)
		message = str(previous_ack)
		# Sending a reply to client
		UDPServerSocket.sendto(message.encode(), address)

	if(sequence_num == NFE):
		if(debug==1):
			print("Seq# " + str(sequence_num) + " Time Received : " + str(timediff(initial_time, curr_time)) + " Packet dropped : false")
		#print("ACK sent for ", sequence_num)
		NFE = (NFE+1)%256
		previous_ack = sequence_num
		received+=1
		message = str(sequence_num)
		# Sending a reply to client
		UDPServerSocket.sendto(message.encode(), address) 


