import effect

# TODO: Add substitute (automatic rez when you die)
# TODO: Add names to items (based on stats / slot)

class Item(object):
  UNUSABLE = 0
  def __init__(self):
    self.info = {"name": "Not Implemented",
                 "value": 2**100,
                 "item_level": 100}
  def apply(self, character, monster, logs):  # monsters don't get items
    # Will return an error code if the item can't be used.
    pass
  def get_name(self):
    return self.info["name"]
  def get_value(self):
    return self.info["value"]
  def get_item_level(self):
    return self.info["item_level"]

class MinorHealthPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor HP Pot",
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(200)
    logs.append("You restored {} HP".format(hp_gained))

class HealthPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "HP Pot",
                 "value": 500,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(600)
    logs.append("You restored {} HP".format(hp_gained))

class MajorHealthPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major HP Pot",
                 "value": 2500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(1800)
    logs.append("You restored {} HP".format(hp_gained))

class SuperHealthPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Super HP Pot",
                 "value": 15000,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    hp_gained = character.restore_hp(5400)
    logs.append("You restored {} HP".format(hp_gained))

class MinorMagicPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor SP Pot",
                 "value": 200,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    sp_gained = character.restore_sp(50)
    logs.append("You restored {} SP".format(sp_gained))

class MagicPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "SP Pot",
                 "value": 1200,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    sp_gained = character.restore_sp(200)
    logs.append("You restored {} SP".format(sp_gained))

class MajorMagicPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major SP Pot",
                 "value": 7500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    sp_gained = character.restore_sp(600)
    logs.append("You restored {} SP".format(sp_gained))

class InnFood(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Inn-made Bento",
                 "value": 0,
                 "item_level": 1}

  def apply(self, character, monster, logs):
    if monster:
      logs.append("You cannot eat the Inn-made Bento in combat.")
      return Item.UNUSABLE
    else:
      character.add_buff(effect.WellFed(300))
      logs.append("You ate the Inn-made Bento")

class MinorSurgePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor Surge Pot",
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Surge(5, 1.5))
    logs.append("You gain the Surge buff")

class SurgePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Surge Pot",
                 "value": 500,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Surge(10, 2.0))
    logs.append("You gain the Surge buff")

class MajorSurgePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major Surge Pot",
                 "value": 2500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Surge(15, 2.5))
    logs.append("You gain the Surge buff")

class MinorConcentratePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor Concentrate Pot",
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Concentrate(5, 1.5))
    logs.append("You gain the Concentrate buff")

class ConcentratePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Concentrate Pot",
                 "value": 500,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Concentrate(10, 2.0))
    logs.append("You gain the Concentrate buff")

class MajorConcentratePotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major Concentrate Pot",
                 "value": 2500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Concentrate(15, 2.5))
    logs.append("You gain the Concentrate buff")

class MinorSwiftnessPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor Swiftness Pot",
                 "value": 100,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Swiftness(5, 1.5))
    logs.append("You gain the Swiftness buff")

class SwiftnessPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Swiftness Pot",
                 "value": 500,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Swiftness(10, 2.0))
    logs.append("You gain the Swiftness buff")

class MajorSwiftnessPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major Swiftness Pot",
                 "value": 2500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    character.add_buff(effect.Swiftness(15, 2.5))
    logs.append("You gain the Swiftness buff")

class MinorBulkUpPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Minor BulkUp Pot",
                 "value": 300,
                 "item_level": 1}
  def apply(self, character, monster, logs):
    character.add_buff(effect.BulkUp(5, 1.4))
    logs.append("You gain the BulkUp buff")

class BulkUpPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "BulkUp Pot",
                 "value": 1500,
                 "item_level": 10}
  def apply(self, character, monster, logs):
    character.add_buff(effect.BulkUp(10, 1.7))
    logs.append("You gain the BulkUp buff")

class MajorBulkUpPotion(Item):
  def __init__(self):
    super().__init__()
    self.info = {"name": "Major BulkUp Pot",
                 "value": 7500,
                 "item_level": 30}
  def apply(self, character, monster, logs):
    character.add_buff(effect.BulkUp(15, 2.0))
    logs.append("You gain the BulkUp buff")
