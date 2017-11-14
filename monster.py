import collections
import random
from equipment import Equipment
from effect import Debuff

# TODO: Should Monster and Character subclass from something?
NORMAL_CHANCES = [0.0, 0.2, 0.04, 0.008, 0.00016]
BOSS_CHANCES = [0.0, 0.4, 0.16, 0.064, 0.0256]
RUNE_CHANCE = 0.002
BOSS_RUNE_CHANCE = 0.01
#RUNE_CHANCE = 0.5
#BOSS_RUNE_CHANCE = 0.5

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
    # DEBUG
    self.max_hp = 10000
    self.current_hp = self.max_hp
    # TODO: Name generation
    if boss:
      self.name = "Boss Monster, Level %d" % level
    else:
      self.name = "Generic Monster, Level %d" % level
    # TODO: Should monsters get traits? If so, we might want to break them
    #       out from "character"
    self.traits = collections.defaultdict(int)
    self.buffs = []
    self.debuffs = []

  def hp_string(self):
    percent = int(100 * self.current_hp / self.max_hp)
    return "%d%%" % percent

  def pass_time(self, amount):
    remaining_debuffs = []
    for debuff in self.debuffs:
      debuff.pass_time(amount)
      if debuff.active():
        remaining_debuffs.append(debuff)
    self.debuffs = remaining_debuffs

  def add_debuff(self, new_debuff):
    Debuff.add_debuff(self.debuffs, new_debuff)

  def __str__(self):
    debug = True
    pieces = []
    pieces.append("Name: %s\n" % self.name)
    pieces.append("HP: %s\n" % self.hp_string())
    pieces.append("Buffs: None\n")
    pieces.append("Debuffs: ")
    pieces.append(", ".join(str(debuff) for debuff in self.debuffs))
    if self.debuffs:
      pieces.append("\n")
    else:
      pieces.append("None\n")
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
    rune_chance = BOSS_RUNE_CHANCE if self.boss else RUNE_CHANCE
    while random.random() < rune_chance:
      treasure.append("Rune")
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
