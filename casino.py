#!/usr/local/anaconda3/bin/python
#==============================================================================
#     File: cardgame.py
#  Created: 08/03/2017, 10:08
#   Author: Bernie Roesler
#
"""
  Description: General wrapper to manage card games. Can start new games,
  resume old (not yet implemented), or just exit.
"""
#==============================================================================
import sys
import cardgame

#------------------------------------------------------------------------------
#       Casino Royale with Cheese
#------------------------------------------------------------------------------
class Casino:
    """ Wrapper class to govern the playing and loading of all games. """
    PROMPT = "(Casino)> "

    def __init__(self):
        self.name = "TUI"

    # Display welcome message
    def __welcome(self):
        print("~~~~~~~~~~ Welcome to the {} Casino! ~~~~~~~~~~\n"
              "  So you want to try your luck against the dealer?\n\n"
              "  Choose an option to continue:\n".format(self.name))

    def __casinoMenu(self):
        print("---------- Options ----------\n"
              "    ? -- print this menu\n"
              "    n -- start a new game\n"
              "    r -- resume saved game\n"
              "    e -- exit\n")

    def __parse(self, p):
        opt = { '?' : self.__casinoMenu,
                'n' : self.newGame,
                'r' : self.resumeGame,
                'e' : self.__exit,
              }
        if p:
            if p in opt:
                opt[p]()
            else:
                print("Invalid input. Press ? for help.")

    def __gameMenu(self):
        print("---------- Choose a game: ----------\n"
              "  ? -- print this menu\n"
              "  1 -- blackjack\n"
              "  ...more coming soon!")

    def __gameParse(self, p):
        opt = { '?' : self.__gameMenu,
                '1' : self.__Blackjack 
              }
        if p:
            if p in opt:
                opt[p]()
            else:
                print("Invalid input.")

    def newGame(self):
        # TODO put in options for other games here
        self.__gameMenu()
        while True:
            try:
                if __debug__:
                    choice = "1"
                else:
                    choice = input(Casino.PROMPT)
                self.__gameParse(choice)
            except (KeyboardInterrupt, EOFError):
                self.__exit()

    # Some way to make this function generic? i.e. just take "Blackjack" as
    # argument and run init, then play "new game". Then that game object is
    # stored so we could pause, drop back into casino.run() and then resumeGame
    # by using "g.play()" again. Also works for re-loading saved game.
    def __Blackjack(self):
        g = cardgame.Blackjack()
        g.gameInit(useDefaults=True) # start with default, user can change later
        g.play()

    # Load saved game
    def resumeGame(self):
        print("Not supported")
        pass

    # Quit altogether
    def __exit(self):
        print("\nExiting...")
        sys.exit()

    # Fire it up!
    def run(self):
        self.__welcome()
        self.__casinoMenu()
        while True:
            try:
                if __debug__:
                    choice = "n"
                else:
                    choice = input(Casino.PROMPT)
                self.__parse(choice)
            except (KeyboardInterrupt, EOFError):
                self.__exit()

#------------------------------------------------------------------------------
#       Main loop
#------------------------------------------------------------------------------
if __name__ == "__main__":
    casino = Casino()
    casino.run()

#==============================================================================
#==============================================================================