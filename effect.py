from equipment import STATS, DEFENSES

STACK_MULTIPLY = ["XP Gain"] + STATS + DEFENSES
STACK_MAX = ["Blinded", "Stunned", "Immortal"]

class Effect(object):

  def __init__(self, duration):
    self.duration = duration
    self.quantity = 0

  def pass_time(self, time_passed):
    self.duration -= time_passed

  @classmethod
  def stackable(cls):
    return False

  def get_name(self):
    return "Not Implemented"

  def active(self):
    return self.duration > 0

  def get_effects(self):
    pass

  def update(self, buff):
    """Returns True if buff is the same kind, False otherwise."""
    # Update the duration and effects of this buff, using the new buff.
    assert not self.stackable()

  @classmethod
  def get_combined_impact(cls, impact, buffs, debuffs):
    if impact in STACK_MULTIPLY:
      combined_impact = 1.0
      for effect in buffs + debuffs:
        impacts = effect.get_impacts()
        if impact in impacts:
          combined_impact *= impacts[impact]
    elif impact in STACK_MAX:
      combined_impact = 0.0
      for effect in buffs + debuffs:
        impacts = effect.get_impacts()
        if impact in impacts:
          combined_impact = max(impact, combined_impact)
    else:
      assert False
    return combined_impact

  def __str__(self):
    if self.quantity:
      return "%s (%d): %d" % (self.get_name(), self.quantity, self.duration)
    else:
      return "%s: %d" % (self.get_name(), self.duration)

class Buff(Effect):
  @classmethod
  def add_buff(cls, buff_list, new_buff):
    if new_buff.stackable():
      buff_list.append(new_buff)
    else:
      for buff in buff_list:
        updated = buff.update(new_buff)
        if updated:
          break
      else:
        buff_list.append(new_buff)

class Debuff(Effect):
  @classmethod
  def add_debuff(cls, debuff_list, new_debuff):
    if new_debuff.stackable():
      debuff_list.append(new_debuff)
    else:
      for debuff in debuff_list:
        updated = debuff.update(new_debuff)
        if updated:
          break
      else:
        debuff_list.append(new_debuff)

class WellRested(Buff):
  # +25% xp, +15% stats
  def get_impacts(self):
    impacts = {}
    impacts["XP Gain"] = 1.25
    for stat in STATS:
      impacts[stat] = 1.15
    return impacts

  def get_name(self):
    return "Well Rested"

  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class WellFed(Buff):
  # +10% xp, +5% stats
  def get_impacts(self):
    impacts = {}
    impacts["XP Gain"] = 1.10
    for stat in STATS:
      impacts[stat] = 1.05
    return impacts

  def get_name(self):
    return "Well Fed"

  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class Blessed(Buff):
  # +10% stats and defenses
  def get_impacts(self):
    impacts = {}
    for stat in STATS + DEFENSES:
      impacts[stat] = 1.10
    return impacts

  def get_name(self):
    return "Blessed"

  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class Protection(Buff):
  # 100% increase to def / mdef
  def get_impacts(self):
    impacts = {}
    for stat in DEFENSES:
      impacts[stat] = 2.00
    return impacts

  def get_name(self):
    return "Protection"

  # TODO: Move these identical update functions somewhere?
  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class Blinded(Debuff):
  def get_impacts(self):
    impacts = {}
    impacts["Blinded"] = 1
    return impacts

  def get_name(self):
    return "Blinded"

  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class Stunned(Debuff):
  def get_impacts(self):
    impacts = {}
    impacts["Stunned"] = 1
    return impacts

  def get_name(self):
    return "Stunned"

  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False

class LastStand(Buff):
  # 100% increase to def / mdef
  def get_impacts(self):
    impacts = {}
    impacts["Immortal"] = 1
    return impacts

  def get_name(self):
    return "Last Stand"

  # TODO: Move these identical update functions somewhere?
  def update(self, buff):
    if buff.get_name() == self.get_name():
      self.duration = max(self.duration, buff.duration)
      return True
    else:
      return False
