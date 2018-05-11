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
        print('MAKE PACKET')
        newData = bytearray(nextSeqNum)
        newData.append(checksum)
        for bit in data:
            newData.append(bit)
        return newData
        



    def getAckNum(self,data):
        print('GET ACKNUM')
        return data[self.ackNum]

    
    def handle_timeout(self,sndpckt,base,nextSeqNum):
        print('HANDLE TIMEOUT')
        try:
            for i in range(base,nextSeqNum):
                self.simulator.u_send(sndpckt[i])
        except socket.timeout:
            handle_timeout(sndpckt,base,nextSeqNum)

    def getChecksum(self,data):
        print('MAKE CHECKSUM')
        mod = 100
        check = 0
        for i in range(len(data)):
            check+=data[i]
        return check%mod

    def isCorrupt(self,data,nextSeqNum,checksum):
        print('CORRUPT CHECK')
        ack = data[1]
        seqNum = data[0]
        check = data[2]
        print('-'*60)
        print(ack)
        print(bytes(123))
        print('-'*60)
        print(seqNum)
        print(nextSeqNum)
        print('-'*60)
        print(check)
        print(checksum)
        if(seqNum!=nextSeqNum or check==checksum or ack!=bytes(123)):
            return True
        else:
            return False


    def send(self, data):
        print('SEND')
        self.data = data # Actual data
        self.seqNums = [x for x in range(1,255)]*((len(data)/255)+1)
        self.nextSeqNum = 0 # Sequence number
        self.base = 0 # Pointer to where you are up to in the data
        self.window = 4 # Window which can be modified
        self.sndpckt = [] # Packet to be sent
        self.checksum = self.getChecksum(self.data)

        self.indData = 2 # Actual data
        self.indCheck = 1 # Checksum
        self.ackNum = 0 # Ack number (seq num)


        self.sndpckt.append(self.make_pkt(self.seqNums[self.nextSeqNum],self.data,self.checksum))
        #print(self.sndpckt)
        #print(self.sndpckt[0][self.ackNum])

        
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



        response = self.simulator.u_receive()

        if(self.isCorrupt(response,self.nextSeqNum,self.checksum)):
            print('IT IS CORRUPT')



        '''

        if(self.notCorrupt(response)):
            self.base = self.getAckNum(response)
            if(self.base==self.nextSeqNum):
                try:
        '''



        '''
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
