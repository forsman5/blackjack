import random

SUITS = ['Heart', 'Spade', 'Club', 'Diamond']
VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

userHand = []
dealerHand = []

def cleanUp(deck, userHand, dealerHand):                 #Empty the hands and make new deck
    userHand, dealerHand, deck = [], [], createDeck()

def DealerLogic(deck, hand):

    if getHandValue(hand) >= 17:
        print('The dealer will stand')

    else:
        while getHandValue(hand) <= 16:
            hit(deck, hand)
            print('The dealer will hit')

TestDeck = createDeck()
TestHand = getNewHand(TestDeck)
DealerLogic(TestDeck, TestHand)
