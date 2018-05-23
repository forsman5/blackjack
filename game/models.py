from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import fields
import random

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money = models.IntegerField(default=2500)
    email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

class Hand(models.Model):
    # Sum of the value of each of the cards in this hand
    # Get as close to 21 as possible without going over, use aces to create this
    @property
    def value(self):
        cards = self.card_set.all()
        handValue = 0
        numAce = 0

        for card in card:
            handValue += card.value

            if card.amount == 'A':
                numAce += 1

        while handValue > 21 and numAce > 0:

            handValue -= 10
            numAce -= 1

        return handValue

    # hit from the passed in deck, into this hand
    def hit(self, deck):
        card = deck[0]

        # removes it from the deck, adds it to the hand
        card.hand = self

        card.save()

    # returns a string!
    # returns all possible values under 21 separated by slashes
    def getStringValue(self):
        # TODO: implement this
        # i recommend you split out a new function to calculate number of aces
        return "17 / 7"

    # utility models
    def isBust(self):
        # returns true if this hand is bust, false otherwise
        return self.value > 21

    # return true if this hand has blackjack
    def isBlackjack(self):
        return (len(self) == 2 and self.value == 21)

    # create and save to the database and return the new hand
    # has a length of two cards
    @classmethod
    def create_new_hand(cls, deck):
        hand = cls()
        hand.save()

        # draw and associate the new cards
        hand.hit(deck)
        hand.hit(deck)

        return hand

    # Create a new hand and its appropiate cards. Save them to the database.
    # This hand represents a full deck. Create this hand
    @classmethod
    def create_new_deck(cls):
        deck = cls()
        deck_temp = []

        deck.save()

        for s in Card.SUITS:
            for v in Card.VALUES:
                card = Card(suit=s[0], amount=v[0])
                card.hand = deck
                deck_temp.append(card)

        # once all objects are created, randomize the order
        random.shuffle(deck_temp)

        for card in deck_temp:
            card.save()
            deck.add(card)

        return deck

    # helper methods to bypass call to .card_set
    def add(self, item):
        self.card_set.add(item)

    def remove(self, item):
        self.card_set.remove(item)

    # as a hand is just a set of cards, when attempting to index the hand, grab the cards directly
    def __getitem__(self, key):
        return self.card_set.all()[key]

    # to reduce the amount of calls to hand.card_set
    def __len__(self):
        return self.card_set.count()

    def __str__(self):
        string = ""

        for card in self:
            string += str(card) + " "

        return string

class Game(models.Model):
    # to prevent users from accessing this game in random post requests, this is random
    id = models.BigIntegerField(default=fields.makeId, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.IntegerField()
    dealer_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='dealer_hand')
    player_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='player_hand')
    deck = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='deck', null=True)

    # returns true if this game has been completed
    @property
    def complete(self):
        return self.deck == None

    def __str__(self):
        return "Dealer: \n" + str(self.dealer_hand) + "\nPlayer: \n" + str(self.player_hand) + "\n"

    @classmethod
    def create(cls, user, bet):
        deck = Hand.create_new_deck()
        dealerHand = Hand.create_new_hand(deck)
        playerHand = Hand.create_new_hand(deck)

        game = cls(user=user, bet=bet, deck=deck, dealer_hand=dealerHand, player_hand=playerHand)

        game.save()

        # remove bet from user
        user.profile.money -= bet
        user.save()

        return game

    # finish the game. delete the deck. Mark game finished. Update money transactions
    # If the game cannot be finished, ie, a winner has not yet been decided, return False
    # If the forfeit parameter is true, disregard any other logic and end the game in a player loss
    #   Else, behave as normal
    #
    # Note: When game is initialized, the money for a bet is already removed from the user
    def finish(self, forfeit):
        # TODO: implement
        if (forfeit == True):
            # Mark the game complete TODO
            pass
        else:
            # determine if the game is can be completed
            if (gameComplete == True): # TODO
                pass
            else:
                # Unattach the deck, ending the game
                self.deck = None
                winner = self.winner()

                if (winner == 1): # TODO: If winner is player. What does winner() return in this case??
                    pass
                else:
                    # Dealer wins
                    pass

    # return true if the player can double
    def canDouble(self):
        return (len(self.player_hand) == 2 and self.player_hand.value >= 9 and self.player_hand.value <= 11)

    # return true if the player can insure against a possible dealer blackjack
    # Assumes the first card in the dealer card set is the only card shown to player
    def canInsure(self):
        return (len(self.dealer_hand) == 2 and self.dealer_hand[0].amount == 'A')

    # return true if the player can split
    def canSplit(self):
        return (len(self.player_hand) == 2 and self.player_hand[0].amount == self.player_hand[1].amount)

    # return None if game is not over, true for player, false for dealer
    def winner(self):
        if not self.complete:
            return None

        # TODO: implement

        # if player.isbust return false
        # if dealer.isbust

class Card(models.Model):
    SUITS = (
        ('CB', 'Club'),
        ('SP', 'Spade'),
        ('HT', 'Heart'),
        ('DM', 'Diamond')
    )

    VALUES = (
        ('A', 'Ace'),
        ('K', 'King'),
        ('Q', 'Queen'),
        ('J', 'Jack'),
        ('10', 'Ten'),
        ('9', 'Nine'),
        ('8', 'Eight'),
        ('7', 'Seven'),
        ('6', 'Six'),
        ('5', 'Five'),
        ('4', 'Four'),
        ('3', 'Three'),
        ('2', 'Two')
    )

    hand = models.ForeignKey(Hand, on_delete=models.CASCADE)
    amount = models.CharField(max_length=2, choices=VALUES)
    suit = models.CharField(max_length=2, choices=SUITS)

    # Returns the "points" associated with this card
    @property
    def value(self):
        if self.amount == 'A':
            val = 11
        elif self.amount == 'J' or self.amount == 'Q' or self.amount == 'K':
            val = 10
        else:
            val = int(self.amount)

        return val

    # return the filename of the image of this card
    @property
    def filename(self):
        # TODO: Implement
        #return CARD_FILE_LOC + self.amout + self.suit + ".png"
        return ""

    def __str__(self):
        return self.amount + " of " + self.suit

# signal handling below
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
