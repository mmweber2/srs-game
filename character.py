from equipment import Equipment

class Character(object):
  def __init__(self):
    # Helm, Chest, Legs, Accessory
    self.equipment = [None, None, None, None]
    self.stats = {"Strength": 20, "Stamina": 20, "Defense": 20, "Speed": 20,
                  "Intellect": 20, "Magic Defense": 20}

  def make_initial_equipment(self, choice):
    for i in range(len(self.equipment)):
      self.equipment[i] = Equipment.get_new_armor(1, slot=i, require=choice)

  def __str__(self):
    pieces = []
    pieces.append("Character:\n")
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
