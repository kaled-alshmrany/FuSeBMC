/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <stdio.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <pthread.h>
#include <stdarg.h>


#include "../ftpData.h"
#include "connection.h"

int socketPrintf(ftpDataType * ftpData, int clientId, const char *__restrict __fmt, ...)
{

GOAL_7:;

	#define COMMAND_BUFFER								9600
	#define SOCKET_PRINTF_BUFFER						2048
	int bytesWritten = 0;
	char theBuffer[SOCKET_PRINTF_BUFFER];
	char commandBuffer[COMMAND_BUFFER];
	int theStringSize = 0, theCommandSize = 0;
	memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
	memset(&commandBuffer, 0, COMMAND_BUFFER);
	//printf("\nWriting to socket id %d, TLS %d: ", clientId, ftpData->clients[clientId].tlsIsEnabled);

	//pthread_mutex_lock(&ftpData->clients[clientId].writeMutex);

	va_list args;
	va_start(args, __fmt);
	while (*__fmt != '\0')
	{
GOAL_8:;

		int i = 0;
		theStringSize = 0;
		switch(*__fmt)
		{
			case 'd':
GOAL_19:;

			case 'D':
GOAL_18:;

			{
				int theInteger = va_arg(args, int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER, "%d", theInteger);
			}
			break;

			case 'c':
GOAL_17:;

			case 'C':
GOAL_16:;

			{
				int theCharInteger = va_arg(args, int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER, "%c", theCharInteger);
			}
			break;

			case 'f':
GOAL_15:;

			case 'F':
GOAL_14:;

			{
				float theDouble = va_arg(args, double);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER, "%f", theDouble);
			}
			break;

			case 's':
GOAL_13:;

			case 'S':
GOAL_12:;

			{
				char * theString = va_arg(args, char *);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER, "%s", theString);
			}
			break;

			case 'l':
GOAL_11:;

			case 'L':
GOAL_10:;

			{
				long long int theLongLongInt = va_arg(args, long long int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER, "%lld",  theLongLongInt);
			}
			break;

			default:
GOAL_9:;

			{
				printf("\n Switch is default (%c)", *__fmt);
			}
			break;
		}

		for (i = 0; i <theStringSize; i++)
		{
GOAL_20:;

			if (theCommandSize < COMMAND_BUFFER)
			{
GOAL_21:;

				commandBuffer[theCommandSize++] = theBuffer[i];
			}
		}

		++__fmt;
	}
	va_end(args);

	if (ftpData->clients[clientId].socketIsConnected != 1 ||
		ftpData->clients[clientId].socketDescriptor < 0)
	{
GOAL_22:;

		printf("\n Client is not connected!");
		return -1;
	}

	if (ftpData->clients[clientId].tlsIsEnabled != 1)
	{
GOAL_23:;

		//printf("\nwriting[%d] %s",theCommandSize, commandBuffer);
		//fflush(0);
		bytesWritten = write(ftpData->clients[clientId].socketDescriptor, commandBuffer, theCommandSize);
	}
	else 
{

GOAL_24:;
 if (ftpData->clients[clientId].tlsIsEnabled == 1)
	{
GOAL_25:;

		#ifdef OPENSSL_ENABLED
		bytesWritten = SSL_write(ftpData->clients[clientId].ssl, commandBuffer, theCommandSize);
		#endif
	}
}


	//printf("\n%s", commandBuffer);

	//pthread_mutex_unlock(&ftpData->clients[clientId].writeMutex);

	return bytesWritten;
}

int socketWorkerPrintf(ftpDataType * ftpData, int clientId, const char *__restrict __fmt, ...)
{

GOAL_26:;

	#define COMMAND_BUFFER								9600
	#define SOCKET_PRINTF_BUFFER2						4096

	int bytesWritten = 0, i = 0, theStringToWriteSize = 0;
	char theBuffer[SOCKET_PRINTF_BUFFER2];
	char writeBuffer[COMMAND_BUFFER];
	int theStringSize = 0;

	memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
	memset(&writeBuffer, 0, COMMAND_BUFFER);

	va_list args;
	va_start(args, __fmt);
	while (*__fmt != '\0')
	{
GOAL_27:;

		theStringSize = 0;

		switch(*__fmt)
		{
			case 'd':
GOAL_38:;

			case 'D':
GOAL_37:;

			{
				int theInteger = va_arg(args, int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER2, "%d", theInteger);
			}
			break;

			case 'c':
GOAL_36:;

			case 'C':
GOAL_35:;

			{
				int theCharInteger = va_arg(args, int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER2, "%c", theCharInteger);
			}
			break;

			case 'f':
GOAL_34:;

			case 'F':
GOAL_33:;

			{
				float theDouble = va_arg(args, double);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER2, "%f", theDouble);
			}
			break;

			case 's':
GOAL_32:;

			case 'S':
GOAL_31:;

			{
				char * theString = va_arg(args, char *);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER2, "%s", theString);
			}
			break;

			case 'l':
GOAL_30:;

			case 'L':
GOAL_29:;

			{
				long long int theLongLongInt = va_arg(args, long long int);
				memset(&theBuffer, 0, SOCKET_PRINTF_BUFFER2);
				theStringSize = snprintf(theBuffer, SOCKET_PRINTF_BUFFER2, "%lld",  theLongLongInt);
			}
			break;

			default:
GOAL_28:;

			{
				printf("\n Switch is default (%c)", *__fmt);
			}
			break;
		}
		++__fmt;

		//printf("\nThe string: %s", theBuffer);

		for (i = 0; i <theStringSize; i++)
		{
GOAL_39:;

			//Write the buffer
			if (theStringToWriteSize >= COMMAND_BUFFER)
			{
GOAL_40:;


				int theReturnCode = 0;
				if (ftpData->clients[clientId].dataChannelIsTls != 1)
				{
GOAL_41:;

					theReturnCode = write(ftpData->clients[clientId].workerData.socketConnection, writeBuffer, theStringToWriteSize);
				}
				else 
{

GOAL_42:;
 if (ftpData->clients[clientId].dataChannelIsTls == 1)
				{
GOAL_43:;

					#ifdef OPENSSL_ENABLED
					if (ftpData->clients[clientId].workerData.passiveModeOn == 1){
						theReturnCode = SSL_write(ftpData->clients[clientId].workerData.serverSsl, writeBuffer, theStringToWriteSize);
						//printf("%s", writeBuffer);
					}
					else if (ftpData->clients[clientId].workerData.activeModeOn == 1){
						theReturnCode = SSL_write(ftpData->clients[clientId].workerData.clientSsl, writeBuffer, theStringToWriteSize);
						//printf("%s", writeBuffer);
					}
					#endif
				}
}


				if (theReturnCode > 0)
				{
GOAL_44:;

					bytesWritten += theReturnCode;
				}

				if (theReturnCode < 0)
				{
GOAL_45:;

					printf("\nWrite error");
					va_end(args);
					return theReturnCode;
				}

				memset(&writeBuffer, 0, COMMAND_BUFFER);
				theStringToWriteSize = 0;
			}

			if (theStringToWriteSize < COMMAND_BUFFER)
			{
GOAL_46:;

				writeBuffer[theStringToWriteSize++] = theBuffer[i];
			}
		}
	}
	va_end(args);


	//printf("\nData to write: %s (%d bytes)", writeBuffer, theStringToWriteSize);
	//Write the buffer
	if (theStringToWriteSize > 0)
	{
GOAL_47:;

		//printf("\nwriting data size %d", theStringToWriteSize);
		int theReturnCode = 0;

		if (ftpData->clients[clientId].dataChannelIsTls != 1)
		{
GOAL_48:;

			theReturnCode = write(ftpData->clients[clientId].workerData.socketConnection, writeBuffer, theStringToWriteSize);
		}
		else 
{

GOAL_49:;
 if (ftpData->clients[clientId].dataChannelIsTls == 1)
		{
GOAL_50:;

			#ifdef OPENSSL_ENABLED
			if (ftpData->clients[clientId].workerData.passiveModeOn == 1){
				theReturnCode = SSL_write(ftpData->clients[clientId].workerData.serverSsl, writeBuffer, theStringToWriteSize);
				//printf("%s", writeBuffer);
			}
			else if (ftpData->clients[clientId].workerData.activeModeOn == 1){
				theReturnCode = SSL_write(ftpData->clients[clientId].workerData.clientSsl, writeBuffer, theStringToWriteSize);
				//printf("%s", writeBuffer);
			}
			#endif
		}
}


		if (theReturnCode > 0)
		{
GOAL_51:;

			bytesWritten += theReturnCode;
		}

		if (theReturnCode < 0)
		{
GOAL_52:;

			return theReturnCode;
		}

		memset(&writeBuffer, 0, COMMAND_BUFFER);
		theStringToWriteSize = 0;
	}

	//printf("\nbytesWritten = %d", bytesWritten);

	return bytesWritten;
}

/* Return the higher socket available*/
int getMaximumSocketFd(int mainSocket, ftpDataType * ftpData)
{

GOAL_53:;

    int toReturn = mainSocket;
    int i = 0;

    for (i = 0; i < ftpData->ftpParameters.maxClients; i++)
    {
GOAL_54:;

        if (ftpData->clients[i].socketDescriptor > toReturn) {
GOAL_55:;

            toReturn = ftpData->clients[i].socketDescriptor;
        }
    }
    //Must be incremented by one
    toReturn++;
    return toReturn;
}

int createSocket(ftpDataType * ftpData)
{

GOAL_56:;

  //printf("\nCreating main socket on port %d", ftpData->ftpParameters.port);
  int sock, errorCode;
  struct sockaddr_in temp;

  //Socket creation
  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1)
  {
GOAL_57:;

	  return -1;
  }
  temp.sin_family = AF_INET;
  temp.sin_addr.s_addr = INADDR_ANY;
  temp.sin_port = htons(ftpData->ftpParameters.port);

  //No blocking socket
  errorCode = fcntl(sock, F_SETFL, O_NONBLOCK);

    int reuse = 1;
    
#ifdef SO_REUSEADDR
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_58:;

        perror("setsockopt(SO_REUSEADDR) failed");
}

#endif

#ifdef SO_REUSEPORT
    if (setsockopt(sock, SOL_SOCKET, SO_REUSEPORT, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_59:;
 
        perror("setsockopt(SO_REUSEPORT) failed");
}

#endif
  //Bind socket
  errorCode = bind(sock,(struct sockaddr*) &temp,sizeof(temp));
  if (errorCode == -1)
  {
GOAL_60:;

	  if (sock != -1)
	  {
GOAL_61:;

		close(sock);
	  }
	  return -1;
  }

  //Number of client allowed
  errorCode = listen(sock, ftpData->ftpParameters.maxClients + 1);
  if (errorCode == -1)
  {
GOAL_62:;

	  if (sock != -1)
	  {
GOAL_63:;

		close(sock);
	  }
	  return -1;
  }
 
  return sock;
}

int createPassiveSocket(int port)
{

GOAL_64:;

  int sock, returnCode;
  struct sockaddr_in temp;

  //Socket creation
  sock = socket(AF_INET, SOCK_STREAM, 0);
  if (sock == -1)
  {
GOAL_65:;

	  return -1;
  }

  temp.sin_family = AF_INET;
  temp.sin_addr.s_addr = INADDR_ANY;
  temp.sin_port = htons(port);

  int reuse = 1;

#ifdef SO_REUSEADDR
   if (setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_66:;

        perror("setsockopt(SO_REUSEADDR) failed");
}

#endif

#ifdef SO_REUSEPORT
   if (setsockopt(sock, SOL_SOCKET, SO_REUSEPORT, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_67:;
 
       perror("setsockopt(SO_REUSEPORT) failed");
}

#endif

  //Bind socket
  returnCode = bind(sock,(struct sockaddr*) &temp,sizeof(temp));

  if (returnCode == -1)
  {
GOAL_68:;

	  printf("\n Could not bind %d errno = %d", sock, errno);

	  if (sock != -1)
	  {
GOAL_69:;

		  close(sock);
	  }
	return returnCode;
  }

  //Number of client allowed
  returnCode = listen(sock, 1);

  if (returnCode == -1)
  {
GOAL_70:;

	  printf("\n Could not listen %d errno = %d", sock, errno);
	  if (sock != -1)
	  {
GOAL_71:;

		  close(sock);
	  }
      return returnCode;
  }

  return sock;
}

int createActiveSocket(int port, char *ipAddress)
{

GOAL_72:;

  int sockfd;
  struct sockaddr_in serv_addr;

  //printf("\n Connection socket is going to start ip: %s:%d \n", ipAddress, port);
  memset(&serv_addr, 0, sizeof(struct sockaddr_in)); 
  serv_addr.sin_family = AF_INET;
  serv_addr.sin_port = htons(port); 
  if(inet_pton(AF_INET, ipAddress, &serv_addr.sin_addr)<=0)
  {
GOAL_73:;

      printf("\n inet_pton error occured\n");
      return -1;
  } 

  if((sockfd = socket(AF_INET, SOCK_STREAM, 0)) < 0)
  {
GOAL_74:;

      printf("\n2 Error : Could not create socket \n");
      return -1;
  }
  else
  {
GOAL_75:;

      printf("\ncreateActiveSocket created socket = %d \n", sockfd);
  }
  
  
  int reuse = 1;
#ifdef SO_REUSEADDR
   if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_76:;

        perror("setsockopt(SO_REUSEADDR) failed");
}

#endif

#ifdef SO_REUSEPORT
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, (const char*)&reuse, sizeof(reuse)) < 0) 
{

GOAL_77:;
 
       perror("setsockopt(SO_REUSEPORT) failed");
}

#endif
  

  if(connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
  {
GOAL_78:;

     printf("\n3 Error : Connect Failed \n");

   	  if (sockfd != -1)
   	  {
GOAL_79:;

   		close(sockfd);
   	  }

     return -1;
  }

 // printf("\n Connection socket %d is going to start ip: %s:%d \n",sockfd, ipAddress, port);

  return sockfd;
}

void fdInit(ftpDataType * ftpData)
{

GOAL_80:;

    FD_ZERO(&ftpData->connectionData.rset);
    FD_ZERO(&ftpData->connectionData.wset);
    FD_ZERO(&ftpData->connectionData.eset);
    FD_ZERO(&ftpData->connectionData.rsetAll);
    FD_ZERO(&ftpData->connectionData.wsetAll);
    FD_ZERO(&ftpData->connectionData.esetAll);    

    FD_SET(ftpData->connectionData.theMainSocket, &ftpData->connectionData.rsetAll);    
    FD_SET(ftpData->connectionData.theMainSocket, &ftpData->connectionData.wsetAll);
    FD_SET(ftpData->connectionData.theMainSocket, &ftpData->connectionData.esetAll);
}

void fdAdd(ftpDataType * ftpData, int index)
{

GOAL_87:;

    FD_SET(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.rsetAll);    
    FD_SET(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.wsetAll);
    FD_SET(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.esetAll);
    ftpData->connectionData.maxSocketFD = getMaximumSocketFd(ftpData->connectionData.theMainSocket, ftpData) + 1;
}

void fdRemove(ftpDataType * ftpData, int index)
{

GOAL_88:;

    FD_CLR(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.rsetAll);    
    FD_CLR(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.wsetAll);
    FD_CLR(ftpData->clients[index].socketDescriptor, &ftpData->connectionData.esetAll);
}

void closeSocket(ftpDataType * ftpData, int processingSocket)
{

GOAL_89:;

	int theReturnCode = 0;

#ifdef OPENSSL_ENABLED

	if (ftpData->clients[processingSocket].dataChannelIsTls == 1)
	{
		if(ftpData->clients[processingSocket].workerData.passiveModeOn == 1)
		{
			printf("\nSSL worker Shutdown 1");
			theReturnCode = SSL_shutdown(ftpData->clients[processingSocket].ssl);
			printf("\nnSSL worker Shutdown 1 return code : %d", theReturnCode);

			if (theReturnCode < 0)
			{
				printf("SSL_shutdown failed return code %d", theReturnCode);
			}
			else if (theReturnCode == 0)
			{
				printf("\nSSL worker Shutdown 2");
				theReturnCode = SSL_shutdown(ftpData->clients[processingSocket].ssl);
				printf("\nnSSL worker Shutdown 2 return code : %d", theReturnCode);

				if (theReturnCode <= 0)
				{
					printf("SSL_shutdown (2nd time) failed");
				}
			}
		}
	}
#endif

    //Close the socket
    shutdown(ftpData->clients[processingSocket].socketDescriptor, SHUT_RDWR);
    theReturnCode = close(ftpData->clients[processingSocket].socketDescriptor);

    resetClientData(ftpData, processingSocket, 0);
    //resetWorkerData(ftpData, processingSocket, 0);
    
    //Update client connecteds
    ftpData->connectedClients--;
    if (ftpData->connectedClients < 0) 
    {
GOAL_90:;

        ftpData->connectedClients = 0;
    }

    //printf("Client id: %d disconnected", processingSocket);
    //printf("\nServer: Clients connected:%d", ftpData->connectedClients);
    return;
}

void closeClient(ftpDataType * ftpData, int processingSocket)
{

GOAL_91:;

   // printf("\nQUIT FLAG SET!\n");

    if (ftpData->clients[processingSocket].workerData.threadIsAlive == 1)
    {
GOAL_92:;

    	cancelWorker(ftpData, processingSocket);
    }

    FD_CLR(ftpData->clients[processingSocket].socketDescriptor, &ftpData->connectionData.rsetAll);    
    FD_CLR(ftpData->clients[processingSocket].socketDescriptor, &ftpData->connectionData.wsetAll);
    FD_CLR(ftpData->clients[processingSocket].socketDescriptor, &ftpData->connectionData.esetAll);

    closeSocket(ftpData, processingSocket);

    ftpData->connectionData.maxSocketFD = ftpData->connectionData.theMainSocket+1;
    ftpData->connectionData.maxSocketFD = getMaximumSocketFd(ftpData->connectionData.theMainSocket, ftpData) + 1;
    return;
}

void checkClientConnectionTimeout(ftpDataType * ftpData)
{

GOAL_93:;

    int processingSock;
    for (processingSock = 0; processingSock < ftpData->ftpParameters.maxClients; processingSock++)
    {
GOAL_94:;

        /* No connection active*/
        if (ftpData->clients[processingSock].socketDescriptor < 0 ||
            ftpData->clients[processingSock].socketIsConnected == 0) 
            {
GOAL_95:;

                continue;
            }

        /* Max idle time check, close the connection if time is elapsed */
        if (ftpData->ftpParameters.maximumIdleInactivity != 0 &&
            (int)time(NULL) - ftpData->clients[processingSock].lastActivityTimeStamp > ftpData->ftpParameters.maximumIdleInactivity)
            {
GOAL_96:;

                ftpData->clients[processingSock].closeTheClient = 1;
            }
    }
}

void flushLoginWrongTriesData(ftpDataType * ftpData)
{

GOAL_97:;

    int i;
    //printf("\n flushLoginWrongTriesData size of the vector : %d", ftpData->loginFailsVector.Size);
    
    for (i = (ftpData->loginFailsVector.Size-1); i >= 0; i--)
    {
GOAL_98:;

        //printf("\n last login fail attempt : %d", ((loginFailsDataType *) ftpData->loginFailsVector.Data[i])->failTimeStamp);
        
        if ( (time(NULL) - ((loginFailsDataType *) ftpData->loginFailsVector.Data[i])->failTimeStamp) > WRONG_PASSWORD_ALLOWED_RETRY_TIME)
        {
GOAL_99:;

            //printf("\n Deleting element : %d", i);
            ftpData->loginFailsVector.DeleteAt(&ftpData->loginFailsVector, i, deleteLoginFailsData);
        }
    }
}

int selectWait(ftpDataType * ftpData)
{

GOAL_100:;

    struct timeval selectMaximumLockTime;
    selectMaximumLockTime.tv_sec = 10;
    selectMaximumLockTime.tv_usec = 0;
    ftpData->connectionData.rset = ftpData->connectionData.rsetAll;
    ftpData->connectionData.wset = ftpData->connectionData.wsetAll;
    ftpData->connectionData.eset = ftpData->connectionData.esetAll;
    return select(ftpData->connectionData.maxSocketFD, &ftpData->connectionData.rset, NULL, &ftpData->connectionData.eset, &selectMaximumLockTime);
}

int isClientConnected(ftpDataType * ftpData, int cliendId)
{

GOAL_101:;

    if (ftpData->clients[cliendId].socketDescriptor < 0 ||
        ftpData->clients[cliendId].socketIsConnected == 0) 
    {
GOAL_102:;

        return 0;
    }

    return 1;
}

int getAvailableClientSocketIndex(ftpDataType * ftpData)
{

GOAL_103:;

    int socketIndex;
    for (socketIndex = 0; socketIndex < ftpData->ftpParameters.maxClients; socketIndex++)
    {
GOAL_104:;

        if (isClientConnected(ftpData, socketIndex) == 0) 
        {
GOAL_105:;

            return socketIndex;
        }
    }

    /* no socket are available for a new client connection */
    return -1;
}

int evaluateClientSocketConnection(ftpDataType * ftpData)
{

GOAL_106:;

    if (FD_ISSET(ftpData->connectionData.theMainSocket, &ftpData->connectionData.rset))
    {
GOAL_107:;

        int availableSocketIndex;
        if ((availableSocketIndex = getAvailableClientSocketIndex(ftpData)) != -1) //get available socket  
        {
GOAL_109:;

            if ((ftpData->clients[availableSocketIndex].socketDescriptor = accept(ftpData->connectionData.theMainSocket, (struct sockaddr *)&ftpData->clients[availableSocketIndex].client_sockaddr_in, (socklen_t*)&ftpData->clients[availableSocketIndex].sockaddr_in_size))!=-1)
            {
GOAL_111:;

                int error, numberOfConnectionFromSameIp, i;
                numberOfConnectionFromSameIp = 0;
                ftpData->connectedClients++;
                ftpData->clients[availableSocketIndex].socketIsConnected = 1;

                error = fcntl(ftpData->clients[availableSocketIndex].socketDescriptor, F_SETFL, O_NONBLOCK);

                fdAdd(ftpData, availableSocketIndex);

                error = getsockname(ftpData->clients[availableSocketIndex].socketDescriptor, (struct sockaddr *)&ftpData->clients[availableSocketIndex].server_sockaddr_in, (socklen_t*)&ftpData->clients[availableSocketIndex].sockaddr_in_server_size);
                inet_ntop(AF_INET,
                          &(ftpData->clients[availableSocketIndex].server_sockaddr_in.sin_addr),
                          ftpData->clients[availableSocketIndex].serverIpAddress,
                          INET_ADDRSTRLEN);
                //printf("\n Server IP: %s", ftpData->clients[availableSocketIndex].serverIpAddress);
                //printf("Server: New client connected with id: %d", availableSocketIndex);
                //printf("\nServer: Clients connected: %d", ftpData->connectedClients);
                sscanf (ftpData->clients[availableSocketIndex].serverIpAddress,"%d.%d.%d.%d",   &ftpData->clients[availableSocketIndex].serverIpAddressInteger[0],
                                                                                                &ftpData->clients[availableSocketIndex].serverIpAddressInteger[1],
                                                                                                &ftpData->clients[availableSocketIndex].serverIpAddressInteger[2],
                                                                                                &ftpData->clients[availableSocketIndex].serverIpAddressInteger[3]);

                inet_ntop(AF_INET,
                          &(ftpData->clients[availableSocketIndex].client_sockaddr_in.sin_addr),
                          ftpData->clients[availableSocketIndex].clientIpAddress,
                          INET_ADDRSTRLEN);
                //printf("\n Client IP: %s", ftpData->clients[availableSocketIndex].clientIpAddress);
                ftpData->clients[availableSocketIndex].clientPort = (int) ntohs(ftpData->clients[availableSocketIndex].client_sockaddr_in.sin_port);      
                //printf("\nClient port is: %d\n", ftpData->clients[availableSocketIndex].clientPort);

                ftpData->clients[availableSocketIndex].connectionTimeStamp = (int)time(NULL);
                ftpData->clients[availableSocketIndex].lastActivityTimeStamp = (int)time(NULL);
                
                for (i = 0; i <ftpData->ftpParameters.maxClients; i++)
                {
GOAL_113:;

                    if (i == availableSocketIndex)
                    {
GOAL_114:;

                        continue;
                    }
                    
                    if (strcmp(ftpData->clients[availableSocketIndex].clientIpAddress, ftpData->clients[i].clientIpAddress) == 0) {
GOAL_115:;

                        numberOfConnectionFromSameIp++;
                    }
                }
                if (ftpData->ftpParameters.maximumConnectionsPerIp > 0 &&
                    numberOfConnectionFromSameIp >= ftpData->ftpParameters.maximumConnectionsPerIp)
                {
GOAL_116:;

                	int theReturnCode = socketPrintf(ftpData, availableSocketIndex, "sss", "530 too many connection from your ip address ", ftpData->clients[availableSocketIndex].clientIpAddress, " \r\n");
                    ftpData->clients[availableSocketIndex].closeTheClient = 1;
                }
                else
                {
GOAL_117:;

                	int returnCode = socketPrintf(ftpData, availableSocketIndex, "s", ftpData->welcomeMessage);
                	if (returnCode <= 0)
                	{
GOAL_118:;

                		ftpData->clients[availableSocketIndex].closeTheClient = 1;
                	}
                }
                
                return 1;
            }
            else
            {
GOAL_112:;

                //Errors while accepting, socket will be closed
                ftpData->clients[availableSocketIndex].closeTheClient = 1;
                printf("\n2 Errno = %d", errno);
                return 1;
            }
        }
        else
        {
GOAL_110:;

            int socketRefuseFd, socketRefuse_in_size;
            socketRefuse_in_size = sizeof(struct sockaddr_in);
            struct sockaddr_in socketRefuse_sockaddr_in;
            if ((socketRefuseFd = accept(ftpData->connectionData.theMainSocket, (struct sockaddr *)&socketRefuse_sockaddr_in, (socklen_t*)&socketRefuse_in_size))!=-1)
            {
GOAL_119:;

            	int theReturnCode = 0;
                char *messageToWrite = "10068 Server reached the maximum number of connection, please try later.\r\n";
                write(socketRefuseFd, messageToWrite, strlen(messageToWrite));
                shutdown(socketRefuseFd, SHUT_RDWR);
                theReturnCode = close(socketRefuseFd);
            }

            return 0;
        }
    }
    else
    {
GOAL_108:;

        //No new socket
        return 0;
    }
}
/*
 * auth.c
 *
 *  Created on: 30 dic 2018
 *      Author: ugo
 */

#ifdef PAM_SUPPORT_ENABLED

#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include <pwd.h>
#include <security/pam_appl.h>

#include "auth.h"
#include "ftpData.h"

struct pam_response *reply;

// //function used to get user input
int function_conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_ptr)
{
    *resp = reply;
        return PAM_SUCCESS;
}

int authenticateSystem(const char *username, const char *password)
{
    const struct pam_conv local_conversation = { function_conversation, NULL };
    pam_handle_t *local_auth_handle = NULL; // this gets set by pam_start

    int retval;
    retval = pam_start("sudo", username, &local_conversation, &local_auth_handle);

    if (retval != PAM_SUCCESS)
    {
		printf("pam_start returned: %d\n ", retval);
		return 0;
    }

    reply = (struct pam_response *)malloc(sizeof(struct pam_response));
    reply[0].resp = strdup(password);
    reply[0].resp_retcode = 0;
    retval = pam_authenticate(local_auth_handle, 0);

    if (retval != PAM_SUCCESS)
    {
		if (retval == PAM_AUTH_ERR)
		{
			printf("Authentication failure.\n");
		}
		else
		{
			printf("pam_authenticate returned %d\n", retval);
		}
		return 0;
    }

    retval = pam_end(local_auth_handle, retval);

    if (retval != PAM_SUCCESS)
    {
		printf("pam_end returned\n");
		return 0;
    }

    return 1;
}


void loginCheck(char *name, char *password, loginDataType *login, DYNMEM_MemoryTable_DataType **memoryTable)
{
    if (authenticateSystem(name, password) == 1)
    {
    	struct passwd *pass;
    	pass = getpwnam(name);

    	if (pass == NULL)
    	{
    		login->userLoggedIn = 0;
    		return;
    	}
    	else
    	{
			//printf("Authenticate with %s - %s through system\n", login, password);
			setDynamicStringDataType(&login->name, name, strlen(name), &*memoryTable);
			setDynamicStringDataType(&login->homePath, pass->pw_dir, strlen(pass->pw_dir), &*memoryTable);
			//setDynamicStringDataType(&login->homePath, "/", 1, &*memoryTable);
			setDynamicStringDataType(&login->absolutePath, pass->pw_dir, strlen(pass->pw_dir), &*memoryTable);
            setDynamicStringDataType(&login->ftpPath, "/", strlen("/"), &*memoryTable);

			if (login->homePath.text[login->homePath.textLen-1] != '/')
			{
				appendToDynamicStringDataType(&login->homePath, "/", 1, &*memoryTable);
			}

			if (login->absolutePath.text[login->absolutePath.textLen-1] != '/')
			{
				appendToDynamicStringDataType(&login->absolutePath, "/", 1, &*memoryTable);
			}

			//setDynamicStringDataType(&login->ftpPath, "/", strlen("/"), &*memoryTable);

			login->ownerShip.uid = pass->pw_gid;
			login->ownerShip.gid = pass->pw_uid;
			login->ownerShip.ownerShipSet = 1;
			login->userLoggedIn = 1;

//			printf("\nLogin as: %s", pass->pw_name);
//			printf("\nPasswd: %s", pass->pw_passwd);
//			printf("\nDir: %s", pass->pw_dir);
//			printf("\nGid: %d", pass->pw_gid);
//			printf("\nUid: %d", pass->pw_uid);
//			printf("\nlogin->homePath.text: %s", login->homePath.text);
//			printf("\nlogin->absolutePath.text: %s", login->absolutePath.text);
    	}
    }

}


#endif



/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "configRead.h"
#include "../ftpData.h"
#include "dynamicVectors.h"

#ifdef OPENSSL_ENABLED
	#include "openSsl.h"
#endif

#include "fileManagement.h"
#include "daemon.h"
#include "dynamicMemory.h"

#define PARAMETER_SIZE_LIMIT        1024

/* Private Functions */
static int parseConfigurationFile(ftpParameters_DataType *ftpParameters, DYNV_VectorGenericDataType *parametersVector);
static int searchParameter(char *name, DYNV_VectorGenericDataType *parametersVector);
static int readConfigurationFile(char *path, DYNV_VectorGenericDataType *parametersVector, DYNMEM_MemoryTable_DataType ** memoryTable);

void destroyConfigurationVectorElement(DYNV_VectorGenericDataType *theVector)
{

GOAL_120:;

    int i;
    for (i = 0; i < theVector->Size; i++)
    {
GOAL_121:;

		//printf("\n(parameter_DataType *)theVector->Data[%d])->value = %ld", i, ((parameter_DataType *)theVector->Data)->value);
		DYNMEM_free(((parameter_DataType *)theVector->Data[i])->value, &theVector->memoryTable);
		//printf("\n(parameter_DataType *)theVector->Data[%d])->name = %ld", i, ((parameter_DataType *)theVector->Data)->name);
		DYNMEM_free(((parameter_DataType *)theVector->Data[i])->name, &theVector->memoryTable);
		DYNMEM_free(theVector->Data[i], &theVector->memoryTable);
    }
}

/* Public Functions */
int searchUser(char *name, DYNV_VectorGenericDataType *usersVector)
{

GOAL_122:;

    int returnCode = -1;
    int i = 0;

    for (i = 0; i <usersVector->Size; i++)
    {
GOAL_123:;

        if (strcmp(name, ((usersParameters_DataType *) usersVector->Data[i])->name) == 0)
        {
GOAL_124:;

            return i;
        }
    }

    return returnCode;
}

void configurationRead(ftpParameters_DataType *ftpParameters, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_125:;

    int returnCode = 0;
    DYNV_VectorGenericDataType configParameters;
    DYNV_VectorGeneric_Init(&configParameters);

    if (FILE_IsFile(LOCAL_CONFIGURATION_FILENAME) == 1)
    {
GOAL_126:;

        printf("\nReading configuration from \n -> %s \n", LOCAL_CONFIGURATION_FILENAME);
        returnCode = readConfigurationFile(LOCAL_CONFIGURATION_FILENAME, &configParameters, &*memoryTable);
    }
    else 
{

GOAL_127:;
 if (FILE_IsFile(DEFAULT_CONFIGURATION_FILENAME) == 1)
    {
GOAL_128:;

        printf("\nReading configuration from \n -> %s\n", DEFAULT_CONFIGURATION_FILENAME);
        returnCode = readConfigurationFile(DEFAULT_CONFIGURATION_FILENAME, &configParameters, &*memoryTable);
    }
}


    if (returnCode == 1) 
    {
GOAL_129:;

        parseConfigurationFile(ftpParameters, &configParameters);
    }
    else
    {
GOAL_130:;

        printf("\nError: could not read the configuration file located at: \n -> %s or at \n -> %s", DEFAULT_CONFIGURATION_FILENAME, LOCAL_CONFIGURATION_FILENAME);
        exit(1);
    }

    DYNV_VectorGeneric_Destroy(&configParameters, destroyConfigurationVectorElement);
    //printf("\n\nconfigParameters.memoryTable = %d ***", configParameters.memoryTable);

    return;
}

void applyConfiguration(ftpParameters_DataType *ftpParameters)
{

GOAL_131:;

    /* Fork the process daemon mode */
    if (ftpParameters->daemonModeOn == 1)
    {
GOAL_132:;

        daemonize("uFTP");
    }

    if (ftpParameters->singleInstanceModeOn == 1)
    {
GOAL_133:;

        int returnCode = isProcessAlreadyRunning();

        if (returnCode == 1)
        {
GOAL_134:;

            printf("\nThe process is already running..");
            exit(0);
        }
    }
}

void initFtpData(ftpDataType *ftpData)
{

GOAL_135:;

    int i;
     /* Intializes random number generator */
    srand(time(NULL));    

    ftpData->generalDynamicMemoryTable = NULL;

	#ifdef OPENSSL_ENABLED
	initOpenssl();
	ftpData->serverCtx = createServerContext();
	ftpData->clientCtx = createClientContext();
	configureContext(ftpData->serverCtx, ftpData->ftpParameters.certificatePath, ftpData->ftpParameters.privateCertificatePath);
	configureClientContext(ftpData->clientCtx, ftpData->ftpParameters.certificatePath, ftpData->ftpParameters.privateCertificatePath);
	#endif

    ftpData->connectedClients = 0;
    ftpData->clients = (clientDataType *) DYNMEM_malloc((sizeof(clientDataType) * ftpData->ftpParameters.maxClients), &ftpData->generalDynamicMemoryTable, "ClientData");

	//printf("\nDYNMEM_malloc called");
	//printf("\nElement location: %ld", (long int) ftpData->generalDynamicMemoryTable);
	//printf("\nElement size: %ld", ftpData->generalDynamicMemoryTable->size);
	//printf("\nElement address: %ld", (long int) ftpData->generalDynamicMemoryTable->address);
	//printf("\nElement nextElement: %ld",(long int) ftpData->generalDynamicMemoryTable->nextElement);
	//printf("\nElement previousElement: %ld",(long int) ftpData->generalDynamicMemoryTable->previousElement);


    ftpData->serverIp.ip[0] = 127;
    ftpData->serverIp.ip[1] = 0;
    ftpData->serverIp.ip[2] = 0;
    ftpData->serverIp.ip[3] = 1;

    memset(ftpData->welcomeMessage, 0, 1024);
    strcpy(ftpData->welcomeMessage, "220 Hello\r\n");

    DYNV_VectorGeneric_InitWithSearchFunction(&ftpData->loginFailsVector, searchInLoginFailsVector);

    //Client data reset to zero
    for (i = 0; i < ftpData->ftpParameters.maxClients; i++)
    {
GOAL_136:;

        resetWorkerData(ftpData, i, 1);
        resetClientData(ftpData, i, 1);
        ftpData->clients[i].clientProgressiveNumber = i;
    }

    return;
}

/*Private functions*/
static int readConfigurationFile(char *path, DYNV_VectorGenericDataType *parametersVector, DYNMEM_MemoryTable_DataType ** memoryTable)
{

GOAL_137:;

    #define STATE_START              0
    #define STATE_NAME               1
    #define STATE_VALUE              2
    #define STATE_STORE              3
    #define STATE_TO_NEW_LINE        4

    int theFileSize = 0;
    int i, state, nameIndex, valueIndex, allowSpacesInValue;
    char * theFileContent;

    theFileSize = FILE_GetStringFromFile(path, &theFileContent, &*memoryTable);

    char name[PARAMETER_SIZE_LIMIT];
    char value[PARAMETER_SIZE_LIMIT];
    memset(name, 0, PARAMETER_SIZE_LIMIT);
    memset(value, 0, PARAMETER_SIZE_LIMIT);
    nameIndex = 0;
    valueIndex = 0;
    i = 0;
    state = STATE_START;

    allowSpacesInValue = 0;

    while (i < theFileSize)
    {
GOAL_138:;


        switch (state)
         {
            case STATE_START:
GOAL_143:;

            {
                /* Skip Special chars not allowed in the name */
                if (theFileContent[i] == ' ' ||
                    theFileContent[i] == '\r' ||
                    theFileContent[i] == '\n' ||
                    theFileContent[i] == '\t')
                {
GOAL_144:;

                i++;
                }
                /* 1st char is a sharp comment case */
                else 
{

GOAL_145:;
 if (theFileContent[i] == '#')
                {
GOAL_146:;

                    state = STATE_TO_NEW_LINE;
                    i++;
                }
                /* Name Start */
                else
                {
GOAL_147:;

                    state = STATE_NAME;
                }
}

            }
            break;

            case STATE_NAME:
GOAL_142:;

            {
                /* Not allowed chars in the name */
                if (theFileContent[i] == ' ' ||
                    theFileContent[i] == '\r' ||
                    theFileContent[i] == '\t')
                {
GOAL_148:;

                    i++;
                }
                /* Unexpected end of line no parameter acquisition */
                else 
{

GOAL_149:;
 if (theFileContent[i] == '\n')
                {
GOAL_150:;

                    i++;
                    nameIndex = 0;
                    memset(name, 0, PARAMETER_SIZE_LIMIT);
                    state = STATE_START;
                }
                /* Name ends and value starts */
                else 
{

GOAL_151:;
 if (theFileContent[i] == '=')
                {
GOAL_152:;

                    i++;
                    /* Name stored proceed to value*/
                    if (nameIndex > 0) 
{

GOAL_154:;

                        state = STATE_VALUE;
                    
}
else 
{

GOAL_155:;
 if (nameIndex == 0) 
{

GOAL_156:;
 /* No void name allowed*/
                        state = STATE_TO_NEW_LINE;
}

}

                }
                else
                {
GOAL_153:;

                    if (nameIndex < PARAMETER_SIZE_LIMIT) 
{

GOAL_157:;

                        name[nameIndex++] = theFileContent[i];
}

                    i++;
                }
}

}

            }
            break;

            case STATE_VALUE:
GOAL_141:;

            {
                /* Skip not allowed values */
                if ((theFileContent[i] == ' ' && allowSpacesInValue == 0) ||
                    theFileContent[i] == '\r' ||
                    theFileContent[i] == '\t')
                {
GOAL_158:;

                    i++;
                }
                /* Toggle the allow spaces flag */
                else 
{

GOAL_159:;
 if (theFileContent[i] == '"')
                {
GOAL_160:;

                    i++;

                    if (allowSpacesInValue == 0) 
{

GOAL_162:;

                        allowSpacesInValue = 1;
                    
}
else 
{

GOAL_163:;

                        allowSpacesInValue = 0;
}

                }    
                else 
{

GOAL_161:;
 if (theFileContent[i] == '\n' ||
                         i == (theFileSize-1))
                {
GOAL_164:;

                    /* Value stored proceed to save */
                    if (valueIndex > 0) 
                    {
GOAL_166:;

                        state = STATE_STORE;
                    }
                    else 
{

GOAL_167:;
 if (valueIndex == 0) /* No void value allowed*/
                    {
GOAL_168:;

                        memset(name, 0, PARAMETER_SIZE_LIMIT);
                        memset(value, 0, PARAMETER_SIZE_LIMIT);
                        nameIndex = 0;
                        valueIndex = 0;
                        state = STATE_START;
                    }
}

                    i++;
                }
                else
                {
GOAL_165:;

                    if (valueIndex < PARAMETER_SIZE_LIMIT) 
{

GOAL_169:;

                        value[valueIndex++] = theFileContent[i];
}

                    i++;
                }
}

}

            }
            break;

            case STATE_TO_NEW_LINE:
GOAL_140:;

            {
                /* Wait until a new line is found */
                if (theFileContent[i] == '\n')
                {
GOAL_170:;

                    state = STATE_START;
                }
                i++;
            }
            break;
            
            case STATE_STORE:
GOAL_139:;

            {
                parameter_DataType parameter;
                parameter.name = DYNMEM_malloc(nameIndex+1, &parametersVector->memoryTable, "readConfig");
                parameter.value = DYNMEM_malloc(valueIndex+1, &parametersVector->memoryTable, "readConfig");
                strcpy(parameter.name, name);
                strcpy(parameter.value, value);
                parameter.name[nameIndex]  = '\0';
                parameter.value[valueIndex] = '\0';
                memset(name, 0, PARAMETER_SIZE_LIMIT);
                memset(value, 0, PARAMETER_SIZE_LIMIT);
                nameIndex = 0;
                valueIndex = 0;
                state = STATE_START;
                //printf("\nParameter read: %s = %s", parameter.name, parameter.value);
                parametersVector->PushBack(parametersVector, &parameter, sizeof(parameter_DataType));
            }
            break;
         }
    }
    
    /* che if there is a value to store */
    if (state == STATE_STORE &&
        valueIndex > 0)
    {
GOAL_171:;

        parameter_DataType parameter;
        parameter.name = DYNMEM_malloc(nameIndex+1, &parametersVector->memoryTable, "readConfig");
        parameter.value = DYNMEM_malloc(valueIndex+1, &parametersVector->memoryTable, "readConfig");
        strcpy(parameter.name, name);
        strcpy(parameter.value, value);
        parameter.name[nameIndex]  = '\0';
        parameter.value[valueIndex] = '\0';
        memset(name, 0, PARAMETER_SIZE_LIMIT);
        memset(value, 0, PARAMETER_SIZE_LIMIT);
        nameIndex = 0;
        valueIndex = 0;
        //printf("\nParameter read: %s = %s", parameter.name, parameter.value);
        parametersVector->PushBack(parametersVector, &parameter, sizeof(parameter_DataType));
    }

    if (theFileSize > 0)
    {
GOAL_172:;

        DYNMEM_free(theFileContent, &*memoryTable);
    }

    return 1;
}

static int searchParameter(char *name, DYNV_VectorGenericDataType *parametersVector)
{

GOAL_173:;

    int returnCode = -1;
    int i = 0;
    
    for (i = 0; i <parametersVector->Size; i++)
    {
GOAL_174:;

        if (strcmp(name, ((parameter_DataType *) parametersVector->Data[i])->name) == 0)
        {
GOAL_175:;

            return i;
        }
    }
    return returnCode;
}

static int parseConfigurationFile(ftpParameters_DataType *ftpParameters, DYNV_VectorGenericDataType *parametersVector)
{

GOAL_176:;

    int searchIndex, userIndex;

    char    userX[PARAMETER_SIZE_LIMIT], 
            passwordX[PARAMETER_SIZE_LIMIT], 
            homeX[PARAMETER_SIZE_LIMIT], 
            userOwnerX[PARAMETER_SIZE_LIMIT], 
            groupOwnerX[PARAMETER_SIZE_LIMIT];
    
    //printf("\nReading configuration settings..");
    
    searchIndex = searchParameter("MAXIMUM_ALLOWED_FTP_CONNECTION", parametersVector);
    if (searchIndex != -1)
    {
GOAL_177:;

        ftpParameters->maxClients = atoi(((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nMAXIMUM_ALLOWED_FTP_CONNECTION: %d", ftpParameters->maxClients);
    }
    else
    {
GOAL_178:;

        ftpParameters->maxClients = 10;
        //printf("\nMAXIMUM_ALLOWED_FTP_CONNECTION parameter not found in the configuration file, using the default value: %d", ftpParameters->maxClients);
    }
    
    searchIndex = searchParameter("MAX_CONNECTION_NUMBER_PER_IP", parametersVector);
    if (searchIndex != -1)
    {
GOAL_179:;

        ftpParameters->maximumConnectionsPerIp = atoi(((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nMAX_CONNECTION_NUMBER_PER_IP: %d", ftpParameters->maximumConnectionsPerIp);
    }
    else
    {
GOAL_180:;

        ftpParameters->maximumConnectionsPerIp = 4;
        //printf("\nMAX_CONNECTION_NUMBER_PER_IP parameter not found in the configuration file, using the default value: %d", ftpParameters->maximumConnectionsPerIp);
    }

    searchIndex = searchParameter("MAX_CONNECTION_TRY_PER_IP", parametersVector);
    if (searchIndex != -1)
    {
GOAL_181:;

        ftpParameters->maximumUserAndPassowrdLoginTries = atoi(((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nMAX_CONNECTION_TRY_PER_IP: %d", ftpParameters->maximumUserAndPassowrdLoginTries);
    }
    else
    {
GOAL_182:;

        ftpParameters->maximumUserAndPassowrdLoginTries = 3;
        //printf("\nMAX_CONNECTION_TRY_PER_IP parameter not found in the configuration file, using the default value: %d", ftpParameters->maximumUserAndPassowrdLoginTries);
    }
    

    
    searchIndex = searchParameter("FTP_PORT", parametersVector);
    if (searchIndex != -1)
    {
GOAL_183:;

        ftpParameters->port = atoi(((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nFTP_PORT: %d", ftpParameters->port);
    }
    else
    {
GOAL_184:;

        ftpParameters->port = 21;
        //printf("\nFTP_PORT parameter not found in the configuration file, using the default value: %d", ftpParameters->maxClients);
    }
    
    
    ftpParameters->daemonModeOn = 0;
    searchIndex = searchParameter("DAEMON_MODE", parametersVector);
    if (searchIndex != -1)
    {
GOAL_185:;

        if(compareStringCaseInsensitive(((parameter_DataType *) parametersVector->Data[searchIndex])->value, "true", strlen("true")) == 1) 
{

GOAL_187:;

            ftpParameters->daemonModeOn = 1;
}

        
        //printf("\nDAEMON_MODE value: %d", ftpParameters->daemonModeOn);
    }
    else
    {
GOAL_186:;

        //printf("\nDAEMON_MODE parameter not found in the configuration file, using the default value: %d", ftpParameters->daemonModeOn);
    }
    
    ftpParameters->singleInstanceModeOn = 0;
    searchIndex = searchParameter("SINGLE_INSTANCE", parametersVector);
    if (searchIndex != -1)
    {
GOAL_188:;

        if(compareStringCaseInsensitive(((parameter_DataType *) parametersVector->Data[searchIndex])->value, "true", strlen("true")) == 1) 
{

GOAL_190:;

            ftpParameters->singleInstanceModeOn = 1;
}


    }
    else
    {
GOAL_189:;

       // printf("\nSINGLE_INSTANCE parameter not found in the configuration file, using the default value: %d", ftpParameters->singleInstanceModeOn);
    }

    ftpParameters->pamAuthEnabled = 0;
    searchIndex = searchParameter("ENABLE_PAM_AUTH", parametersVector);
    if (searchIndex != -1)
    {
GOAL_191:;

        if(compareStringCaseInsensitive(((parameter_DataType *) parametersVector->Data[searchIndex])->value, "true", strlen("true")) == 1) 
{

GOAL_193:;

        	ftpParameters->pamAuthEnabled = 1;
}

    }
    else
    {
GOAL_192:;

       // printf("\nENABLE_PAM_AUTH parameter not found in the configuration file, using the default value: %d", ftpParameters->pamAuthEnabled);
    }

    ftpParameters->maximumIdleInactivity = 3600;
    searchIndex = searchParameter("IDLE_MAX_TIMEOUT", parametersVector);
    if (searchIndex != -1)
    {
GOAL_194:;

        ftpParameters->maximumIdleInactivity = atoi(((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nIDLE_MAX_TIMEOUT value: %d", ftpParameters->maximumIdleInactivity);
    }
    else
    {
GOAL_195:;

        //printf("\nIDLE_MAX_TIMEOUT parameter not found in the configuration file, using the default value: %d", ftpParameters->maximumIdleInactivity);
    }

    searchIndex = searchParameter("FTP_SERVER_IP", parametersVector);
    if (searchIndex != -1)
    {
GOAL_196:;

        sscanf (((parameter_DataType *) parametersVector->Data[searchIndex])->value,"%d.%d.%d.%d",  &ftpParameters->ftpIpAddress[0],
                                                                                                    &ftpParameters->ftpIpAddress[1],
                                                                                                    &ftpParameters->ftpIpAddress[2],
                                                                                                    &ftpParameters->ftpIpAddress[3]);
        //printf("\nFTP_SERVER_IP value: %d.%d.%d.%d",    ftpParameters->ftpIpAddress[0],
        //                                                ftpParameters->ftpIpAddress[1],
        //                                                ftpParameters->ftpIpAddress[2],
        //                                                ftpParameters->ftpIpAddress[3]);
    }
    else
    {
GOAL_197:;

        ftpParameters->ftpIpAddress[0] = 127;
        ftpParameters->ftpIpAddress[1] = 0;
        ftpParameters->ftpIpAddress[2] = 0;
        ftpParameters->ftpIpAddress[3] = 1;       
        //printf("\nFTP_SERVER_IP parameter not found in the configuration file, listening on all available networks");
    }    
    

    searchIndex = searchParameter("CERTIFICATE_PATH", parametersVector);
    if (searchIndex != -1)
    {
GOAL_198:;

        strcpy(ftpParameters->certificatePath, ((parameter_DataType *) parametersVector->Data[searchIndex])->value);
       // printf("\nCERTIFICATE_PATH: %s", ftpParameters->certificatePath);
    }
    else
    {
GOAL_199:;

    	strcpy(ftpParameters->certificatePath, "cert.pem");
       // printf("\nCERTIFICATE_PATH parameter not found in the configuration file, using the default value: %s", ftpParameters->certificatePath);
    }

    searchIndex = searchParameter("PRIVATE_CERTIFICATE_PATH", parametersVector);
    if (searchIndex != -1)
    {
GOAL_200:;

        strcpy(ftpParameters->privateCertificatePath, ((parameter_DataType *) parametersVector->Data[searchIndex])->value);
        //printf("\nPRIVATE_CERTIFICATE_PATH: %s", ftpParameters->certificatePath);
    }
    else
    {
GOAL_201:;

    	strcpy(ftpParameters->privateCertificatePath, "key.pem");
        //printf("\nPRIVATE_CERTIFICATE_PATH parameter not found in the configuration file, using the default value: %s", ftpParameters->privateCertificatePath);
    }

    /* USER SETTINGS */
    userIndex = 0;
    memset(userX, 0, PARAMETER_SIZE_LIMIT);
    memset(passwordX, 0, PARAMETER_SIZE_LIMIT);
    memset(homeX, 0, PARAMETER_SIZE_LIMIT);
    memset(userOwnerX, 0, PARAMETER_SIZE_LIMIT);
    memset(groupOwnerX, 0, PARAMETER_SIZE_LIMIT);
    
    DYNV_VectorGeneric_Init(&ftpParameters->usersVector);
    while(1)
    {
GOAL_202:;

        int searchUserIndex, searchPasswordIndex, searchHomeIndex, searchUserOwnerIndex, searchGroupOwnerIndex, returnCode;
        usersParameters_DataType userData;

        returnCode = snprintf(userX, PARAMETER_SIZE_LIMIT, "USER_%d", userIndex);
        returnCode = snprintf(passwordX, PARAMETER_SIZE_LIMIT, "PASSWORD_%d", userIndex);
        returnCode = snprintf(homeX, PARAMETER_SIZE_LIMIT, "HOME_%d", userIndex);
        returnCode = snprintf(groupOwnerX, PARAMETER_SIZE_LIMIT, "GROUP_NAME_OWNER_%d", userIndex);
        returnCode = snprintf(userOwnerX, PARAMETER_SIZE_LIMIT, "USER_NAME_OWNER_%d", userIndex);
        userIndex++;
        
        searchUserIndex = searchParameter(userX, parametersVector);
        searchPasswordIndex = searchParameter(passwordX, parametersVector);
        searchHomeIndex = searchParameter(homeX, parametersVector);
        searchUserOwnerIndex = searchParameter(userOwnerX, parametersVector);
        searchGroupOwnerIndex = searchParameter(groupOwnerX, parametersVector);        
        
        //printf("\ngroupOwnerX = %s", groupOwnerX);
        //printf("\nuserOwnerX = %s", userOwnerX);
        //printf("\nsearchUserOwnerIndex = %d", searchUserOwnerIndex);
        //printf("\nsearchGroupOwnerIndex = %d", searchGroupOwnerIndex);

        
        if (searchUserIndex == -1 ||
            searchPasswordIndex == -1 ||
            searchHomeIndex == -1)
        {
GOAL_203:;

            //printf("\n BREAK ");
            break;
        }

        userData.ownerShip.groupOwnerString = NULL;
        userData.ownerShip.userOwnerString = NULL;

        userData.name = DYNMEM_malloc((strlen(((parameter_DataType *) parametersVector->Data[searchUserIndex])->value) + 1), &ftpParameters->usersVector.memoryTable, "userData");
        userData.password = DYNMEM_malloc((strlen(((parameter_DataType *) parametersVector->Data[searchPasswordIndex])->value) + 1), &ftpParameters->usersVector.memoryTable, "userData");
        userData.homePath = DYNMEM_malloc((strlen(((parameter_DataType *) parametersVector->Data[searchHomeIndex])->value) + 1), &ftpParameters->usersVector.memoryTable, "userData");

        strcpy(userData.name, ((parameter_DataType *) parametersVector->Data[searchUserIndex])->value);
        strcpy(userData.password, ((parameter_DataType *) parametersVector->Data[searchPasswordIndex])->value);
        strcpy(userData.homePath, ((parameter_DataType *) parametersVector->Data[searchHomeIndex])->value);

        userData.name[strlen(((parameter_DataType *) parametersVector->Data[searchUserIndex])->value)] = '\0';
        userData.password[strlen(((parameter_DataType *) parametersVector->Data[searchPasswordIndex])->value)] = '\0';
        userData.homePath[strlen(((parameter_DataType *) parametersVector->Data[searchHomeIndex])->value)] = '\0';
        
        if (searchUserOwnerIndex != -1 &&
            searchGroupOwnerIndex != -1)
        {
GOAL_204:;

            userData.ownerShip.groupOwnerString = DYNMEM_malloc((strlen(((parameter_DataType *) parametersVector->Data[searchGroupOwnerIndex])->value) + 1), &ftpParameters->usersVector.memoryTable, "userOwnershipData");
            userData.ownerShip.userOwnerString  = DYNMEM_malloc((strlen(((parameter_DataType *) parametersVector->Data[searchUserOwnerIndex])->value) + 1), &ftpParameters->usersVector.memoryTable, "userOwnershipData");

            strcpy(userData.ownerShip.groupOwnerString, ((parameter_DataType *) parametersVector->Data[searchGroupOwnerIndex])->value);
            strcpy(userData.ownerShip.userOwnerString, ((parameter_DataType *) parametersVector->Data[searchUserOwnerIndex])->value);

            userData.ownerShip.groupOwnerString[strlen(((parameter_DataType *) parametersVector->Data[searchGroupOwnerIndex])->value)] = '\0';
            userData.ownerShip.userOwnerString[strlen(((parameter_DataType *) parametersVector->Data[searchUserOwnerIndex])->value)] = '\0';
            
            userData.ownerShip.gid = FILE_getGID(userData.ownerShip.groupOwnerString);
            userData.ownerShip.uid = FILE_getUID(userData.ownerShip.userOwnerString);


            if (userData.ownerShip.gid != -1 &&
            	userData.ownerShip.uid != -1)
            {
GOAL_206:;

            	userData.ownerShip.ownerShipSet = 1;
            }
            else
            {
GOAL_207:;

                userData.ownerShip.gid = 0;
                userData.ownerShip.uid = 0;
            	userData.ownerShip.ownerShipSet = 0;
            }
        }
        else
        {
GOAL_205:;

            userData.ownerShip.ownerShipSet = 0;
            userData.ownerShip.gid = 0;
            userData.ownerShip.uid = 0;
            userData.ownerShip.groupOwnerString = NULL;
            userData.ownerShip.userOwnerString  = NULL;
        }
//
//        printf("\n\nUser parameter found");
//        printf("\nName: %s", userData.name);
//        printf("\nPassword: %s", userData.password);
//        printf("\nHomePath: %s", userData.homePath);
//        printf("\ngroupOwnerStr: %s", userData.ownerShip.groupOwnerString);
//        printf("\nuserOwnerStr: %s", userData.ownerShip.userOwnerString);
//        printf("\nuserData.gid = %d", userData.ownerShip.gid);
//        printf("\nuserData.uid = %d", userData.ownerShip.uid);
//        printf("\nuserData.ownerShipSet = %d", userData.ownerShip.ownerShipSet);
        ftpParameters->usersVector.PushBack(&ftpParameters->usersVector, &userData, sizeof(usersParameters_DataType));
    }

    return 1;
}
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <syslog.h>
#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/resource.h>
#include <signal.h>

#include "fileManagement.h"

#define LOCKFILE "/var/run/uFTP.pid"
#define LOCKMODE (S_IRUSR|S_IWUSR|S_IRGRP|S_IROTH)
#define MAXIMUM_IDLE_TIME			60

static int WatchDogTime = 0, WatchDogTimerTimeOut = MAXIMUM_IDLE_TIME;

int isProcessAlreadyRunning(void)
{

GOAL_208:;

    int fd;
    int returnCode;
    char buf[30];
    memset(buf, 0,30);
    fd = open(LOCKFILE, O_RDWR|O_CREAT, LOCKMODE);
    if (fd < 0) 
    {
GOAL_209:;

        syslog(LOG_ERR, "can’t open %s: %s", LOCKFILE, strerror(errno));
        exit(1);
    }
    //printf("\nFile pid opened.");
    
    if ((returnCode = FILE_LockFile(fd)) < 0) 
    {
GOAL_210:;

        if (errno == EACCES || errno == EAGAIN) 
        {
GOAL_211:;

        close(fd);
        return(1);
        }
        syslog(LOG_ERR, "can’t lock %s: %s", LOCKFILE, strerror(errno));
        exit(1);
    }
    
    //printf("\nFILE_LockFile returnCode = %d", returnCode);    
    ftruncate(fd, 0);
    returnCode = snprintf(buf, 100, "%ld", (long)getpid());
    returnCode = write(fd, buf, strlen(buf)+1);
    return(0);
}

void daemonize(const char *cmd)
	{

GOAL_212:;

    int
    i, fd0, fd1, fd2;
    pid_t pid;
    struct rlimit rl;
    struct sigaction sa;
    
    /*
    * Clear file creation mask.
    */
    umask(0);
    
    /*
    * Get maximum number of file descriptors.
    */
    if (getrlimit(RLIMIT_NOFILE, &rl) < 0) 
{

GOAL_213:;

    printf("%s: can’t get file limit", cmd);
}

    
    /*
    * Become a session leader to lose controlling TTY.
    */
    if ((pid = fork()) < 0) 
{

GOAL_214:;

        printf("%s: can’t fork", cmd);
    
}
else 
{

GOAL_215:;
 if (pid != 0) 
{

GOAL_216:;
 /* parent */
        exit(0);
}

}

    
    setsid();
    
    /*
    * Ensure future opens won’t allocate controlling TTYs.
    */
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    
    sa.sa_flags = 0;
    if (sigaction(SIGHUP, &sa, NULL) < 0) 
{

GOAL_217:;

        printf("%s: can’t ignore SIGHUP", cmd);
}

    if ((pid = fork()) < 0) 
{

GOAL_218:;

        printf("%s: can’t fork", cmd);
    
}
else 
{

GOAL_219:;
 if (pid != 0) 
{

GOAL_220:;
 /* parent */
    exit(0);
}

}

    /*
    * Change the current working directory to the root so
    * we won’t prevent file systems from being unmounted.
    */
    if (chdir("/") < 0) 
{

GOAL_221:;

        printf("%s: can’t change directory to /", cmd);
}

    /*
    * Close all open file descriptors.
    */
    if (rl.rlim_max == RLIM_INFINITY) 
{

GOAL_222:;

        rl.rlim_max = 1024;
}

    for (i = 0; i < rl.rlim_max; i++) 
{

GOAL_223:;

        close(i);
}

    /*
    * Attach file descriptors 0, 1, and 2 to /dev/null.
    */
    fd0 = open("/dev/null", O_RDWR);
    fd1 = dup(0);
    fd2 = dup(0);
    }

void respawnProcess(void)
	{

GOAL_224:;

	  pid_t spawnedProcess;

	  //Respawn
	  while(1)
			{
GOAL_225:;

			spawnedProcess = fork();

			if (spawnedProcess == 0)
				{
GOAL_226:;

				//is child, exit from the loop
				printf("\nRespawn mode is active");
				break;
				}
			else
				{
GOAL_227:;

				int returnStatus;
				waitpid(spawnedProcess, &returnStatus, 0);
				printf("\nwaitpid done with status: %d", returnStatus);

				if (WIFEXITED(returnStatus))
					{
GOAL_228:;

					if (WEXITSTATUS(returnStatus) == 99)
						{
GOAL_229:;

						printf("\nWIFEXITED verified the respawn is now disabled with return code %d.", WEXITSTATUS(returnStatus));
						exit(3);
						}
					}
				sleep(1);
				}
			}
		return;
	}

void *watchDog(void * arg)
{

GOAL_230:;

	WatchDogTime = (int)time(NULL);

	while(1)
	{
GOAL_231:;

		//Check if the time is expired
		if ((int)time(NULL) - WatchDogTime > WatchDogTimerTimeOut)
		{
GOAL_232:;

			printf("\nWatchDog Time Expired");
			exit(98);
		}

		//printf("\nWatchDog Time ok %d, %d", (int)time(NULL), WatchDogTime);

		sleep(5);
	}
}

void setWatchDogTimeout(int theTime)
{

GOAL_233:;

	WatchDogTimerTimeOut = theTime;
}

void updateWatchDogTime(int theTime)
{

GOAL_234:;

	WatchDogTime = theTime;
}
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
#ifdef OPENSSL_ENABLED
#include <stdio.h>
#include <unistd.h>
#include <sys/socket.h>
#include <string.h>
#include <arpa/inet.h>
#include <openssl/ssl.h>
#include <openssl/err.h>

#include "openSsl.h"
#include "fileManagement.h"




#define MUTEX_TYPE       pthread_mutex_t
#define MUTEX_SETUP(x)   pthread_mutex_init(&(x), NULL)
#define MUTEX_CLEANUP(x) pthread_mutex_destroy(&(x))
#define MUTEX_LOCK(x)    pthread_mutex_lock(&(x))
#define MUTEX_UNLOCK(x)  pthread_mutex_unlock(&(x))
#define THREAD_ID        pthread_self()

/* This array will store all of the mutexes available to OpenSSL. */
static MUTEX_TYPE *mutex_buf = NULL;

void initOpenssl()
{
    OpenSSL_add_all_algorithms();		/* Load cryptos, et.al. */
    SSL_load_error_strings();			/* Bring in and register error messages */
    ERR_load_BIO_strings();
    ERR_load_crypto_strings();
    SSL_library_init();
    thread_setup();
}

void cleanupOpenssl()
{
	thread_cleanup();
    EVP_cleanup();

}

SSL_CTX *createServerContext()
{
    const SSL_METHOD *method;
    SSL_CTX *ctx;

    method = TLS_server_method();

    ctx = SSL_CTX_new(method);
    if (!ctx)
    {
		perror("Unable to create server SSL context");
		ERR_print_errors_fp(stderr);
		exit(0);
    }

    return ctx;
}

SSL_CTX *createClientContext(void)
{
	const SSL_METHOD *method;
    SSL_CTX *ctx;
    method = TLS_client_method();		/* Create new client-method instance */
    ctx = SSL_CTX_new(method);			/* Create new context */
    //SSL_CTX_set_options(ctx, SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);
    //SSL_CTX_set_options(ctx, SSL_OP_NO_SESSION_RESUMPTION_ON_RENEGOTIATION | SSL_OP_CIPHER_SERVER_PREFERENCE| SSL_OP_NO_SSLv2 | SSL_OP_NO_SSLv3 | SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1);
    //SSL_CTX_set_ecdh_auto(ctx, 1);

    if (ctx == NULL)
    {
    	perror("Unable to create server SSL context");
        ERR_print_errors_fp(stderr);
        abort();
        exit(0);
    }
    return ctx;
}


void configureClientContext(SSL_CTX *ctx, char *certificatePath, char* privateCertificatePath)
{/*
	if (FILE_IsFile(certificatePath) != 1)
	{
		printf("\ncertificate file: %s not found!", certificatePath);
		exit(0);
	}

	if (FILE_IsFile(privateCertificatePath) != 1)
	{
		printf("\ncertificate file: %s not found!", privateCertificatePath);
		exit(0);
	}

     Set the key and cert
    if (SSL_CTX_use_certificate_file(ctx, certificatePath, SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    if (SSL_CTX_use_PrivateKey_file(ctx, privateCertificatePath, SSL_FILETYPE_PEM) <= 0 ) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    } */
}

void configureContext(SSL_CTX *ctx, char *certificatePath, char* privateCertificatePath)
{
	if (FILE_IsFile(certificatePath) != 1)
	{
		printf("\ncertificate file: %s not found!", certificatePath);
		exit(0);
	}

	if (FILE_IsFile(privateCertificatePath) != 1)
	{
		printf("\ncertificate file: %s not found!", privateCertificatePath);
		exit(0);
	}

    SSL_CTX_set_ecdh_auto(ctx, 1);

    /* Set the key and cert */
    if (SSL_CTX_use_certificate_file(ctx, certificatePath, SSL_FILETYPE_PEM) <= 0) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }

    if (SSL_CTX_use_PrivateKey_file(ctx, privateCertificatePath, SSL_FILETYPE_PEM) <= 0 ) {
        ERR_print_errors_fp(stderr);
        exit(EXIT_FAILURE);
    }
}


void ShowCerts(SSL* ssl)
{   X509 *cert;
    char *line;

    cert = SSL_get_peer_certificate(ssl);	/* get the server's certificate */
    if ( cert != NULL )
    {
        printf("Server certificates:\n");
        line = X509_NAME_oneline(X509_get_subject_name(cert), 0, 0);
        printf("Subject: %s\n", line);
        free(line);							/* free the malloc'ed string */
        line = X509_NAME_oneline(X509_get_issuer_name(cert), 0, 0);
        printf("Issuer: %s\n", line);
        free(line);							/* free the malloc'ed string */
        X509_free(cert);					/* free the malloc'ed certificate copy */
    }
    else
        printf("No certificates.\n");
}


void handle_error(const char *file, int lineno, const char *msg)
{
  fprintf(stderr, "** %s:%d %s\n", file, lineno, msg);
  ERR_print_errors_fp(stderr);
  /* exit(-1); */
}

static void locking_function(int mode, int n, const char *file, int line)
{
  if(mode & CRYPTO_LOCK)
    MUTEX_LOCK(mutex_buf[n]);
  else
    MUTEX_UNLOCK(mutex_buf[n]);
}

static unsigned long id_function(void)
{
  return ((unsigned long)THREAD_ID);
}

int thread_setup(void)
{
  int i;

  mutex_buf = malloc(CRYPTO_num_locks() * sizeof(MUTEX_TYPE));
  if(!mutex_buf)
    return 0;
  for(i = 0;  i < CRYPTO_num_locks();  i++)
    MUTEX_SETUP(mutex_buf[i]);
  CRYPTO_set_id_callback(id_function);
  CRYPTO_set_locking_callback(locking_function);
  return 1;
}

int thread_cleanup(void)
{
  int i;

  if(!mutex_buf)
    return 0;
  CRYPTO_set_id_callback(NULL);
  CRYPTO_set_locking_callback(NULL);
  for(i = 0;  i < CRYPTO_num_locks();  i++)
    MUTEX_CLEANUP(mutex_buf[i]);
  free(mutex_buf);
  mutex_buf = NULL;
  return 1;
}

#endif
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <time.h>
#include "logFunctions.h"
#include <sys/time.h>
#include <stdlib.h>
#include <stdio.h>

void printTimeStamp(void)
{

GOAL_235:;

   // time_t ltime; /* calendar time */
   // ltime=time(NULL); /* get current cal time */
   // printf("\n\n %s -->",asctime( localtime(&ltime) ) );
}

void makeTimeout(struct timespec *tsp, long seconds)
{

GOAL_236:;

    struct timeval now;
    /* get the current time */
    gettimeofday(&now, NULL);
    tsp->tv_sec = now.tv_sec;
    tsp->tv_nsec = now.tv_usec * 1000; /* usec to nsec */
    /* add the offset to get timeout value */
    tsp->tv_sec += seconds;
}/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <stdio.h>
#include <signal.h>
#include <stdlib.h>
#include <string.h>
#include "../ftpServer.h"

static void ignore_sigpipe(void);

/* Catch Signal Handler functio */
void signal_callback_handler(int signum) 
{

GOAL_237:;


GOAL_463:;

    printf("Caught signal SIGPIPE %d\n",signum);
}

static void ignore_sigpipe(void)
{

GOAL_238:;

        // ignore SIGPIPE (or else it will bring our program down if the client
        // closes its socket).
        // NB: if running under gdb, you might need to issue this gdb command:
        //          handle SIGPIPE nostop noprint pass
        //     because, by default, gdb will stop our program execution (which we
        //     might not want).
        struct sigaction sa;

        memset(&sa, 0, sizeof(sa));
        sa.sa_handler = SIG_IGN;

        if (sigemptyset(&sa.sa_mask) < 0 || sigaction(SIGPIPE, &sa, 0) < 0) {
GOAL_239:;

                perror("Could not ignore the SIGPIPE signal");
                exit(0);
        }
}

void onUftpClose(int sig)
{

GOAL_240:;


GOAL_464:;

    printf("\nuFTP exit()\n");
    deallocateMemory();
    exit(0);
}

void signalHandlerInstall(void)
{

GOAL_241:;


GOAL_462:;

    //signal(SIGPIPE, signal_callback_handler);
    signal(SIGINT,onUftpClose);	
    signal(SIGUSR2,SIG_IGN);	
    signal(SIGPIPE,SIG_IGN);
    signal(SIGALRM,SIG_IGN);
    signal(SIGTSTP,SIG_IGN);
    signal(SIGTTIN,SIG_IGN);
    signal(SIGTTOU,SIG_IGN);
    signal(SIGURG,SIG_IGN);
    signal(SIGXCPU,SIG_IGN);
    signal(SIGXFSZ,SIG_IGN);
    signal(SIGVTALRM,SIG_IGN);
    signal(SIGPROF,SIG_IGN);
    signal(SIGIO,SIG_IGN);
    signal(SIGCHLD,SIG_IGN);
}/*
 * errorHandling.c
 *
 *  Created on: 22 dic 2018
 *      Author: ugo
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "errorHandling.h"


void report_error(const char *msg, const char *file, int line_no, int use_perror)
{

GOAL_242:;

	fprintf(stderr,"[%s:%d] ",file,line_no);

	if(use_perror != 0)
	{
GOAL_243:;

		perror(msg);
	}
	else
	{
GOAL_244:;

		fprintf(stderr, "%s\n",msg);
	}
}

void report_error_q(const char *msg, const char *file, int line_no, int use_perror)
{

GOAL_245:;

	report_error(msg, file, line_no, use_perror);
	exit(EXIT_FAILURE);
}
/*
 * auth.c
 *
 *  Created on: 30 dic 2018
 *      Author: ugo
 */

#ifdef PAM_SUPPORT_ENABLED

#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include <pwd.h>
#include <security/pam_appl.h>

#include "auth.h"
#include "ftpData.h"

struct pam_response *reply;

// //function used to get user input
int function_conversation(int num_msg, const struct pam_message **msg, struct pam_response **resp, void *appdata_ptr)
{
    *resp = reply;
        return PAM_SUCCESS;
}

int authenticateSystem(const char *username, const char *password)
{
    const struct pam_conv local_conversation = { function_conversation, NULL };
    pam_handle_t *local_auth_handle = NULL; // this gets set by pam_start

    int retval;
    retval = pam_start("sudo", username, &local_conversation, &local_auth_handle);

    if (retval != PAM_SUCCESS)
    {
		printf("pam_start returned: %d\n ", retval);
		return 0;
    }

    reply = (struct pam_response *)malloc(sizeof(struct pam_response));
    reply[0].resp = strdup(password);
    reply[0].resp_retcode = 0;
    retval = pam_authenticate(local_auth_handle, 0);

    if (retval != PAM_SUCCESS)
    {
		if (retval == PAM_AUTH_ERR)
		{
			printf("Authentication failure.\n");
		}
		else
		{
			printf("pam_authenticate returned %d\n", retval);
		}
		return 0;
    }

    retval = pam_end(local_auth_handle, retval);

    if (retval != PAM_SUCCESS)
    {
		printf("pam_end returned\n");
		return 0;
    }

    return 1;
}


void loginCheck(char *name, char *password, loginDataType *login, DYNMEM_MemoryTable_DataType **memoryTable)
{
    if (authenticateSystem(name, password) == 1)
    {
    	struct passwd *pass;
    	pass = getpwnam(name);

    	if (pass == NULL)
    	{
    		login->userLoggedIn = 0;
    		return;
    	}
    	else
    	{
			//printf("Authenticate with %s - %s through system\n", login, password);
			setDynamicStringDataType(&login->name, name, strlen(name), &*memoryTable);
			setDynamicStringDataType(&login->homePath, pass->pw_dir, strlen(pass->pw_dir), &*memoryTable);
			//setDynamicStringDataType(&login->homePath, "/", 1, &*memoryTable);
			setDynamicStringDataType(&login->absolutePath, pass->pw_dir, strlen(pass->pw_dir), &*memoryTable);
            setDynamicStringDataType(&login->ftpPath, "/", strlen("/"), &*memoryTable);

			if (login->homePath.text[login->homePath.textLen-1] != '/')
			{
				appendToDynamicStringDataType(&login->homePath, "/", 1, &*memoryTable);
			}

			if (login->absolutePath.text[login->absolutePath.textLen-1] != '/')
			{
				appendToDynamicStringDataType(&login->absolutePath, "/", 1, &*memoryTable);
			}

			//setDynamicStringDataType(&login->ftpPath, "/", strlen("/"), &*memoryTable);

			login->ownerShip.uid = pass->pw_gid;
			login->ownerShip.gid = pass->pw_uid;
			login->ownerShip.ownerShipSet = 1;
			login->userLoggedIn = 1;

//			printf("\nLogin as: %s", pass->pw_name);
//			printf("\nPasswd: %s", pass->pw_passwd);
//			printf("\nDir: %s", pass->pw_dir);
//			printf("\nGid: %d", pass->pw_gid);
//			printf("\nUid: %d", pass->pw_uid);
//			printf("\nlogin->homePath.text: %s", login->homePath.text);
//			printf("\nlogin->absolutePath.text: %s", login->absolutePath.text);
    	}
    }

}


#endif



/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <pwd.h>
#include <grp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/resource.h>

#include "fileManagement.h"
#include "dynamicVectors.h"
#include "dynamicMemory.h"

static int FILE_CompareString(const void * a, const void * b);
static int FILE_CompareString(const void * a, const void * b)
{

GOAL_246:;

    return strcmp (*(const char **) a, *(const char **) b);
}

static int FILE_CompareStringParameter(const void * a, const void * b);

static int FILE_CompareStringParameter(const void * a, const void * b)
{

GOAL_247:;

    const FILE_StringParameter_DataType * typeA = *(const FILE_StringParameter_DataType **)a;
    const FILE_StringParameter_DataType * typeB = *(const FILE_StringParameter_DataType **)b;
   //printf("Comparing  %s with %s",typeA->Name, typeB->Name);
    return strcmp(typeA->Name, typeB->Name);
}

int FILE_fdIsValid(int fd)
{

GOAL_248:;

    return fcntl(fd, F_GETFD);
}

/* Check if inode is a directory */
int FILE_IsDirectory(char *DirectoryPath)
{

GOAL_249:;

    struct stat sb;
    if (stat(DirectoryPath, &sb) == 0 && S_ISDIR(sb.st_mode))
    {
GOAL_250:;

        return 1;
    }
    else
    {
GOAL_251:;

        return 0;
    }
    
    return 0;
}

long int FILE_GetAvailableSpace(const char* path)
{

GOAL_252:;

    struct statvfs stat;

    if (statvfs(path, &stat) != 0)
    {
GOAL_253:;

        // error happens, just quits here
        return -1;
    }

    // the available size is f_bsize * f_bavail
    return stat.f_bsize * stat.f_bavail;
}

/* Get the file size */
long long int FILE_GetFileSize(FILE *TheFilePointer)
{

GOAL_254:;

#ifdef LARGE_FILE_SUPPORT_ENABLED
	//#warning LARGE FILE SUPPORT IS ENABLED!
    long long int Prev = 0, TheFileSize = 0;
    Prev = ftello64(TheFilePointer);
    fseeko64(TheFilePointer, 0, SEEK_END);
    TheFileSize = ftello64(TheFilePointer);
    fseeko64(TheFilePointer, Prev, SEEK_SET);
    return TheFileSize;
#endif

#ifndef LARGE_FILE_SUPPORT_ENABLED
	#warning LARGE FILE SUPPORT IS NOT ENABLED!
    long long int Prev = 0, TheFileSize = 0;
    Prev = ftell(TheFilePointer);
    fseek(TheFilePointer, 0, SEEK_END);
    TheFileSize = ftell(TheFilePointer);
    fseek(TheFilePointer, Prev, SEEK_SET);
    return TheFileSize;
#endif
}

long long int FILE_GetFileSizeFromPath(char *TheFileName)
{

GOAL_255:;



#ifdef LARGE_FILE_SUPPORT_ENABLED
	//#warning LARGE FILE SUPPORT IS ENABLED!
  if (FILE_IsFile(TheFileName) == 1)
  {
      FILE *TheFilePointer;
      TheFilePointer = fopen64(TheFileName, "rb");
      long long int Prev = 0, TheFileSize = 0;
      Prev = ftello64(TheFilePointer);
      fseeko64(TheFilePointer, 0L, SEEK_END);
      TheFileSize = ftello64(TheFilePointer);
      fseeko64(TheFilePointer, Prev, SEEK_SET);
      fclose(TheFilePointer);
      return TheFileSize;
  }
  else
  {
      return 0;
  }
#endif

#ifndef LARGE_FILE_SUPPORT_ENABLED
#warning LARGE FILE SUPPORT IS NOT ENABLED!
  if (FILE_IsFile(TheFileName) == 1)
  {
GOAL_256:;

      FILE *TheFilePointer;
      TheFilePointer = fopen(TheFileName, "rb");
      long long int Prev = 0, TheFileSize = 0;
      Prev = ftell(TheFilePointer);
      fseek(TheFilePointer, 0L, SEEK_END);
      TheFileSize = ftell(TheFilePointer);
      fseek(TheFilePointer, Prev, SEEK_SET);
      fclose(TheFilePointer);
      return TheFileSize;
  }
  else
  {
GOAL_257:;

      return 0;
  }
#endif


}

/* Check if a file is valid */
int FILE_IsFile(const char *TheFileName)
{

GOAL_258:;

    FILE *TheFile;

    #ifdef LARGE_FILE_SUPPORT_ENABLED
	//#warning LARGE FILE SUPPORT IS ENABLED!
      TheFile = fopen64(TheFileName, "rb");
    #endif

    #ifndef LARGE_FILE_SUPPORT_ENABLED
#warning LARGE FILE SUPPORT IS NOT ENABLED!
      TheFile = fopen(TheFileName, "rb");
    #endif

    if (TheFile != NULL)
      {
GOAL_259:;

          fclose(TheFile);
          return 1;
      }

    return 0;
}

void FILE_GetDirectoryInodeList(char * DirectoryInodeName, char *** InodeList, int * FilesandFolders, int Recursive, DYNMEM_MemoryTable_DataType ** memoryTable)
{

GOAL_260:;

    int FileAndFolderIndex = *FilesandFolders;

    //Allocate the array for the 1st time
    if (*InodeList == NULL)
    {
GOAL_261:;

        (*InodeList) = (char **) DYNMEM_malloc(sizeof(char *) * (1), &*memoryTable, "InodeList");
    }

    
    if (FILE_IsDirectory(DirectoryInodeName))
    {
GOAL_262:;

        //printf("\nReading directory: %s", DirectoryInodeName);
        
        DIR *TheDirectory;
        struct dirent *dir;
        TheDirectory = opendir(DirectoryInodeName);
        if (TheDirectory)
        {
GOAL_264:;

            
            
            while ((dir = readdir(TheDirectory)) != NULL)
            {
GOAL_265:;

                if ( dir->d_name[0] == '.' && strlen(dir->d_name) == 1) 
{

GOAL_266:;

                    continue;
}


                if ( dir->d_name[0] == '.' && dir->d_name[1] == '.' && strlen(dir->d_name) == 2) 
{

GOAL_267:;

                    continue;                                
}


                //Set the row to needed size
                int ReallocSize = sizeof(char *) * (FileAndFolderIndex+1)+1;
                (*InodeList) = (char ** ) DYNMEM_realloc((*InodeList), ReallocSize, &*memoryTable);
                int nsize = strlen(dir->d_name) * sizeof(char) + strlen(DirectoryInodeName) * sizeof(char) + 2;
                //Allocate the path string size
                (*InodeList)[FileAndFolderIndex]  = (char *) DYNMEM_malloc (nsize , &*memoryTable, "InodeList");
                strcpy((*InodeList)[FileAndFolderIndex], DirectoryInodeName );
                strcat((*InodeList)[FileAndFolderIndex], "/" );
                strcat((*InodeList)[FileAndFolderIndex], dir->d_name );
                (*InodeList)[FileAndFolderIndex][ strlen(dir->d_name)  + strlen(DirectoryInodeName) + 1 ] = '\0';
                (*FilesandFolders)++;
                FileAndFolderIndex++;

                if ( Recursive == 1 && FILE_IsDirectory((*InodeList)[*FilesandFolders-1]) == 1  )
                {
GOAL_268:;

                    FILE_GetDirectoryInodeList ( (*InodeList)[FileAndFolderIndex-1], InodeList, FilesandFolders, Recursive, &*memoryTable);
                    FileAndFolderIndex = (*FilesandFolders);
                }

            }
            closedir(TheDirectory);
        }

        qsort ((*InodeList), *FilesandFolders, sizeof (const char *), FILE_CompareString);
    }
    else 
{

GOAL_263:;
 if (FILE_IsFile(DirectoryInodeName))
    {
GOAL_269:;

        //printf("\nAdding single file to inode list: %s", DirectoryInodeName);
        int ReallocSize = sizeof(char *) * (FileAndFolderIndex+1)+1;
        (*InodeList) = (char ** ) DYNMEM_realloc((*InodeList), ReallocSize, &*memoryTable);
        int nsize = strlen(DirectoryInodeName) * sizeof(char) + 2;

        (*InodeList)[FileAndFolderIndex]  = (char *) DYNMEM_malloc (nsize, &*memoryTable, "InodeList");
        strcpy((*InodeList)[FileAndFolderIndex], DirectoryInodeName );
        (*InodeList)[FileAndFolderIndex][strlen(DirectoryInodeName)] = '\0';
        (*FilesandFolders)++;
        FileAndFolderIndex++;
    }
    else
    {
GOAL_270:;

        //printf("\n%s is not a file or a directory", DirectoryInodeName);
        //No valid path specified, returns zero elements
        (*FilesandFolders) = 0;
    }
}

}

int FILE_GetDirectoryInodeCount(char * DirectoryInodeName)
{

GOAL_271:;

    int FileAndFolderIndex = 0;

    DIR *TheDirectory;
    struct dirent *dir;
    TheDirectory = opendir(DirectoryInodeName);

    if (TheDirectory)
    {
GOAL_272:;

        while ((dir = readdir(TheDirectory)) != NULL)
        {
GOAL_273:;

            if ( dir->d_name[0] == '.' && strlen(dir->d_name) == 1) 
{

GOAL_274:;

                continue;
}


            if ( dir->d_name[0] == '.' && dir->d_name[1] == '.' && strlen(dir->d_name) == 2) 
{

GOAL_275:;

                continue;                                
}


            FileAndFolderIndex++;

        }
        
        closedir(TheDirectory);
    }

    return FileAndFolderIndex;
}

int FILE_GetStringFromFile(char * filename, char **file_content, DYNMEM_MemoryTable_DataType ** memoryTable)
{

GOAL_276:;

    long long int file_size = 0;
    int c, count;

    if (FILE_IsFile(filename) == 0)
    {
GOAL_277:;

        return 0;
    }


    #ifdef LARGE_FILE_SUPPORT_ENABLED
		//#warning LARGE FILE SUPPORT IS ENABLED!
        FILE *file = fopen64(filename, "rb");
    #endif

    #ifndef LARGE_FILE_SUPPORT_ENABLED
#warning LARGE FILE SUPPORT IS NOT ENABLED!
        FILE *file = fopen(filename, "rb");
    #endif

    if (file == NULL)
    {
GOAL_278:;

        fclose(file);
        return 0;
    }

    file_size = FILE_GetFileSize(file);

    count = 0;
    *file_content  = (char *) DYNMEM_malloc((file_size * sizeof(char) + 100), &*memoryTable, "getstringfromfile");

    while ((c = fgetc(file)) != EOF)
    {
GOAL_279:;

        (*file_content)[count++] = (char) c;
    }
    (*file_content)[count] = '\0';



    fclose(file);



    return count;
}

void FILE_ReadStringParameters(char * filename, DYNV_VectorGenericDataType *ParametersVector)
{

GOAL_280:;

    FILE *File;
    char Line[FILE_MAX_LINE_LENGHT];
    int i;
    int c;
    char FirstChar = 0;
    char SeparatorChar = 0;
    char ParameterChar = 0;
    int BufferNameCursor = 0;
    int BufferValueCursor = 0;
    FILE_StringParameter_DataType TheParameter;

    memset (TheParameter.Name, 0, FILE_MAX_PAR_VAR_SIZE);
    memset (TheParameter.Value, 0, FILE_MAX_PAR_VAR_SIZE);

    File = fopen(filename, "r");
    if(File == NULL)
    {
GOAL_281:;

        printf("error while opening file %s", filename);
    }
    else
    {
GOAL_282:;

    //printf("Parameter initializing from file %s", filename);

    while(fgets(Line, FILE_MAX_LINE_LENGHT, File) != NULL)
            {
GOAL_283:;

            //printf("LINE: %s", Line);
            i = 0;

            while (i<FILE_MAX_LINE_LENGHT)
            {
GOAL_284:;

            c = Line[i++];
            if (((char) c == ' ' && FirstChar != '#') || (char) c == '\r' || (c == 9 && FirstChar != '#' ) || (c == 10) || (c == 13))
                    {
GOAL_285:;

                    continue;
                    }

            if ((char) c == '\0' )
                    {
GOAL_286:;

              if ((FirstChar != '#' && FirstChar != '=' && FirstChar != 0 ) && SeparatorChar == '=' && ParameterChar != 0 )
                    {
GOAL_288:;

                    TheParameter.Name[BufferNameCursor] = '\0';
                    TheParameter.Value[BufferValueCursor] = '\0';
                    //printf("Adding name: %s value: %s", TheParameter.Name, TheParameter.Value);
                    //printf("TheParameter.Name[0] = %d", TheParameter.Name[0]);

                    ParametersVector->PushBack(ParametersVector, &TheParameter, sizeof(FILE_StringParameter_DataType));
                            BufferNameCursor = 0;
                            BufferValueCursor = 0;
                            memset (TheParameter.Name, 0, FILE_MAX_PAR_VAR_SIZE);
                            memset (TheParameter.Value, 0, FILE_MAX_PAR_VAR_SIZE);
                }

                    FirstChar = 0;
                    SeparatorChar = 0;
                    ParameterChar = 0;

                    if ((char) c == '\0')
                            {
GOAL_289:;

                            break;
                            }
               }
               else
                    {
GOAL_287:;

                     //printf("Checking chars");

                            //first char, parameter name
                            if (FirstChar == 0)
                                    {
GOAL_290:;

                                    FirstChar = (char) c;
                                    //printf("FirstChar = %c", FirstChar);
                                    }
                            else 
{

GOAL_291:;
 if (FirstChar != 0 && SeparatorChar == 0 && (char) c == '=')
                                    {
GOAL_292:;

                                    SeparatorChar = (char) c;
                                    //printf("SeparatorChar = %c", SeparatorChar);
                                    }
                            else 
{

GOAL_293:;
 if (FirstChar != 0 && SeparatorChar != 0 && ParameterChar == 0)
                                    {
GOAL_294:;

                                    ParameterChar = (char) c;
                                    //printf("ParameterChar = %c", ParameterChar);
                                    }
}

}


                            //Get the parameter name
                            if ( FirstChar != '#' && FirstChar != 0 && SeparatorChar == 0 && BufferNameCursor < FILE_MAX_PAR_VAR_SIZE ) 
{

GOAL_295:;

                                    if(BufferNameCursor < FILE_MAX_PAR_VAR_SIZE) 
{

GOAL_296:;

                                            TheParameter.Name[BufferNameCursor++] = (char) c;
}

}


                            //Get the parameter value
                            if ( FirstChar != '#' && FirstChar != 0 && SeparatorChar != 0 && ParameterChar != 0 && BufferValueCursor < FILE_MAX_PAR_VAR_SIZE ) 
{

GOAL_297:;

                                    if(BufferValueCursor < FILE_MAX_PAR_VAR_SIZE) 
{

GOAL_298:;

                                            TheParameter.Value[BufferValueCursor++] = (char) c;
}

}

                    }
                }
            }

            fclose(File);
            }

   // printf("ParametersVector->Size %d", ParametersVector->Size);

    for (i = 0; i < ParametersVector->Size; i++)
            {
GOAL_299:;

            //printf("ParametersVector->Data[%d])->Name = %s",i, ((FILE_StringParameter_DataType *)ParametersVector->Data[i])->Name);
            }

    qsort(ParametersVector->Data, ParametersVector->Size, sizeof(void *), FILE_CompareStringParameter);

    //printf("Sorted");
    for (i = 0; i < ParametersVector->Size; i++)
            {
GOAL_300:;

            //printf("ParametersVector->Data[%d])->Name = %s",i, ((FILE_StringParameter_DataType *)ParametersVector->Data[i])->Name);
            }

}

int FILE_StringParametersLinearySearch(DYNV_VectorGenericDataType *TheVectorGeneric, void * name)
{

GOAL_301:;

    int i;
    for(i=0; i<TheVectorGeneric->Size; i++)
    {
GOAL_302:;

        if(strcmp(((FILE_StringParameter_DataType *)TheVectorGeneric->Data[i])->Name, (char *) name) == 0)
        {
GOAL_303:;

            return i;
        }
    }
    return -1;
}

int FILE_StringParametersBinarySearch(DYNV_VectorGenericDataType *TheVectorGeneric, void * Needle)
	{

GOAL_304:;


	long long int CompareResult;

	if (TheVectorGeneric->Size <= 0)
		{
GOAL_305:;

		return -1;
		}

	int littler = 0;
	int last = TheVectorGeneric->Size - 1;
	int middle = (littler + last) / 2;

	while (littler <= last)
		{
GOAL_306:;

		CompareResult = strcmp(((FILE_StringParameter_DataType *)TheVectorGeneric->Data[middle])->Name, Needle);
		//printf("CompareResult = %d.\n", CompareResult);

		if ((CompareResult == 0))
			{
GOAL_307:;

			//printf("%d found at location %d.\n", Needle, middle);
			return middle;
			}
			else 
{

GOAL_308:;
 if (CompareResult < 0)
			{
GOAL_309:;

			littler = middle + 1;
			//printf("Needle bigger than middle  at %d .\n", middle);
			}
		else
			{
GOAL_310:;

			last = middle - 1;
			//printf("Needle lower than middle  at %d.\n", middle);
			}
}


			middle = (littler + last)/2;
			}

	if (littler > last)
		{
GOAL_311:;

		//printf("Not found! %d is not present in the list.\n", Needle);
		return -1;
		}

  return -1;

	}

char * FILE_GetFilenameFromPath(char * FileName)
{

GOAL_312:;

	int i = 0;
	char * TheStr = FileName;
	for (i = 0; i< strlen(FileName); i++)
		{
GOAL_313:;

		if (FileName[i] == '/' || FileName[i] == '\\')
		{
GOAL_314:;

			TheStr = FileName+i+1;
			}
		}

	return TheStr;
}

char * FILE_GetListPermissionsString(char *file, DYNMEM_MemoryTable_DataType ** memoryTable) {

GOAL_315:;

    struct stat st, stl;
    char *modeval = DYNMEM_malloc(sizeof(char) * 10 + 1, &*memoryTable, "getperm");
    if(stat(file, &st) == 0) 
    {
GOAL_316:;

        mode_t perm = st.st_mode;
        modeval[0] = (S_ISDIR(st.st_mode)) ? 'd' : '-';
        modeval[1] = (perm & S_IRUSR) ? 'r' : '-';
        modeval[2] = (perm & S_IWUSR) ? 'w' : '-';
        modeval[3] = (perm & S_IXUSR) ? 'x' : '-';
        modeval[4] = (perm & S_IRGRP) ? 'r' : '-';
        modeval[5] = (perm & S_IWGRP) ? 'w' : '-';
        modeval[6] = (perm & S_IXGRP) ? 'x' : '-';
        modeval[7] = (perm & S_IROTH) ? 'r' : '-';
        modeval[8] = (perm & S_IWOTH) ? 'w' : '-';
        modeval[9] = (perm & S_IXOTH) ? 'x' : '-';
        modeval[10] = '\0';

        if(lstat(file, &stl) == 0)
        {
GOAL_318:;

            if (S_ISLNK(stl.st_mode)) 
{

GOAL_319:;
 
                modeval[0] = 'l'; // is a link
        
}
}
           
    }
    else {
GOAL_317:;

        return NULL;
    }
    
    return modeval;
}

int checkParentDirectoryPermissions(char *fileName, int uid, int gid)
{

GOAL_320:;

	char theFileName[4096];
	memset(theFileName, 0, 4096);

	int i;
	int theFileNameLen = 0;
	int theLen = strlen(fileName);
	int theParentLen = 0;

	for (i = 0; i < theLen; i++)
	{
GOAL_321:;

		if (fileName[i] == '/')
		{
GOAL_322:;

			theParentLen = i;
		}
	}

	for (i = 0; i < theParentLen; i++)
	{
GOAL_323:;

		if (i < 4096) 
{

GOAL_324:;

			theFileName[theFileNameLen++] = fileName[i];
}

	}

	//printf ("\n checking parent permissions on : %s", theFileName);
	return checkUserFilePermissions(theFileName, uid, gid);
}


int checkUserFilePermissions(char *fileName, int uid, int gid)
{

GOAL_325:;


	if (uid == 0 || gid == 0)
	{
GOAL_326:;

		//printf("\n User is root");
		return FILE_PERMISSION_RW;
	}

	static int init = 0;
	if (init == 0)
	{
GOAL_327:;


	}

	init = 1;

	int filePermissions = FILE_PERMISSION_NO_RW;
    int returnCode = 0;
    char *toReturn;
    struct stat info;

    if ((returnCode = stat(fileName, &info)) == -1)
    {
GOAL_328:;

    	return -1;
    }

    if (info.st_uid == uid ||
		info.st_gid == gid)
    {
GOAL_329:;

		//printf("\n User is owner");
    	filePermissions = FILE_PERMISSION_RW;
    }
    else
    {
GOAL_330:;

        mode_t perm = info.st_mode;
    	if ((perm & S_IROTH)){
GOAL_331:;

    		//printf("\nfile can be readen");
    		filePermissions |= FILE_PERMISSION_R;
    	}

    	if ((perm & S_IWOTH)){
GOAL_332:;

    		//printf("\nfile can be written");
    		filePermissions |= FILE_PERMISSION_W;
    	}
    }

    return filePermissions;
}

char * FILE_GetOwner(char *fileName, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_333:;

    int returnCode = 0;
    char *toReturn;
    struct stat info;

    if ((returnCode = stat(fileName, &info)) == -1) 
{

GOAL_334:;

        return NULL;
}


    struct passwd *pw;
    if ( (pw = getpwuid(info.st_uid)) == NULL) 
{

GOAL_335:;

        return NULL;
}


    toReturn = (char *) DYNMEM_malloc (strlen(pw->pw_name) + 1, &*memoryTable, "getowner");
    strcpy(toReturn, pw->pw_name);

    return toReturn;
}

char * FILE_GetGroupOwner(char *fileName, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_336:;

    char *toReturn;
    struct stat info;
    if (stat(fileName, &info) == -1 ) 
{

GOAL_337:;

        return NULL;
}

    struct group  *gr;
    
    if ((gr = getgrgid(info.st_gid)) == NULL) 
{

GOAL_338:;

        return NULL;
}

    
    toReturn = (char *) DYNMEM_malloc (strlen(gr->gr_name) + 1, &*memoryTable, "getowner");
    strcpy(toReturn, gr->gr_name);
    
    return toReturn;
}

time_t FILE_GetLastModifiedData(char *path)
{

GOAL_339:;

    struct stat statbuf;
    if (stat(path, &statbuf) == -1)
    {
GOAL_340:;

    	time_t theTime = 0;
    	return theTime;
    }
    return statbuf.st_mtime;
}

void FILE_AppendToString(char ** sourceString, char *theString, DYNMEM_MemoryTable_DataType ** memoryTable)
{

GOAL_341:;

    int theNewSize = strlen(*sourceString) + strlen(theString);
    *sourceString = DYNMEM_realloc(*sourceString, theNewSize + 10, &*memoryTable);
    strcat(*sourceString, theString);
    (*sourceString)[theNewSize] = '\0';
}

void FILE_DirectoryToParent(char ** sourceString, DYNMEM_MemoryTable_DataType ** memoryTable)
{

GOAL_342:;

    //printf("\n");
   int i = 0, theLastSlash = -1, strLen = 0;

   strLen = strlen(*sourceString);
   //printf("\nstrLen = %d", strLen);

   for (i = 0; i < strLen; i++)
   {
GOAL_343:;

       //printf("%c", (*sourceString)[i]);
       if ( (*sourceString)[i] == '/')
       {
GOAL_344:;

           theLastSlash = i;
           //printf("\n theLastSlash = %d", theLastSlash);
       }
   }

   if (theLastSlash > -1)
   {
GOAL_345:;

       int theNewSize = theLastSlash;
       if (theLastSlash == 0)
       {
GOAL_346:;

           theNewSize = 1;
       }
       *sourceString = DYNMEM_realloc(*sourceString, theNewSize+1, &*memoryTable);
       (*sourceString)[theNewSize] = '\0';
   }
}

int FILE_LockFile(int fd)
{

GOAL_347:;

    struct flock fl;
    fl.l_type = F_WRLCK;
    fl.l_start = 0;
    fl.l_whence = SEEK_SET;
    fl.l_len = 0;
    return(fcntl(fd, F_SETLK, &fl));
}

int FILE_doChownFromUidGid(const char *file_path, uid_t uid, gid_t gid)
{

GOAL_348:;

    if (chown(file_path, uid, gid) == -1)
    {
GOAL_349:;

        return 0;
    }

    return 1;
}

int FILE_doChownFromUidGidString (  const char *file_path,
                    const char *user_name,
                    const char *group_name) 
{

GOAL_350:;

    uid_t          uid;
    gid_t          gid;
    struct passwd *pwd;
    struct group  *grp;

    pwd = getpwnam(user_name);
    if (pwd == NULL) 
    {
GOAL_351:;

        return 0;
    }
    uid = pwd->pw_uid;

    grp = getgrnam(group_name);
    if (grp == NULL)
    {
GOAL_352:;

        return 0;
    }
    gid = grp->gr_gid;

    if (chown(file_path, uid, gid) == -1)
    {
GOAL_353:;

        return 0;
    }

    return 1;
}

uid_t FILE_getUID(const char *user_name)
{

GOAL_354:;

    struct passwd *pwd;
    pwd = getpwnam(user_name);

    if (pwd == NULL) 
    {
GOAL_355:;

        return -1;
    }

    return pwd->pw_uid;
}

gid_t FILE_getGID(const char *group_name)
{

GOAL_356:;

    struct group  *grp;
    grp = getgrnam(group_name);
    if (grp == NULL)
    {
GOAL_357:;

        return -1;
    }

    return grp->gr_gid;
}


void FILE_checkAllOpenedFD(void)
{

GOAL_358:;

	int openedFd = 0, i,ret;

	struct rlimit rl;
	if (getrlimit(RLIMIT_NOFILE, &rl) < 0) 
{

GOAL_359:;

		printf("%s: can’t get file limit", "");
}


	if (rl.rlim_max == RLIM_INFINITY) 
{

GOAL_360:;

		rl.rlim_max = 1024;
}


	for (i = 0; i < rl.rlim_max; i++)
	{
GOAL_361:;

		ret = FILE_fdIsValid(i);
		//printf("\nret = %d", ret);
		if (ret != -1)
		{
GOAL_362:;

			struct stat statbuf;
			fstat(i, &statbuf);
			if (S_ISSOCK(statbuf.st_mode))
			{
GOAL_363:;

				//printf("\n fd %d is socket", i);
			}
			else 
{

GOAL_364:;
 if (S_ISDIR(statbuf.st_mode))
			{
GOAL_365:;

				//printf("\n fd %d is dir", i);
			}
}


			/*
			else if (S_ISSOCK(statbuf.st_mode))
			{
				printf("\n fd %d is socket", fd);
			}
			else if (S_ISSOCK(statbuf.st_mode))
			{
				printf("\n fd %d is socket", fd);
			}
			else if (S_ISSOCK(statbuf.st_mode))
			{
				printf("\n fd %d is socket", fd);
			}
			else if (S_ISSOCK(statbuf.st_mode))
			{
				printf("\n fd %d is socket", fd);
			}
			*/

			openedFd++;
		}
	}
	//printf("\n\nOpened fd : %d", openedFd);
}
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */


#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <pthread.h>
#include <netinet/in.h>
#include <unistd.h>

#include "ftpServer.h"
#include "ftpCommandsElaborate.h"
#include "ftpData.h"
#include "library/configRead.h"
#include "library/fileManagement.h"
#include "library/connection.h"
#include "library/dynamicMemory.h"

void cleanDynamicStringDataType(dynamicStringDataType *dynamicString, int init, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_366:;

    if (init == 1)
    {
GOAL_367:;

        dynamicString->text = 0;
        dynamicString->textLen = 0;
    }
    else
    {
GOAL_368:;

        if (dynamicString->textLen != 0)
        {
GOAL_369:;

            if (dynamicString->text != 0) {
GOAL_370:;

            	DYNMEM_free(dynamicString->text, &*memoryTable);
            }
        }

        dynamicString->textLen = 0;
    }
}

void cleanLoginData(loginDataType *loginData, int init, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_371:;

    loginData->userLoggedIn = 0;
    cleanDynamicStringDataType(&loginData->homePath, init, &*memoryTable);
    cleanDynamicStringDataType(&loginData->ftpPath, init, &*memoryTable);
    cleanDynamicStringDataType(&loginData->name, init, &*memoryTable);
    cleanDynamicStringDataType(&loginData->password, init, &*memoryTable);
    cleanDynamicStringDataType(&loginData->absolutePath, init, &*memoryTable);
}

void setDynamicStringDataType(dynamicStringDataType *dynamicString, char *theString, int stringLen, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_372:;

    if (dynamicString->textLen == 0)
    {
GOAL_373:;

    	//printf("\nMemory data address before memset call : %lld", memoryTable);
        dynamicString->text = (char *) DYNMEM_malloc (((sizeof(char) * stringLen) + 1), &*memoryTable, "setDynamicString");
        //printf("\nMemory data address after memset call : %lld", memoryTable);
        memset(dynamicString->text, 0, stringLen + 1);
        memcpy(dynamicString->text, theString, stringLen);
        dynamicString->textLen = stringLen;
    }
    else
    {
GOAL_374:;

        if(stringLen != dynamicString->textLen)
        {
GOAL_375:;

            dynamicString->text = (char *) DYNMEM_realloc (dynamicString->text, ((sizeof(char) * stringLen) + 1), &*memoryTable);
        }

        memset(dynamicString->text, 0, stringLen + 1);
        memcpy(dynamicString->text, theString, stringLen);
        dynamicString->textLen = stringLen; 
    }
}


int getSafePath(dynamicStringDataType *safePath, char *theDirectoryName, loginDataType *loginData, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_376:;

	#define STRING_SIZE		4096
    int theLen, i;
    char * theDirectoryNamePointer;
    theDirectoryNamePointer = theDirectoryName;
    
    if (theDirectoryName == NULL) 
{

GOAL_377:;

        return 0;
}

    
    theLen = strlen(theDirectoryName);
    
    if (theLen <= 0) 
{

GOAL_378:;

        return 0;
}

    
    if (theLen == 2 &&
        theDirectoryName[0] == '.' &&
        theDirectoryName[1] == '.')
        {
GOAL_379:;

        return 0;
        }
    
    if (theLen == 3 &&
        ((theDirectoryName[0] == '.' &&
          theDirectoryName[1] == '.' &&
          theDirectoryName[2] == '/') ||
         (theDirectoryName[0] == '/' &&
          theDirectoryName[1] == '.' &&
          theDirectoryName[2] == '.')
         )
        )
        {
GOAL_380:;

        return 0;
        }

    //Check for /../
    char theDirectoryToCheck[STRING_SIZE];
    int theDirectoryToCheckIndex = 0;
    memset(theDirectoryToCheck, 0, STRING_SIZE);
    
    for (i = 0; i< theLen; i++)
    {
GOAL_381:;

        if (theDirectoryName[i] == '/')
        {
GOAL_382:;

        if (theDirectoryToCheckIndex == 2 &&
            theDirectoryToCheck[0] == '.' &&
            theDirectoryToCheck[1] == '.')
            {
GOAL_383:;

            return 0;
            }

        theDirectoryToCheckIndex = 0;
        memset(theDirectoryToCheck, 0, STRING_SIZE);
        continue;
        }
        
        if (theDirectoryToCheckIndex<STRING_SIZE)
            {
GOAL_384:;

            theDirectoryToCheck[theDirectoryToCheckIndex++] = theDirectoryName[i];
            }
        else 
{

GOAL_385:;

            return 0; /* Directory size too long */
}

    }
    
    if (theDirectoryName[0] == '/')
    {
GOAL_386:;

        while (theDirectoryNamePointer[0] == '/') 
{

GOAL_388:;

            theDirectoryNamePointer++;
}


        //printf("\nMemory data address 2nd call : %lld", memoryTable);
        setDynamicStringDataType(safePath, loginData->homePath.text, loginData->homePath.textLen, &*memoryTable);
        //printf("\nMemory data address 3rd call : %lld", memoryTable);
        appendToDynamicStringDataType(safePath, theDirectoryNamePointer, strlen(theDirectoryNamePointer), &*memoryTable);
    }
    else
    {
GOAL_387:;

        setDynamicStringDataType(safePath, loginData->absolutePath.text, loginData->absolutePath.textLen, &*memoryTable);

        if (loginData->absolutePath.text[loginData->absolutePath.textLen-1] != '/')
        {
GOAL_389:;

            appendToDynamicStringDataType(safePath, "/", 1, &*memoryTable);
        }
        
        appendToDynamicStringDataType(safePath, theDirectoryName, strlen(theDirectoryName), &*memoryTable);
    }
    
    return 1;
}

void appendToDynamicStringDataType(dynamicStringDataType *dynamicString, char *theString, int stringLen, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_390:;

	//printf("\nRealloc dynamicString->text = %lld", dynamicString->text);
    int theNewSize = dynamicString->textLen + stringLen;

    dynamicString->text = DYNMEM_realloc(dynamicString->text, theNewSize + 1, &*memoryTable);

    memset(dynamicString->text+dynamicString->textLen, 0, stringLen+1);
    memcpy(dynamicString->text+dynamicString->textLen, theString, stringLen);

    dynamicString->text[theNewSize] = '\0';
    dynamicString->textLen = theNewSize;
}

void setRandomicPort(ftpDataType *data, int socketPosition)
{

GOAL_391:;

    static unsigned short int randomizeInteger = 0;
    unsigned short int randomicPort = 5000;
    int i;

    randomizeInteger += 1;
    
    if (randomizeInteger >  100 ) 
{

GOAL_392:;

        randomizeInteger = 1;
}


    while(randomicPort < 10000) 
{

GOAL_393:;

        randomicPort = ((rand() + socketPosition + randomizeInteger) % (50000)) + 10000;
}

   i = 0;

   while (i < data->ftpParameters.maxClients)
   {
GOAL_394:;

       if (randomicPort == data->clients[i].workerData.connectionPort ||
           randomicPort < 10000)
       {
GOAL_395:;

        randomicPort = ((rand() + socketPosition + i + randomizeInteger) % (50000)) + 10000;
        i = 0;
       }
       else 
       {
GOAL_396:;

        i++;
       }
   }
   
   
   data->clients[socketPosition].workerData.connectionPort = randomicPort;
   //printf("data->clients[%d].workerData.connectionPort = %d", socketPosition, data->clients[socketPosition].workerData.connectionPort);
}

int writeListDataInfoToSocket(ftpDataType *ftpData, int clientId, int *filesNumber, int commandType, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_397:;

    int i, x, returnCode;
    int fileAndFoldersCount = 0;
    char **fileList = NULL;
    FILE_GetDirectoryInodeList(ftpData->clients[clientId].listPath.text, &fileList, &fileAndFoldersCount, 0, &*memoryTable);
    *filesNumber = fileAndFoldersCount;

    returnCode = socketWorkerPrintf(ftpData, clientId, "sds", "total ", fileAndFoldersCount ,"\r\n");
    if (returnCode <= 0)
    {
GOAL_398:;

        return -1;
    }
    
    for (i = 0; i < fileAndFoldersCount; i++)
    {
GOAL_399:;

        ftpListDataType data;
        data.owner = NULL;
        data.groupOwner = NULL;
        data.inodePermissionString = NULL;
        data.fileNameWithPath = NULL;
        data.finalStringPath = NULL;
        data.linkPath = NULL;       
        data.isFile = 0;
        data.isDirectory = 0;

        //printf("\nPROCESSING: %s", fileList[i]);
        
        if (FILE_IsDirectory(fileList[i]) == 1)
        {
GOAL_400:;

            //printf("\nis directory");
            //fflush(0);
            data.isDirectory = 1;
            data.isFile = 0;
            data.isLink = 0;
            data.fileSize = 4096;
            data.numberOfSubDirectories = FILE_GetDirectoryInodeCount(fileList[i]);
        }
        else 
{

GOAL_401:;
 if (FILE_IsFile(fileList[i]) == 1)
        {
GOAL_402:;

            //printf("\nis file");
            //fflush(0);
            data.isDirectory = 0;
            data.isFile = 1;
            data.isLink = 0;
            data.numberOfSubDirectories = 1; /* to Do*/
            data.fileSize = FILE_GetFileSizeFromPath(fileList[i]);
        }
}

        if (data.isDirectory == 0 && data.isFile == 0)
        {
GOAL_403:;

            //printf("\nNot a directory, not a file, broken link");
            continue;
        }
        
      
        //printf("\nFILE SIZE : %lld", data.fileSize);

        data.owner = FILE_GetOwner(fileList[i], &*memoryTable);
        data.groupOwner = FILE_GetGroupOwner(fileList[i], &*memoryTable);
        data.fileNameWithPath = fileList[i];
        data.fileNameNoPath = FILE_GetFilenameFromPath(fileList[i]);
        data.inodePermissionString = FILE_GetListPermissionsString(fileList[i], &*memoryTable);
        data.lastModifiedData = FILE_GetLastModifiedData(fileList[i]);

        if (strlen(data.fileNameNoPath) > 0)
        {
GOAL_404:;

            data.finalStringPath = (char *) DYNMEM_malloc (strlen(data.fileNameNoPath)+1, &*memoryTable, "dataFinalPath");
            strcpy(data.finalStringPath, data.fileNameNoPath);
        }
        
        if (data.inodePermissionString != NULL &&
            strlen(data.inodePermissionString) > 0 &&
            data.inodePermissionString[0] == 'l')
            {
GOAL_405:;

                int len = 0;
                data.isLink = 1;
                data.linkPath = (char *) DYNMEM_malloc (CLIENT_COMMAND_STRING_SIZE*sizeof(char), &*memoryTable, "dataLinkPath");
                if ((len = readlink (fileList[i], data.linkPath, CLIENT_COMMAND_STRING_SIZE)) > 0)
                {
GOAL_406:;

                    data.linkPath[len] = 0;
                    FILE_AppendToString(&data.finalStringPath, " -> ", &*memoryTable);
                    FILE_AppendToString(&data.finalStringPath, data.linkPath, &*memoryTable);
                }
            }

        memset(data.lastModifiedDataString, 0, LIST_DATA_TYPE_MODIFIED_DATA_STR_SIZE);       
        strftime(data.lastModifiedDataString, LIST_DATA_TYPE_MODIFIED_DATA_STR_SIZE, "%b %d %Y", localtime(&data.lastModifiedData));
        
        
        switch (commandType)
        {
            case COMMAND_TYPE_LIST:
GOAL_409:;

            {
            			returnCode = socketWorkerPrintf(ftpData, clientId, "ssdssssslsssss",
                        data.inodePermissionString == NULL? "Unknown" : data.inodePermissionString
                        ," "
                        ,data.numberOfSubDirectories
                        ," "
                        ,data.owner == NULL? "Unknown" : data.owner
						," "
                        ,data.groupOwner == NULL? "Unknown" : data.groupOwner
						," "
                        ,data.fileSize
                        ," "
                        ,data.lastModifiedDataString == NULL? "Unknown" : data.lastModifiedDataString
						," "
                        ,data.finalStringPath == NULL? "Unknown" : data.finalStringPath
						,"\r\n");
            		/*
                returnCode = dprintf(theSocket, "%s %d %s %s %lld %s %s\r\n", 
                data.inodePermissionString == NULL? "Unknown" : data.inodePermissionString
                ,data.numberOfSubDirectories
                ,data.owner == NULL? "Unknown" : data.owner
                ,data.groupOwner == NULL? "Unknown" : data.groupOwner
                ,data.fileSize
                ,data.lastModifiedDataString == NULL? "Unknown" : data.lastModifiedDataString
                ,data.finalStringPath == NULL? "Unknown" : data.finalStringPath);
                */
            }
            break;
            
            case COMMAND_TYPE_NLST:
GOAL_408:;

            {
            	returnCode = socketWorkerPrintf(ftpData, clientId, "ss", data.fileNameNoPath, "\r\n");
            }
            break;

            
            default:
GOAL_407:;

            {
                printf("\nWarning switch default in function writeListDataInfoToSocket (%d)", commandType);
            }
            break;
        }
        
       
        if (data.fileNameWithPath != NULL) 
{

GOAL_410:;

            DYNMEM_free(data.fileNameWithPath, &*memoryTable);
}

        
        if (data.linkPath != NULL) 
{

GOAL_411:;

        	DYNMEM_free(data.linkPath, &*memoryTable);
}


        if (data.finalStringPath != NULL) 
{

GOAL_412:;

        	DYNMEM_free(data.finalStringPath, &*memoryTable);
}


        if (data.owner != NULL) 
{

GOAL_413:;

        	DYNMEM_free(data.owner, &*memoryTable);
}

        
        if (data.groupOwner != NULL) 
{

GOAL_414:;

        	DYNMEM_free(data.groupOwner, &*memoryTable);
}

        
        if (data.inodePermissionString != NULL) 
{

GOAL_415:;

        	DYNMEM_free(data.inodePermissionString, &*memoryTable);
}

          
        if (returnCode <= 0)
        {
GOAL_416:;

            for (x = i+1; x < fileAndFoldersCount; x++) 
{

GOAL_417:;

            	DYNMEM_free (fileList[x], &*memoryTable);
}

            DYNMEM_free (fileList, &*memoryTable);
            return -1;
        }
        
        }

		if (fileList != NULL)
		{
GOAL_418:;

			DYNMEM_free (fileList, &*memoryTable);
		}

        return 1;
    }

int searchInLoginFailsVector(void * loginFailsVector, void *element)
{

GOAL_419:;

    int i = 0;
    //printf("((DYNV_VectorGenericDataType *)loginFailsVector)->Size = %d", ((DYNV_VectorGenericDataType *)loginFailsVector)->Size);

    for (i = 0; i < ((DYNV_VectorGenericDataType *)loginFailsVector)->Size; i++)
    {
GOAL_420:;

        if (strcmp( ((loginFailsDataType *) element)->ipAddress, (((loginFailsDataType *) ((DYNV_VectorGenericDataType *)loginFailsVector)->Data[i])->ipAddress)) == 0)
        {
GOAL_421:;

            //printf("\n\n***IP address found: %s in %d", ((loginFailsDataType *) element)->ipAddress, i);
            return i;
        }
    }

    return -1;
}

void deleteLoginFailsData(void *element)
{

GOAL_422:;

    ; //NOP
}

void getListDataInfo(char * thePath, DYNV_VectorGenericDataType *directoryInfo, DYNMEM_MemoryTable_DataType **memoryTable)
{

GOAL_423:;

    int i;
    int fileAndFoldersCount = 0;
    ftpListDataType data;
    FILE_GetDirectoryInodeList(thePath, &data.fileList, &fileAndFoldersCount, 0, &*memoryTable);
    
    //printf("\nNUMBER OF FILES: %d", fileAndFoldersCount);
    //fflush(0);
    
    for (i = 0; i < fileAndFoldersCount; i++)
    {
GOAL_424:;

        data.owner = NULL;
        data.groupOwner = NULL;
        data.inodePermissionString = NULL;
        data.fileNameWithPath = NULL;
        data.finalStringPath = NULL;
        data.linkPath = NULL;       

        data.numberOfSubDirectories = 1; /* to Do*/
        data.isFile = 0;
        data.isDirectory = 0;
        
        
        //printf("\nPROCESSING: %s", data.fileList[i]);
        //fflush(0);
        
        if (FILE_IsDirectory(data.fileList[i]) == 1)
        {
GOAL_425:;

            //printf("\nis file");
            //fflush(0);
            data.isDirectory = 1;
            data.isFile = 0;
            data.isLink = 0;
            data.fileSize = 4096;
        }
        else 
{

GOAL_426:;
 if (FILE_IsFile(data.fileList[i]) == 1)
        {
GOAL_427:;

            //printf("\nis file");
            //fflush(0);
            data.isDirectory = 0;
            data.isFile = 1;
            data.isLink = 0;
            data.fileSize = FILE_GetFileSizeFromPath(data.fileList[i]);
        }
}

        if (data.isDirectory == 0 && data.isFile == 0)
        {
GOAL_428:;

            //printf("\nNot a directory, not a file, broken link");
            continue;
        }
        
       // printf("\nFILE SIZE : %lld", data.fileSize);

        data.owner = FILE_GetOwner(data.fileList[i], &*memoryTable);
        data.groupOwner = FILE_GetGroupOwner(data.fileList[i], &*memoryTable);
        data.fileNameWithPath = data.fileList[i];
        data.fileNameNoPath = FILE_GetFilenameFromPath(data.fileList[i]);
        data.inodePermissionString = FILE_GetListPermissionsString(data.fileList[i], &*memoryTable);
        data.lastModifiedData = FILE_GetLastModifiedData(data.fileList[i]);

        if (strlen(data.fileNameNoPath) > 0)
        {
GOAL_429:;

            data.finalStringPath = (char *) DYNMEM_malloc (strlen(data.fileNameNoPath)+1, &*memoryTable, "FinalStringPath");
            strcpy(data.finalStringPath, data.fileNameNoPath);
        }
        
        if (data.inodePermissionString != NULL &&
            strlen(data.inodePermissionString) > 0 &&
            data.inodePermissionString[0] == 'l')
            {
GOAL_430:;

                int len = 0;
                data.isLink = 1;
                data.linkPath = (char *) DYNMEM_malloc (CLIENT_COMMAND_STRING_SIZE*sizeof(char), &*memoryTable, "data.linkPath");
                if ((len = readlink (data.fileList[i], data.linkPath, CLIENT_COMMAND_STRING_SIZE)) > 0)
                {
GOAL_431:;

                    data.linkPath[len] = 0;
                    FILE_AppendToString(&data.finalStringPath, " -> ", &*memoryTable);
                    FILE_AppendToString(&data.finalStringPath, data.linkPath, &*memoryTable);
                }
            }

        memset(data.lastModifiedDataString, 0, LIST_DATA_TYPE_MODIFIED_DATA_STR_SIZE);       
        strftime(data.lastModifiedDataString, 80, "%b %d %Y", localtime(&data.lastModifiedData));

        /*
        -1 List one file per line
        -A List all files except "." and ".."
        -a List all files including those whose names start with "."
        -C List entries by columns
        -d List directory entries instead of directory contents
        -F Append file type indicator (one of "*", "/", "=", "@" or "|") to names
        -h Print file sizes in human-readable format (e.g. 1K, 234M, 2G)
        -L List files pointed to by symlinks
        -l Use a long listing format
        -n List numeric UIDs/GIDs instead of user/group names
        -R List subdirectories recursively
        -r Sort filenames in reverse order
        -S Sort by file size
        -t Sort by modification time 
         */

        directoryInfo->PushBack(directoryInfo, &data, sizeof(ftpListDataType));
    }
}

void deleteListDataInfoVector(DYNV_VectorGenericDataType *theVector)
{

GOAL_432:;


    int i;
    for (i = 0; i < theVector->Size; i++)
    {
GOAL_433:;

		ftpListDataType *data = (ftpListDataType *)theVector->Data[i];

		if (data->owner != NULL)
		{
GOAL_434:;

			DYNMEM_free(data->owner, &theVector->memoryTable);
		}
		if (data->groupOwner != NULL)
		{
GOAL_435:;

			DYNMEM_free(data->groupOwner, &theVector->memoryTable);
		}
		if (data->inodePermissionString != NULL)
		{
GOAL_436:;

			DYNMEM_free(data->inodePermissionString, &theVector->memoryTable);
		}
		if (data->fileNameWithPath != NULL)
		{
GOAL_437:;

			DYNMEM_free(data->fileNameWithPath, &theVector->memoryTable);
		}
		if (data->finalStringPath != NULL)
		{
GOAL_438:;

			DYNMEM_free(data->finalStringPath, &theVector->memoryTable);
		}
		if (data->linkPath != NULL)
		{
GOAL_439:;

			DYNMEM_free(data->linkPath, &theVector->memoryTable);
		}
    }
}

void cancelWorker(ftpDataType *data, int clientId)
{

GOAL_440:;

	void *pReturn;
	int returnCode = pthread_cancel(data->clients[clientId].workerData.workerThread);
	returnCode = pthread_join(data->clients[clientId].workerData.workerThread, &pReturn);
	data->clients[clientId].workerData.threadHasBeenCreated = 0;
}


void resetWorkerData(ftpDataType *data, int clientId, int isInitialization)
{

GOAL_441:;


	  printf("\nReset of worker id: %d", clientId);
      data->clients[clientId].workerData.connectionPort = 0;
      data->clients[clientId].workerData.passiveModeOn = 0;
      data->clients[clientId].workerData.socketIsConnected = 0;
      data->clients[clientId].workerData.commandIndex = 0;
      data->clients[clientId].workerData.passiveListeningSocket = 0;
      data->clients[clientId].workerData.socketConnection = 0;
      data->clients[clientId].workerData.bufferIndex = 0;
      data->clients[clientId].workerData.commandReceived = 0;
      data->clients[clientId].workerData.retrRestartAtByte = 0;
      data->clients[clientId].workerData.threadIsAlive = 0;
      data->clients[clientId].workerData.activeModeOn = 0;
      data->clients[clientId].workerData.passiveModeOn = 0;
      data->clients[clientId].workerData.activeIpAddressIndex = 0;

      memset(data->clients[clientId].workerData.buffer, 0, CLIENT_BUFFER_STRING_SIZE);
      memset(data->clients[clientId].workerData.activeIpAddress, 0, CLIENT_BUFFER_STRING_SIZE);
      memset(data->clients[clientId].workerData.theCommandReceived, 0, CLIENT_BUFFER_STRING_SIZE);

      cleanDynamicStringDataType(&data->clients[clientId].workerData.ftpCommand.commandArgs, isInitialization, &data->clients[clientId].workerData.memoryTable);
      cleanDynamicStringDataType(&data->clients[clientId].workerData.ftpCommand.commandOps, isInitialization, &data->clients[clientId].workerData.memoryTable);

      /* wait main for action */
      if (isInitialization != 1)
      {
GOAL_442:;

        if (data->clients[clientId].workerData.theStorFile != NULL)
        {
GOAL_444:;

            fclose(data->clients[clientId].workerData.theStorFile);
            data->clients[clientId].workerData.theStorFile = NULL;
        }

			#ifdef OPENSSL_ENABLED

        	if (data->clients[clientId].workerData.serverSsl != NULL)
        	{
        		SSL_free(data->clients[clientId].workerData.serverSsl);
        		data->clients[clientId].workerData.serverSsl = NULL;
        	}


        	if (data->clients[clientId].workerData.clientSsl != NULL)
        	{
        		SSL_free(data->clients[clientId].workerData.clientSsl);
        		data->clients[clientId].workerData.clientSsl = NULL;
        	}


			#endif
      }
      else
      {
GOAL_443:;

        DYNV_VectorGeneric_Init(&data->clients[clientId].workerData.directoryInfo);
        data->clients[clientId].workerData.theStorFile = NULL;
        data->clients[clientId].workerData.threadHasBeenCreated = 0;
      }


    //Clear the dynamic vector structure
    int theSize = data->clients[clientId].workerData.directoryInfo.Size;
    char ** lastToDestroy = NULL;
    if (theSize > 0)
    {
GOAL_445:;

        lastToDestroy = ((ftpListDataType *)data->clients[clientId].workerData.directoryInfo.Data[0])->fileList;
        data->clients[clientId].workerData.directoryInfo.Destroy(&data->clients[clientId].workerData.directoryInfo, deleteListDataInfoVector);
        DYNMEM_free(lastToDestroy, &data->clients[clientId].workerData.memoryTable);
    }

		#ifdef OPENSSL_ENABLED
		data->clients[clientId].workerData.serverSsl = SSL_new(data->serverCtx);
		data->clients[clientId].workerData.clientSsl = SSL_new(data->clientCtx);
		#endif
}

void resetClientData(ftpDataType *data, int clientId, int isInitialization)
{

GOAL_446:;

    if (isInitialization != 1)
    {
GOAL_447:;

	if (data->clients[clientId].workerData.threadIsAlive == 1)
	{
GOAL_449:;

		cancelWorker(data, clientId);
	}

	pthread_mutex_destroy(&data->clients[clientId].conditionMutex);
	pthread_cond_destroy(&data->clients[clientId].conditionVariable);

	pthread_mutex_destroy(&data->clients[clientId].writeMutex);

	#ifdef OPENSSL_ENABLED
	if (data->clients[clientId].ssl != NULL)
	{
		SSL_free(data->clients[clientId].ssl);
		data->clients[clientId].ssl = NULL;
	}
	#endif
    }
    else
    {
GOAL_448:;


    }

    if (pthread_mutex_init(&data->clients[clientId].writeMutex, NULL) != 0)
    {
GOAL_450:;

        printf("\nclientData->writeMutex init failed\n");
        exit(0);
    }

	if (pthread_mutex_init(&data->clients[clientId].conditionMutex, NULL) != 0)
		  {
GOAL_451:;

		  printf("\ndata->clients[clientId].workerData.conditionMutex init failed\n");
		  exit(0);
		  }

	if (pthread_cond_init(&data->clients[clientId].conditionVariable, NULL) != 0)
	{
GOAL_452:;

		printf("\ndata->clients[clientId].workerData.conditionVariable init failed\n");
		exit(0);
	}

    data->clients[clientId].tlsIsNegotiating = 0;
    data->clients[clientId].tlsIsEnabled = 0;
    data->clients[clientId].dataChannelIsTls = 0;
    data->clients[clientId].socketDescriptor = -1;
    data->clients[clientId].socketCommandReceived = 0;
    data->clients[clientId].socketIsConnected = 0;
    data->clients[clientId].bufferIndex = 0;
    data->clients[clientId].commandIndex = 0;
    data->clients[clientId].closeTheClient = 0;
    data->clients[clientId].sockaddr_in_size = sizeof(struct sockaddr_in);
    data->clients[clientId].sockaddr_in_server_size = sizeof(struct sockaddr_in);
    
    data->clients[clientId].serverIpAddressInteger[0] = 0;
    data->clients[clientId].serverIpAddressInteger[1] = 0;
    data->clients[clientId].serverIpAddressInteger[2] = 0;
    data->clients[clientId].serverIpAddressInteger[3] = 0;
    
    
    memset(&data->clients[clientId].client_sockaddr_in, 0, data->clients[clientId].sockaddr_in_size);
    memset(&data->clients[clientId].server_sockaddr_in, 0, data->clients[clientId].sockaddr_in_server_size);
    memset(data->clients[clientId].clientIpAddress, 0, INET_ADDRSTRLEN);
    memset(data->clients[clientId].buffer, 0, CLIENT_BUFFER_STRING_SIZE);
    memset(data->clients[clientId].theCommandReceived, 0, CLIENT_COMMAND_STRING_SIZE);
    cleanLoginData(&data->clients[clientId].login, isInitialization, &data->clients[clientId].memoryTable);
    
    //Rename from and to data init
    cleanDynamicStringDataType(&data->clients[clientId].renameFromFile, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].renameToFile, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].fileToStor, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].fileToRetr, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].listPath, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].nlistPath, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].ftpCommand.commandArgs, isInitialization, &data->clients[clientId].memoryTable);
    cleanDynamicStringDataType(&data->clients[clientId].ftpCommand.commandOps, isInitialization, &data->clients[clientId].memoryTable);

    data->clients[clientId].connectionTimeStamp = 0;
    data->clients[clientId].tlsNegotiatingTimeStart = 0;
    data->clients[clientId].lastActivityTimeStamp = 0;

	#ifdef OPENSSL_ENABLED
	//data->clients[clientId].workerData.ssl = SSL_new(data->ctx);
	data->clients[clientId].ssl = SSL_new(data->serverCtx);
	#endif

	//printf("\nclient memory table :%lld", data->clients[clientId].memoryTable);
}

int compareStringCaseInsensitive(char * stringIn, char * stringRef, int stringLenght)
{

GOAL_453:;

    int i = 0;
    char * alfaLowerCase = "qwertyuiopasdfghjklzxcvbnm ";
    char * alfaUpperCase = "QWERTYUIOPASDFGHJKLZXCVBNM ";

    int stringInIndex;
    int stringRefIndex;

    for (i = 0; i <stringLenght; i++)
    {
GOAL_454:;

        stringInIndex  = isCharInString(alfaUpperCase, strlen(alfaUpperCase), stringIn[i]);
        if (stringInIndex == -1)
        {
GOAL_455:;

            stringInIndex  = isCharInString(alfaLowerCase, strlen(alfaLowerCase), stringIn[i]);
        }

        stringRefIndex = isCharInString(alfaUpperCase, strlen(alfaUpperCase), stringRef[i]);
        if (stringRefIndex == -1)
        {
GOAL_456:;

            stringRefIndex  = isCharInString(alfaLowerCase, strlen(alfaLowerCase), stringRef[i]);
        }

        if (stringRefIndex == -1 || stringInIndex == -1)
        {
GOAL_457:;

            return 0;
        }

        if (stringRefIndex != stringInIndex)
        {
GOAL_458:;

            return 0;
        }
    }

    return 1;
}

int isCharInString(char *theString, int stringLen, char theChar)
{

GOAL_459:;

    int i;
    for (i = 0; i < stringLen; i++)
    {
GOAL_460:;

        if (theString[i] == theChar)
        {
GOAL_461:;

            return i;
        }
    }

    return -1;
}
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <string.h>
#include <stdio.h>     
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <netdb.h>
#include <errno.h>

/* FTP LIBS */
#include "library/fileManagement.h"
#include "library/logFunctions.h"
#include "library/configRead.h"
#include "library/signals.h"
#include "library/openSsl.h"
#include "library/connection.h"
#include "library/dynamicMemory.h"
#include "library/errorHandling.h"
#include "library/daemon.h"

#include "ftpServer.h"
#include "ftpData.h"
#include "ftpCommandsElaborate.h"

ftpDataType ftpData;


pthread_t watchDogThread;

static int processCommand(int processingElement);

void workerCleanup(void *socketId)
{

GOAL_465:;

	int theSocketId = *(int *)socketId;
	int returnCode = 0;




	//printf("\nWorker %d cleanup", theSocketId);

	#ifdef OPENSSL_ENABLED
    int error;
    error = fcntl(ftpData.clients[theSocketId].workerData.socketConnection, F_SETFL, O_NONBLOCK);

	if (ftpData.clients[theSocketId].dataChannelIsTls == 1)
	{
		if(ftpData.clients[theSocketId].workerData.passiveModeOn == 1)
		{
			//printf("\nSSL worker Shutdown 1");
			returnCode = SSL_shutdown(ftpData.clients[theSocketId].workerData.serverSsl);
			//printf("\nnSSL worker Shutdown 1 return code : %d", returnCode);

			if (returnCode < 0)
			{
				//printf("SSL_shutdown failed return code %d", returnCode);
			}
			else if (returnCode == 0)
			{
				//printf("\nSSL worker Shutdown 2");
				returnCode = SSL_shutdown(ftpData.clients[theSocketId].workerData.serverSsl);
				//printf("\nnSSL worker Shutdown 2 return code : %d", returnCode);

				if (returnCode <= 0)
				{
					//printf("SSL_shutdown (2nd time) failed");
				}
			}
		}

		if(ftpData.clients[theSocketId].workerData.activeModeOn == 1)
		{
			//printf("\nSSL worker Shutdown 1");
			returnCode = SSL_shutdown(ftpData.clients[theSocketId].workerData.clientSsl);
			//printf(" return code : %d", returnCode);

			if (returnCode < 0)
			{
				//printf("SSL_shutdown failed return code %d", returnCode);
			}
			else if (returnCode == 0)
			{
				returnCode = SSL_shutdown(ftpData.clients[theSocketId].workerData.clientSsl);

				if (returnCode <= 0)
				{
					//printf("SSL_shutdown (2nd time) failed");
				}
			}
		}
	}
	#endif

    shutdown(ftpData.clients[theSocketId].workerData.socketConnection, SHUT_RDWR);
    shutdown(ftpData.clients[theSocketId].workerData.passiveListeningSocket, SHUT_RDWR);
    returnCode = close(ftpData.clients[theSocketId].workerData.socketConnection);
    returnCode = close(ftpData.clients[theSocketId].workerData.passiveListeningSocket);
    resetWorkerData(&ftpData, theSocketId, 0);
   // printf("\nWorker cleaned!");
    //printf("\nWorker memory table :%lld", ftpData.clients[theSocketId].workerData.memoryTable);
    if (ftpData.clients[theSocketId].workerData.memoryTable != NULL) 
{

GOAL_466:;

    	;//printf("\nMemory table element label: %s", ftpData.clients[theSocketId].workerData.memoryTable->theName);
    
}
else 
{

GOAL_467:;

    	;//printf("\nNo data to print");
}

}

void *connectionWorkerHandle(void * socketId)
{

GOAL_468:;

  int theSocketId = *(int *)socketId;
  pthread_cleanup_push(workerCleanup,  (void *) &theSocketId);
  ftpData.clients[theSocketId].workerData.threadIsAlive = 1;
  ftpData.clients[theSocketId].workerData.threadHasBeenCreated = 1;
  int returnCode;

  //printf("\nWORKER CREATED!");

  //Passive data connection mode
  if (ftpData.clients[theSocketId].workerData.passiveModeOn == 1)
  {
GOAL_471:;

    int tries = 30;
    while (tries > 0)
    {
GOAL_473:;

        setRandomicPort(&ftpData, theSocketId);
        ftpData.clients[theSocketId].workerData.passiveListeningSocket = createPassiveSocket(ftpData.clients[theSocketId].workerData.connectionPort);

        if (ftpData.clients[theSocketId].workerData.passiveListeningSocket != -1)
        {
GOAL_474:;

            break;
        }

        tries--;
    }

    if (ftpData.clients[theSocketId].workerData.passiveListeningSocket == -1)
    {
GOAL_475:;

        ftpData.clients[theSocketId].closeTheClient = 1;
        //printf("\n Closing the client 1");
        pthread_exit(NULL);
    }

    if (ftpData.clients[theSocketId].workerData.socketIsConnected == 0)
    {
GOAL_476:;

    	returnCode = socketPrintf(&ftpData, theSocketId, "sdsdsdsdsdsds", "227 Entering Passive Mode (", ftpData.clients[theSocketId].serverIpAddressInteger[0], ",", ftpData.clients[theSocketId].serverIpAddressInteger[1], ",", ftpData.clients[theSocketId].serverIpAddressInteger[2], ",", ftpData.clients[theSocketId].serverIpAddressInteger[3], ",", (ftpData.clients[theSocketId].workerData.connectionPort / 256), ",", (ftpData.clients[theSocketId].workerData.connectionPort % 256), ")\r\n");
        if (returnCode <= 0)
        {
GOAL_477:;

            ftpData.clients[theSocketId].closeTheClient = 1;
            //printf("\n Closing the client 2");
            pthread_exit(NULL);
        }

        //Wait for sockets
        if ((ftpData.clients[theSocketId].workerData.socketConnection = accept(ftpData.clients[theSocketId].workerData.passiveListeningSocket, 0, 0))!=-1)
        {
GOAL_478:;

            ftpData.clients[theSocketId].workerData.socketIsConnected = 1;
			#ifdef OPENSSL_ENABLED
            if (ftpData.clients[theSocketId].dataChannelIsTls == 1)
            {

            	returnCode = SSL_set_fd(ftpData.clients[theSocketId].workerData.serverSsl, ftpData.clients[theSocketId].workerData.socketConnection);

        		if (returnCode == 0)
        		{
        			printf("\nSSL ERRORS ON WORKER SSL_set_fd");
        			ftpData.clients[theSocketId].closeTheClient = 1;
        		}

                returnCode = SSL_accept(ftpData.clients[theSocketId].workerData.serverSsl);

				if (returnCode <= 0)
				{
					printf("\nSSL ERRORS ON WORKER");
					ERR_print_errors_fp(stderr);
					ftpData.clients[theSocketId].closeTheClient = 1;
				}
				else
				{
					//printf("\nSSL ACCEPTED ON WORKER");
				}
            }
			#endif
        }
        else
        {
GOAL_479:;

            ftpData.clients[theSocketId].closeTheClient = 1;
            printf("\n Closing the client 3");
            pthread_exit(NULL);
        }
    }
  }
  else 
{

GOAL_472:;
 if (ftpData.clients[theSocketId].workerData.activeModeOn == 1)
  {
GOAL_480:;

    ftpData.clients[theSocketId].workerData.socketConnection = createActiveSocket(ftpData.clients[theSocketId].workerData.connectionPort, ftpData.clients[theSocketId].workerData.activeIpAddress);

	#ifdef OPENSSL_ENABLED
	if (ftpData.clients[theSocketId].dataChannelIsTls == 1)
	{
		returnCode = SSL_set_fd(ftpData.clients[theSocketId].workerData.clientSsl, ftpData.clients[theSocketId].workerData.socketConnection);

		if (returnCode == 0)
		{
			printf("\nSSL ERRORS ON WORKER SSL_set_fd");
			ftpData.clients[theSocketId].closeTheClient = 1;
		}
		//SSL_set_connect_state(ftpData.clients[theSocketId].workerData.clientSsl);
		returnCode = SSL_connect(ftpData.clients[theSocketId].workerData.clientSsl);
		if (returnCode <= 0)
		{
			printf("\nSSL ERRORS ON WORKER %d error code: %d", returnCode, SSL_get_error(ftpData.clients[theSocketId].workerData.clientSsl, returnCode));
			ERR_print_errors_fp(stderr);
		}
		else
		{
			//printf("\nSSL ACCEPTED ON WORKER");
		}
	}
	#endif

    if (ftpData.clients[theSocketId].workerData.socketConnection < 0)
    {
GOAL_481:;

        ftpData.clients[theSocketId].closeTheClient = 1;
        printf("\n Closing the client 4");
        pthread_exit(NULL);
    }

    returnCode = socketPrintf(&ftpData, theSocketId, "s", "200 connection accepted\r\n");

    if (returnCode <= 0)
    {
GOAL_482:;

        ftpData.clients[theSocketId].closeTheClient = 1;
        printf("\n Closing the client 5");
        pthread_exit(NULL);
    }

    ftpData.clients[theSocketId].workerData.socketIsConnected = 1;
  }
}



  //printf("\nftpData.clients[theSocketId].workerData.socketIsConnected = %d", ftpData.clients[theSocketId].workerData.socketIsConnected);

//Endless loop ftp process
  while (1)
  {
GOAL_483:;


    if (ftpData.clients[theSocketId].workerData.socketIsConnected > 0)
    {
GOAL_484:;

    	printf("\nWorker %d is waiting for commands!", theSocketId);
        //Conditional lock on tconditionVariablehread actions
        pthread_mutex_lock(&ftpData.clients[theSocketId].conditionMutex);
    	//int sleepTime = 1000;
        while (ftpData.clients[theSocketId].workerData.commandReceived == 0)
        {
GOAL_486:;

        	//usleep(sleepTime);
        	//if (sleepTime < 200000)
        	//{
        		//sleepTime+= 1000;
        	//}
            pthread_cond_wait(&ftpData.clients[theSocketId].conditionVariable, &ftpData.clients[theSocketId].conditionMutex);
        }
        pthread_mutex_unlock(&ftpData.clients[theSocketId].conditionMutex);

        //printf("\nWorker %d unlocked", theSocketId);

        if (ftpData.clients[theSocketId].workerData.commandReceived == 1 &&
            compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "STOR", strlen("STOR")) == 1 &&
            ftpData.clients[theSocketId].fileToStor.textLen > 0)
        {
GOAL_487:;


        	if ((checkParentDirectoryPermissions(ftpData.clients[theSocketId].fileToStor.text, ftpData.clients[theSocketId].login.ownerShip.uid, ftpData.clients[theSocketId].login.ownerShip.gid) & FILE_PERMISSION_W) != FILE_PERMISSION_W)
        	{
GOAL_489:;

            	returnCode = socketPrintf(&ftpData, theSocketId, "s", "550 No permissions to write the file\r\n");

                if (returnCode <= 0)
                {
GOAL_490:;

                    ftpData.clients[theSocketId].closeTheClient = 1;
                    printf("\n Closing the client 6");
                    pthread_exit(NULL);
                }

                break;
        	}

            #ifdef LARGE_FILE_SUPPORT_ENABLED
					//#warning LARGE FILE SUPPORT IS ENABLED!
                    ftpData.clients[theSocketId].workerData.theStorFile = fopen64(ftpData.clients[theSocketId].fileToStor.text, "wb");
            #endif

            #ifndef LARGE_FILE_SUPPORT_ENABLED
					#warning LARGE FILE SUPPORT IS NOT ENABLED!
                    ftpData.clients[theSocketId].workerData.theStorFile = fopen(ftpData.clients[theSocketId].fileToStor.text, "wb");
            #endif

            if (ftpData.clients[theSocketId].workerData.theStorFile == NULL)
            {
GOAL_491:;

            	returnCode = socketPrintf(&ftpData, theSocketId, "s", "553 Unable to write the file\r\n");

                if (returnCode <= 0)
                {
GOAL_492:;

                    ftpData.clients[theSocketId].closeTheClient = 1;
                    printf("\n Closing the client 6");
                    pthread_exit(NULL);
                }

                break;
            }

            returnCode = socketPrintf(&ftpData, theSocketId, "s", "150 Accepted data connection\r\n");

            if (returnCode <= 0)
            {
GOAL_493:;

                ftpData.clients[theSocketId].closeTheClient = 1;
                printf("\n Closing the client 7");
                pthread_exit(NULL);
            }

            while(1)
            {
GOAL_494:;


            	if (ftpData.clients[theSocketId].dataChannelIsTls != 1)
            	{
GOAL_495:;

            		ftpData.clients[theSocketId].workerData.bufferIndex = read(ftpData.clients[theSocketId].workerData.socketConnection, ftpData.clients[theSocketId].workerData.buffer, CLIENT_BUFFER_STRING_SIZE);
            	}
            	else 
{

GOAL_496:;
 if (ftpData.clients[theSocketId].dataChannelIsTls == 1)
            	{
GOAL_497:;


					#ifdef OPENSSL_ENABLED
            		if (ftpData.clients[theSocketId].workerData.passiveModeOn == 1)
            			ftpData.clients[theSocketId].workerData.bufferIndex = SSL_read(ftpData.clients[theSocketId].workerData.serverSsl, ftpData.clients[theSocketId].workerData.buffer, CLIENT_BUFFER_STRING_SIZE);
            		else if(ftpData.clients[theSocketId].workerData.activeModeOn == 1)
            			ftpData.clients[theSocketId].workerData.bufferIndex = SSL_read(ftpData.clients[theSocketId].workerData.clientSsl, ftpData.clients[theSocketId].workerData.buffer, CLIENT_BUFFER_STRING_SIZE);
					#endif
            	}
            	else
            	{
GOAL_498:;

            		printf("\nError state");
            	}
}


                if (ftpData.clients[theSocketId].workerData.bufferIndex == 0)
                {
GOAL_499:;

                    break;
                }
                else 
{

GOAL_500:;
 if (ftpData.clients[theSocketId].workerData.bufferIndex > 0)
                {
GOAL_501:;

                    fwrite(ftpData.clients[theSocketId].workerData.buffer, ftpData.clients[theSocketId].workerData.bufferIndex, 1, ftpData.clients[theSocketId].workerData.theStorFile);
                    usleep(100);
                }
                else 
{

GOAL_502:;
 if (ftpData.clients[theSocketId].workerData.bufferIndex < 0)
                {
GOAL_503:;

                    break;
                }
}

}

            }

            int theReturnCode;
            theReturnCode = fclose(ftpData.clients[theSocketId].workerData.theStorFile);
            ftpData.clients[theSocketId].workerData.theStorFile = NULL;

            if (ftpData.clients[theSocketId].login.ownerShip.ownerShipSet == 1)
            {
GOAL_504:;

                FILE_doChownFromUidGid(ftpData.clients[theSocketId].fileToStor.text, ftpData.clients[theSocketId].login.ownerShip.uid, ftpData.clients[theSocketId].login.ownerShip.gid);
            }

            returnCode = socketPrintf(&ftpData, theSocketId, "s", "226 file stor ok\r\n");
            if (returnCode <= 0)
            {
GOAL_505:;

                ftpData.clients[theSocketId].closeTheClient = 1;
                printf("\n Closing the client 8");
                pthread_exit(NULL);
            }

            break;
        }
      else 
{

GOAL_488:;
 if (ftpData.clients[theSocketId].workerData.commandReceived == 1 &&
               (  (compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "LIST", strlen("LIST")) == 1)
               || (compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "NLST", strlen("NLST")) == 1))
              )
        {
GOAL_506:;

          int theFiles = 0, theCommandType;

          if (compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "LIST", strlen("LIST")) == 1) 
{

GOAL_508:;

              theCommandType = COMMAND_TYPE_LIST;
          
}
else 
{

GOAL_509:;
 if (compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "NLST", strlen("NLST")) == 1) 
{

GOAL_510:;

              theCommandType = COMMAND_TYPE_NLST;
}

}



      	if ((checkUserFilePermissions(ftpData.clients[theSocketId].listPath.text, ftpData.clients[theSocketId].login.ownerShip.uid, ftpData.clients[theSocketId].login.ownerShip.gid) & FILE_PERMISSION_R) != FILE_PERMISSION_R)
          {
GOAL_511:;

              returnCode = socketPrintf(&ftpData, theSocketId, "s", "550 No permissions\r\n");
              if (returnCode <= 0)
              {
GOAL_512:;

                  ftpData.clients[theSocketId].closeTheClient = 1;
                  printf("\n Closing the client 8");
                  pthread_exit(NULL);
              }
              break;
          }

          returnCode = socketPrintf(&ftpData, theSocketId, "s", "150 Accepted data connection\r\n");
          if (returnCode <= 0)
          {
GOAL_513:;

              ftpData.clients[theSocketId].closeTheClient = 1;
              printf("\n Closing the client 8");
              pthread_exit(NULL);
          }

          //returnCode = writeListDataInfoToSocket(ftpData.clients[theSocketId].listPath.text, ftpData.clients[theSocketId].workerData.socketConnection, &theFiles, theCommandType);
          returnCode = writeListDataInfoToSocket(&ftpData, theSocketId, &theFiles, theCommandType, &ftpData.clients[theSocketId].workerData.memoryTable);
          if (returnCode <= 0)
          {
GOAL_514:;

              ftpData.clients[theSocketId].closeTheClient = 1;
              printf("\n Closing the client 9");
              pthread_exit(NULL);
          }

          returnCode = socketPrintf(&ftpData, theSocketId, "sds", "226 ", theFiles, " matches total\r\n");
          if (returnCode <= 0)
          {
GOAL_515:;

              ftpData.clients[theSocketId].closeTheClient = 1;
              printf("\n Closing the client 10");
              pthread_exit(NULL);
          }

          break;
      }
        else 
{

GOAL_507:;
 if (ftpData.clients[theSocketId].workerData.commandReceived == 1 &&
                 compareStringCaseInsensitive(ftpData.clients[theSocketId].workerData.theCommandReceived, "RETR", strlen("RETR")) == 1)
        {
GOAL_516:;

            long long int writenSize = 0, writeReturn = 0;
            writeReturn = socketPrintf(&ftpData, theSocketId, "s", "150 Accepted data connection\r\n");
            if (writeReturn <= 0)
            {
GOAL_517:;

                ftpData.clients[theSocketId].closeTheClient = 1;
                printf("\n Closing the client 11");
                pthread_exit(NULL);
            }

        	if ((checkUserFilePermissions(ftpData.clients[theSocketId].fileToRetr.text, ftpData.clients[theSocketId].login.ownerShip.uid, ftpData.clients[theSocketId].login.ownerShip.gid) & FILE_PERMISSION_R) != FILE_PERMISSION_R)
            {
GOAL_518:;

                writeReturn = socketPrintf(&ftpData, theSocketId, "s", "550 no reading permission on the file\r\n");
                if (writeReturn <= 0)
                {
GOAL_519:;

                  ftpData.clients[theSocketId].closeTheClient = 1;
                  printf("\n Closing the client 12");
                  pthread_exit(NULL);
                }

                break;
            }

            writenSize = writeRetrFile(&ftpData, theSocketId, ftpData.clients[theSocketId].workerData.retrRestartAtByte, ftpData.clients[theSocketId].workerData.theStorFile);
            ftpData.clients[theSocketId].workerData.retrRestartAtByte = 0;

            if (writenSize <= -1)
            {
GOAL_520:;

              writeReturn = socketPrintf(&ftpData, theSocketId, "s", "550 unable to open the file for reading\r\n");

              if (writeReturn <= 0)
              {
GOAL_521:;

                ftpData.clients[theSocketId].closeTheClient = 1;
                printf("\n Closing the client 12");
                pthread_exit(NULL);
              }
              break;
            }

            writeReturn = socketPrintf(&ftpData, theSocketId, "s", "226-File successfully transferred\r\n226 done\r\n");

            if (writeReturn <= 0)
            {
GOAL_522:;

              ftpData.clients[theSocketId].closeTheClient = 1;
              printf("\n Closing the client 13");
              pthread_exit(NULL);
            }
            break;
        }
}

}

      break;
    }
      else
      {
GOAL_485:;

          break;
      }

  }

  pthread_exit((void *)1);
  pthread_cleanup_pop(0);
  pthread_exit((void *)2);
  return NULL;
}

void runFtpServer(void)
{

GOAL_524:;

    printf("\nHello uFTP server %s starting..\n", UFTP_SERVER_VERSION);


    /* Needed for Select*/
    static int processingSock = 0, returnCode = 0;

    /* Handle signals */
    signalHandlerInstall();

    /*Read the configuration file */
    configurationRead(&ftpData.ftpParameters, &ftpData.generalDynamicMemoryTable);

    /* apply the reden configuration */
    applyConfiguration(&ftpData.ftpParameters);

    /* initialize the ftp data structure */
    initFtpData(&ftpData);

    printf("\nRespawn routine okay\n");

    //Fork the process
    respawnProcess();

    //Socket main creator
    ftpData.connectionData.theMainSocket = createSocket(&ftpData);
    printf("\nuFTP server starting..");

    /* init fd set needed for select */
    fdInit(&ftpData);

    /* the maximum socket fd is now the main socket descriptor */
    ftpData.connectionData.maxSocketFD = ftpData.connectionData.theMainSocket+1;

    returnCode = pthread_create(&watchDogThread, NULL, watchDog, NULL);

	if(returnCode != 0)
		{
GOAL_525:;

		printf("pthread_create WatchDog Error %d", returnCode);
		exit(0);
		}

  //Endless loop ftp process
    while (1)
    {
GOAL_526:;

    //Update watchdog timer
   	updateWatchDogTime((int)time(NULL));


	/*
	printf("\nUsed memory : %lld", DYNMEM_GetTotalMemory());
	int memCount = 0;
	for (memCount = 0; memCount < ftpData.ftpParameters.maxClients; memCount++)
	{
		if (ftpData.clients[memCount].memoryTable != NULL)
		{
			printf("\nftpData.clients[%d].memoryTable = %s", memCount, ftpData.clients[memCount].memoryTable->theName);
		}
		if (ftpData.clients[memCount].workerData.memoryTable != NULL)
		{
			printf("\nftpData.clients[%d].workerData.memoryTable = %s", memCount, ftpData.clients[memCount].workerData.memoryTable->theName);
		}

		if (ftpData.clients[memCount].workerData.directoryInfo.memoryTable != NULL)
		{
			printf("\nftpData.clients[%d].workerData.directoryInfo.memoryTable = %s", memCount, ftpData.clients[memCount].workerData.directoryInfo.memoryTable->theName);
		}
	}
	*/

        /* waits for socket activity, if no activity then checks for client socket timeouts */
        if (selectWait(&ftpData) == 0)
        {
GOAL_527:;

            checkClientConnectionTimeout(&ftpData);
            flushLoginWrongTriesData(&ftpData);
        }



        /*Main loop handle client commands */
        for (processingSock = 0; processingSock < ftpData.ftpParameters.maxClients; processingSock++)
        {
GOAL_528:;

            /* close the connection if quit flag has been set */
            if (ftpData.clients[processingSock].closeTheClient == 1)
            {
GOAL_529:;

                closeClient(&ftpData, processingSock);
                continue;
            }

            /* Check if there are client pending connections, accept the connection if possible otherwise reject */  
            if ((returnCode = evaluateClientSocketConnection(&ftpData)) == 1)
            {
GOAL_530:;

                break;
            }

            /* no data to check client is not connected, continue to check other clients */
          if (isClientConnected(&ftpData, processingSock) == 0) 
          {
GOAL_531:;

              /* socket is not conneted */
              continue;
          }

          if (FD_ISSET(ftpData.clients[processingSock].socketDescriptor, &ftpData.connectionData.rset) || 
              FD_ISSET(ftpData.clients[processingSock].socketDescriptor, &ftpData.connectionData.eset))
          {
GOAL_532:;


			#ifdef OPENSSL_ENABLED
				if (ftpData.clients[processingSock].tlsIsNegotiating == 1)
				{
					returnCode = SSL_accept(ftpData.clients[processingSock].ssl);

					if (returnCode <= 0)
					{
						//printf("\nSSL NOT YET ACCEPTED: %d", returnCode);
						ftpData.clients[processingSock].tlsIsEnabled = 0;
						ftpData.clients[processingSock].tlsIsNegotiating = 1;

						if ( ((int)time(NULL) - ftpData.clients[processingSock].tlsNegotiatingTimeStart) > TLS_NEGOTIATING_TIMEOUT )
						{
							ftpData.clients[processingSock].closeTheClient = 1;
							//printf("\nTLS timeout closing the client time:%lld, start time: %lld..", (int)time(NULL), ftpData.clients[processingSock].tlsNegotiatingTimeStart);
						}

					}
					else
					{
						//printf("\nSSL ACCEPTED");
						ftpData.clients[processingSock].tlsIsEnabled = 1;
						ftpData.clients[processingSock].tlsIsNegotiating = 0;
					}


					continue;
				}
			#endif

        	  if (ftpData.clients[processingSock].tlsIsEnabled == 1)
        	  {
GOAL_533:;

				  #ifdef OPENSSL_ENABLED
        		  ftpData.clients[processingSock].bufferIndex = SSL_read(ftpData.clients[processingSock].ssl, ftpData.clients[processingSock].buffer, CLIENT_BUFFER_STRING_SIZE);
				  #endif
        	  }
        	  else
        	  {
GOAL_534:;

        		  ftpData.clients[processingSock].bufferIndex = read(ftpData.clients[processingSock].socketDescriptor, ftpData.clients[processingSock].buffer, CLIENT_BUFFER_STRING_SIZE);
        	  }

            //The client is not connected anymore
            if ((ftpData.clients[processingSock].bufferIndex) == 0)
            {
GOAL_535:;

              closeClient(&ftpData, processingSock);
            }

            //Debug print errors
            if (ftpData.clients[processingSock].bufferIndex < 0)
            {
GOAL_536:;

                //ftpData.clients[processingSock].closeTheClient = 1;
                printf("\n1 Errno = %d", errno);
                perror("1 Error: ");
                continue;
            }

            //Some commands has been received
            if (ftpData.clients[processingSock].bufferIndex > 0)
            {
GOAL_537:;

              int i = 0;
              int commandProcessStatus = 0;
              for (i = 0; i < ftpData.clients[processingSock].bufferIndex; i++)
              {
GOAL_538:;

                  if (ftpData.clients[processingSock].commandIndex < CLIENT_COMMAND_STRING_SIZE)
                  {
GOAL_539:;

                      if (ftpData.clients[processingSock].buffer[i] != '\r' && ftpData.clients[processingSock].buffer[i] != '\n')
                      {
GOAL_541:;

                          ftpData.clients[processingSock].theCommandReceived[ftpData.clients[processingSock].commandIndex++] = ftpData.clients[processingSock].buffer[i];
                      }

                      if (ftpData.clients[processingSock].buffer[i] == '\n') 
                          {
GOAL_542:;

                              ftpData.clients[processingSock].socketCommandReceived = 1;
                              //printf("\n Processing the command: %s", ftpData.clients[processingSock].theCommandReceived);
                              commandProcessStatus = processCommand(processingSock);
                              //Echo unrecognized commands
                              if (commandProcessStatus == FTP_COMMAND_NOT_RECONIZED) 
                              {
GOAL_543:;

                                  int returnCode = 0;
                                  returnCode = socketPrintf(&ftpData, processingSock, "s", "500 Unknown command\r\n");
                                  if (returnCode < 0)
                                  {
GOAL_545:;

                                	  ftpData.clients[processingSock].closeTheClient = 1;
                                  }
                                  printf("\n COMMAND NOT SUPPORTED ********* %s", ftpData.clients[processingSock].buffer);
                              }
                              else 
{

GOAL_544:;
 if (commandProcessStatus == FTP_COMMAND_PROCESSED)
                              {
GOAL_546:;

                                  ftpData.clients[processingSock].lastActivityTimeStamp = (int)time(NULL);
                                  
                              }
                              else 
{

GOAL_547:;
 if (commandProcessStatus == FTP_COMMAND_PROCESSED_WRITE_ERROR)
                              {
GOAL_548:;

                                  ftpData.clients[processingSock].closeTheClient = 1;
                                  printf("\n Write error WARNING!");
                              }
}

}

                          }
                  }
                  else
                  {
GOAL_540:;

                      //Command overflow can't be processed
                      int returnCode;
                      ftpData.clients[processingSock].commandIndex = 0;
                      memset(ftpData.clients[processingSock].theCommandReceived, 0, CLIENT_COMMAND_STRING_SIZE);
                      returnCode = socketPrintf(&ftpData, processingSock, "s", "500 Unknown command\r\n");
                      if (returnCode <= 0) 
{

GOAL_549:;
 
                          ftpData.clients[processingSock].closeTheClient = 1;
}

                      
                      printf("\n Command too long closing the client.");
                      break;
                  }
              }
              usleep(100);
              memset(ftpData.clients[processingSock].buffer, 0, CLIENT_BUFFER_STRING_SIZE);
            }
        }
      }
  }

  //Server Close
  shutdown(ftpData.connectionData.theMainSocket, SHUT_RDWR);
  close(ftpData.connectionData.theMainSocket);
  return;
}

static int processCommand(int processingElement)
{

GOAL_550:;

    int toReturn = 0;
    //printTimeStamp();
    //printf ("\nCommand received from (%d): %s", processingElement, ftpData.clients[processingElement].theCommandReceived);

    cleanDynamicStringDataType(&ftpData.clients[processingElement].ftpCommand.commandArgs, 0, &ftpData.clients[processingElement].memoryTable);
    cleanDynamicStringDataType(&ftpData.clients[processingElement].ftpCommand.commandOps, 0, &ftpData.clients[processingElement].memoryTable);

    if (ftpData.clients[processingElement].login.userLoggedIn == 0 &&
        (compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "USER", strlen("USER")) != 1 &&
         compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PASS", strlen("PASS")) != 1 &&
         compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "QUIT", strlen("QUIT")) != 1 &&
		 compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PBSZ", strlen("PBSZ")) != 1 &&
		 compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PROT", strlen("PROT")) != 1 &&
		 compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "CCC", strlen("CCC")) != 1 &&
         compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "AUTH", strlen("AUTH")) != 1))
        {
GOAL_551:;

            toReturn = notLoggedInMessage(&ftpData, processingElement);
            ftpData.clients[processingElement].commandIndex = 0;
            memset(ftpData.clients[processingElement].theCommandReceived, 0, CLIENT_COMMAND_STRING_SIZE);
            return 1;
        }

    //Process Command
    if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "USER", strlen("USER")) == 1)
    {
GOAL_552:;

        //printf("\nUSER COMMAND RECEIVED");
        toReturn = parseCommandUser(&ftpData, processingElement);
    }
    else 
{

GOAL_553:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PASS", strlen("PASS")) == 1)
    {
GOAL_554:;

        //printf("\nPASS COMMAND RECEIVED");
        toReturn = parseCommandPass(&ftpData, processingElement);
    }
    else 
{

GOAL_555:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "SITE", strlen("SITE")) == 1)
    {
GOAL_556:;

        //printf("\nSITE COMMAND RECEIVED");
        toReturn = parseCommandSite(&ftpData, processingElement);
    }
    else 
{

GOAL_557:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "AUTH", strlen("AUTH")) == 1)
    {
GOAL_558:;

        //printf("\nAUTH COMMAND RECEIVED");
        toReturn = parseCommandAuth(&ftpData, processingElement);
    }
    else 
{

GOAL_559:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PROT", strlen("PROT")) == 1)
    {
GOAL_560:;

        //printf("\nPROT COMMAND RECEIVED");
        toReturn = parseCommandProt(&ftpData, processingElement);
    }
    else 
{

GOAL_561:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PBSZ", strlen("PBSZ")) == 1)
    {
GOAL_562:;

        //printf("\nPBSZ COMMAND RECEIVED");
        toReturn = parseCommandPbsz(&ftpData, processingElement);
    }
    else 
{

GOAL_563:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "CCC", strlen("CCC")) == 1)
    {
GOAL_564:;

        //printf("\nCCC COMMAND RECEIVED");
        toReturn = parseCommandCcc(&ftpData, processingElement);
    }
    else 
{

GOAL_565:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PWD", strlen("PWD")) == 1)
    {
GOAL_566:;

        //printf("\nPWD COMMAND RECEIVED");
        toReturn = parseCommandPwd(&ftpData, processingElement);
    }
    else 
{

GOAL_567:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "SYST", strlen("SYST")) == 1)
    {
GOAL_568:;

        //printf("\nSYST COMMAND RECEIVED");
        toReturn = parseCommandSyst(&ftpData, processingElement);
    }
    else 
{

GOAL_569:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "FEAT", strlen("FEAT")) == 1)
    {
GOAL_570:;

        //printf("\nFEAT COMMAND RECEIVED");
        toReturn = parseCommandFeat(&ftpData, processingElement);
    }
    else 
{

GOAL_571:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "TYPE I", strlen("TYPE I")) == 1)
    {
GOAL_572:;

        //printf("\nTYPE I COMMAND RECEIVED");
        toReturn = parseCommandTypeI(&ftpData, processingElement);
    }
    else 
{

GOAL_573:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "STRU F", strlen("STRU F")) == 1)
    {
GOAL_574:;

        //printf("\nTYPE I COMMAND RECEIVED");
        toReturn = parseCommandStruF(&ftpData, processingElement);
    }    
    else 
{

GOAL_575:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "MODE S", strlen("MODE S")) == 1)
    {
GOAL_576:;

        //printf("\nMODE S COMMAND RECEIVED");
        toReturn = parseCommandModeS(&ftpData, processingElement);
    }    
    else 
{

GOAL_577:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "TYPE A", strlen("TYPE A")) == 1)
    {
GOAL_578:;

        //printf("\nTYPE A COMMAND RECEIVED");
        toReturn = parseCommandTypeI(&ftpData, processingElement);
    }    
    else 
{

GOAL_579:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PASV", strlen("PASV")) == 1)
    {
GOAL_580:;

        //printf("\nPASV COMMAND RECEIVED");
        toReturn = parseCommandPasv(&ftpData, processingElement);
    }
    else 
{

GOAL_581:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "PORT", strlen("PORT")) == 1)
    {
GOAL_582:;

        //printf("\nPORT COMMAND RECEIVED");
        toReturn = parseCommandPort(&ftpData, processingElement);
    }
    else 
{

GOAL_583:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "LIST", strlen("LIST")) == 1)
    {
GOAL_584:;

        //printf("\nLIST COMMAND RECEIVED");
        toReturn = parseCommandList(&ftpData, processingElement);
    }
    else 
{

GOAL_585:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "CWD", strlen("CWD")) == 1)
    {
GOAL_586:;

        //printf("\nCWD COMMAND RECEIVED");
        toReturn = parseCommandCwd(&ftpData, processingElement);
    }
    else 
{

GOAL_587:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "CDUP", strlen("CDUP")) == 1)
    {
GOAL_588:;

        //printf("\nCDUP COMMAND RECEIVED");
        toReturn = parseCommandCdup(&ftpData, processingElement);
    }
    else 
{

GOAL_589:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "REST", strlen("REST")) == 1)
    {
GOAL_590:;

        //printf("\nREST COMMAND RECEIVED");
        toReturn = parseCommandRest(&ftpData, processingElement);
    }
    else 
{

GOAL_591:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "RETR", strlen("RETR")) == 1)
    {
GOAL_592:;

        //printf("\nRETR COMMAND RECEIVED");
        toReturn = parseCommandRetr(&ftpData, processingElement);
    }
    else 
{

GOAL_593:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "STOR", strlen("STOR")) == 1)
    {
GOAL_594:;

        //printf("\nSTOR COMMAND RECEIVED");
        toReturn = parseCommandStor(&ftpData, processingElement);
    }
    else 
{

GOAL_595:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "MKD", strlen("MKD")) == 1)
    {
GOAL_596:;

        //printf("\nMKD command received");
        toReturn = parseCommandMkd(&ftpData, processingElement);
    }
    else 
{

GOAL_597:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "ABOR", strlen("ABOR")) == 1)
    {
GOAL_598:;

        //printf("\nABOR command received");
        toReturn = parseCommandAbor(&ftpData, processingElement);
    }
    else 
{

GOAL_599:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "DELE", strlen("DELE")) == 1)
    {
GOAL_600:;

        //printf("\nDELE comman200 OKd received");
        toReturn = parseCommandDele(&ftpData, processingElement);
    }
    else 
{

GOAL_601:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "OPTS", strlen("OPTS")) == 1)
    {
GOAL_602:;

        //printf("\nOPTS command received");
        toReturn = parseCommandOpts(&ftpData, processingElement);
    }    
    else 
{

GOAL_603:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "MDTM", strlen("MDTM")) == 1)
    {
GOAL_604:;

        printf("\nMTDM command received");
    	toReturn = parseCommandMdtm(&ftpData, processingElement);
    }
    else 
{

GOAL_605:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "NLST", strlen("NLST")) == 1)
    {
GOAL_606:;

       // printf("\nNLST command received");
        toReturn = parseCommandNlst(&ftpData, processingElement);
    }
    else 
{

GOAL_607:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "QUIT", strlen("QUIT")) == 1)
    {
GOAL_608:;

        //printf("\nQUIT command received");
        toReturn = parseCommandQuit(&ftpData, processingElement);
    }
    else 
{

GOAL_609:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "RMD", strlen("RMD")) == 1)
    {
GOAL_610:;

       // printf("\nRMD command received");
        toReturn = parseCommandRmd(&ftpData, processingElement);
    }
    else 
{

GOAL_611:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "RNFR", strlen("RNFR")) == 1)
    {
GOAL_612:;

       // printf("\nRNFR command received");
        toReturn = parseCommandRnfr(&ftpData, processingElement);
    }
    else 
{

GOAL_613:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "RNTO", strlen("RNTO")) == 1)
    {
GOAL_614:;

       // printf("\nRNTO command received");
        toReturn = parseCommandRnto(&ftpData, processingElement);
    }
    else 
{

GOAL_615:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "SIZE", strlen("SIZE")) == 1)
    {
GOAL_616:;

        //printf("\nSIZE command received");
        toReturn = parseCommandSize(&ftpData, processingElement);
    }
    else 
{

GOAL_617:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "APPE", strlen("APPE")) == 1)
    {
GOAL_618:;

       // printf("\nAPPE command received");
        //To implement
    }
    else 
{

GOAL_619:;
 if(compareStringCaseInsensitive(ftpData.clients[processingElement].theCommandReceived, "NOOP", strlen("NOOP")) == 1)
    {
GOAL_620:;

        //printf("\nNOOP command received");
        toReturn = parseCommandNoop(&ftpData, processingElement);
    }
    else
    {
GOAL_621:;

        ; //Parse unsupported command not needed
    }
}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}

}


    ftpData.clients[processingElement].commandIndex = 0;
    memset(ftpData.clients[processingElement].theCommandReceived, 0, CLIENT_COMMAND_STRING_SIZE);
    return toReturn;
}

void deallocateMemory(void)
{

GOAL_622:;

	int i = 0;
//  printf("\n Deallocating the memory.. ");
//	printf("\nDYNMEM_freeAll called");
//	printf("\nElement size: %ld", ftpData.generalDynamicMemoryTable->size);
//	printf("\nElement address: %ld", (long int) ftpData.generalDynamicMemoryTable->address);
//	printf("\nElement nextElement: %ld",(long int) ftpData.generalDynamicMemoryTable->nextElement);
//	printf("\nElement previousElement: %ld",(long int) ftpData.generalDynamicMemoryTable->previousElement);

	for (i = 0; i < ftpData.ftpParameters.maxClients; i++)
	{
GOAL_623:;

		DYNMEM_freeAll(&ftpData.clients[i].memoryTable);
		DYNMEM_freeAll(&ftpData.clients[i].workerData.memoryTable);
	}

	DYNMEM_freeAll(&ftpData.loginFailsVector.memoryTable);
	DYNMEM_freeAll(&ftpData.ftpParameters.usersVector.memoryTable);
    DYNMEM_freeAll(&ftpData.generalDynamicMemoryTable);

    //printf("\n\nUsed memory at end: %lld", DYNMEM_GetTotalMemory());

    //printf("\n ftpData.generalDynamicMemoryTable = %ld", ftpData.generalDynamicMemoryTable);
	#ifdef OPENSSL_ENABLED
    SSL_CTX_free(ftpData.serverCtx);
    cleanupOpenssl();
	#endif
}
/*
 * The MIT License
 *
 * Copyright 2018 Ugo Cirmignani.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdio.h>
#include <stdlib.h>


#include "ftpServer.h"

int main(int argc, char** argv) 
{

GOAL_624:;


    runFtpServer();
    return (EXIT_SUCCESS);
}
