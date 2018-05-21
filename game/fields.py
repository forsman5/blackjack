#
# Simple utility file for some field related methods
#
import random
import time

START_TIME = 12049
ID_LENGTH = 15

# get a random id based on the system time
def makeId():
    t = int(time.time() * 1000) - START_TIME
    u = random.SystemRandom().getrandbits(ID_LENGTH)
    return ((t << ID_LENGTH) | u)

# Given an id, return what time the id was calculated
def reverseId(id):
    t = id >> ID_LENGTH
    return t + START_TIME
