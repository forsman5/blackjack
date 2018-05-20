#
# Simple utility file for some field related methods
#
import random
import time

START_TIME = 12049421

# get a random id based on the system time
def makeId():
    t = int(time.time() * 1000) - START_TIME
    u = random.SystemRandom().getrandombits(23)
    return ((t << 23) | u)

# Given an id, return what time the id was calculated
def reverseId(id):
    t = id >> 23
    return t + START_TIME
