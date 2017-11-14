"""Represents the current state of the game. Main game logic module."""
import random
from character import Character, TRAITS
from monster import Monster
from combat import Combat
from equipment import Equipment
from quest import Quest
import rooms
from items import Item

TOWN_BUILDINGS = [rooms.ArmorShop, rooms.Enchanter, rooms.Forge,
                  rooms.Alchemist, rooms.TrainingRoom, rooms.Temple,
                  rooms.Inn, rooms.WeaponShop, rooms.Dungeon]

TOWER_BUILDINGS = [rooms.ArmorShop, rooms.Enchanter, rooms.Forge,
                   rooms.Alchemist, rooms.TrainingRoom, rooms.Temple,
                   rooms.Inn, rooms.WeaponShop]

CHOICES = {"CHAR_CREATE": ["Strength", "Stamina", "Speed", "Intellect"],
           "RUNE_WORLD": ["Explore", "", "Item", "Leave Rune"],
           "TOWER": ["Explore", "Rest", "Item", "Leave Tower"],
           "DUNGEON": ["Explore", "Rest", "Item", "Leave Dungeon"],
           "COMBAT": ["Attack", "Skill", "Item", "Escape"],
           "LOOT_EQUIPMENT": ["", "Keep Current", "Keep New", ""],
           "ACCEPT_QUEST": ["", "Accept Quest", "Decline Quest", ""]}

TOWER_LEVELS = 100
UPDATE_TIME = 360
DEBUG_FLOOR = 1
DEBUG_BUILDING = None
DEBUG_GOLD = None
#DEBUG_BUILDING = rooms.Alchemist
#DEBUG_GOLD = 1000

# TODO: It is probably not best to be passing logs around to everything?
#       it could be part of the GameState, or we could use a logger for real

# TODO: Add top floor state

# TODO: Adding gaining skills on level up

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
    if DEBUG_GOLD:
      self.character.gold = DEBUG_GOLD
    self.floor = 1
    self.frontier = 1
    self.time_spent = 0
    self.energy = 200
    self.towns = self.generate_towns()
    self.tower_lock = [True] * (TOWER_LEVELS + 1)
    self.tower_lock[1] = False
    self.tower_faction = [1.0] * (TOWER_LEVELS + 1)
    self.tower_update_ready = False
    self.tower_quests = self.generate_quests()
    # Number of encounters remaining in current tower ascension
    self.ascension_encounters = 0
    # Monster currently in combat with
    self.monster = None
    self.quest = None
    # When we defeat a monster, treasure goes here so we can handle it a piece
    # at a time
    self.treasure_queue = []
    self.equipment_choice = None
    self.current_shop = None
    self.rune_level = -1
    self.levelups = 0

  ###
  # Helper methods for changing state
  ###

  @staticmethod
  def generate_quests():
    quests = [None]
    for i in xrange(1, TOWER_LEVELS + 1):
      quests.append(Quest(i))
    return quests

  @staticmethod
  def generate_towns():
    # Level 0 does not exist
    tower = [None]
    for level in range(1, TOWER_LEVELS + 1):
      shop_set = set()
      while len(shop_set) < 3:
        shop_set.add(random.choice(TOWN_BUILDINGS))
      shops = []
      for shop in shop_set:
        shops.append(shop(level))
      tower.append(shops)
    if DEBUG_BUILDING:  # pylint: disable=not-callable
      tower[DEBUG_FLOOR][0] = DEBUG_BUILDING(DEBUG_FLOOR)
    return tower

  def tower_update(self):
    self.tower_quests = self.generate_quests()
    for level in xrange(1, 101):
      for shop in range(3):
        self.towns[level][shop].refresh()

  def time_to_refresh(self):
    return UPDATE_TIME - (self.time_spent % UPDATE_TIME)

  def pass_time(self, amount, logs):
    old_period = self.time_spent / UPDATE_TIME
    if self.rune_level == -1:
      self.time_spent += amount
    new_period = self.time_spent / UPDATE_TIME
    if old_period != new_period:
      self.tower_update_ready = True
      logs.append("Tower ready for update.")
    self.character.pass_time(amount)
    if self.monster:
      self.monster.pass_time(amount)

  def current_state(self):
    """Return the current state."""
    return self.state[-1]

  def faction_update(self, base_floor):
    for floor in xrange(max(1, base_floor - 4),
                        min(base_floor + 4, TOWER_LEVELS) + 1):
      difference = abs(floor - base_floor)
      multiplier = .95 + (.01 * difference)
      assert .94 < multiplier < 1.0
      self.tower_faction[floor] *= multiplier

  def get_choices(self):
    """Return choices for next actions for the UI."""
    current_state = self.current_state()
    if current_state in CHOICES:
      return CHOICES[current_state]
    if current_state == "TOWN":
      choices = [shop.get_name() for shop in self.towns[self.floor]]
      return ["Leave Town"] + choices
    elif current_state == "SHOP":
      return self.current_shop.get_buttons(self.character)
    elif current_state == "OUTSIDE":
      choices = []
      choices.append("" if self.tower_lock[self.floor] else "Ascend Tower")
      choices.append("Quest" if self.tower_quests[self.floor] else "")
      choices.append("Town")
      choices.append("Descend Tower")
      return choices
    elif current_state == "QUEST":
      if self.quest.complete():
        return ["Complete Quest", "", "", "Leave Quest"]
      else:
        return ["Continue Quest", "Rest", "Item", "Leave Quest"]
    elif current_state == "USE_ITEM":
      choices = []
      for i in range(len(self.character.items)):
        choices.append("Use Item #%d" % (i + 1))
      while len(choices) < 3:
        choices.insert(0, "")
      choices.append("Never Mind")
      return choices
    elif current_state == "LEVEL_UP":
      return self.character.get_trait_choices()
      # Next: Handle the trait choice, then implement the traits
    elif current_state == "USE_SKILL":
      choices = [""] * (3 - len(self.character.skills))
      for skill in self.character.skills:
        if skill.sp_cost() > self.character.current_sp:
          choices.append("")
        else:
          choices.append(skill.get_name())
      choices.append("Never Mind")
      return choices
    else:
      return ["Error", "Error", "Error", "Error"]

  def handle_treasure(self, logs):
    while self.treasure_queue:
      item = self.treasure_queue.pop()
      if isinstance(item, int):
        amount_gained = self.character.gain_gold(item)
        logs.append("You got %d gold." % amount_gained)
      elif isinstance(item, Equipment):
        logs.append("You got the following equipment")
        logs.append(str(item))
        self.add_state("LOOT_EQUIPMENT")
        self.equipment_choice = item
        break  # Have to give choice to player
      elif item == "Rune":
        logs.append("You found a corrupted rune.")
        self.character.runes += 1
      else:
        assert False

  def handle_rune_completion(self, logs):
    self.leave_state()
    if self.rune_level == 0:
      logs.append("Unpurified, the rune dissolves into dust.")
      return
    item = Equipment.get_new_armor(self.rune_level, slot=4, rarity=4)
    self.treasure_queue.append(item)
    self.rune_level = -1
    self.handle_treasure(logs)

  ###
  # Helper methods for changing state
  ###

  def state_change_checks(self):
    if self.current_state() == "TOWN":
      self.character.restore_hp()
      self.character.restore_sp()
    if self.current_state() == "OUTSIDE" or self.current_state == "TOWN":
      if self.tower_update_ready:
        self.tower_update()
        self.tower_update_ready = False

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

  def start_combat(self, logs, boss, level=None):
    if level is None:
      level = self.floor
    self.add_state("COMBAT")
    self.monster = Monster(level, boss)
    logs.append("You have encountered a monster")

  def apply_choice_rune_world(self, logs, choice_text):
    if choice_text == "Explore":
      self.rune_level += 1
      self.start_combat(logs, False, level=self.rune_level)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Rune":
      self.pass_time(0, logs)
      logs.append("You leave the world of the rune")
      self.handle_rune_completion(logs)

  def apply_choice_accept_quest(self, logs, choice_text):
    if choice_text == "Accept Quest":
      self.change_state("QUEST")
      logs.append("You accept the quest.")
    elif choice_text == "Decline Quest":
      self.quest = None
      self.leave_state()
      logs.append("You decline the quest.")

  def apply_choice_use_item(self, logs, choice_text):
    if choice_text.startswith("Use Item #"):
      self.pass_time(0, logs)
      choice = int(choice_text[-1])
      assert choice > 0
      choice -= 1
      item = self.character.items.pop(choice)
      result = item.apply(self.character, self.monster, logs)
      if result == Item.UNUSABLE:
        logs.append("That item cannot be used right now.")
        self.character.items.append(item)
      else:
        self.leave_state()
    elif choice_text == "Never Mind":
      self.pass_time(0, logs)
      self.leave_state()

  def apply_choice_quest(self, logs, choice_text):
    if choice_text == "Continue Quest":
      self.pass_time(random.randint(1, 3), logs)
      logs.append("You continue the quest...")
      self.add_state("COMBAT")
      self.monster = self.quest.get_monster()
      # TODO: Merge this with start_combat somehow
      logs.append("You have encountered a monster")
      #return ["Continue Quest", "Rest", "Item", "Leave Quest"]
    elif choice_text == "Rest":
      self.pass_time(5, logs)
      logs.append("You rest")
      hp_gained = self.character.rest()
      logs.append("You regain %d HP" % hp_gained)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Quest":
      self.pass_time(1, logs)
      self.leave_state()
    elif choice_text == "Complete Quest":
      logs.append("You complete the quest.")
      amount_gained = self.character.gain_gold(self.quest.gp_reward)
      logs.append("You gain %d gold." % amount_gained)
      levelups = self.character.gain_exp(self.quest.xp_reward, self.floor, logs,
                                         level_adjust=False)
      self.treasure_queue = self.quest.get_treasure()
      self.faction_update(self.floor)
      # Fixes a bug when the tower update is pending
      regenerate_quest = self.tower_update_ready
      self.leave_state()
      if self.current_state() == "OUTSIDE":
        if regenerate_quest:
          self.tower_quests[self.floor] = Quest(self.floor)
        else:
          self.tower_quests[self.floor] = None
      if levelups > 0:
        self.levelups = levelups
        self.add_state("LEVEL_UP")
      self.handle_treasure(logs)

  def apply_choice_tower(self, logs, choice_text):
    if choice_text == "Explore":
      self.pass_time(random.randint(1, 10), logs)
      logs.append("You explore the tower...")
      if self.ascension_encounters > 0:
        self.ascension_encounters -= 1
        random_number = random.random()
        if random_number < .01:
          logs.append("You find a treasure hoard!")
          self.find_treasure(logs, 8)
        elif random_number < .025:
          logs.append("You find a shop")
          self.character.restore_hp()
          self.character.restore_sp()
          shop = random.choice(TOWER_BUILDINGS)(self.floor)
          self.add_state("SHOP")
          self.current_shop = shop
          shop.enter_shop(self.tower_faction[self.floor])
        elif random_number < .125:
          logs.append("You find a treasure chest")
          self.find_treasure(logs, 1)
        elif random_number < .165:
          self.start_combat(logs, True)  # Boss monster
        else:
          self.start_combat(logs, False)
      else:
        self.floor += 1
        self.frontier = max(self.frontier, self.floor)
        self.change_state("OUTSIDE")
        logs.append("Congratulations, you have reached floor %d" % self.floor)
    elif choice_text == "Rest":
      self.pass_time(5, logs)
      logs.append("You rest")
      hp_gained = self.character.rest()
      logs.append("You regain %d HP" % hp_gained)
      if random.random() < .2:
        self.start_combat(logs, False)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Tower":
      self.pass_time(10, logs)
      logs.append("You leave the tower")
      self.change_state("OUTSIDE")

  def find_treasure(self, logs, item_count):
    treasure = []
    for i in range(item_count):
      if random.random() < .5:
        min_gold = self.floor * 10
        max_gold = self.floor * 20
        treasure.append(random.randint(min_gold, max_gold))
      else:
        rarity = min(random.randint(1, 4) for _ in range(3))
        level = max(1, int(self.floor + random.gauss(0, 1)))
        treasure.append(Equipment.get_new_armor(level, rarity))
    self.treasure_queue = treasure
    self.handle_treasure(logs)

  # TODO: Duplication with apply_choice_tower
  def apply_choice_dungeon(self, logs, choice_text):
    if choice_text == "Explore":
      self.pass_time(random.randint(1, 5), logs)
      logs.append("You explore the dungeon...")
      random_number = random.random()
      if random_number < .02:
        logs.append("You find a treasure hoard!")
        self.find_treasure(logs, 8)
      elif random_number < .20:
        logs.append("You find a treasure chest")
        self.find_treasure(logs, 1)
      else:
        self.start_combat(logs, False)
    elif choice_text == "Rest":
      self.pass_time(5, logs)
      logs.append("You rest")
      hp_gained = self.character.rest()
      logs.append("You regain %d HP" % hp_gained)
      if random.random() < .2:
        self.start_combat(logs, False)
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Leave Dungeon":
      self.pass_time(5, logs)
      logs.append("You leave the dungeon")
      self.leave_state()

  def apply_death(self, logs):
    # TODO: Clean this up. The code flow is messy
    self.leave_state()  # COMBAT
    self.monster.buffs = []
    self.monster.debuffs = []
    self.monster = None
    # TODO: This is hacky. Should probably have TOWER also be an add_state
    if self.current_state() == "QUEST":
      self.character.apply_death(logs)
      self.leave_state()
    elif self.current_state() == "RUNE_WORLD":
      self.character.apply_death(logs, penalty=False)
      self.handle_rune_completion(logs)
      return
    else:
      self.character.apply_death(logs)
    self.change_state("TOWN")
    self.pass_time(random.randint(0, 3 * self.floor), logs)

  def dungeon_victory_update(self, base_floor):
    for floor in xrange(max(1, base_floor - 3),
                        min(base_floor + 3, TOWER_LEVELS) + 1):
      difference = abs(floor - base_floor)
      multiplier = 1.0 - (.008 / (2 ** abs(difference)))
      assert .992 <= multiplier < 1.0
      self.tower_faction[floor] *= multiplier

  def handle_combat_result(self, logs, result):
    if result == Combat.CHARACTER_DEAD:
      self.apply_death(logs)
    elif result == Combat.MONSTER_DEAD:
      logs.append("You have defeated %s" % self.monster.name)
      levelups = self.character.gain_exp(self.monster.calculate_exp(),
                                         self.monster.level, logs)
      self.treasure_queue = self.monster.get_treasure()
      self.monster = None
      self.leave_state()
      if self.current_state() == "QUEST":
        self.quest.defeat_monster()
      if self.current_state() == "DUNGEON":
        self.dungeon_victory_update(self.floor)
      if levelups > 0:
        self.levelups = levelups
        self.add_state("LEVEL_UP")
      self.handle_treasure(logs)

  def apply_choice_combat(self, logs, choice_text):
    if choice_text == "Attack":
      self.pass_time(1, logs)
      result = Combat.perform_turn("Attack", None, self.character, self.monster,
                                   logs)
      self.handle_combat_result(logs, result)
    elif choice_text == "Skill":
      self.add_state("USE_SKILL")
    elif choice_text == "Item":
      self.pass_time(0, logs)
      self.add_state("USE_ITEM")
    elif choice_text == "Escape":
      self.pass_time(1, logs)
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

  def apply_choice_use_skill(self, logs, choice_text):
    if choice_text == "Never Mind":
      self.leave_state()
    else:
      for skill in self.character.skills:
        if skill.get_name() == choice_text:
          self.leave_state()  # USE_SKILL
          self.pass_time(1, logs)
          self.character.current_sp -= skill.sp_cost()
          result = Combat.perform_turn("Skill", skill, self.character,
                                       self.monster, logs)
          self.handle_combat_result(logs, result)
          break
      else:
        assert False

  def apply_choice_level_up(self, logs, choice_text):
    assert self.levelups > 0
    learned = self.character.learn_trait(choice_text)
    if learned:
      self.levelups -= 1
      if self.levelups == 0:
        self.leave_state()

  def apply_choice_town(self, logs, choice_text):
    if choice_text == "Leave Town":
      self.pass_time(2, logs)
      self.change_state("OUTSIDE")
      logs.append("Left town")
    else:
      shop = None
      for shop in self.towns[self.floor]:
        if shop.get_name() == choice_text:
          self.current_shop = shop
          break
      if shop:
        self.pass_time(1, logs)
        logs.append("Went to the %s" % shop.get_name())
        self.add_state("SHOP")
        shop.enter_shop(self.tower_faction[self.floor])

  def apply_choice_shop(self, logs, choice_text):
    time_cost, result = self.current_shop.apply_choice(choice_text, logs,
                                                       self.character)
    self.pass_time(time_cost, logs)
    if result == self.current_shop.LEAVE_ROOM:
      self.leave_state()
    elif result == self.current_shop.NO_CHANGE:
      pass
    elif result == self.current_shop.USE_ITEM:
      self.add_state("USE_ITEM")
    elif result == self.current_shop.PURIFY_RUNE:
      self.character.runes -= 1
      self.rune_level = 0
      self.add_state("RUNE_WORLD")
    elif result == self.current_shop.ENTER_DUNGEON:
      self.add_state("DUNGEON")
    else:
      assert False

  def apply_choice_outside(self, logs, choice_text):
    if choice_text == "Ascend Tower":
      self.pass_time(10, logs)
      if self.frontier <= self.floor:
        self.change_state("TOWER")
        self.ascension_encounters = random.randint(5, 10)
        logs.append("Entered tower")
      else:
        self.floor += 1
        logs.append("Ascended to floor %d" % self.floor)
    elif choice_text == "Quest":
      self.pass_time(5, logs)
      self.add_state("ACCEPT_QUEST")
      logs.append("You look for a quest giver...")
      self.quest = self.tower_quests[self.floor]
    elif choice_text == "Town":
      self.pass_time(5, logs)
      self.change_state("TOWN")
      logs.append("Went to town")
      if self.tower_lock[self.floor]:
        self.tower_lock[self.floor] = False
        logs.append("Ascend Tower unlocked")
    elif choice_text == "Descend Tower":
      self.pass_time(10, logs)
      if self.floor > 1:
        self.floor -= 1
        logs.append("Descended to floor %d" % self.floor)
      else:
        logs.append("Cannot descend while on floor 1.")

  def apply_choice_loot_equipment(self, logs, choice_text):
    if choice_text == "Keep Current":
      recycle = self.equipment_choice
    elif choice_text == "Keep New":
      recycle = self.character.equip(self.equipment_choice)
      self.equipment_choice = None
    logs.append("Recycled %s" % recycle)
    materials = recycle.get_recycled_materials()
    self.character.gain_materials(materials)
    logs.append("Received %s" % Equipment.materials_string(materials))
    # Add materials to character, add materials inventory to character string
    self.leave_state()
    self.handle_treasure(logs)

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
      print exc  # pylint: disable=print-statement
      logs.append("apply_choice not implemented yet, state: %s" % current_state)
    return logs

  def loot_choice_text(self):
    slot = self.equipment_choice.slot
    return Equipment.equipment_comparison_text(self.character.equipment[slot],
                                               self.equipment_choice)

  def use_item_text(self):
    pieces = []
    for i, item in enumerate(self.character.items):
      pieces.append("Use Item #%d: %s" % (i + 1, item.get_name()))
    return "\n".join(pieces)

  def trait_text(self):
    pieces = []
    pieces.append("Select a trait")
    choices = self.get_choices()
    for choice in choices:
      if choice in TRAITS:
        pieces.append("%s: %s" % (choice, TRAITS[choice]))
    return "\n".join(pieces)

  def skill_select_text(self):
    pieces = []
    for skill in self.character.skills:
      insufficient_sp = ("" if self.character.current_sp >= skill.sp_cost()
                         else " (Insufficient SP)")
      pieces.append("%s: %d sp%s\n%s" % (skill.get_name(), skill.sp_cost(),
                                        insufficient_sp, 
                                        skill.get_description()))
    return "\n".join(pieces)

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
      return self.loot_choice_text()
    elif current_state == "ACCEPT_QUEST" or current_state == "QUEST":
      return str(self.tower_quests[self.floor])
    elif current_state == "SHOP":
      return self.current_shop.get_text(self.character)
    elif current_state == "USE_ITEM":
      return self.use_item_text()
    elif current_state == "RUNE_WORLD":
      return "Rune world level %d" % (self.rune_level + 1)
    elif current_state == "DUNGEON":
      return "Level %d Dungeon" % self.floor
    elif current_state == "LEVEL_UP":
      return self.trait_text()
    elif current_state == "USE_SKILL":
      return self.skill_select_text()
    else:
      return "Error, no text for state %s" % current_state
