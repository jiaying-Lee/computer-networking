from socket import *
from datetime import datetime

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(1)
sentToAddr = ('127.0.0.1',12000)

for i in range(1,11):

	startTime = datetime.now()
	message1 = 'Ping ' + str(i) + ' ' + str(startTime.strftime("%H:%M:%S.%f"))
	clientSocket.sendto(message1.encode(), sentToAddr)
	print('\npinging...')

	try:
		message2, fromAddress = clientSocket.recvfrom(1024)
		endTime = datetime.now()
		rtt = (endTime - startTime).microseconds / 1000000
		print(message2)
		print('RTT:',rtt,'seconds')

	except timeout:
		print('Request timed out')

clientSocket.close()

