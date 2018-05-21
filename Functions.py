import random

SUITS = ['Heart', 'Spade', 'Club', 'Diamond']
VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

userHand = []
dealerHand = []

def hit(deck, hand):                                     #Hand could be either user or dealer hand
    hand.append(deck.pop(0))


def getNewHand(deck):                                    #Return a new hand of size two (beginning hand of round)
    hand = []
    hit(deck, hand)
    hit(deck, hand)

    return hand


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
