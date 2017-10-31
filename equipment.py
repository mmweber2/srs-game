import random
import collections

# TODO: Should probably move these to a different place
STATS = ["Strength", "Stamina", "Speed", "Intellect"]
DEFENSES = ["Defense", "Magic Defense"]

class Equipment(object):
  def __init__(self, item_level, attributes, slot, rarity):
    self.item_level = item_level
    self.attributes = attributes
    # Uncommon / Rare / Epic / Legendary
    self.rarity = rarity
    self.slot = slot

  @classmethod
  def get_stat_value(cls, item_level, rarity):
    return random.randint(max(1, item_level / 2), item_level)

  @classmethod
  def get_new_armor(cls, item_level, slot=None, require=None, rarity=1):
    attributes = collections.defaultdict(int)
    slots = 1 + rarity
    if require:
      attributes[require] = cls.get_stat_value(item_level, rarity)
      slots -= 1
    for i in range(slots):
      attributes[random.choice(STATS)] += cls.get_stat_value(item_level, rarity)
    for d in DEFENSES:
      attributes[d] = cls.get_stat_value(item_level, rarity)
