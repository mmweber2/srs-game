"""Represents the current state of the game. Main game logic module."""
import random
from character import Character
from monster import Monster
from combat import Combat
from equipment import Equipment

TOWN_BUILDINGS = ["Armorer", "Enchanter", "Alchemist", "Training", "Forge",
                  "Temple", "Inn"]
TOWER_LEVELS = 100

# TODO: Add time costs to everything.
#       When we do this, have a function that applies time so we can also
#       check for day change stuff, like quests changing or shop inventory
#       changing

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
    # Monster currently in combat with
    self.monster = None
    # When we defeat a monster, treasure goes here so we can handle it a piece
    # at a time
    self.treasure_queue = []
    self.equipment_choice = None

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
    elif current_state == "COMBAT":
      return ["Attack", "Skill", "Item", "Escape"]
    elif current_state == "LOOT_EQUIPMENT":
      return ["", "Keep Current", "Keep New", ""]
    else:
      return ["Error", "Error", "Error", "Error"]

  def handle_treasure(self, logs):
    while self.treasure_queue:
      item = self.treasure_queue.pop()
      if type(item) is int:
        logs.append("You got %d gold." % item)
        self.character.gold += item
      elif type(item) is Equipment:
        logs.append("You got the following equipment")
        logs.append(str(item))
        self.add_state("LOOT_EQUIPMENT")
        self.equipment_choice = item
        break  # Have to give choice to player
      else:
        assert False

  ###
  # Helper methods for changing state
  ###

  def state_change_checks(self):
    if self.current_state() == "TOWN":
      self.character.restore_hp()

  def change_state(self, state):
    self.state.pop()
    self.state.append(state)
    self.state_change_checks()

  def add_state(self, state):
    self.state.append(state)
    self.state_change_checks()

  def leave_state(self):
    self.state.pop()
    self.state_change_checks()

  ###
  # Methods for applying choices in various states
  ###

  def apply_choice_char_create(self, logs, choice_text):
    self.character.make_initial_equipment(choice_text)
    logs.append("Generated %s equipment." % choice_text)
    self.change_state("TOWN")

  def start_combat(self, logs, boss):
    self.add_state("COMBAT")
    self.monster = Monster(self.floor, boss)
    logs.append("You have encountered a monster")

  def apply_choice_tower(self, logs, choice_text):
    if choice_text == "Explore":
      logs.append("You explore the tower...")
      # TODO: Add non-combat options in here
      if self.ascension_encounters > 0:
        self.ascension_encounters -= 1
        self.start_combat(logs, False)
      else:
        # TODO: Add boss every tenth floor
        self.floor += 1
        self.frontier = max(self.frontier, self.floor)
        self.change_state("OUTSIDE")
        logs.append("Congratulations, you have reached floor %d" % self.floor)
    elif choice_text == "Rest":
      logs.append("You rest")
      hp_gained = self.character.rest()
      logs.append("You regain %d HP" % hp_gained)
      if random.random() < .2:
        self.start_combat(logs, False)
    elif choice_text == "Item":
      logs.append("Not implemented yet")
    elif choice_text == "Leave Tower":
      self.change_state("OUTSIDE")

  def apply_death(self, logs):
    self.character.apply_death(logs)
    self.leave_state()
    self.change_state("TOWN")
    self.monster = None

  def apply_choice_combat(self, logs, choice_text):
    # return ["Attack", "Skill", "Item", "Escape"]
    if choice_text == "Attack":
      result = Combat.perform_turn("Attack", None, self.character, self.monster,
                                   logs)
      if result == Combat.CHARACTER_DEAD:
        self.apply_death(logs)
      elif result == Combat.MONSTER_DEAD:
        logs.append("You have defeated %s" % self.monster.name)
        self.character.gain_exp(self.monster.calculate_exp(),
                                self.monster.level, logs)
        self.treasure_queue = self.monster.get_treasure()
        self.monster = None
        self.leave_state()
        self.handle_treasure(logs)
    elif choice_text == "Skill":
      logs.append("Not implemented yet")
    elif choice_text == "Item":
      logs.append("Not implemented yet")
    elif choice_text == "Escape":
      logs.append("You attempt to escape...")
      result = Combat.perform_turn("Escape", None, self.character, self.monster,
                                   logs)
      # TODO: Maybe monster can die in this case (eventually DoTs)
      if result == Combat.CHARACTER_DEAD:
        self.apply_death(logs)
      elif result == Combat.CHARACTER_ESCAPED:
        logs.append("You escaped successfully")
        self.monster = None
        self.leave_state()

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

  def apply_choice_loot_equipment(self, logs, choice_text):
    if choice_text == "Keep Current":
      # TODO: Implement whatever raw materials system
      pass
    elif choice_text == "Keep New":
      self.character.equip(self.equipment_choice)
      self.equipment_choice = None
    self.leave_state()
    self.handle_treasure(logs)

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
    except AttributeError as exc:
      print exc
      logs.append("apply_choice not implemented yet, state: %s" % current_state)
      # Hack. TODO: remove
      if len(self.state) > 1:
        self.leave_state()
    return logs

  def equipment_choice_text(self):
    pieces = []
    slot = self.equipment_choice.slot
    pieces.append("Current Equipment:\n")
    pieces.append(str(self.character.equipment[slot]))
    pieces.append("\nNew Equipment:\n")
    pieces.append(str(self.equipment_choice))
    return "".join(pieces)

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
    elif current_state == "COMBAT":
      return str(self.monster)
    elif current_state == "LOOT_EQUIPMENT":
      return self.equipment_choice_text()
    else:
      return "Error, no text for state %s" % current_state
