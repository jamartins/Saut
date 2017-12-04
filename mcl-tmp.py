# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 21:22:11 2017

@author: ritam

"""
import rospy, tf
from geometry_msgs.msg import PoseStamped
import math as m
import random as r
import numpy as np
from resampling import Low_variance_resampling,stratified_resample,residual_resampling
from matplotlib import pyplot

LARGURA = 900
COMP = 1000

def show(room,final):
    
    pyplot.figure(figsize=(30.,30.))
    pyplot.title('MCL')
    
    pyplot.axis([0,COMP,0,LARGURA])
    pyplot.grid(b=True, color='0.75', linestyle='--')
    
    for particle in room:
        pyplot.gca().add_patch(pyplot.Circle((particle[0],particle[1]),15.,facecolor='#ffb266',edgecolor='#994c00', alpha=0.5))
        pyplot.gca().add_patch(pyplot.Arrow(particle[0], particle[1], 30*m.cos(particle[2]), 30*m.sin(particle[2]), alpha=1., facecolor='#994c00', edgecolor='#994c00',width=15))
    
    
    
    pyplot.gca().add_patch(pyplot.Circle((final[0],final[1]),15.,facecolor='#6666ff',edgecolor='#0000cc', alpha=0.5))
    pyplot.gca().add_patch(pyplot.Arrow(final[0], final[1], 30*m.cos(final[2]), 30*m.sin(final[2]), alpha=1., facecolor='#000000', edgecolor='#000000',width=15))
                                 
    pyplot.savefig('Particles')
    
    
def add_particle():
#a <= N <= b
    return((r.uniform(0,LARGURA), r.uniform(0,COMP),r.uniform(0,2*m.pi)))

def gaussian_prob(particle,sensor):
    
    sigma=0.5 #????
    
    mu_x= particle[0]-sensor[0]
    mu_y= particle[1]-sensor[1]
    mu_teta= particle[2]-sensor[2]
    
    exp= -(((mu_x+mu_y+mu_teta)/3)**2)/(2*sigma**2)
    
    return (1/(m.sqrt(2*m.pi)*sigma)*m.e**exp)

def motion_update(x,y,teta):   
    if 0 < x < COMP and 0 < y < LARGURA:
        return ((x,y,teta))
    else:
        return add_particle() #kidnapped


####Sensing and sensor related functions:  

class Sensor:
    #x,y,yaw,seqnr, verbose


    def __init__(self, verbose=False):
    	self.verbose = verbose
    	self.x = 0
    	self.y= 0
    	self.yaw=0
     	self.seqnr=-1

    	rospy.init_node('listener', anonymous=True)
    	topic = '/crazyflie/vrpn_client_node/crazyflie/pose' 
        rospy.Subscriber(topic, PoseStamped, self.readingCallback)
        if self.verbose:
        	print 'just subscribed ' + topic +  '\n'

    def readingCallback(self, data):
        if self.verbose:
        	print 'callbacked'
        point = data.pose.position
        quatrnion = data.pose.orientation
        euler = tf.transformations.euler_from_quaternion((quatrnion.x, quatrnion.y, quatrnion.z, quatrnion.w))
        self.x = point.x
        self.y = point.y
        self.yaw = euler[2]
        self.seqnr = data.header.seq
        if self.verbose:
        	print ("this is yaw :" + str(self.seqnr))
        	print ("I heard position " + str(point.x) + str(point.y) + str(point.z)  + ' and quat :'+ str(quatrnion.x) + str(quatrnion.y) + str(quatrnion.z) + str(quatrnion.w))
    
    def getReadings(self):
    	return (self.x, self.y, self.yaw)


def mcl():
        
    sensor = Sensor()
    n_particles = 1500
    
    #noise = n_particles*0.1 ?
    
    room=list()
    weights=np.array([])
    
    for n in range(n_particles):
        room.append(add_particle())
        weights = np.append(weights,1)
   
    while True:
        sum_w = 0
        x=np.array([])
        y=np.array([])
        teta=np.array([])
        #--- lê sensor 
        #v,w,position_s=sensing()
        xpos, ypos, tetaangl = sensor.getReadings()

        #room = [ motion_update(particle) 
        new_prob=np.array([])
        s_weight = np.array([])

        fake_pos_s = (100,200,80)
        
        for particle in room:
            
            room[room.index(particle)] = motion_update(xpos, ypos, tetaangl)
            #new_prob= np.append(new_prob,gaussian_prob(particle, (xpos, ypos, tetaangl)))
            new_prob= np.append(new_prob,gaussian_prob(particle, fake_pos_s))
            sum_w += new_prob[-1]
        
        weights = weights*new_prob
        weights = weights / sum_w #normalização
        
        #if  condition for resampling:
            #resample
        s_weight = np.sort(weights)
        n=0
        
        print(np.where(weights==s_weight[0])[0][0])
        for i in range(100):     #weighted mean in a small window around the best particle
            if s_weight[i]==s_weight[i-1]:
                continue
            for position in range(len(np.where(weights==s_weight[i])[0])):
                n+=1
                x = np.append(x,room[np.where(weights==s_weight[i])[0][position]][0])
                y = np.append(y,room[np.where(weights==s_weight[i])[0][position]][1])
                teta = np.append(teta,room[np.where(weights==s_weight[i])[0][position]][2])
            if n ==50:
                break
            
        robot=(np.median(x),np.median(y),np.median(teta))
        print(robot)
        show(room,robot)
        print('ciclo')
        room,weights=residual_resampling(weights,room)
        #room,weights = stratified_resample(weights,room)
        #if np.var(weights) !=0 :
         #   if (1/np.var(weights))<(n_particles/2):
          #      print("resampled")
           #     room,weights = Low_variance_resampling(room,weights)
        timer = raw_input("what")
        
        
  #resampling se preciso
  # mensagens --- sensing DO!!!
  
if __name__ == '__main__':

	mcl()
