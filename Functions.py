def DealerLogic(deck, hand):

    if getHandValue(hand) >= 17:
        print('The dealer will stand')

    else:
        while getHandValue(hand) <= 16:
            hit(deck, hand)
            print('The dealer will hit')
