from equipment import Equipment

class Character(object):
  def __init__(self):
    # Weapon, Helm, Chest, Legs, Accessory
    self.equipment = [None, None, None, None, None]
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}
    self.gold = 100
    self.name = "Hero?"
    self.max_hp = 5 * self.stats["Stamina"]
    self.current_hp = self.max_hp

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equip(i, Equipment.get_new_armor(1, slot=i, require=choice))

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
    pieces.append("HP: %d / %d\n" % (self.current_hp, self.max_hp))
    for stat in self.stats:
      pieces.append("%s: %d (%d)\n" % (stat, self.get_effective_stat(stat),
                                       self.stats[stat]))
    pieces.append("Equipment:\n")
    for piece in self.equipment:
      pieces.append(str(piece) + "\n")
    return "".join(pieces)

  def get_effective_stat(self, stat):
    value = self.stats[stat]
    for piece in self.equipment:
      if piece:
        value += piece.get_stat_value(stat)
    return value

  def equip(self, slot, item):
    self.equipment[slot] = item
    # TODO: Separate function?
    new_max_hp = self.get_effective_stat("Stamina") * 5
    difference = new_max_hp - self.max_hp
    self.current_hp += difference
    self.max_hp = new_max_hp
