import random

class Combat(object):
  CHARACTER_DEAD = 0
  MONSTER_DEAD = 1
  CHARACTER_TURN = 2
  MONSTER_TURN = 3
  TARGET_DEAD = 4
  TARGET_ALIVE = 5

  @classmethod
  def perform_turn(cls, action, info, character, monster, logs):
    # Character action
    death = cls.perform_action(action, info, character, monster, logs)
    if death == cls.TARGET_DEAD:
      return cls.MONSTER_DEAD
    next_turn = cls.get_next_actor(character, monster)
    while next_turn == cls.MONSTER_TURN:
      action, info = monster.get_action(character)
      result = cls.perform_action(action, info, monster, character, logs)
      if result == cls.TARGET_DEAD: 
        return cls.CHARACTER_DEAD
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
    damage = random.randint(10, 20)
    damage *= float(actor.stats["Strength"]) / target.stats["Defense"]
    damage = int(damage)
    logs.append("Hits for %d damage" % damage)
    return cls.apply_damage(target, damage)

  @classmethod
  def get_next_actor(cls, character, monster):
    character_chance = float(character.stats["Speed"]) / monster.stats["Speed"]
    print character_chance
    if random.randint() < character_chance:
      return cls.CHARACTER_TURN
    else:
      return cls.MONSTER_TURN
