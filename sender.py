# Written by S. Mevawala, modified by D. Gitzel

import logging
import socket

import channelsimulator
import utils
import sys
import time
import numpy as np

class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=1, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)

        # ------- Added ------


    def make_pkt(self,nextSeqNum,data,checksum):
        #print('MAKE SEND PACKET')

        newData = bytearray()
        newData.append(nextSeqNum)
        newData.append(checksum)
        newData.append(1)#len(self.dataSegments))
        newData+=data

        return newData
        
        



    def getAckNum(self,data):
        #print('GET ACKNUM')
        return data[self.ackNum]

    
    def handle_timeout(self,sndpckt,base,nextSeqNum):
        print('(sender) HANDLE TIMEOUT')
        for i in range(base,nextSeqNum):
            print('(sender) RESENDING PACKET: '+str(i))
            self.simulator.u_send(sndpckt[i])


    def getChecksum(self,data):
        #print('MAKE CHECKSUM')
        mod = 100
        check = 0
        for i in range(len(data)):
            check+=data[i]
        return check%mod

    def isCorrupt(self,data,nextSeqNum,checksum):
        #print('CORRUPT CHECK')
        ack = data[1]
        seqNum = data[0]
        check = data[2]

        if(seqNum!=nextSeqNum):
            print('(sender) SEQNUM GOT: '+str(seqNum)+' EXPECTED: '+str(nextSeqNum))
            return True
        elif(ack!=123):
            print('(sender) GOT NACK')
            return True
        elif(self.getChecksum(data[0:2])!=check):
            print('(sender) INCORRECT CHECKSUM')
            return True
        return False

            
        


    def send(self, data):
        print('(sender) SEND')
        self.data = data # Actual data
        self.seqNums = [x for x in range(1,255)]*((len(data)/255)+1)
        self.nextSeqNum = 0 # Sequence number
        self.base = 0 # Pointer to where you are up to in the data
        self.window = 4 # Window which can be modified
        self.sndpckt = [] # Packet to be sent
        self.checksum = self.getChecksum(self.data)

        self.indData = 3 # Actual data/checksum
        self.dataSegNum = 2
        self.indCheck = 1 # Checksum/ack
        self.ackNum = 0 # seq number/seq num

        # Split data into mtu size

        # -------- Segments data ----------
        self.mtu = 1000
        self.dataSegments = []

        index = 0
        while(index<len(self.data)):
            if(index+self.mtu>len(self.data)):
                self.dataSegments.append(self.data[index:])
            else:
                self.dataSegments.append(self.data[index:index+self.mtu])
            index += self.mtu 
        # ---------------------------------

        self.seqNums = [x for x in range(len(self.dataSegments))]
        self.sndpkt = []
        self.numComplete = 0
        while(self.nextSeqNum<len(self.dataSegments)):
            self.sndpkt.append(self.make_pkt(self.nextSeqNum%255,self.dataSegments[self.nextSeqNum],self.getChecksum(self.dataSegments[self.nextSeqNum])))
        
            print('(sender) SEND PACKET: '+str(self.nextSeqNum))
            self.simulator.u_send(self.sndpkt[self.nextSeqNum])

            print('(sender) WAITING FOR ACK')
            flag = True
            while(flag):
                try:
                    response = self.simulator.u_receive()
                    print('(sender) RECEIVED DATA')
                    if(response[0]==self.nextSeqNum%255):
                        print('(sender) NOT CORRUPT')
                        self.nextSeqNum+=1
                        flag = False
                    else:
                        print('(sender) CORRUPT')
                        self.simulator.u_send(self.sndpkt[self.nextSeqNum])
                except socket.timeout:
                    print('(sender) TIMEOUT. RESENDING')
                    self.simulator.u_send(self.sndpkt[self.nextSeqNum])
        print('(sender) DONE TRASMITTING')
        num=0
        while(num<10):
            pkt = bytearray()
            pkt.append(1)
            pkt.append(1)
            self.simulator.u_send(pkt)
            num+=1

        '''
        while(self.nextSeqNum<len(self.dataSegments)):
            #time.sleep(.5)

            while(self.nextSeqNum<self.base+self.window and self.nextSeqNum<len(self.dataSegments)):

                self.sndpkt.append(self.make_pkt(self.nextSeqNum,self.dataSegments[self.nextSeqNum],self.getChecksum(self.dataSegments[self.nextSeqNum])))
                
                print('(sender) SEND PACKET: '+str(self.nextSeqNum))
                self.simulator.u_send(self.sndpkt[self.nextSeqNum])
                

                self.nextSeqNum+=1

            while(self.base<self.nextSeqNum):
                #time.sleep(.5)
                print('(sender) WAITING FOR ACK')
                try:
                    response = self.simulator.u_receive()
                    print('(sender) RECEIVED DATA')

                    checksum = response[2]
                    ackNum = response[0]
                    ack = response[1]
                    print('(sender) Received ack num: '+str(ackNum))
                    if(not self.isCorrupt(response,self.base,self.checksum)):
                        print('(sender) NOT CORRUPT')
                        self.base+=1
                    else:
                        print('(sender) CORRUPT')
                        self.handle_timeout(self.sndpkt,self.base,self.nextSeqNum)
                except socket.timeout:
                    print('(sender) DID NOT RECEIVE ACK, TIMEOUT')
                    self.handle_timeout(self.sndpkt,self.base,self.nextSeqNum)
        print('(sender) DONE TRANSMITTING')
        flag = True
        num=0
        while(num<10):
            pkt = bytearray()
            pkt.append(1)
            pkt.append(1)
            self.simulator.u_send(pkt)
            num+=1
        '''

                
                


        #self.sndpckt.append(self.make_pkt(self.seqNums[self.nextSeqNum],self.data,self.checksum))
        #print(self.sndpckt)
        #print(self.sndpckt[0][self.ackNum])

        #while True:

        #    if(self.nextSeqNum<self.base+self.window):
        #        self.sndpckt.append(self.make_pkt(self.nextSeqNum,self.data,self.checksum))

        '''
        while True:
            if(self.nextSeqNum<self.base+self.window):
                # If seq num is inside window
                self.sndpckt.append(self.make_pkt(self.seqNums[self.nextSeqNum],self.data,self.checksum))

                if(self.base==self.nextSeqNum): # If pointer is caught up you can send
                    try:
                        self.simulator.u_send(self.data)
                    except socket.timeout:
                        self.handle_timeout(self.sndpckt,self.base,self.nextSeqNum)
                else:
                    self.simulator.u_send(self.data)
                self.nextSeqNum+=1
            else:
                print('Error')
                sys.exit()


            response = None
            while(not response):

                response = self.simulator.u_receive()
                print(response)
                if(self.isCorrupt(response,self.nextSeqNum,self.checksum)):
                    print('IT IS CORRUPT')
            



            

            if(self.notCorrupt(response)):
                self.base = self.getAckNum(response)
                if(self.base==self.nextSeqNum):
                    try:
            



            if(self.base!=self.nextSeqNum):
                try:
                    base = self.getAckNum(self.simulator.u_receive())+1
                except socket.timeout:
                    self.handle_timeout(self.sndpckt,self.base,self.nextSeqNum)
            else:
                base = self.getAckNum(self.simulator.u_receive())+1
        '''
            
        




        
        











class BogoSender(Sender):

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.u_send(data)  # send data
                ack = self.simulator.u_receive()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass


if __name__ == "__main__":
    # test out BogoSender
    DATA = bytearray(sys.stdin.read())
    sndr = Sender()
    sndr.send(DATA)
