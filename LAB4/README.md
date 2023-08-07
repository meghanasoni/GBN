Run the following commands in two terminals:

python3 senderGBN.py -d -s RECEIVER_NAME/IP_ADDRESS -p PORT_NUMBER -l PACKET_LENGTH -r PACKET_GEN_RATE -n MAX_PACKETS -w WINDOW_SIZE -b MAX_BUFFER_SIZE
python3 receiverGBN.py -d -p PORT_NUMBER -n MAX_PACKETS -e PACKET_DROP_PROBAB