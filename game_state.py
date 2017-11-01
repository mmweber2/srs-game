"""Represents the current state of the game. Main game logic module."""
from character import Character

class GameState(object):
  """
    GameState represents all the state for the current game, and functions for
    interacting with the GameState.

    In general, the GameState is updated by the player making one of four
    choices, and the UI will then call GameState.apply_choice, which updates
    the GameState.
  """
  def __init__(self):
    self.state = ["CHAR_CREATE"]
    self.character = Character()
    self.floor = 1
    self.tower = []
    # FIXME: Generate tower

  def current_state(self):
    """Return the current state."""
    return self.state[-1]

  def get_choices(self):
    """Return choices for next actions for the UI."""
    if self.current_state() == "CHAR_CREATE":
      return ["Strength", "Stamina", "Speed", "Intellect"]
    elif self.current_state() == "TOWN":
      return ["Climb Tower", "Armor Shop", "Training", "Item Shop"]
    else:
      return ["Error", "Error", "Error", "Error"]

  def apply_choice(self, choice):
    """Apply the given action choice to this gamestate, modifying it."""
    logs = []
    if self.current_state() == "CHAR_CREATE":
      self.character.make_initial_equipment(self.get_choices()[choice])
      logs.append("Generated %s equipment." % self.get_choices()[choice])
      self.state.pop()
      self.state.append("TOWN")
    else:
      assert False
    return logs

  # TODO: This and get_choices should probably be done differently (with a dict
  #       for example
  def panel_text(self):
    """Return text to display to the player about the current game state."""
    if self.current_state() == "CHAR_CREATE":
      return "Please choose the starting specialization for your character"
    elif self.current_state() == "TOWN":
      return "Town on tower level %d" % self.floor
    else:
      return "Error, unhandled state %s" % self.current_state()
