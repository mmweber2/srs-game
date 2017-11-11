from effect import WellFed

class Item(object):
  UNUSABLE = 0
  def __init__(self):
    self.info = {"name": "Not Implemented",
                 "value": 2**100,
                 "item_level": 100}
  def apply(self, character, monster, logs):  # monsters don't get items
    # Will return an error code if the item can't be used.
    pass
  # TODO: Is there a cleaner way to do this?
  def get_name(self):
    return self.info["name"]
  def get_value(self):
    return self.info["value"]
  def get_item_level(self):
    return self.info["item_level"]

class MinorHealthPotion(Item):
  def __init__(self):
    self.info = {"name": "Minor HP Pot",
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(100)
    logs.append("You restored %d HP" % hp_gained)

class HealthPotion(Item):
  def __init__(self):
    self.info = {"name": "HP Pot",
                 "value": 1000,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    character.restore_hp(400)
    logs.append("You restored %d HP" % hp_gained)

class MajorHealthPotion(Item):
  def __init__(self):
    self.info = {"name": "Major HP Pot",
                 "value": 10000,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    character.restore_hp(1600)
    logs.append("You restored %d HP" % hp_gained)

class SuperHealthPotion(Item):
  def __init__(self):
    self.info = {"name": "Major HP Pot",
                 "value": 100000,
                 "item_level": 60}
  def apply(self, character, monster, logs):
    character.restore_hp(6400)
    logs.append("You restored %d HP" % hp_gained)

class InnFood(Item):
  def __init__(self):
    self.info = {"name": "Inn-made Bento",
                 "value": 0,
                 "item_level": 1}

  def apply(self, character, monster, logs):
    if monster:
      logs.append("You cannot eat the Inn-made Bento in combat.")
      return Item.UNUSABLE
    else:
      character.add_buff(WellFed(300))
      logs.append("You ate the Inn-made Bento")
