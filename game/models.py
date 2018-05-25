from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from . import fields

# for deck shuffle
import random

# for end - user defined settings
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    money = models.IntegerField(default=2500)
    email_confirmed = models.BooleanField(default=False)

    # return a queryset of all games this user has not yet completed
    @property
    def unfinished_games(self):
        # Cannot filter on property!
        # thus, the condiition inside of this filter is reflective of the game.complete property
        # this cannot be done because it would require the loading of the django object, instead of generating sql
        return Game.objects.filter(user=self.user).exclude(deck__isnull=True)

    def __str__(self):
        return self.user.email

class Hand(models.Model):
    # this sets if this is a deck. if this is true, forbid certain actions
    is_deck = models.BooleanField(default = False)

    # this sets if the hand is standing. If this is None, this is a deck
    standing = models.NullBooleanField(default = False)

    # Sum of the value of each of the cards in this hand
    # Get as close to 21 as possible without going over, use aces to create this
    @property
    def value(self):
        # Return simply the highest possible of getStringValue
        return int(self.string_value.split(settings.VALUE_SEPARATOR)[0])

    # returns a string!
    # returns all possible values under 21 separated by slashes (settings.VALUE_SEPARATOR)
    # The highest (best) current possible value is the first value in the string
    @property
    def string_value(self):
        # forbidden for decks
        if self.is_deck: raise settings.DECK_ACCESS_ERROR

        numAce, handValue = 0, 0

        for card in self:
            handValue += card.value

            if card.amount == 'A':
                numAce += 1

        valueArr = [handValue]

        while numAce > 0:
            handValue -= 10
            numAce -= 1
            valueArr.append(handValue)

        filteredArr = [str(val) for val in valueArr if val <= 21]

        # filter the list to only values less than 22
        return settings.VALUE_SEPARATOR.join(filteredArr) if len(filteredArr) > 0 else str(min(valueArr))

    # hit from the passed in deck, into this hand
    def hit(self, deck):
        # forbidden for decks
        if self.is_deck: raise settings.DECK_ACCESS_ERROR

        # ensure that this action is only taken when it can be
        # this is to prevent players from spoofing ajax requests to see cards
        #   and then acting with that knowledge. Can't get the second card until you have stood
        if self.standing or self.isBlackjack() or self.isBust(): raise settings.GAME_ACTION_ERROR

        card = deck[0]

        # removes it from the deck, adds it to the hand
        card.hand = self

        # must stand if either of these are true
        if self.value == 21 or self.isBust():
            self.stand()

        card.save()

    # utility models
    def isBust(self):
        # forbidden for decks
        if self.is_deck: raise settings.DECK_ACCESS_ERROR

        # returns true if this hand is bust, false otherwise
        return self.value > 21

    # return true if this hand has blackjack
    def isBlackjack(self):
        # forbidden for decks
        if self.is_deck: raise settings.DECK_ACCESS_ERROR

        return (len(self) == 2 and self.value == 21)

    # quick helper method to have a hand stand
    def stand(self):
        # ensure this is only being called at the right time
        if self.is_deck: raise settings.DECK_ACCESS_ERROR
        if self.standing: raise settings.GAME_ACTION_ERROR

        self.standing = True
        self.save()

    # create and save to the database and return the new hand
    # has a length of two cards
    @classmethod
    def create_new_hand(cls, deck):
        hand = cls()
        hand.save()

        # draw and associate the new cards
        hand.hit(deck)
        hand.hit(deck)

        if hand.isBlackjack():
            hand.stand()

        return hand

    # Create a new hand and its appropiate cards. Save them to the database.
    # This hand represents a full, shuffled deck. Create this hand
    # decks parameter represents the number of full normal card decks to be returned.
    #   ie, if decks = 2, this will return two decks shuffled together
    @classmethod
    def create_new_deck(cls, decks = 1):
        deck = cls(is_deck = True, standing=None)
        deck_temp = []

        deck.save()

        for i in range(0, decks):
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
        string = 'Deck: ' + str(self.is_deck) + '\n'

        if not self.standing == None:
            string += 'Standing: ' + str(self.standing)

        for card in self:
            string += str(card) + ' '

        if not self.is_deck:
            string += '\nValue: ' + str(self.string_value)

        return string

class Game(models.Model):
    # to prevent users from accessing this game in random post requests, this is random
    id = models.BigIntegerField(default=fields.makeId, primary_key=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.IntegerField()
    dealer_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='dealer_hand')
    player_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='player_hand')
    player_split_hand = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='player_split_hand', null=True, default=None)
    deck = models.ForeignKey(Hand, on_delete=models.CASCADE, related_name='deck', null=True)
    time_started = models.DateTimeField(auto_now_add=True)
    time_finished = models.DateTimeField(null=True, default=None)

    # flags for user actions taken
    has_doubled = models.BooleanField(default=False)
    has_insured = models.BooleanField(default=False)

    # returns true if this game has been completed
    @property
    def complete(self):
        # could also return self.time_finished == None
        return self.deck == None

    # in keeping with the same style
    @property
    def has_split(self):
        return self.player_split_hand != None

    @classmethod
    def create(cls, user, bet):
        deck = Hand.create_new_deck(settings.DECK_SIZE)
        dealerHand = Hand.create_new_hand(deck)
        playerHand = Hand.create_new_hand(deck)

        game = cls(user=user, bet=bet, deck=deck, dealer_hand=dealerHand, player_hand=playerHand)

        game.save()

        # remove bet from user
        user.profile.money -= bet
        user.save()

        # check for blackjack here!
        if game.player_hand.isBlackjack():
            game.finish()

        return game

    # finish the game. delete the deck. Mark game finished. Update money transactions
    # If the game cannot be finished, ie, a winner has not yet been decided, return False
    # If the forfeit parameter is true, disregard any other logic and end the game in a player loss
    #   Else, behave as normal
    #
    # Note: When game is initialized, the money for a bet is already removed from the user
    def finish(self, forfeit = False):
        # TODO: implement
        if (forfeit == True):
            # Mark the game complete TODO
            pass
        else:
            # cannot finish before the player has stood
            if not self.player_hand.standing: raise settings.GAME_ACTION_ERROR

            # Unattach the deck, ending the game
            self.deck.delete()  # remove from the database
            self.deck = None

            # TODO: Handle splits

            # check for the base cases first
            if (self.player_hand.isBlackjack()):
                pass
            elif (self.player_hand.isBust()):
                pass
            elif (self.dealer_hand.isBlackjack()):
                pass
            else:
                self.processDealerLogic()

                if (self.dealer_hand.isBust()):
                    pass
                else:
                    winner = self.winner()

                    if (winner == 1): # TODO: If winner is player. What does winner() return in this case??
                        pass
                    else:
                        # Dealer wins
                        pass

        self.save()
        self.user.save()

    # return true if the player can double
    def canDouble(self):
        return (not self.has_doubled and len(self.player_hand) == 2 and self.player_hand.value >= 9 and self.player_hand.value <= 11)

    # return true if the player can insure against a possible dealer blackjack
    # Assumes the first card in the dealer card set is the only card shown to player
    def canInsure(self):
        return (not self.has_insured and len(self.dealer_hand) == 2 and self.dealer_hand[0].amount == 'A')

    # return true if the player can split
    def canSplit(self):
        return (not self.has_split and len(self.player_hand) == 2 and self.player_hand[0].amount == self.player_hand[1].amount)

    # Split the hand on the table
    def split(self):
        # guard from improper usage
        if not self.canSplit(): raise settings.GAME_ACTION_ERROR

        self.player_split_hand = Hand.objects.create()

        # move the second card over to the new hand
        # to do this, we need to directly reference it, or else the reassign is forgotten before save
        temp = self.player_hand[1]
        temp.hand = self.player_split_hand
        temp.save()
        
        self.player_hand.hit(self.deck)
        self.player_split_hand.hit(self.deck)

        # now both hands should have two cards, as intended

        # update the bet, doubling it
        self.user.profile.money -= self.bet
        self.bet *= 2

        self.user.profile.save()
        self.save()

    # The player insures
    def insure(self):
        # guard from improper usage
        if not self.canInsure(): raise settings.GAME_ACTION_ERROR

        self.has_insured = True

        # TODO: implement

        self.save()

    # The player doubles their bet, hits once, and stands
    # Must send the new cards back as a post response
    # will call finish
    def double(self):
        # guard from improper usage
        if not self.canDouble(): raise settings.GAME_ACTION_ERROR

        # TODO: Sabrina - implement. Use split() for a bit of help
        pass

    # return None if game is not over, true for player, false for dealer
    def winner(self):
        if not self.complete:
            return None

        # TODO: implement

        # if player.isbust return false
        # if dealer.isbust

    # the player has stood. Now, the dealer's turn
    # will call finish
    def processDealerLogic(self):
        # ensure this is being called at the right time
        if (not self.player_hand.standing or self.player_hand.isBust() or self.player_hand.isBlackjack()):
            raise settings.GAME_ACTION_ERROR

        while self.dealer_hand.value <= 16:
            self.dealer_hand.hit(self.deck)

        self.dealer_hand.stand()

    def __str__(self):
        return "Dealer: \n" + str(self.dealer_hand) + "\nPlayer: \n" + str(self.player_hand) + "\n"

class Card(models.Model):
    SUITS = (
        ('CB', 'Clubs'),
        ('SP', 'Spades'),
        ('HT', 'Hearts'),
        ('DM', 'Diamonds')
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

    # helper method for templates
    @property
    def string_value(self):
        if self.amount == 'A':
            return '11 / 1'
        else:
            return self.value

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
