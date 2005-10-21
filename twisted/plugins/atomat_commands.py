"""Atomat command line plugins."""

from atomat import cliplug

from atomat.commands import import_
import_ = cliplug.CommandFactory(import_.Import)
