#!/usr/local/anaconda3/bin/python
#==============================================================================
#     File: blackjack.py
#  Created: 08/02/2017, 21:19
#   Author: Bernie Roesler
#
"""
  Description: Set up and play a game of blackjack!
"""
#==============================================================================
# Standard imports
import names
import pickle
import random
import sys

# Custom imports
import cards
from my_util import cmp, flatten

#------------------------------------------------------------------------------
#       Individual casino game
#------------------------------------------------------------------------------
class CasinoGame:
    """ Individual casino game class """
    # Class variables
    PROMPT = "(*)>"

    def __init__(self, name=""):
        self.name = name
        CasinoGame.PROMPT = "({})> ".format(self.name)

    def __save(self):
        choice = input("Save game? [y/n] > ")
        if choice == "y":
            # save game
            pickle_file = ".casinogame_pickle_dump_" + str(id(self))
            pickle.dump(self, open(pickle_file, "wb"))

    # Pause game drops back into main loop
    def __pause(self):
        print("Game paused.")
        self.__save()

        if __debug__:
            sys.exit()
        else:
            raise GamePause

    # Quit altogether
    def __exit(self):
        print("\nExiting...")
        sys.exit()

    def gameStatus(self):
        self.table.tableStatus()

    #--------------------------------------------------------------------------
    #        Play the game
    #--------------------------------------------------------------------------
    def play(self):
        self.__welcome()
        # Loop between rounds of game
        while True:
            try:
                # Get user input
                choice = input(CasinoGame.PROMPT)
                self.__gameParse(choice)
            except GamePause:
                break
            except (KeyboardInterrupt, EOFError):
                self.__exit()    

    #--------------------------------------------------------------------------
    #        Interface
    #--------------------------------------------------------------------------
    def __welcome(self):
        print("\n~~~~~~~~~~ Welcome to the {} table! ~~~~~~~~~~\n"
              "Choose an option to continue:\n".format(self.name))
        self.__gameMenu()

    def __gameMenu(self):
        print("---------- Menu ----------\n"
              "  ? -- print this menu\n"
              "  g -- show game status\n"
              "  h -- play a round\n"
              "  p -- pause game\n"
              "  o -- set options\n"
              "  r -- restart game\n"
              "  s -- save game\n"
              "  x -- exit casino\n")

    # Parse user input in main play loop
    def __gameParse(self, p):
        opt = {'?' : self.__gameMenu,
               'g' : self.gameStatus,
               'h' : self.playRound,
               'p' : self.__pause,
               'r' : self.gameInit,
               'o' : self.gameInit, # TODO new "setOpts" to give menu to reset each option
               's' : self.__save,
               'x' : self.__exit,
              }
        if p:
            if p in opt:
                opt[p]() # execute
            else:
                print("Invalid input. Press ? for help.")

#------------------------------------------------------------------------------
#       Blackjack game class
#------------------------------------------------------------------------------
class Blackjack(CasinoGame):
    """ The actual logic of the blackjack game. """

    # Logical defaults
    DEFAULT_NP = 3    # number of players
    DEFAULT_M  = 10   # [$] minimum bet
    DEFAULT_S  = 0    # user seat at table
    DEFAULT_MONEY = 1000.00

    def __init__(self, nd=6):
        CasinoGame.__init__(self, name="Blackjack")
        self.table  = None
        self.deck   = cards.Deck(nd)
        self.user   = None    # Keep track who the interactive user is
        self.dealer = None

    # Prompt user to set up game variables. Creates new instance of the Table.
    def gameInit(self, useDefaults=True):
        if not useDefaults:
            choice = input(CasinoGame.PROMPT+" Use defaults? [y/n] > ") or "y"
            useDefaults = (choice == "y")

        if useDefaults:
            np = Blackjack.DEFAULT_NP
            m  = Blackjack.DEFAULT_M
            n  = "TheUser"
        else:
            n  = input(CasinoGame.PROMPT+" What is your name? > ") or ""
            np = input(CasinoGame.PROMPT+" Enter number of players > ") \
                    or Blackjack.DEFAULT_NP
            m  = input(CasinoGame.PROMPT+" Enter minimum bet > $") \
                    or Blackjack.DEFAULT_M

        # Use defaults here
        s  = Blackjack.DEFAULT_S
        mo = Blackjack.DEFAULT_MONEY

        # Create Table
        self.table = cards.Table(int(np), float(m))

        # Create dealer -- special seat outside of "table" with "unlimited" money
        self.dealer = cards.Seat(cards.Player(name="Dealer",m=1e9))

        # Create user-Player
        self.user = cards.Player(n, mo, isUser=True)
        self.table.seatPlayer(self.user, int(s))

        # Create computer Players to fill table
        self.table.around(self.__genPlayer)

    # Create computer player
    def __genPlayer(self, seat):
        if seat.isEmpty:
            n = names.get_first_name()
            m = random.randrange( 0.5*Blackjack.DEFAULT_MONEY,
                                 10.0*Blackjack.DEFAULT_MONEY)
            p = cards.Player(n, m, isUser=False)
            seat.fillSeat(p)

    #--------------------------------------------------------------------------
    #        Main Gameplay
    #--------------------------------------------------------------------------
    # Play a hand of blackjack
    def playRound(self):
        ### Clean up (return outstanding cards to deck)
        # NOTE putting clearTable here allows user to view the gameStatus at
        # the end of the hand, and then clear it for a new hand only
        self.clearTable()

        ### Shuffle the deck!
        self.deck.shuffle()

        ### Place bets
        self.table.around(self.takeBet)

        ### Deal a round (one up, one down)
        print("...Dealing the round...")
        self.dealRound()

        ### Score everyone's hands
        self.scorePlayers()

        ### If dealer has Ace, ask if anyone wants insurance
        # if Blackjack.hasAce(self.dealer):
        #     self.table.around(self.askInsurance)

        ### Check for dealer blackjack
        if self.hasBlackjack(self.dealer):
            self.settleBets()
            return

        ### for each player, choose option
        print("...Time to play!...")
        self.playHands()

        ### dealer plays (special rules for dealer)
        print("...Dealer's turn...")
        self.dealerPlay()

        ### Settle bets
        print("...Settling bets...")
        self.settleBets()
        print("done.")

    #--------------------------------------------------------------------------
    #        Perform ops for entire table
    #--------------------------------------------------------------------------
    # Return all players' cards to the deck
    def clearTable(self):
        self.table.around(self.clearHand)
        self.clearHand(self.dealer)

    # Deal a round
    def dealRound(self):
        # Deal 1 face-down
        self.table.around(self.deal(ncard=1, faceup=True))
        self.dealer.player.drawCard(self.deck, faceup=False)
        # Deal 1 face-up
        self.table.around(self.deal(ncard=1, faceup=True))
        self.dealer.player.drawCard(self.deck, faceup=True)

    # Calculate scores for all players' hands
    def scorePlayers(self):
        self.table.around(self.scorePlayer)
        self.scorePlayer(self.dealer)

    # Play all players' hands
    def playHands(self):
        self.table.around(self.playHand)

    # Settle all players' bets with the dealer
    def settleBets(self):
        self.table.around(self.settleBet(self.dealer))

    #--------------------------------------------------------------------------
    #        Individual Player Methods: all take seat index and seat object
    #--------------------------------------------------------------------------
    # Return player's cards to the deck
    def clearHand(self, seat):
        if not seat.isEmpty:
            def returnCards(h):
                h.forAllCards(self.deck.returnCard)
            seat.player.forAllHands(returnCards)
            seat.player.discardAllHands()  # clear player's hands

    # Deal cards to a player
    def deal(self, ncard=1, faceup=False):
        def op(seat):
            if not seat.isEmpty:
                # Deal ncards to player at seat
                for n in range(ncard):
                    c = self.deck.dealCard(faceup)
                    seat.player.receiveCard(c)
                    # Status update
                    if c.faceup:
                        print(seat.player.name, "received", c)
                    else:
                        print(seat.player.name, "received card face down.")
        return op

    # Take minimum bet from player
    def takeBet(self, seat):
        if not seat.isEmpty:
            hasBet = seat.player.placeBet(self.table.minbet)
            if not hasBet:
                seat.vacateSeat()

    # Sum the value of cards in each hand
    def scorePlayer(self, seat):
        if not seat.isEmpty:
            seat.player.forAllHands(self.scoreHand)

    # TODO "could be a function"
    def scoreHand(self, hand):
        # Create list of "blackjack" values of cards
        vals = [card.val for card in hand.cards]

        # Face cards == 10
        def fil(x):
            return x if (x < 10) else 10
        bj_vals = list(map(fil, vals))
        score_a = sum(bj_vals)

        # Determine value of aces
        ace_ind = [i for i, x in enumerate(bj_vals) if x == cards.Card.ACE]
        if (not ace_ind) or (score_a > 21):
            hand.score = score_a
        else:
            # Set aces to 11
            for i in ace_ind: bj_vals[i] = 11
            score_b = sum(bj_vals)
            if score_b > 21:
                hand.score = score_a
            else:
                hand.score = score_b

    # TODO function?
    def settleBet(self, other):
        print("Dealer has: ", other.player.hand[0].score)
        # NOTE what we're really doing:
        # lst = list(map(lambda x:
        #             list(map(lambda y:
        #                 cmp(x,y),
        #                     dealer.hand)),
        #                         player.hand))
        # BUT our operations are INDEPEDENT of the implementation of seats,
        # players and hands!

        # Transfer money from a to b
        def transfer(a, b):
            b.player.money += a.player.bet + b.player.bet
            a.player.bet = 0.0
            b.player.bet = 0.0

        # Compare two hands and return -1 if a < b, 0 if a == b, 1 if a > b
        # TODO simplify logic??
        def compare(a, b):
            if (a.score > 21) and (b.score > 21):
                return 0   # it's a tie!
            elif a.score > 21:
                return -1  # "a < b" so b wins
            elif b.score > 21:
                return 1   # "a > b" so a wins
            else:
                return cmp(a, b)

        # a procedure that takes the player's hand as the argument, and returns
        # a procedure that loops over all of the other player's hands
        def lambda_x(x):
            # return a procedure that takes one argument
            return other.player.forAllHands(lambda y: compare(x, y))

        # a procedure that takes player's seat as argument, and settles all of
        # the bets with the dealer
        def op(seat):
            if not seat.isEmpty:
                thename = "### You" if seat.player.isUser else seat.player.name
                # A procedure that returns a list given a procedure that is
                # a function of one element (i.e. map)
                lst = flatten(seat.player.forAllHands(lambda_x))
                for b in lst:
                    if b > 0:  # player won!
                        print("{} won ${}!".format(thename, seat.player.bet))
                        transfer(other, seat)
                    if b == 0: # push
                        print("{} pushed.".format(thename))
                        # NOTE "negative" bet just returns money to wallet
                        seat.player.placeBet(-seat.player.bet)
                        other.player.placeBet(-other.player.bet)
                    if b < 0:  # dealer won!
                        print("{} lost ${} :(".format(thename, seat.player.bet))
                        transfer(seat, other)
        return op

    # function?
    def hasBlackjack(self, seat):
        if not seat.isEmpty:
            def op(h):
                if h.score == 21:
                    return True
                return False
            bj_bool = seat.player.forAllHands(op)
            return any([x for x in bj_bool if x])
        else:
            return False

    #--------------------------------------------------------------------------
    #        Play the hand
    #--------------------------------------------------------------------------
    def playHand(self, seat):
        if not seat.isEmpty:
            # Operation to perform on each hand a player has
            def play(h):
                while True:
                    try:
                        # Check for bust
                        if h.score > 21:
                            print("You busted!")
                            break

                        if __debug__:
                            choice = "s"
                        else:
                            choice = self.__getChoice(seat, h)

                        # Execute procedure
                        op = self.__handParse(choice)
                        if op:
                            op(seat, h)
                            self.scoreHand(h)

                    # Move on to next player
                    except BlackjackStand:
                        break

            # Perform the operation on all hands
            seat.player.forAllHands(play)

    # Dealer just hits until he has 17 or higher
    def dealerPlay(self):
        for h in self.dealer.player.hand:
            # Turn dealer cards face up
            h.forAllCards(cards.Card.turnUp)
            while h.score < 17:
                self.__handHit(self.dealer, h)
                self.scoreHand(h)

    # Playing options for each (seat, hand)
    def __handHit(self, seat, h):
        print("{}: \"Hit me!\"".format(seat.player.name))
        # Deal one card to player
        self.deal(ncard=1, faceup=True)(seat)

    # function
    def __handStand(self, seat, h):
        # Do nothing.
        print("{}: \"I'll stand.\"".format(seat.player.name))
        raise BlackjackStand

    def __handDoubleDown(self, seat, h):
        print("{}: \"Go big or go home!\"".format(seat.player.name))
        # Double bet, take one extra card, stand.
        seat.player.placeBet(seat.player.bet)
        self.deal(ncard=1, faceup=True)(seat)
        raise BlackjackStand

    # function
    def __handSurrender(self, seat, h):
        print("{}: \"I surrender :(\"".format(seat.player.name))
        # Keep 1/2 bet only, house gets the rest
        seat.player.money += 0.5*seat.player.bet
        seat.player.bet = 0  # Set bet to 0, and score to 0 so we guarantee loss
        h.score = 0
        raise BlackjackStand

    # function
    def __handSplit(self, seat, h):
        pass
        # print("{}: \"I'd like to split my hand.\"".format(seat.player.name))
        # raise BlackjackStand
        # TODO Check if player has a pair
        # if h.hasPair():
            # make another hand
            # seat.player.addHand(

    #--------------------------------------------------------------------------
    #        Interface
    #--------------------------------------------------------------------------
    # TODO only loop over prompt if input is empty/invalid...
    def __getChoice(self, seat, hand):
        if seat.player.isUser:
            print("########## It's your turn! ##########")
            print("### Your hand is:\n{}".format(str(hand)))
            print("### Your score for your hand is:", hand.score)
            self.__handMenu()
            return input(CasinoGame.PROMPT)
        else:   # Computer random choice
            # return self.chooseRand(seat.player, hand)
            return "s" # dummy out for now

    def gameStatus(self):
        self.dealer.player.playerStatus()  # dealer is unique to blackjack
        super(Blackjack, self).gameStatus() # just the table

    # function
    def __handMenu(self):
        print("---------- Options ----------\n"
              "  ? -- print this menu\n"
              "  g -- show game status\n"
              "  h -- hit (draw another card)\n"
              "  s -- stand (move on to next player)\n"
              "  d -- double-down (double bet and take one hit)\n"
              "  x -- surrender (take 1/2 your bet and quit)\n"
              "  p -- split (if you have a pair)")

    def __handParse(self, c):
        opt = {'?' : self.__handMenu,
               'g' : self.gameStatus,
               'h' : self.__handHit,
               's' : self.__handStand,
               'd' : self.__handDoubleDown,
               'x' : self.__handSurrender,
               'p' : self.__handSplit,
              }
        if c:
            if c in opt:
                return opt[c]
            else:
                print("Invalid input.")


# Just here for the exception
class GamePause(Exception): pass
class BlackjackStand(Exception): pass

#==============================================================================
#==============================================================================
