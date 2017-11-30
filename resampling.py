# -*- coding: utf-8 -*-
"""
Created on Sun Nov 19 22:19:11 2017

@author: ritam
"""
import numpy as np
import random
import math as m

LARGURA = 900
COMP = 1000
    
def add_particle():
#a <= N <= b
    return((random.uniform(0,LARGURA), random.uniform(0,COMP),random.uniform(0,2*m.pi)))

"""
   This algorithm separates the sample space into N divisions. A single random
    offset is used to to choose where to sample from for all divisions. This
    guarantees that every sample is exactly 1/N apart.
"""
# systematic resampling while still considering relative particle weights
def Low_variance_resampling(room,w):
    prime_room=list()
    prime_w=np.array([])
    room_size = len(room)
    r=random.uniform(0,1/room_size)
    
    w_cum=w[0]
    i=1
    
    for p in range(room_size):
        #make N subdivisions, and choose positions with a consistent random offset
        threshold=(r+(p-1))*(1/room_size)
        while threshold > w_cum:
            i += 1
            w_cum += w[i]
        prime_room.append(room[i])
        prime_w = np.append(prime_w,w[i])
    
    #verificiar se ever happens
    while len(prime_room) < room_size:
        prime_room.append(add_particle())
        prime_w = np.append(prime_w,1)
        
    return prime_room,prime_w

#    This algorithms aims to make selections relatively uniformly across the
#   particles. It divides the cumulative sum of the weights into N equal
#   divisions, and then selects one particle randomly from each division. This
#   guarantees that each sample is between 0 and 2/N apart.
def stratified_resample(w,room):
    room_size = len(room)
    prime_room=list()
    prime_w=np.array([])
    positions=np.array(range(room_size))
    positions = (random.uniform(0,room_size)+ positions.astype(int))/room_size
    
    cumulative_sum = np.cumsum(w)
    j=0
    p=0
    
    while j < room_size:#p?
        if positions[p] < cumulative_sum[j]:
            
            prime_room.append(room[j])
            prime_w = np.append(prime_w,w[j])
    
            p = p+1
        else:
            j = j+1
            
    #verificiar se ever happens
    while len(prime_room) < room_size:
        prime_room.append(add_particle())
        prime_w = np.append(prime_w,1)
        
    return prime_room,prime_w

"""
 Based on observation that we don't need to use random numbers to select
 most of the weights. Take int(N*w^i) samples of each particle i, and then
 resample any remaining using a standard resampling algorithm [1]
"""    
def residual_resampling(w,room):
    room_size = len(room)
    prime_room=list()
    prime_w=np.array([])
    
    # take int(N*w) copies of each weight, which ensures particles with the
    # same weight are drawn uniformly
    
    copies = np.floor(room_size*w)
    
    for p in range(room_size):
        for c in range(int(copies[p])):
            prime_room.append(room[p])
            prime_w = np.append(prime_w,w[p])
    
    # use multinormal resample on the residual to fill up the rest. This
    # maximizes the variance of the samples
    
    fractional= w - copies
    fractional = fractional /sum(fractional)
    cumulative_sum = np.cumsum(fractional)
    # avoid round-off errors: ensures sum is exactly one
    cumulative_sum[-1] = 1
    
    l = room_size-len(prime_room)
    
    while len(prime_room) < room_size :
        p = np.searchsorted(cumulative_sum, random.uniform(0,l))-1
        
        prime_room.append(room[p])
        prime_w = np.append(prime_w,w[p])
            
    return prime_room,prime_w