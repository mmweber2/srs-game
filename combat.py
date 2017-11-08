import random

class Combat(object):
  CHARACTER_DEAD = 0
  MONSTER_DEAD = 1
  CHARACTER_TURN = 2
  MONSTER_TURN = 3
  TARGET_DEAD = 4
  TARGET_ALIVE = 5
  ACTOR_SUCCEEDED = 6
  ACTOR_FAILED = 7
  CHARACTER_ESCAPED = 8
  MONSTER_ESCAPED = 9
  ACTOR_ESCAPED = 10

  @classmethod
  def perform_turn(cls, action, info, character, monster, logs):
    # Character action
    result = cls.perform_action(action, info, character, monster, logs)
    if result == cls.TARGET_DEAD:
      return cls.MONSTER_DEAD
    elif result == cls.ACTOR_ESCAPED:
      return cls.CHARACTER_ESCAPED
    next_turn = cls.get_next_actor(character, monster)
    while next_turn == cls.MONSTER_TURN:
      action, info = monster.get_action(character)
      result = cls.perform_action(action, info, monster, character, logs)
      if result == cls.TARGET_DEAD:
        return cls.CHARACTER_DEAD
      elif result == cls.ACTOR_ESCAPED:
        return cls.MONSTER_ESCAPED
      next_turn = cls.get_next_actor(character, monster)
    return cls.CHARACTER_TURN

  @classmethod
  def perform_action(cls, action, info, actor, target, logs):
    """Performs an action. Returns if target died."""
    try:
      method_name = "action_" + action.lower()
      method = getattr(Combat, method_name)
      return method(info, actor, target, logs)
    except AttributeError as exc:
      print exc
      logs.append("Combat option %s not implemented" % action)
      return cls.TARGET_ALIVE

  @classmethod
  def apply_damage(cls, target, damage):
    target.current_hp -= damage
    return cls.TARGET_DEAD if target.current_hp <= 0 else cls.TARGET_ALIVE

  @classmethod
  def action_attack(cls, _, actor, target, logs):
    """Attacks, applies damage, returns True if target dies."""
    logs.append("%s attacks %s" % (actor.name, target.name))
    damage = actor.get_damage()
    damage_type = actor.get_damage_type()
    if damage_type == "Physical":
      attack = actor.get_effective_stat("Strength")
      defense = target.get_effective_stat("Defense")
    elif damage_type == "Magic":
      attack = actor.get_effective_stat("Intellect")
      defense = target.get_effective_stat("Magic Defense")
    else:
      assert False
    factor = float(attack) / defense
    factor = factor ** .5
    damage = int(damage * factor)
    logs.append("Hits for %d %s damage" % (damage, damage_type))
    return cls.apply_damage(target, damage)

  @classmethod
  def get_next_actor(cls, character, monster):
    result = cls.skill_check("Speed", character, monster)
    if result == cls.ACTOR_SUCCEEDED:
      return cls.CHARACTER_TURN
    else:
      return cls.MONSTER_TURN

  @classmethod
  def skill_check(cls, stat, actor, target):
    actor_stat = actor.get_effective_stat(stat)
    target_stat = target.get_effective_stat(stat)
    total_stat = actor_stat + target_stat
    # TODO: Consider applying a dampening factor to this (like sqrt again?)
    actor_chance = float(actor_stat) / total_stat
    if random.random() < actor_chance:
      return cls.ACTOR_SUCCEEDED
    else:
      return cls.ACTOR_FAILED

  @classmethod
  def action_escape(cls, _, actor, target, logs):
    result = cls.skill_check("Speed", actor, target)
    if result == cls.ACTOR_SUCCEEDED:
      return cls.ACTOR_ESCAPED
    else:
      logs.append("Escape unsuccessful")
      return cls.ACTOR_FAILED
