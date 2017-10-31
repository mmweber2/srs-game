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

  def get_ui_string(self):
    pass


