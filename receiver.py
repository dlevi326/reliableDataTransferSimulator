# Written by S. Mevawala, modified by D. Gitzel

import logging

import channelsimulator
import utils
import sys
import socket

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
        print('MAKE CHECKSUM')
        mod = 100
        check = 0
        for i in range(len(data)):
            check+=data[i]
        return check%mod

    def make_pkt(self,expectedSeqNum,ack,checksum):
        print('MAKE RCV PACKET')
        newData = bytearray()
        newData.append(expectedSeqNum)
        newData.append(123)
        newData.append(checksum)

        return newData

    def receive(self):


        data = self.simulator.u_receive()
        print('RECEIVE')

        self.expectedSeqNum = 0
        self.ACK_DATA = bytes(123)
        self.seqNums = [x for x in range(1,255)]*((len(data)/255)+1)
        
        self.indData = 2 # Actual data
        self.indCheck = 1 # Checksum
        self.ackNum = 0 # Ack number (seq num)


        sndpkt = self.make_pkt(self.seqNums[self.expectedSeqNum],self.ACK_DATA,self.getChecksum(data[self.indData:]))
        print(sndpkt)
        self.simulator.u_send(sndpkt)
















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
