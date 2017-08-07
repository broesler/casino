#!/usr/local/anaconda3/bin/python
#==============================================================================
#     File: cards.py
#  Created: 08/02/2017, 16:19
#   Author: Bernie Roesler
#
"""
  Description: Implement a deck of cards
"""
#==============================================================================
import random
import pprint

#------------------------------------------------------------------------------
#       Table for playing card games
#------------------------------------------------------------------------------
class Table:
    """ A table for a card game.
    Keyword inputs:
        n -- a number of seats
        m -- a minimum bet per hand at the table
    Contains:
        seat  -- list of seat objects
        cards -- list of cards (i.e. face-up for Texas Hold 'Em)
    """

    def __init__(self, n=5, m=1):
        self.n_seats = n
        self.minbet  = m
        self.seat    = [ Seat() for i in range(n) ]
        self.cards   = []

    def seatPlayer(self, player, n):
        if n < self.n_seats:
            if self.seat[n].isEmpty:
                self.seat[n].fillSeat(player)
            else:
                if player.isUser:
                    print("Seat's taken!")

    def removePlayer(self, n):
        if n < self.n_seats:
            self.seat[n].vacateSeat()

    # Perform procedure on each player at the table, using seat number and
    # seat object itself
    def around(self, op):
        return list(map(op, self.seat))

    #--------------------------------------------------------------------------
    #        Pretty-printing
    #--------------------------------------------------------------------------
    def tableStatus(self):
        for i, s in enumerate(self.seat):
            print("---------- Seat: ", i)
            print(str(s.player))

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def __repr__(self):
        return self.__str__()

#------------------------------------------------------------------------------
#        Seats are placeholders for players
#------------------------------------------------------------------------------
class Seat:
    """ A seat at the table.
    Keyword inputs:
        player -- a Player object to sit at the seat
    """

    def __init__(self, player=None):
        self.player = player
        self.isEmpty = False if player else True

    def fillSeat(self, player):
        self.player = player
        self.isEmpty = False

    def vacateSeat(self):
        self.player = None
        self.isEmpty = True

    def __str__(self):
        return str(self.player)

    def __repr__(self):
        return self.__str__()

#------------------------------------------------------------------------------
#       Generic card player
#------------------------------------------------------------------------------
class Player:
    """ Player of a card game.
    Keyword inputs:
        name   -- [string] name of player
        m      -- [float] initial wallet amount
        isUser -- [boolean] whether player is user-interactive
    """

    def __init__(self, name="Player", m=100.0, isUser=False):
        self.name = name
        self.hand = []
        self.n_hands = 0
        self.money = m
        self.bet = 0.0
        self.isUser = isUser

    def placeBet(self, bet):
        if bet > self.money:
            print("{} is out of money!".format(self.name))
            return False
        self.money -= bet
        self.bet += bet
        return True

    def addHand(self, h):
        self.hand.append(h)
        self.n_hands += 1

    def discardAllHands(self):
        self.hand = []
        self.n_hands = 0

    def receiveCard(self, card, h=0):
        if h >= self.n_hands:
            self.addHand(Hand(card))
        else:
            self.hand[h].addCard(card)

    # def giveCard(self, card, h=0):

    def drawCard(self, deck, h=0, faceup=False):
        if h > self.n_hands:
            raise RuntimeError("Player's hand does not exist!")
        card = deck.dealCard(faceup)
        self.receiveCard(card, h)

    # Perform operation on all hands we are holding
    def forAllHands(self, op):
        return list(map(op, self.hand))

    #--------------------------------------------------------------------------
    #        Pretty-printing
    #--------------------------------------------------------------------------
    def playerStatus(self):
        print("\n---------- Player: ", self.name)
        print(str(self))

    # Show entire hand
    def showAllHands(self):
        lst = [str(h) for h in self.hand]
        return '\n'.join(lst)

    # Show face-up cards only
    def showAllFaceup(self):
        lst = list(map(lambda x: str(Hand(x.faceUpCards())), self.hand))
        return '\n'.join(lst)

    def __str__(self):
        if self.isUser:
            this_hand = self.showAllHands()
        else:
            this_hand = self.showAllFaceup()

        markUser = "*" if self.isUser else ""

        return ("  name   : {}{}\n"
                "  hand   : \n{}\n"
                "  money  : ${:8.2f}\n"
                "  bet    : ${:8.2f}\n") \
                    .format(self.name, markUser, this_hand, self.money, self.bet)

    def __repr__(self):
        return pprint.pformat(self.__dict__)

#------------------------------------------------------------------------------
#       Deck of n*52 cards
#------------------------------------------------------------------------------
# TODO generalize Deck to just a stack of any number of cards
class Deck:
    # Create list of cards
    def __init__(self, n=1):
        self.cards = []
        self.cardsLeft = 0
        self.Ndecks = n
        # Allow multiple decks
        for deck in range(n):
            for suit in range(4):
                for val in range(1,14):
                    self.cards.append(Card(val, suit))
                    self.cardsLeft += 1

    # shuffle cards in place
    def shuffle(self):
        random.shuffle(self.cards)

    # Deal "top" of deck
    def dealCard(self, faceup=False):
        if self.cardsLeft > 0:
            self.cardsLeft -= 1
            c = self.cards.pop(0)
            if faceup:
                c.turnUp()
            return c
        else:
            print("No cards left!")

    # Return card to bottom of deck
    def returnCard(self, card):
        # List of cards in deck that match given card
        ff = list(filter(lambda c: c.equiv(card), self.cards))
        if len(ff) < self.Ndecks:
            self.cards.append(card)
            self.cardsLeft += 1
        else:
            raise RuntimeError("Card already in deck!")

    # Pretty print all cards in deck
    def __str__(self):
        lst = [str(card) for card in self.cards]
        return "\n".join(lst)

#------------------------------------------------------------------------------
#       Hand == collection of cards
#------------------------------------------------------------------------------
class Hand:
    """ Collection of cards for an individual player. """
    def __init__(self, c=[]):
        if type(c) is not list: c = [c]
        self.cards = c
        self.score = 0   # score set by each game

    # Add and remove cards from hand
    def addCard(self, cards):
        if type(cards) is not list: cards = [cards]
        for c in cards:
            self.cards.append(c)

    def playCard(self, card):
        if card in self.cards:
            self.cards.remove(card)
        else:
            raise RuntimeError("Player does not have card to play!")

    # Sorting
    def sortBySuit(self):
        self.cards = sorted(self.cards, key=lambda s: s.getSuit())

    def sortByVal(self):
        self.cards = sorted(self.cards, key=lambda s: s.getVal())

    # Filters
    def faceUpCards(self):
        return list(filter(lambda c: c.faceup, self.cards))

    def faceDownCards(self):
        return list(filter(lambda c: not c.faceup, self.cards))

    # Operate on all cards in hand (keeps cards representation separate)
    def forAllCards(self, op):
        return list(map(op, self.cards))

    # Determine if hand has a pair
    def hasPair(self):
        # NOTE slow for big lists
        return any([self.cards.count(x) for x in self.cards])

    # Comparison between hands
    def __eq__(self, b):
        return self.score == b.score

    def __lt__(self, b):
        return self.score < b.score

    # Pretty print all cards in hand
    def __str__(self):
        lst = [str(card) for card in self.cards]
        if lst:
            return "[\n  " + "\n  ".join(lst) + "\n]"
        else:
            return ""

    def __repr__(self):
        return pprint.pformat(self.__dict__)

#------------------------------------------------------------------------------
#       Individual Cards
#------------------------------------------------------------------------------
class Card:
    """ Defines the Card class holding suit and value """

    # Macros for the suits
    SPADES   = 0
    HEARTS   = 1
    DIAMONDS = 2
    CLUBS    = 3

    # Macros for the face cards
    JACK  = 11
    QUEEN = 12
    KING  = 13
    ACE   =  1

    def __init__(self, val, suit, faceup=False):
        if val < 1 or val > 13:
            raise RuntimeError("Card value outside of range!")
        self.suit = suit
        self.val = val
        self.faceup = faceup  # default is face down

    def getSuit(self):
        return self.suit

    def getVal(self):
        return self.val

    def getFaceUp(self):
        return self.faceup

    def turnUp(self):
        self.faceup = True

    def turnDown(self):
        self.faceup = False

    #--------------------------------------------------------------------------
    #        Pretty-printing
    #--------------------------------------------------------------------------
    def suitAsStr(self):
        opt = { Card.SPADES   : "Spades",
                Card.HEARTS   : "Hearts",
                Card.DIAMONDS : "Diamonds",
                Card.CLUBS    : "Clubs",
              }
        return opt[self.suit]

    def valAsStr(self):
        opt = { Card.ACE   : "Ace",
                Card.JACK  : "Jack",
                Card.QUEEN : "Queen",
                Card.KING  : "King",
                }

        if self.val in opt:
            return opt[self.val]
        else:
            return str(self.val)

    def __str__(self):
        if self.faceup:
            facestr = " (face up)"
        else:
            facestr = " (face down)"
        return self.valAsStr() + " of " + self.suitAsStr() + facestr

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    #--------------------------------------------------------------------------
    #        Comparison between cards
    #--------------------------------------------------------------------------
    # To check if cards are the same card
    def equiv(self, b):
        return (self.suit == b.suit) and (self.val == b.val)

    # for comparison operators:
    def __eq__(self, b):
        return self.val == b.val

    def __lt__(self, b):
        return self.val < b.val

#------------------------------------------------------------------------------
#       Main function
#------------------------------------------------------------------------------
if __name__ == "__main__":
    a = Card(Card.ACE, Card.HEARTS)
    b = Card(10, Card.SPADES)
    c = Card(10, Card.CLUBS)
    d = Card(7, Card.DIAMONDS)
    e = Card(Card.JACK, Card.SPADES)
    f = Card(7, Card.DIAMONDS)
    h1 = Hand([a, b, c, d, e])
    h1.addCard(e)
    # h1.addCard([a, b, c, d, e])
    h1.sortBySuit()
    # print(h1)
    p1 = Player("Bernie", 1000, isUser=True)
    p1.addHand(h1)
    h2 = Hand()
    h2.addCard([d, e, b])
    p1.addHand(h2)
    # print(p1.hand)
    print(p1)
    p2 = Player("Bob", 56, isUser=False)
    h1.cards[0].faceup = True
    p2.addHand(h1)
    print(p2)
    print(b == c) # True
    print(b < c)  # False
    print(d == f) # True
    # d = Deck(2)
    # d.shuffle()

#==============================================================================
#==============================================================================
