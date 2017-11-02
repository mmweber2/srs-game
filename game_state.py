"""Represents the current state of the game. Main game logic module."""
import random
from character import Character

TOWN_BUILDINGS = ["Armorer", "Enchanter", "Alchemist", "Training", "Forge",
                  "Temple", "Inn"]
TOWER_LEVELS = 100

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
    self.frontier = 1
    self.time_spent = 0
    self.energy = 200
    self.towns = self.generate_towns()
    # When you complete a quest on a level, you gain some faction for that level
    # and some for surrounding levels, decreasing cost of things?
    self.tower_faction = [0] * 100
    # TODO. This is to prevent quest scumming.
    self.current_quest = [None] * 100
    # TODO: Same with shop contents? Should it reset at some point?
    # Number of encounters remaining in current tower ascension
    # Could be battles or other things (finding treasure, finding a shop)
    self.ascension_encounters = 0

  @staticmethod
  def generate_towns():
    # Level 0 does not exist
    tower = [None]
    for _ in range(TOWER_LEVELS):
      shop_set = set()
      while len(shop_set) < 3:
        shop_set.add(random.choice(TOWN_BUILDINGS))
      tower.append(("Leave Town",) + tuple(shop_set))
    return tower

  def current_state(self):
    """Return the current state."""
    return self.state[-1]

  def get_choices(self):
    """Return choices for next actions for the UI."""
    current_state = self.current_state()
    if current_state == "CHAR_CREATE":
      return ["Strength", "Stamina", "Speed", "Intellect"]
    elif current_state == "TOWN":
      return self.towns[self.floor]
    elif current_state == "ARMORER":
      # TODO
      return ["Armor 1", "Armor 2", "Armor 3", "Leave Shop"]
    elif current_state == "ENCHANTER":
      return ["Enchant Weapon", "Enchant Armor", "Enchant Accessory",
              "Leave Shop"]
    elif current_state == "ALCHEMIST":
      # TODO
      return ["Item 1", "Item 2", "Item 3", "Leave Shop"]
    elif current_state == "TRAINING":
      return ["Gain XP", "Train Skill", "Train Passives", "Leave Shop"]
    elif current_state == "FORGE":
      return ["", "Reforge Weapon", "Reforge Armor", "Leave Shop"]
    elif current_state == "TEMPLE":
      return ["", "Blessing", "Purify Rune", "Leave Temple"]
    elif current_state == "INN":
      return ["", "Rest", "Buy Food", "Leave Inn"]
    elif current_state == "OUTSIDE":
      return ["Ascend Tower", "Quest", "Town", "Descend Tower"]
    elif current_state == "TOWER":
      return ["Explore", "Rest", "Item", "Leave Tower"]
    else:
      return ["Error", "Error", "Error", "Error"]

  ###
  # Helper methods for changing state
  ###

  def change_state(self, state):
    self.state.pop()
    self.state.append(state)

  def add_state(self, state):
    self.state.append(state)

  def leave_state(self):
    self.state.pop()

  ###
  # Methods for applying choices in various states
  ###

  def apply_choice_char_create(self, logs, choice_text):
    self.character.make_initial_equipment(choice_text)
    logs.append("Generated %s equipment." % choice_text)
    self.change_state("TOWN")

  def apply_choice_tower(self, logs, choice_text):
    if choice_text == "Explore":
      logs.append("Not implemented yet")
    elif choice_text == "Rest":
      logs.append("Not implemented yet")
    elif choice_text == "Item":
      logs.append("Not implemented yet")
    elif choice_text == "Leave Tower":
      self.change_state("OUTSIDE")

  def apply_choice_town(self, logs, choice_text):
    if choice_text == "Leave Town":
      self.change_state("OUTSIDE")
      logs.append("Left town")
    else:
      logs.append("Went to the %s" % choice_text)
      next_state = choice_text.upper()
      self.add_state(next_state)

  def apply_choice_outside(self, logs, choice_text):
    if choice_text == "Ascend Tower":
      if self.frontier <= self.floor:
        self.change_state("TOWER")
        self.ascension_encounters = random.randint(5, 10)
        logs.append("Entered tower")
      else:
        self.floor += 1
        logs.append("Ascended to floor %d" % self.floor)
    elif choice_text == "Quest":
      logs.append("Not implemented yet")
    elif choice_text == "Town":
      self.change_state("TOWN")
      logs.append("Went to town")
    elif choice_text == "Descend Tower":
      if self.floor > 1:
        self.floor -= 1
        logs.append("Descended to floor %d" % self.floor)
      else:
        logs.append("Cannot descend while on floor 1.")

  # TODO: Implement: ARMORER, ENCHANTER, ALCHEMIST, TRAINING,
  #                  FORGE, TEMPLE, INN

  def apply_choice(self, choice):
    """Apply the given action choice to this gamestate, modifying it."""
    logs = []
    current_state = self.current_state()
    choice_text = self.get_choices()[choice]
    method_name = "apply_choice_" + current_state.lower()
    try:
      method = getattr(GameState, method_name)
      method(self, logs, choice_text)
    except AttributeError:
      logs.append("apply_choice not implemented yet, state: %s" % current_state)
      # Hack. TODO: remove
      if len(self.state) > 1:
        self.leave_state()
    return logs

  # TODO: This and get_choices should probably be done differently (with a dict
  #       for example
  def panel_text(self):
    """Return text to display to the player about the current game state."""
    # TODO: Add explanations for menu choices, as well.
    current_state = self.current_state()
    if current_state == "CHAR_CREATE":
      return "Please choose the starting specialization for your character"
    elif current_state == "TOWN":
      return "Town on tower level %d" % self.floor
    elif current_state == "OUTSIDE":
      return "Outside town on tower level %d" % self.floor
    elif current_state == "TOWER":
      return "Inside the tower ascending to level %d" % (self.floor + 1)
    else:
      return "Error, no text for state %s" % current_state
