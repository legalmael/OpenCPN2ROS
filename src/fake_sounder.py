#!/usr/bin/env python
# coding=utf-8

# Author : Maël LE GALLIC
# Date : 12/06/2018

import rospy
from std_msgs.msg import Float64
from nmea_msgs.msg import Sentence

def checksum(msg):
    return str(hex(reduce((lambda a,b : a^b), map(ord, msg))))[2:]

class FakeSounder:
    def __init__(self):
        rospy.Subscriber('depth', Float64, self.cb_depth, queue_size=10)
        self.pub_nmea = rospy.Publisher('nmea_sentence', Sentence, queue_size=10)
        self.rate = rospy.Rate(rospy.get_param('~rate', 3))
        self.cur_depth = None

    def cb_depth(self, depth_msg):
        self.cur_depth = depth_msg.data

    def sendSDDBT(self):
        if self.cur_depth == None:
            return
        depth = self.cur_depth  # in meters
        depth_feet = 3.280839895 * depth
        depth_fathoms = 0.5464480874 * depth
        msg_comp = "SDDBT," + str(depth_feet) + ",f," + str(depth) + ",M," + str(depth_fathoms) + ",F"
        self.sendSentence(msg_comp)

    def sendSentence(self, msg):
        sentence = Sentence()
        sentence.header.stamp = rospy.Time.now()
        sentence.sentence = "$" + msg + "*" + checksum(msg)
        self.pub_nmea.publish(sentence)

    def run(self):
        while not rospy.is_shutdown():
            self.sendSDDBT()
            self.rate.sleep()

if __name__ == '__main__':
    rospy.init_node('fake_sounder')
    FakeSounder().run()
