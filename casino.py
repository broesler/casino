#!/usr/local/anaconda3/bin/python
#==============================================================================
#     File: casino.py
#  Created: 08/03/2017, 10:08
#   Author: Bernie Roesler
#
"""
  Description: General wrapper to manage card games. Can start new games,
  resume old (not yet implemented), or just exit.
"""
#==============================================================================

import pickle
import os
import sys

import casinogame
from casinogame import GamePause

def ls_sort_mtime(path):
    ''' Sort files in path by mtime. '''
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))

#------------------------------------------------------------------------------
#       Casino Royale with Cheese
#------------------------------------------------------------------------------
class Casino:
    """ Wrapper class to govern the playing and loading of all games. """
    _PROMPT = "(Casino)> "
    _GAME_LIST = []

    def __init__(self):
        self.name = "TUI"

    # Display welcome message
    def __welcome(self):
        print("~~~~~~~~~~ Welcome to the {} Casino! ~~~~~~~~~~\n"
              "So you want to try your luck against the dealer?\n\n"
              "Choose an option to continue:\n".format(self.name))

    def __casinoMenu(self):
        print("---------- Options ----------\n"
              "    ? -- print this menu\n"
              "    n -- start a new game\n"
              "    r -- resume paused game\n"
              "    l -- load saved game\n"
              "    e -- exit\n")

    def __parse(self, p):
        opt = { '?' : self.__casinoMenu,
                'n' : self.newGame,
                'l' : self.loadGame,
                'r' : self.resumeGame,
                'e' : self.__exit,
              }
        if p:
            if p in opt:
                opt[p]()
            else:
                print("Invalid input. Press ? for help.")

    # TODO put in options for other games here
    def __gameMenu(self):
        print("---------- Choose a game: ----------\n"
              "  ? -- print this menu\n"
              "  1 -- blackjack\n"
              "       ...more coming soon!")

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
        self.__gameMenu()
        while True:
            try:
                if __debug__:
                    choice = "1"
                else:
                    choice = input(Casino._PROMPT)
                # Keep the value of the game started (if one)
                g = self.__gameParse(choice)
            except (KeyboardInterrupt, EOFError):
                self.__exit()
            except GamePause:
                # Drop back into casino outer loop, so print menu
                self.__casinoMenu()

    # Some way to make this function generic? i.e. just take "Blackjack" as
    # argument and run init, then play "new game". Then that game object is
    # stored so we could pause, drop back into casino.run() and then resumeGame
    # by using "g.play()" again. Also works for re-loading saved game.
    def __Blackjack(self):
        g = casinogame.Blackjack()
        _GAME_LIST.append(g)
        g.gameInit(useDefaults=True) # start with default, user can change later
        g.play()

    # Resume paused game
    def resumeGame(self, g):
        g = _GAME_LIST.pop()
        g.play()

    # Load saved game
    def loadGame(self):
        # TODO have global/shared variable for path 
        # TODO Parse to get time-stamp and pretty-print options for menu
        # Load user-selected file and g.play()
        path = "./.casino_save/"
        files = ls_sort_mtime(path)
        g = pickle.load(open(os.path.join(path, files[0]), "rb"))
        g.play()

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
                    choice = input(Casino._PROMPT)
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
