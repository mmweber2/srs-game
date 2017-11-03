from equipment import Equipment
import random

class Character(object):
  def __init__(self):
    # Weapon, Helm, Chest, Legs, Accessory
    # TODO: Implement wand vs. sword weapons
    self.equipment = [None, None, None, None, None]
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}
    self.gold = 100
    self.name = "Hero?"
    self.max_hp = 5 * self.stats["Stamina"]
    self.current_hp = self.max_hp
    self.level = 1
    self.exp = 0

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equip(Equipment.get_new_armor(1, slot=i, require=choice))

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
    pieces.append("HP: %d / %d\n" % (self.current_hp, self.max_hp))
    pieces.append("Level: %d\n" % self.level)
    pieces.append("XP: %d / %d\n" % (self.exp, self.next_level_exp()))
    for stat in self.stats:
      pieces.append("%s: %d (%d)\n" % (stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
    pieces.append("Equipment:\n")
    for piece in self.equipment:
      pieces.append(str(piece) + "\n")
    return "".join(pieces)

  def restore_hp(self, amount=None):
    if amount is None:
      self.current_hp = self.max_hp
    else:
      self.current_hp = min(self.max_hp, self.current_hp + amount)

  def apply_death(self, logs):
    logs.append("You have been defeated.")
    logs.append("You were found by a passerby, and brought back to town.")
    self.restore_hp()
    lost_gold = self.gold / 2
    logs.append("You lost %d gold" % lost_gold)
    self.gold -= lost_gold

  def get_effective_stat(self, stat):
    value = self.stats[stat]
    for piece in self.equipment:
      if piece:
        value += piece.get_stat_value(stat)
    return value

  def equip(self, item):
    slot = item.slot
    self.equipment[slot] = item
    # TODO: Separate function?
    new_max_hp = self.get_effective_stat("Stamina") * 5
    difference = new_max_hp - self.max_hp
    self.current_hp += difference
    self.max_hp = new_max_hp

  def next_level_exp(self):
    # TODO: Something more "complex", lol
    return self.level * 100

  def level_up(self, logs):
    for stat in self.stats:
      increase = random.randint(0, 2)
      if increase > 0:
        self.stats[stat] += increase
        logs.append("You have gained %d %s" % (increase, stat))

  def gain_exp(self, exp, encounter_level, logs):
    exp_gained = exp
    level_difference = encounter_level - self.level
    exp_gained = int(exp_gained * (1.1 ** level_difference))
    self.exp += exp_gained
    logs.append("You have gained %d XP" % exp_gained)
    while self.exp > self.next_level_exp():
      self.exp -= self.next_level_exp()
      self.level += 1
      logs.append("You have reached level %d!" % self.level)
      self.level_up(logs)
