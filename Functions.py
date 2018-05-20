import random

SUITS = ['Heart', 'Spade', 'Club', 'Diamond']
VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']

userHand = []
dealerHand = []

def createDeck():
    deck = []

    for s in SUITS:
        for v in VALUES:
            deck.append({'suit': s, 'val': v})

    random.shuffle(deck)
    return deck

def getValue(card):                                      #Assign value to card
    if card['val'] == 'A':
        val = 11
    elif card['val'] == 'J' or card['val'] == 'Q' or card['val'] == 'K':
        val = 10
    else:
        val = int(card['val'])

    return val


def hit(deck, hand):                                     #Hand could be either user or dealer hand
    hand.append(deck.pop(0))


def getNewHand(deck):                                    #Return a new hand of size two (beginning hand of round)
    hand = []
    hit(deck, hand)
    hit(deck, hand)

    return hand


def cleanUp(deck, userHand, dealerHand):                 #Empty the hands and make new deck
    userHand, dealerHand, deck = [], [], createDeck()


def getHandValue(hand):                                  #Return the value of hand
    HandValue = 0
    numAce = 0

    for card in hand:
        HandValue += getValue(card)

        if card['val'] == 'A':

            numAce += 1

    while HandValue > 21 and numAce > 0:

        HandValue -= 10
        numAce -= 1

    return HandValue


def isBlackjack(hand):                                   #Return true if hand is blackjack
    return (len(hand) == 2 and getHandValue(hand) == 21)


def canSplit(hand):                                      #Return True if hand can be split
    return (len(hand) == 2 and hand[0]['val'] == hand[1]['val'])


def canDouble(hand):                                     #Return True if hand can be doubled
    return (len(hand) == 2 and getHandValue(hand) >=9 and getHandValue(hand) <= 11)


def canInsure(hand):                                     #Return True if player can insure hand (first card face up)
    return (len(hand) == 2 and hand[0]['val'] == 'A')


def DealerLogic(deck, hand):

    if getHandValue(hand) >= 17:
        print('The dealer will stand')

    else:
        while getHandValue(hand) <=16:
            hit(deck, hand)
            print('The dealer will hit')

TestDeck = createDeck()
TestHand = getNewHand(TestDeck)
DealerLogic(TestDeck, TestHand)
