"""Represents the current state of the game. Main game logic module."""
import random
from character import Character
from monster import Monster
from combat import Combat
from equipment import Equipment, RARITY
from quest import Quest

TOWN_BUILDINGS = ["Armorer", "Enchanter", "Alchemist", "Training", "Forge",
                  "Temple", "Inn", "Weaponsmith"]
TOWER_LEVELS = 100
UPDATE_TIME = 360
#DEBUG_BUILDING = "Training"
DEBUG_FLOOR = 1
DEBUG_BUILDING = None

# TODO: Add time costs to everything.
#       When we do this, have a function that applies time so we can also
#       check for day change stuff, like quests changing or shop inventory
#       changing

# TODO: It is probably not best to be passing logs around to everything?
#       it could be part of the GameState, or we could use a logger for real

# TODO: Probably shops should be objects that track their own state and
#       can return text and so forth, instead of this game_state kludge
#       "Floor" can be part of that object, so maybe in the tower you find
#       a shop that is more powerful than you "should"
#       START HERE

# TODO: Reforging is too cheap. Probably 25 * (new_level) * (level_difference)?

# BUG: If you rest (and possibly just fight?) in a quest, and the tower resets,
#      the quest resets. Actually, the quest display is wrong, it seems like

# TODO: Need a place to buy accessories? Maybe?

# TODO: Add top floor state

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
    self.tower_lock = [True] * (TOWER_LEVELS + 1)
    self.tower_lock[1] = False
    # TODO:
    # When you complete a quest on a level, you gain some faction for that level
    # and some for surrounding levels, decreasing cost of things?
    self.tower_faction = [0] * (TOWER_LEVELS + 1)
    # This is to prevent quest/shop scumming
    self.tower_quests = self.generate_quests()
    self.armor_shops = self.generate_armor_shops()
    self.weapon_shops = self.generate_weapon_shops()
    self.times_trained = [0] * (TOWER_LEVELS + 1)
    # Number of encounters remaining in current tower ascension
    # Could be battles or other things (finding treasure, finding a shop)
    self.ascension_encounters = 0
    # Monster currently in combat with
    self.monster = None
    self.quest = None
    # When we defeat a monster, treasure goes here so we can handle it a piece
    # at a time
    self.treasure_queue = []
    # TODO: This is starting to get a little unwieldy. Clean up?
    #       There is probably a cleaner way to track all this shop state
    self.equipment_choice = None
    self.shop_choice = None
    self.piece_to_buy = None

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
  def generate_armor_shops():
    # TODO: Don't necessarily have to generate armor for every level, since
    #       not every level has an armor shop. But this is simple.
    shops = [None]
    for i in xrange(1, TOWER_LEVELS + 1):
      armor = []
      for j in range(1, 4):  # Slots for armor pieces. TODO: A bit hacky
        armor.append(Equipment.get_new_armor(i, j))
      shops.append(armor)
    return shops

  @staticmethod
  def generate_weapon_shops():
    # TODO: Same with weapon shops
    shops = [None]
    for i in xrange(1, TOWER_LEVELS + 1):
      weapons = []
      for _ in range(3):
        weapons.append(Equipment.get_new_armor(i, 0))  # 0 -> weapon slot
      shops.append(weapons)
    return shops

  @staticmethod
  def generate_towns():
    # Level 0 does not exist
    tower = [None]
    for _ in range(TOWER_LEVELS):
      shop_set = set()
      while len(shop_set) < 3:
        shop_set.add(random.choice(TOWN_BUILDINGS))
      tower.append(("Leave Town",) + tuple(shop_set))
    if DEBUG_BUILDING:
      tower[DEBUG_FLOOR] = ("Leave Town", DEBUG_BUILDING, "DEBUG", "DEBUG")
    return tower

  def tower_update(self):
    # TODO: Update quests, inventories, etc, since 6 hours has passed
    self.tower_quests = self.generate_quests()
    self.armor_shops = self.generate_armor_shops()
    self.weapon_shops = self.generate_weapon_shops()

  def time_to_refresh(self):
    return UPDATE_TIME - (self.time_spent % UPDATE_TIME)

  def pass_time(self, amount, logs):
    old_period = self.time_spent / UPDATE_TIME
    self.time_spent += amount
    new_period = self.time_spent / UPDATE_TIME
    if old_period != new_period:
      self.tower_update()
      # TODO: Better text?
      logs.append("Tower has updated")

  def current_state(self):
    """Return the current state."""
    return self.state[-1]

  # TODO: Clean this up. While some of them require logic, a lot of them do not,
  #       so we could move those to a dictionary, and leave only the ones that
  #       require logic
  def get_choices(self):
    """Return choices for next actions for the UI."""
    current_state = self.current_state()
    if current_state == "CHAR_CREATE":
      return ["Strength", "Stamina", "Speed", "Intellect"]
    elif current_state == "TOWN":
      return self.towns[self.floor]
    elif current_state == "ARMORER":
      choices = []
      for i in range(len(self.armor_shops[self.floor])):
        if self.armor_shops[self.floor][i] is not None:
          choices.append("Armor #%d" % (i + 1))
        else:
          choices.append("")
      choices.append("Leave Shop")
      return choices
    elif current_state == "WEAPONSMITH":
      # TODO: Clean up duplication with Armorer?
      choices = []
      for i in range(len(self.weapon_shops[self.floor])):
        if self.weapon_shops[self.floor][i] is not None:
          choices.append("Weapon #%d" % (i + 1))
        else:
          choices.append("")
      choices.append("Leave Shop")
      return choices
    elif current_state == "ENCHANTER":
      return ["Enchant Weapon", "Enchant Armor", "Enchant Accessory",
              "Leave Shop"]
    elif current_state == "ENCHANT_ARMOR":
      return ["Enchant Helm", "Enchant Chest", "Enchant Legs", "Never Mind"]
    elif current_state == "ALCHEMIST":
      return ["Item 1", "Item 2", "Item 3", "Leave Shop"]
    elif current_state == "TRAINING":
      return ["", "Gain XP", "Gain Stats", "Leave Shop"]
    elif current_state == "FORGE":
      choices = [""]
      if self.character.equipment[0].reforgable(self.floor):
        choices.append("Reforge Weapon")
      else:
        choices.append("")
      choices.append("Reforge Armor")
      choices.append("Leave Shop")
      return choices
    elif current_state == "FORGE_ARMOR":
      choices = []
      for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
        if self.character.equipment[slot].reforgable(self.floor):
          choices.append("Reforge %s" % name)
        else:
          choices.append("")
      choices.append("Never Mind")
      return choices
    elif current_state == "TEMPLE":
      return ["", "Blessing", "Purify Rune", "Leave Temple"]
    elif current_state == "INN":
      return ["", "Rest", "Buy Food", "Leave Inn"]
    elif current_state == "OUTSIDE":
      choices = []
      choices.append("" if self.tower_lock[self.floor] else "Ascend Tower")
      choices.append("Quest" if self.tower_quests[self.floor] else "")
      choices.append("Town")
      choices.append("Descend Tower")
      return choices
    elif current_state == "TOWER":
      return ["Explore", "Rest", "Item", "Leave Tower"]
    elif current_state == "COMBAT":
      return ["Attack", "Skill", "Item", "Escape"]
    elif current_state == "LOOT_EQUIPMENT":
      return ["", "Keep Current", "Keep New", ""]
    elif current_state == "BUY_EQUIPMENT":
      return ["", "Keep Current", "Buy", ""]
    elif current_state == "ACCEPT_QUEST":
      return ["", "Accept Quest", "Decline Quest", ""]
    elif current_state == "QUEST":
      if self.quest.complete():
        return ["Complete Quest", "", "", "Leave Quest"]
      else:
        return ["Continue Quest", "Rest", "Item", "Leave Quest"]
    else:
      return ["Error", "Error", "Error", "Error"]

  def handle_treasure(self, logs):
    while self.treasure_queue:
      item = self.treasure_queue.pop()
      if isinstance(item, int):
        logs.append("You got %d gold." % item)
        self.character.gold += item
      elif isinstance(item, Equipment):
        # TODO: Auto-equip if strictly better
        #       Auto-shard if strictly worse
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

  def apply_choice_accept_quest(self, logs, choice_text):
    if choice_text == "Accept Quest":
      self.change_state("QUEST")
      logs.append("You accept the quest.")
    elif choice_text == "Decline Quest":
      self.quest = None
      self.leave_state()
      logs.append("You decline the quest.")

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
      self.pass_time(1, logs)
      logs.append("Not implemented yet")
    elif choice_text == "Leave Quest":
      self.pass_time(1, logs)
      self.leave_state()
    elif choice_text == "Complete Quest":
      logs.append("You complete the quest.")
      logs.append("You gain %d gold." % self.quest.gp_reward)
      self.character.gold += self.quest.gp_reward
      self.character.gain_exp(self.quest.xp_reward, self.floor, logs,
                              level_adjust=False)
      self.treasure_queue = self.quest.get_treasure()
      self.leave_state()
      if self.current_state() == "OUTSIDE":
        self.tower_quests[self.floor] = None
      self.handle_treasure(logs)

  def apply_choice_tower(self, logs, choice_text):
    if choice_text == "Explore":
      self.pass_time(random.randint(1, 10), logs)
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
      self.pass_time(5, logs)
      logs.append("You rest")
      hp_gained = self.character.rest()
      logs.append("You regain %d HP" % hp_gained)
      if random.random() < .2:
        self.start_combat(logs, False)
    elif choice_text == "Item":
      self.pass_time(1, logs)
      logs.append("Not implemented yet")
    elif choice_text == "Leave Tower":
      self.pass_time(10, logs)
      self.change_state("OUTSIDE")

  def apply_death(self, logs):
    self.character.apply_death(logs)
    self.leave_state()  # COMBAT
    # TODO: This is hacky. Should probably have TOWER also be an add_state
    if self.current_state() == "QUEST":
      self.leave_state()
    self.change_state("TOWN")
    self.monster = None
    self.pass_time(random.randint(0, 3 * self.floor), logs)
    # TODO: Give quest monsters back their HP

  def apply_choice_combat(self, logs, choice_text):
    if choice_text == "Attack":
      self.pass_time(1, logs)
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
        if self.current_state() == "QUEST":
          self.quest.defeat_monster()
        self.handle_treasure(logs)
    elif choice_text == "Skill":
      self.pass_time(1, logs)
      logs.append("Not implemented yet")
    elif choice_text == "Item":
      logs.append("Not implemented yet")
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

  def apply_choice_town(self, logs, choice_text):
    if choice_text == "Leave Town":
      self.pass_time(5, logs)
      self.change_state("OUTSIDE")
      logs.append("Left town")
    else:
      self.pass_time(3, logs)
      logs.append("Went to the %s" % choice_text)
      next_state = choice_text.upper()
      self.add_state(next_state)

  def apply_choice_training(self, logs, choice_text):
    if choice_text == "Gain XP":
      cost = self.floor * ((self.times_trained[self.floor] + 1) ** 2) * 50
      if cost <= self.character.gold:
        self.pass_time(5, logs)
        self.character.train_xp(self.floor, logs)
        self.times_trained[self.floor] += 1
        self.character.gold -= cost
      else:
        logs.append("Not enough money to train XP")
    elif choice_text == "Gain Stats":
      cost = (self.character.stat_training_cost() * 
              (self.times_trained[self.floor] + 1))
      if cost <= self.character.gold:
        self.pass_time(5, logs)
        self.character.train_stats(logs)
        self.times_trained[self.floor] += 1
        self.character.gold -= cost
      else:
        logs.append("Not enough money to train stats")
    elif choice_text == "Leave Shop":
      self.leave_state()

  def apply_choice_armorer(self, logs, choice_text):
    if choice_text.startswith("Armor #"):
      choice = int(choice_text[-1])
      self.add_state("BUY_EQUIPMENT")
      self.piece_to_buy = self.armor_shops[self.floor][choice - 1]
      self.shop_choice = choice - 1
      logs.append("You consider %s..." % choice_text)
    elif choice_text == "Leave Shop":
      self.leave_state()

  def apply_choice_weaponsmith(self, logs, choice_text):
    if choice_text.startswith("Weapon #"):
      choice = int(choice_text[-1])
      self.add_state("BUY_EQUIPMENT")
      self.piece_to_buy = self.weapon_shops[self.floor][choice - 1]
      self.shop_choice = choice - 1
      logs.append("You consider %s..." % choice_text)
    elif choice_text == "Leave Shop":
      self.leave_state()

  def apply_choice_buy_equipment(self, logs, choice_text):
    self.leave_state()
    if choice_text == "Keep Current":
      pass
    elif choice_text == "Buy":
      if self.current_state() == "ARMORER":
        shop = self.armor_shops[self.floor]
      elif self.current_state() == "WEAPONSMITH":
        shop = self.weapon_shops[self.floor]
      else:
        assert False
      equipment = self.piece_to_buy
      value = equipment.get_value()
      if self.character.gold >= value:
        self.pass_time(1, logs)
        self.character.gold -= value
        recycle = self.character.equip(equipment)
        shop[self.shop_choice] = None
        self.shop_choice = None
        self.piece_to_buy = None
        logs.append("Purchased %s for %d gold." % (str(equipment), value))
        logs.append("Recycled %s" % recycle)
        materials = recycle.get_recycled_materials()
        self.character.gain_materials(materials)
        logs.append("Received %s" % Equipment.materials_string(materials))
      else:
        logs.append("You do not have enough money.")

  def buy_equipment_choice_text(self):
    equip = self.piece_to_buy
    slot = equip.slot
    return self.equipment_comparison_text(self.character.equipment[slot],
                                          equip)

  def apply_reforge(self, item, logs):
    cost = item.reforge_cost_gold(self.floor)
    mat_cost = item.reforge_cost_materials(self.floor)
    if (cost <= self.character.gold and
        mat_cost <= self.character.materials[item.rarity]):
      self.pass_time(3, logs)
      self.character.gold -= cost
      self.character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      improvement = item.reforge(self.floor)
      logs.append("Your %s was reforged (%s)" % (old_item_string, improvement))
    else:
      logs.append("You do not have sufficient payment")

  def apply_choice_forge_armor(self, logs, choice_text):
    item = None
    if choice_text == "Reforge Helm":
      item = self.character.equipment[1]
    elif choice_text == "Reforge Chest":
      item = self.character.equipment[2]
    elif choice_text == "Reforge Legs":
      item = self.character.equipment[3]
    elif choice_text == "Never Mind":
      self.change_state("FORGE")
    if item:
      self.apply_reforge(item, logs)

  def apply_choice_forge(self, logs, choice_text):
    item = None
    if choice_text == "Reforge Weapon":
      item = self.character.equipment[0]
    elif choice_text == "Reforge Armor":
      self.change_state("FORGE_ARMOR")
    elif choice_text == "Leave Shop":
      self.leave_state()
    if item:
      self.apply_reforge(item, logs)

  def apply_enchantment(self, item, logs):
    cost = item.enchant_cost_gold()
    mat_cost = item.enchant_cost_materials()
    if (cost <= self.character.gold and
        mat_cost <= self.character.materials[item.rarity]):
      self.pass_time(3, logs)
      self.character.gold -= cost
      self.character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      enchantment = item.enchant()
      logs.append("Your %s was enchanted (%s)" % (old_item_string, enchantment))
    else:
      logs.append("You do not have sufficient payment")

  def apply_choice_enchanter(self, logs, choice_text):
    item = None
    if choice_text == "Enchant Weapon":
      item = self.character.equipment[0]
    elif choice_text == "Enchant Armor":
      self.change_state("ENCHANT_ARMOR")
    elif choice_text == "Enchant Accessory":
      item = self.character.equipment[4]
    elif choice_text == "Leave Shop":
      self.leave_state()
    if item:
      self.apply_enchantment(item, logs)

  def apply_choice_enchant_armor(self, logs, choice_text):
    item = None
    if choice_text == "Enchant Helm":
      item = self.character.equipment[1]
    elif choice_text == "Enchant Chest":
      item = self.character.equipment[2]
    elif choice_text == "Enchant Legs":
      item = self.character.equipment[3]
    elif choice_text == "Never Mind":
      self.change_state("ENCHANTER")
    if item:
      self.apply_enchantment(item, logs)

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

  # TODO: Implement: ALCHEMIST, TRAINING, FORGE, TEMPLE, INN

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

  @staticmethod
  def equipment_comparison_text(current, new):
    pieces = []
    pieces.append("Current Equipment:\n")
    pieces.append(str(current))
    pieces.append("\nNew Equipment:\n")
    pieces.append(str(new))
    pieces.append("\nComparison:\n")
    pieces.append(Equipment.comparison_text(current, new))
    # TODO: Show difference between two pieces of equipment
    return "".join(pieces)


  def loot_choice_text(self):
    slot = self.equipment_choice.slot
    return self.equipment_comparison_text(self.character.equipment[slot],
                                          self.equipment_choice)

  @staticmethod
  def armor_shop_text(shop, label):
    pieces = []
    for i, item in enumerate(shop):
      if item is not None:
        pieces.append("%s #%d  (%d gold)" % (label, i + 1, item.get_value()))
        pieces.append(str(item))
    if not pieces:
      pieces.append("You cleaned 'em out!")
    return "\n".join(pieces)

  @staticmethod
  def enchanter_shop_text(character):
    pieces = []
    weapon = character.equipment[0]
    pieces.append("Enchant Weapon: %d gold and %d %s materials" %
                  (weapon.enchant_cost_gold(), weapon.enchant_cost_materials(),
                   RARITY[weapon.rarity]))
    pieces.append("Enchant Armor: [submenu]")
    acc = character.equipment[4]
    pieces.append("Enchant Accessory: %d gold and %d %s materials" %
                  (acc.enchant_cost_gold(), acc.enchant_cost_materials(),
                   RARITY[acc.rarity]))
    return "\n".join(pieces)

  @staticmethod
  def enchanter_shop_armor_text(character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      cost = item.enchant_cost_gold()
      material_cost = item.enchant_cost_materials()
      pieces.append("Enchant %s: %d gold and %d %s materials" %
                    (name, cost, material_cost, RARITY[item.rarity]))
    return "\n".join(pieces)

  @staticmethod
  def forge_text(level, character):
    pieces = []
    weapon = character.equipment[0]
    if weapon.reforgable(level):
      pieces.append("Reforge Weapon: %d gold and %d %s materials" %
                    (weapon.reforge_cost_gold(level),
                     weapon.reforge_cost_materials(level),
                     RARITY[weapon.rarity]))
    pieces.append("Reforge Armor: [submenu]")
    return "\n".join(pieces)

  @staticmethod
  def forge_armor_text(level, character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      if item.reforgable(level):
        cost = item.reforge_cost_gold(level)
        material_cost = item.reforge_cost_materials(level)
        pieces.append("Reforge %s: %d gold and %d %s materials" %
                      (name, cost, material_cost, RARITY[item.rarity]))
    return "\n".join(pieces)

  # TODO: Messy that others are static and this is not?
  def training_shop_text(self):
    pieces = []
    floor = self.floor   # Next lines are long
    pieces.append("Gain XP: %d gold (%d xp)" % 
                  (floor * ((self.times_trained[floor] + 1) ** 2) * 50,
                   floor * 25))
    pieces.append("Gain Stats: %d gold (+1 random stat)" %
                  (self.character.stat_training_cost() *
                  (self.times_trained[floor] + 1)))
    return "\n".join(pieces)

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
      return self.loot_choice_text()
    elif current_state == "BUY_EQUIPMENT":
      return self.buy_equipment_choice_text()
    elif current_state == "ACCEPT_QUEST" or current_state == "QUEST":
      return str(self.tower_quests[self.floor])
    elif current_state == "ARMORER":
      return self.armor_shop_text(self.armor_shops[self.floor], "Armor")
    elif current_state == "WEAPONSMITH":
      return self.armor_shop_text(self.weapon_shops[self.floor], "Weapon")
    elif current_state == "ENCHANTER":
      return self.enchanter_shop_text(self.character)
    elif current_state == "ENCHANT_ARMOR":
      return self.enchanter_shop_armor_text(self.character)
    elif current_state == "FORGE":
      return self.forge_text(self.floor, self.character)
    elif current_state == "FORGE_ARMOR":
      return self.forge_armor_text(self.floor, self.character)
    elif current_state == "TRAINING":
      return self.training_shop_text()
    else:
      return "Error, no text for state %s" % current_state
