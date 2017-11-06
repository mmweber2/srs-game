import random
import collections

# TODO: Should probably move these to a different place
STATS = ["Strength", "Stamina", "Speed", "Intellect"]
DEFENSES = ["Defense", "Magic Defense"]
SLOTS = ["Weapon", "Helm", "Chest", "Legs", "Accessory"]
RARITY = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
RARITY_COLORS = ["`160,160,160`", "`0,160,0`", "`0,0,160`", "`160,0,160`",
                 "`255,140,0`"]
ABBREVIATIONS = {"Defense": "Def",
                 "Magic Defense": "MDef"}
WEAPON_STATS = ["Low", "High", "Type"]

class Equipment(object):
  def __init__(self, item_level, attributes, slot, rarity):
    # int, power level of the item
    self.item_level = item_level
    # dictionary from attribute -> value
    self.attributes = attributes
    # Common / Uncommon / Rare / Epic / Legendary
    self.rarity = rarity
    # 0-4, Weapon, Helm, Chest, Legs, Accessory
    self.slot = slot
    # TODO: Implement damage range for weapons
    #       Figure out what is reasonable against growing monster stamina
    #       2-3 hits against a normal monster is probably about right

  @classmethod
  def comparison_text(cls, old, new):
    assert old.slot == new.slot
    pieces = []
    attributes = set().union(old.attributes, new.attributes)
    for a in attributes:
      if a not in STATS and a not in DEFENSES:
        continue
      old_attribute = old.attributes[a] if a in old.attributes else 0
      new_attribute = new.attributes[a] if a in new.attributes else 0
      difference = new_attribute - old_attribute
      if difference != 0:
        color_string = "`255,0,0`" if difference < 0 else "`0,160,0`"
        pieces.append("%s%+d %s" % (color_string, difference, a))
    if old.slot == 0:
      # TODO: Might be worth having an "Average Damage" attribute
      old_average = (old.attributes["Low"] + old.attributes["High"]) / 2.0
      new_average = (new.attributes["Low"] + new.attributes["High"]) / 2.0
      difference = new_average - old_average
      color = "`255,0,0`" if difference < 0 else "`0,160,0`"
      pieces.append("%s%+0.1f average damage" % (color, difference))
      if old.attributes["Type"] != new.attributes["Type"]:
        pieces.append("`0,0,0`Weapon type change")
    return "\n".join(pieces)

  def get_stat_value(self, stat):
    return self.attributes[stat]

  @classmethod
  def make_stat_value(cls, item_level, rarity):
    # TODO: Gaussian stuff?
    min_stat = max(1, item_level / 2)
    max_stat = min_stat + item_level + rarity
    return random.randint(min_stat, max_stat)

  def get_damage(self):
    return random.randint(self.attributes["Low"], self.attributes["High"])

  def get_damage_type(self):
    return self.attributes["Type"]

  def get_recycled_materials(self):
    materials = [0] * len(RARITY)
    for _ in xrange(self.item_level):
      # Will slightly push range down due to rounding
      rarity = int(self.rarity + random.gauss(0, 1))
      if rarity < 0:
        continue
      if rarity >= len(RARITY):
        rarity = len(RARITY) - 1
      materials[rarity] += 1
    return materials

  @classmethod
  def materials_string(cls, materials):
    pieces = []
    for i in xrange(len(materials)):
      if materials[i] > 0:
        pieces.append("%d %s materials" % (materials[i], RARITY[i]))
    if pieces:
      return ", ".join(pieces)
    else:
      return "no materials"

  def get_value(self):
    value = self.item_level * 25
    for attribute in STATS + DEFENSES:
      value += self.attributes[attribute] ** 2
    value *= max(1, self.rarity - 1)
    if self.slot == 0:  # Weapon
      average_damage = (self.attributes["Low"] + self.attributes["High"]) / 2
      value += average_damage
    return value

  @classmethod
  def get_new_armor(cls, item_level, slot=None, require=None, rarity=1):
    attributes = collections.defaultdict(int)
    if slot is None:
      slot = random.randint(0, len(SLOTS) - 1)
    slots = 1 + rarity
    if require:
      attributes[require] = cls.make_stat_value(item_level, rarity)
      slots -= 1
    for _ in range(slots):
      attributes[random.choice(STATS)] += cls.make_stat_value(item_level,
                                                              rarity)
    for defense in DEFENSES:
      attributes[defense] = cls.make_stat_value(item_level, rarity)
    if SLOTS[slot] == "Weapon":
      rarity_factor = 1.0 + (.1 * rarity)
      low = int((10 + 5 * item_level) * random.gauss(1, .2) * rarity_factor)
      high = int((20 + 7 * item_level) * random.gauss(1, .2) * rarity_factor)
      if low > high:
        low, high = high, low
      if low < 1:
        low = 1
      attributes["Low"] = low
      attributes["High"] = high
      if require == "Strength":
        attributes["Type"] = "Physical"
      elif require == "Intellect":
        attributes["Type"] = "Magic"
      else:
        attributes["Type"] = random.choice(("Magic", "Physical"))
    return Equipment(item_level, attributes, slot, rarity)

  def __str__(self):
    pieces = []
    pieces.append(SLOTS[self.slot])
    pieces.append(": ")
    pieces.append(RARITY_COLORS[self.rarity])
    pieces.append("(%d %s) " % (self.item_level, RARITY[self.rarity][0]))
    if SLOTS[self.slot] == "Weapon":
      pieces.append("(%s %d-%d) " % (self.attributes["Type"],
                                    self.attributes["Low"],
                                    self.attributes["High"]))
    defense_pieces = []
    stat_pieces = []
    for attribute in self.attributes:
      if attribute in STATS:
        if self.attributes[attribute] > 0:
          stat_pieces.append("%+d %s " % (self.attributes[attribute],attribute))
      elif attribute in DEFENSES:
        defense_pieces.append("%d %s" % (self.attributes[attribute],
                                         ABBREVIATIONS[attribute]))
      else:
        assert attribute in WEAPON_STATS
    pieces.append("(%s) " % " / ".join(defense_pieces))
    pieces.append("".join(stat_pieces))
    pieces.append("`0,0,0`")
    return "".join(pieces)
