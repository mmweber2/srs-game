import random
import collections

# TODO: Should probably move these to a different place
STATS = ["Strength", "Stamina", "Speed", "Intellect"]
DEFENSES = ["Defense", "Magic Defense"]
SLOTS = ["Helm", "Chest", "Legs", "Accessory"]
RARITY = ["Common", "Uncommon", "Rare", "Epic", "Legendary"]
ABBREVIATIONS = {"Defense": "Def",
                 "Magic Defense": "MDef"}

class Equipment(object):
  def __init__(self, item_level, attributes, slot, rarity):
    # int, power level of the item
    self.item_level = item_level
    # dictionary from attribute -> value
    self.attributes = attributes
    # Uncommon / Rare / Epic / Legendary
    self.rarity = rarity
    # 0-3, Helm, Chest, Legs, Accessory
    self.slot = slot

  def get_stat_value(self, stat):
    return self.attributes[stat]

  @classmethod
  def make_stat_value(cls, item_level, rarity):
    return random.randint(max(1, item_level / 2), item_level)

  @classmethod
  def get_new_armor(cls, item_level, slot=None, require=None, rarity=1):
    attributes = collections.defaultdict(int)
    if slot is None:
      slot = random.randint(0, 3)
    slots = 1 + rarity
    if require:
      attributes[require] = cls.make_stat_value(item_level, rarity)
      slots -= 1
    for i in range(slots):
      attributes[random.choice(STATS)] += cls.make_stat_value(item_level, rarity)
    for d in DEFENSES:
      attributes[d] = cls.make_stat_value(item_level, rarity)
    return Equipment(item_level, attributes, slot, rarity)

  def __str__(self):
    pieces = []
    pieces.append(SLOTS[self.slot])
    pieces.append(":")
    pieces.append("(%d %s)" % (self.item_level, RARITY[self.rarity][0]) )
    defense_pieces = []
    stat_pieces = []
    for attribute in self.attributes:
      if attribute in STATS:
        if self.attributes[attribute] > 0:
          value = "+" + str(self.attributes[attribute])
          stat_pieces.append("%s %s" % (value, attribute))
      elif attribute in DEFENSES:
        defense_pieces.append("%d %s" % (self.attributes[attribute],
                                         ABBREVIATIONS[attribute]))
      else:
        assert False
    pieces.append("(%s)" % "/".join(defense_pieces))
    pieces.append(" ".join(stat_pieces))
    return " ".join(pieces)

