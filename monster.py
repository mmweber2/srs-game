import random

# TODO: Should Monster and Character subclass from something?

class Monster(object):
  def __init__(self, level, boss):
    # TODO: Should level vary somewhat?
    self.stats = {}
    # If you modify these, make sure to modify the XP calc
    # START HERE: Make a common table both rely on, idiot
    for stat in ("Strength", "Defense", "Speed", "Intellect", "Magic Defense"):
      self.stats[stat] = self.roll_stat(level, 12, 2)
    for stat in ("Stamina",):
      self.stats[stat] = self.roll_stat(level, 8, 0)
    if boss:
      for stat in self.stats:
        self.stats[stat] = self.stats[stat] * 1.25
      self.stats["Stamina"] *= 4   # Effectively x5
    for stat in self.stats:
      # 50-150% change
      self.stats[stat] *= random.random() + 0.5
      self.stats[stat] = int(self.stats[stat])
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
      pieces.append("XP value: %d\n" % self.calculate_xp())
    return "".join(pieces)

  def calculate_xp(self):
    effective_level = 0
    for stat in ("Strength", "Defense", "Speed", "Intellect", "Magic Defense"):
      effective_level += (self.stats[stat] / 8.5)
    for stat in ("Stamina",):
      effective_level += (self.stats[stat] / 4.5)
    effective_level /= 6
    return int(10 * effective_level)

  def get_treasure(self):
    pass

  def get_effective_stat(self, stat):
    # TODO: Buffs and such, probably
    return self.stats[stat]

  @classmethod
  def roll_stat(cls, level, die, modifier):
    # TODO: May be too slow, might want to use a different method
    return sum(random.randint(1, die) + modifier for _ in xrange(level))

if __name__ == "__main__":
  test_monster = Monster(1, False)
  print test_monster
