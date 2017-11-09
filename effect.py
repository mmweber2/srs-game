from equipment import STATS, DEFENSES

STACK_MULTIPLY = ["XP Gain"] + STATS + DEFENSES

class Effect(object):

  def __init__(self, duration):
    self.duration = duration

  def pass_time(self, time_passed):
    self.duration -= time_passed
  pass

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
    combined_impact = 1.0
    if impact in STACK_MULTIPLY:
      for effect in buffs + debuffs:
        impacts = effect.get_impacts()
        if impact in impacts:
          combined_impact *= impacts[impact]
    else:
      assert False
    return combined_impact

  def __str__(self):
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
