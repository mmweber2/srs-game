from character import Character

class GameState(object):
  def __init__(self):
    self.state = "CHAR_CREATE"
    self.character = Character()

  def get_choices(self):
    if self.state == "CHAR_CREATE":
      return ["Strength", "Stamina", "Speed", "Intellect"]
    else:
      return ["Error", "Error", "Error", "Error"]

  def apply_choice(self, choice):
    logs = []
    if self.state == "CHAR_CREATE":
      self.character.make_initial_equipment(self.get_choices()[choice])
      logs.append("Generated %s equipment." % self.get_choices()[choice])
      self.state = "START_GAME"
    else:
      assert False
    return logs

