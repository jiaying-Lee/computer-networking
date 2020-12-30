#import socket module
from socket import *
import sys # In order to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM) 
#Prepare a sever socket
#Fill in start
host = '127.0.0.1'
port = 8080
serverSocket.bind((host,port))
serverSocket.listen(1)
#Fill in end
while True:
    #Establish the connection 
    print('Ready to serve...') 
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024)
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        #Send one HTTP header line into socket
        #Fill in start
        connectionSocket.send('\nHTTP/1.1 200 OK\n\n'.encode());
        #Fill in end
        #Send the content of the requested file to the client 
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode()) 
        connectionSocket.send("\r\n".encode())

        connectionSocket.close() 
    except IOError:
        #Send response message for file not found
        #Fill in start
        connectionSocket.send('\nHTTP/1.1 404 not found\n'.encode())
        connectionSocket.send('\n404 Not Found\n'.encode())
        #Fill in end
        #Close client socket
        #Fill in start
        connectionSocket.close()
        #Fill in end
serverSocket.close()
sys.exit()#Terminate the program after sending the corresponding data