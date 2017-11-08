import random
from equipment import Equipment

# TODO: Should Monster and Character subclass from something?
NORMAL_CHANCES = [0.0, 0.2, 0.04, 0.008, 0.00016]
BOSS_CHANCES = [0.0, 0.4, 0.16, 0.064, 0.0256]

class Monster(object):
  def __init__(self, level, boss):
    # TODO: Should level vary somewhat?
    self.stats = {}
    self.level = level
    self.boss = boss
    # If you modify these, make sure to modify the XP calc
    # TODO: Make a common table both rely on, idiot
    for stat in ("Strength", "Defense", "Speed", "Intellect", "Magic Defense"):
      self.stats[stat] = self.roll_stat(level, 10, 1)
    for stat in ("Stamina",):
      self.stats[stat] = self.roll_stat(level, 8, 0)
    if boss:
      for stat in self.stats:
        self.stats[stat] = self.stats[stat] * 1.25
      self.stats["Stamina"] *= 3   # Effectively x3.75
    for stat in self.stats:
      # 75-125% change
      self.stats[stat] *= (random.random() * 0.5) + 0.75
      self.stats[stat] = int(self.stats[stat])
      self.stats[stat] = max(1, self.stats[stat])
    self.max_hp = self.stats["Stamina"] * 5
    self.current_hp = self.max_hp
    # TODO: Name generation
    if boss:
      self.name = "Boss Monster, Level %d" % level
    else:
      self.name = "Generic Monster, Level %d" % level

  def hp_string(self):
    percent = int(100 * self.current_hp / self.max_hp)
    return "%d%%" % percent

  def __str__(self):
    debug = True
    pieces = []
    pieces.append("Name: %s\n" % self.name)
    pieces.append("HP: %s\n" % self.hp_string())
    pieces.append("Buffs: None\n")
    pieces.append("Debuffs: None\n")
    if debug:
      pieces.append("***DEBUG***\n")
      pieces.append("stats: %r\n" % self.stats)
      pieces.append("HP: %d / %d\n" % (self.current_hp, self.max_hp))
      pieces.append("XP value: %d\n" % self.calculate_exp())
    return "".join(pieces)

  def calculate_exp(self):
    effective_level = 0
    for stat in ("Strength", "Defense", "Speed", "Intellect", "Magic Defense"):
      effective_level += (self.stats[stat] / 6.5)
    for stat in ("Stamina",):
      effective_level += (self.stats[stat] / 4.5)
    effective_level /= 6
    return int(10 * effective_level)

  def get_treasure(self):
    # list of treasure from this monster.
    # May be int (for gold), Equipment objects
    # TODO: Item objects, runes, ...?
    treasure = []
    boss_factor = 4 if self.boss else 1
    min_gold = 5 * self.level * boss_factor
    max_gold = 15 * self.level * boss_factor
    treasure.append(random.randint(min_gold, max_gold))
    assert len(NORMAL_CHANCES) == len(BOSS_CHANCES)
    chances = BOSS_CHANCES if self.boss else NORMAL_CHANCES
    for rarity in range(1, len(chances)):
      while random.random() < chances[rarity]:
        treasure.append(Equipment.get_new_armor(self.level, rarity=rarity))
    return treasure

  def get_effective_stat(self, stat):
    # TODO: Buffs and such, probably
    return self.stats[stat]

  def get_damage(self):
    low = 10 + (5 * self.level)
    high = 20 + (7 * self.level)
    return random.randint(low, high)

  def get_damage_type(self):
    if (self.get_effective_stat("Intellect") >
        self.get_effective_stat("Strength")):
      return "Magic"
    else:
      return "Physical"

  @classmethod
  def roll_stat(cls, level, die, modifier):
    # TODO: May be too slow, might want to use a different method
    return sum(random.randint(1, die) + modifier for _ in xrange(level))

  def get_action(self, character):
    # Monster AI
    # TODO: Something more sophisticated, especially for special monsters
    return ("Attack", None)
