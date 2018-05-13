# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket
import time

class Receiver(object):

    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=1, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def getChecksum(self,data):
        #print('MAKE CHECKSUM')
        mod = 100
        check = 0
        for i in range(len(data)):
            check+=data[i]
        return check%mod

    def make_pkt(self,expectedSeqNum,ack,checksum):
        #print('MAKE RCV PACKET')
        newData = bytearray()
        newData.append(expectedSeqNum)
        newData.append(123)
        newData.append(self.getChecksum(newData))

        return newData

    def hasSeqNum(self,data,num):
        if data==num:
            return True
        print('(receiver) GOT DATA SEQ: '+str(data)+' EXPECTED: '+str(num))
        return False

    def notCorrupt(self,data,checksum):
        if data[1] == checksum:
            return True
        else:
            print('(receiver) GOT DATA CHECK: '+str(data[1])+' EXPECTED: '+str(checksum))
            return False

    def isfinished(self,data):
        if len(data)==2:
            return False

    def receive(self):
        self.expectedSeqNum = 0
        self.ACK_DATA = bytes(123)
        #self.seqNums = [x for x in range(1,255)]*((len(data)/255)+1)
        
        self.indData = 2 # Actual data
        self.indCheck = 1 # Checksum
        self.ackNum = 0 # Ack number (seq num)

        f = open('output.txt','w')

        while(True):
            try:
                data = self.simulator.u_receive()
                print('(receiver) RECEIVED DATA')
                if len(data)==2:
                    print('(receiver) FINISHED RECEIVING')
                    break
            except socket.timeout:
                continue

            if(self.notCorrupt(data,self.getChecksum(data[3:])) and self.hasSeqNum(data[0],self.expectedSeqNum%255)):
                sndpkt = self.make_pkt(self.expectedSeqNum%255,self.ACK_DATA,self.getChecksum(data[3:]))
                print('(receiver) NOT CORRUPT, SENDING ACK: '+str(sndpkt[0]))
                self.simulator.u_send(sndpkt)
                print(data[3:])
                f.write(data[3:])
                self.expectedSeqNum+=1
            elif(self.notCorrupt(data,self.getChecksum(data[3:]))):
                if(data[0]<self.expectedSeqNum%255):
                    sndpkt = self.make_pkt(data[0],self.ACK_DATA,self.getChecksum(data[3:]))
                    print('(receiver) PACKET ALREADY RECEIVED, SENDING ACK: '+str(sndpkt[0]))
                    self.simulator.u_send(sndpkt)
        f.close()



        '''
        while(True):
            #time.sleep(.5)
            try:
                data = self.simulator.u_receive()
                print('(receiver) RECEIVED DATA')
                if len(data)==2:
                    print('(receiver) FINISHED!!!!')
                    break
                #if(self.isfinished(data)):
                #    break
            except Exception as e:#socket.timeout:
                print e
                continue

            

            if(self.notCorrupt(data,self.getChecksum(data[3:])) and self.hasSeqNum(data[0],self.expectedSeqNum)):
                
                sndpkt = self.make_pkt(self.expectedSeqNum,self.ACK_DATA,self.getChecksum(data[3:]))
                print('(receiver) NOT CORRUPT, SENDING ACK: '+str(sndpkt[0]))
                self.simulator.u_send(sndpkt)
                print(data[3:])
                f.write(data[3:])
                self.expectedSeqNum+=1
            elif(self.notCorrupt(data,self.getChecksum(data[3:]))):
                if(data[0]<self.expectedSeqNum):
                    sndpkt = self.make_pkt(data[0],self.ACK_DATA,self.getChecksum(data[3:]))
                    print('(receiver) PACKET ALREADY RECEIVED, SENDING ACK: '+str(sndpkt[0]))
                    self.simulator.u_send(sndpkt)
                #print(data[2:])
                #self.expectedSeqNum+=1
            else:
                print('(receiver) CORRUPT, SENDING NACK')
                sndpkt = self.make_pkt(self.expectedSeqNum,0,self.getChecksum(data[3:]))
                #self.simulator.u_send(sndpkt)
            
        print('(receiver) FINISHED RECEIVING')
        '''
        f.close()

















class BogoReceiver(Receiver):
    ACK_DATA = bytes(123)

    def __init__(self):
        super(BogoReceiver, self).__init__()

    def receive(self):
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        while True:
            try:
                 data = self.simulator.u_receive()  # receive data
                 self.logger.info("Got data from socket: {}".format(
                     data.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
	         sys.stdout.write(data)
                 self.simulator.u_send(BogoReceiver.ACK_DATA)  # send ACK
            except socket.timeout:
                sys.exit()

if __name__ == "__main__":
    # test out BogoReceiver
    rcvr = Receiver()
    rcvr.receive()
