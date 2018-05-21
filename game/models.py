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
        return (self.card_set.count() == 2 and self.value == 21)

    # Create a new hand and its appropiate cards. Save them to the database.
    # This hand represents a full deck. Create this hand
    @classmethod
    def create_as_deck(cls):
        deck = cls()
        deck_temp = []

        # is this okay?
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
            deck.card_set.add(card)

        return deck

    def __str__(self):
        string = ""

        for card in self.card_set.all():
            string += str(card)

        return string

class Game(models.Model):
    # to prevent users from accessing this game in random post requests, this is random
    id = models.BigIntegerField(default=fields.makeId, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    complete = models.BooleanField(default=False)
    dealer_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='dealer_hand')
    player_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='player_hand')

    def __str__(self):
        return "Dealer: \n" + str(dealer_hand) + "\nPlayer: \n" + str(player_hand) + "\n"

    # return true if the player can double
    def canDouble(self):
        return (self.player_hand.card_set.count() == 2 and self.player_hand.value >= 9 and self.player_hand.value <= 11)

    # return true if the player can insure against a possible dealer blackjack
    # Assumes the first card in the dealer card set is the only card shown to player
    def canInsure(self):
        return (self.dealer_hand.card_set.count() == 2 and self.dealer_hand.card_set.first().amount == 'A')

    # return true if the player can split
    def canSplit(self):
        return (self.player_hand.card_set.count() == 2 and self.player_hand.card_set.first().amount == self.player_hand.card_set.all()[1].amount)

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
