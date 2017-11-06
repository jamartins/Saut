# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 21:22:11 2017

@author: ritam

"""
import math as m
import random as r
import numpy as np
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

def motion_update(particle,v,w):
    dt= 1   #???
    
    x,y,teta=particle
    
    x += v*dt*m.cos(teta)
    y += v*dt*m.sin(teta)
    teta += w*dt
    
    if 0 < x < COMP and 0 < y < LARGURA:
        return ((x,y,teta))
    else:
        return add_particle() #kidnapped
  
def sensing():
    #receber ros
    v=2
    w=3
    dist=(100,200,80)
    return v,w,dist  
       
def mcl():
    
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
        v,w,position_s=sensing()
        
        #room = [ motion_update(particle) 
        new_prob=np.array([])
        s_weight = np.array([])
        for particle in room:
            
            room[room.index(particle)] = motion_update(particle,v,w)
            new_prob= np.append(new_prob,gaussian_prob(particle,position_s))
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
        input()
        
  #resampling se preciso
  # mensagens --- sensing DO!!!
  #clustering???
mcl()