from equipment import Equipment, RARITY
from effect import WellRested, Blessed

class Room(object):
  NO_CHANGE = 0
  LEAVE_ROOM = 1

  def __init__(self, level):
    self.level = level

  def refresh(self):
    pass

  @classmethod
  def get_name(cls):
    return "Unnamed Room"

  def get_buttons(self, character):
    return ["Not Implemented"] * 4

  def get_text(self, character):
    return "Not Implemented"

  def apply_choice(self, choice_text, logs, character):
    return (0, Room.LEAVE_ROOM)

  def enter_shop(self):
    pass

class TrainingRoom(Room):
  def __init__(self, level):
    super(TrainingRoom, self).__init__(level)
    self.level = level
    self.train_count = 0

  @classmethod
  def get_name(cls):
    return "Trainer"

  def get_buttons(self, character):
    return ["", "Gain XP", "Gain Stats", "Leave Shop"]

  def stat_training_cost(self, character):
    return sum(character.stats.values()) * (self.train_count + 1)

  def xp_training_cost(self):
    return self.level * ((self.train_count + 1) ** 2) * 50

  def get_text(self, character):
    pieces = []
    pieces.append("Gain XP: %d gold (%d xp)" %
                  (self.xp_training_cost(), self.level * 25))
    pieces.append("Gain Stats: %d gold (+1 random stat)" %
                  self.stat_training_cost(character))
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Gain XP":
      cost = self.xp_training_cost()
      if cost <= character.gold:
        character.train_xp(self.level, logs)
        self.train_count += 1
        character.gold -= cost
        return (5, Room.NO_CHANGE)
      else:
        logs.append("Not enough money to train XP")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Gain Stats":
      cost = self.stat_training_cost(character)
      if cost <= character.gold:
        character.train_stats(logs)
        self.train_count += 1
        character.gold -= cost
        return (5, Room.NO_CHANGE)
      else:
        logs.append("Not enough money to train stats")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    assert False

class Enchanter(Room):
  def __init__(self, level):
    super(Enchanter, self).__init__(level)
    self.level = level
    self.enchanting_armor = False

  @classmethod
  def get_name(cls):
    return "Enchanter"

  def get_buttons(self, character):
    if self.enchanting_armor:
      return ["Enchant Helm", "Enchant Chest", "Enchant Legs", "Never Mind"]
    else:
      return ["Enchant Weapon", "Enchant Armor", "Enchant Accessory",
              "Leave Shop"]

  # TODO: If we make an Enchanter shop class, these should probably move there.
  @classmethod
  def enchant_cost_gold(cls, item):
    return item.item_level * 25 * ((item.enchant_count + 1) ** 2)

  @classmethod
  def enchant_cost_materials(cls, item):
    return item.item_level * (item.enchant_count + 1) / 2

  def armor_text(self, character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      cost = self.enchant_cost_gold(item)
      material_cost = self.enchant_cost_materials(item)
      pieces.append("Enchant %s: %d gold and %d %s materials" %
                    (name, cost, material_cost, RARITY[item.rarity]))
    return "\n".join(pieces)

  def normal_text(self, character):
    pieces = []
    weapon = character.equipment[0]
    pieces.append("Enchant Weapon: %d gold and %d %s materials" %
                  (self.enchant_cost_gold(weapon),
                   self.enchant_cost_materials(weapon),
                   RARITY[weapon.rarity]))
    pieces.append("Enchant Armor: [submenu]")
    acc = character.equipment[4]
    pieces.append("Enchant Accessory: %d gold and %d %s materials" %
                  (self.enchant_cost_gold(acc),
                   self.enchant_cost_materials(acc),
                   RARITY[acc.rarity]))
    return "\n".join(pieces)

  def get_text(self, character):
    if self.enchanting_armor:
      return self.armor_text(character)
    else:
      return self.normal_text(character)

  def apply_enchantment(self, item, logs, character):
    cost = self.enchant_cost_gold(item)
    mat_cost = self.enchant_cost_materials(item)
    if (cost <= character.gold and
        mat_cost <= character.materials[item.rarity]):
      character.gold -= cost
      character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      enchantment = item.enchant()
      logs.append("Your %s was enchanted (%s)" % (old_item_string, enchantment))
      return (3, Room.NO_CHANGE)
    else:
      logs.append("You do not have sufficient payment")
      return (0, Room.NO_CHANGE)

  def apply_choice_enchanter(self, choice_text, logs, character):
    item = None
    if choice_text == "Enchant Weapon":
      item = character.equipment[0]
    elif choice_text == "Enchant Armor":
      self.enchanting_armor = True
      return (0, Room.NO_CHANGE)
    elif choice_text == "Enchant Accessory":
      item = character.equipment[4]
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    if item:
      return self.apply_enchantment(item, logs, character)
    assert False

  def apply_choice_enchant_armor(self, choice_text, logs, character):
    item = None
    if choice_text == "Enchant Helm":
      item = character.equipment[1]
    elif choice_text == "Enchant Chest":
      item = character.equipment[2]
    elif choice_text == "Enchant Legs":
      item = character.equipment[3]
    elif choice_text == "Never Mind":
      self.enchanting_armor = False
      return (0, Room.NO_CHANGE)
    if item:
      return self.apply_enchantment(item, logs, character)
    assert False

  def apply_choice(self, choice_text, logs, character):
    if self.enchanting_armor:
      return self.apply_choice_enchant_armor(choice_text, logs, character)
    else:
      return self.apply_choice_enchanter(choice_text, logs, character)

  def enter_shop(self):
    self.enchanting_armor = False

class Forge(Room):
  def __init__(self, level):
    super(Forge, self).__init__(level)
    self.level = level
    self.forging_armor = False

  @classmethod
  def get_name(cls):
    return "Forge"

  def get_buttons(self, character):
    choices = []
    if self.forging_armor:
      for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
        if self.reforgable(character.equipment[slot]):
          choices.append("Reforge %s" % name)
        else:
          choices.append("")
      choices.append("Never Mind")
    else:
      choices.append("")
      if self.reforgable(character.equipment[0]):
        choices.append("Reforge Weapon")
      else:
        choices.append("")
      choices.append("Reforge Armor")
      choices.append("Leave Shop")
    return choices

  def reforge_cost_gold(self, item):
    level = item.item_level
    return (self.level - level) * (25 * ((item.reforge_count + 1) ** 2))

  def reforge_cost_materials(self, item):
    return (self.level - item.item_level) * (item.reforge_count + 1)

  def reforgable(self, item):
    return item.item_level < self.level

  def forge_text(self, character):
    pieces = []
    weapon = character.equipment[0]
    if self.reforgable(weapon):
      pieces.append("Reforge Weapon: %d gold and %d %s materials" %
                    (self.reforge_cost_gold(weapon),
                     self.reforge_cost_materials(weapon),
                     RARITY[weapon.rarity]))
    else:
      pieces.append("Weapon cannot currently be reforged")
    pieces.append("Reforge Armor: [submenu]")
    return "\n".join(pieces)

  def forge_armor_text(self, character):
    pieces = []
    for name, slot in (("Helm", 1), ("Chest", 2), ("Legs", 3)):
      item = character.equipment[slot]
      if self.reforgable(item):
        cost = self.reforge_cost_gold(item)
        material_cost = self.reforge_cost_materials(item)
        pieces.append("Reforge %s: %d gold and %d %s materials" %
                      (name, cost, material_cost, RARITY[item.rarity]))
      else:
        pieces.append("%s cannot currently be reforged" % name)
    return "\n".join(pieces)

  def get_text(self, character):
    if self.forging_armor:
      return self.forge_armor_text(character)
    else:
      return self.forge_text(character)

  def apply_reforge(self, item, character, logs):
    cost = self.reforge_cost_gold(item)
    mat_cost = self.reforge_cost_materials(item)
    if (cost <= character.gold and
        mat_cost <= character.materials[item.rarity]):
      character.gold -= cost
      character.materials[item.rarity] -= mat_cost
      old_item_string = str(item)
      improvement = item.reforge(self.level)
      logs.append("Your %s was reforged (%s)" % (old_item_string, improvement))
      return (3, Room.NO_CHANGE)
    else:
      logs.append("You do not have sufficient payment")
      return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    item = None
    if choice_text == "Reforge Weapon":
      item = character.equipment[0]
    elif choice_text == "Reforge Helm":
      item = character.equipment[1]
    elif choice_text == "Reforge Chest":
      item = character.equipment[2]
    elif choice_text == "Reforge Legs":
      item = character.equipment[3]
    elif choice_text == "Reforge Armor":
      self.forging_armor = True
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)
    elif choice_text == "Never Mind":
      self.forging_armor = False
      return (0, Room.NO_CHANGE)
    if item:
      return self.apply_reforge(item, character, logs)
    assert False

  def enter_shop(self):
    self.forging_armor = False

class ArmorShop(Room):
  def __init__(self, level):
    super(ArmorShop, self).__init__(level)
    self.level = level
    # One for each slot, 1-3
    self.inventory = [Equipment.get_new_armor(level, slot)
                      for slot in range(1, 4)]
    self.buying = False
    self.shop_choice = None

  def refresh(self):
    # TODO: Might make the armor get stronger periodically. The idea being
    #       this pushes towards eventually being able to just overpower the
    #       tower.
    self.inventory = [Equipment.get_new_armor(self.level, slot)
                      for slot in range(1, 4)]

  @classmethod
  def get_name(cls):
    return "Armorer"

  def get_buttons(self, character):
    if self.buying:
      return ["", "Keep Current", "Buy", ""]
    else:
      choices = []
      for i in range(len(self.inventory)):
        if self.inventory[i]:
          choices.append("Armor #%d" % (i + 1))
        else:
          choices.append("")
      choices.append("Leave Shop")
      return choices

  def get_text(self, character):
    if self.buying:
      equip = self.inventory[self.shop_choice]
      slot = equip.slot
      return Equipment.equipment_comparison_text(character.equipment[slot],
                                                 equip)
    else:
      pieces = []
      for i, item in enumerate(self.inventory):
        if item is not None:
          pieces.append("Armor #%d  (%d gold)" % (i + 1, item.get_value()))
          pieces.append(str(item))
      if not pieces:
        pieces.append("You cleaned 'em out!")
      return "\n".join(pieces)

  def apply_choice_buy_equipment(self, choice_text, logs, character):
    if choice_text == "Keep Current":
      self.buying = False
      return (0, Room.NO_CHANGE)
    elif choice_text == "Buy":
      equipment = self.inventory[self.shop_choice]
      value = equipment.get_value()
      if character.gold >= value:
        character.gold -= value
        recycle = character.equip(equipment)
        self.inventory[self.shop_choice] = None
        self.shop_choice = None
        self.buying = False
        logs.append("Purchased %s for %d gold." % (str(equipment), value))
        logs.append("Recycled %s" % recycle)
        materials = recycle.get_recycled_materials()
        character.gain_materials(materials)
        logs.append("Received %s" % Equipment.materials_string(materials))
        return (1, Room.NO_CHANGE)
      else:
        logs.append("You do not have enough money.")
        self.buying = False
        self.shop_choice = None
        return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    if self.buying:
      return self.apply_choice_buy_equipment(choice_text, logs, character)
    elif choice_text.startswith("Armor #"):
      choice = int(choice_text[-1])
      self.shop_choice = choice - 1
      self.buying = True
      logs.append("You consider %s..." % choice_text)
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self):
    self.buying = False
    self.shop_choice = None

# TODO: There is a lot of duplication between this and ArmorShop. Clean it up.
#       Like really, whole functions
class WeaponShop(Room):
  def __init__(self, level):
    super(WeaponShop, self).__init__(level)
    self.level = level
    # One for each slot, 1-3
    self.inventory = [Equipment.get_new_armor(level, 0) for _ in range(3)]
    self.buying = False
    self.shop_choice = None

  def refresh(self):
    # TODO: Might make the armor get stronger periodically. The idea being
    #       this pushes towards eventually being able to just overpower the
    #       tower.
    self.inventory = [Equipment.get_new_armor(self.level, 0) for _ in range(3)]

  @classmethod
  def get_name(cls):
    return "Weaponsmith"

  def get_buttons(self, character):
    if self.buying:
      return ["", "Keep Current", "Buy", ""]
    else:
      choices = []
      for i in range(len(self.inventory)):
        if self.inventory[i]:
          choices.append("Weapon #%d" % (i + 1))
        else:
          choices.append("")
      choices.append("Leave Shop")
      return choices

  def get_text(self, character):
    if self.buying:
      equip = self.inventory[self.shop_choice]
      slot = equip.slot
      return Equipment.equipment_comparison_text(character.equipment[slot],
                                                 equip)
    else:
      pieces = []
      for i, item in enumerate(self.inventory):
        if item is not None:
          pieces.append("Weapon #%d  (%d gold)" % (i + 1, item.get_value()))
          pieces.append(str(item))
      if not pieces:
        pieces.append("You cleaned 'em out!")
      return "\n".join(pieces)

  def apply_choice_buy_equipment(self, choice_text, logs, character):
    if choice_text == "Keep Current":
      self.buying = False
      return (0, Room.NO_CHANGE)
    elif choice_text == "Buy":
      equipment = self.inventory[self.shop_choice]
      value = equipment.get_value()
      if character.gold >= value:
        character.gold -= value
        recycle = character.equip(equipment)
        self.inventory[self.shop_choice] = None
        self.shop_choice = None
        self.buying = False
        logs.append("Purchased %s for %d gold." % (str(equipment), value))
        logs.append("Recycled %s" % recycle)
        materials = recycle.get_recycled_materials()
        character.gain_materials(materials)
        logs.append("Received %s" % Equipment.materials_string(materials))
        return (1, Room.NO_CHANGE)
      else:
        logs.append("You do not have enough money.")
        self.buying = False
        self.shop_choice = None
        return (0, Room.NO_CHANGE)

  def apply_choice(self, choice_text, logs, character):
    if self.buying:
      return self.apply_choice_buy_equipment(choice_text, logs, character)
    elif choice_text.startswith("Weapon #"):
      choice = int(choice_text[-1])
      self.shop_choice = choice - 1
      self.buying = True
      logs.append("You consider %s..." % choice_text)
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Shop":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self):
    self.buying = False
    self.shop_choice = None

class Alchemist(Room):
  @classmethod
  def get_name(cls):
    return "Alchemist"

class Inn(Room):
  @classmethod
  def get_name(cls):
    return "Inn"

  def get_buttons(self, character):
    return ["", "Rest", "Buy Food", "Leave Inn"]

  def get_text(self, character):
    pieces = []
    pieces.append("Rest: (%dg + 30 time) Well Rested buff" % (self.level * 10))
    pieces.append("Buy Food: Not implemented yet")
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Rest":
      cost = 10 * self.level
      if cost <= character.gold:
        character.gold -= cost
        character.add_buff(WellRested(510))
        logs.append("You became well rested.")
        return (30, Room.NO_CHANGE)
      else:
        logs.append("You do not have sufficient money")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Buy Food":
      logs.append("Not implemented yet")
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Inn":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self):
    pass

class Temple(Room):
  @classmethod
  def get_name(cls):
    return "Temple"

  def refresh(self):
    pass

  def get_buttons(self, character):
    return ["", "Blessing", "Purify Rune", "Leave Temple"]

  def get_text(self, character):
    pieces = []
    pieces.append("Blessing: (%dg) Blessed buff" % (self.level * 50))
    pieces.append("Purify Rune: Not implemented yet")
    return "\n".join(pieces)

  def apply_choice(self, choice_text, logs, character):
    if choice_text == "Blessing":
      cost = 50 * self.level
      if cost <= character.gold:
        character.gold -= cost
        character.add_buff(Blessed(241))
        logs.append("You were blessed")
        return (1, Room.NO_CHANGE)
      else:
        logs.append("You do not have sufficient money")
        return (0, Room.NO_CHANGE)
    elif choice_text == "Purify Rune":
      logs.append("Not implemented yet")
      return (0, Room.NO_CHANGE)
    elif choice_text == "Leave Temple":
      return (0, Room.LEAVE_ROOM)

  def enter_shop(self):
    pass
"""
    elif current_state == "ALCHEMIST":
      return ["Item 1", "Item 2", "Item 3", "Leave Shop"]
"""