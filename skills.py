from combat import Combat
import random
import effect

SKILLS = {
          "Withering Attack": "Chance to inflict stacks of wither",
          "Bubble": "Create a barrier that absorbs damage",
          "Drain": "Perform an attack, absorb a percentage of the damage as HP",
          "Final Strike": "Convert HP/MP to one massive attack",
          "Heal": "Restore HP",
          "Full Heal": "Restore all HP",
          "Renew": "Restore HP each turn",
          "Chain Lightning": "Do magical damage, chance to repeat",
          "Auto-Life": "Add a buff that restores HP on fatal damage",
          "Meditate": "Restore MP. May fail depending on current MP",
          # TODO: A few more interesting magical attacks
          # Force bolt?
          # Libra as a buff?
         }

class Skill(object):
  def __init__(self, level=1):
    self.level = level
  def get_name(self):
    return "Not Implemented"
  def get_description(self):
    return "No Description"
  def level_up(self):
    self.level += 1
  def sp_cost(self):
    return 0
  def once_per_battle(self):
    return False
  def apply_skill(self, actor, opponent, logs):
    pass

class QuickAttack(Skill):
  def get_name(self):
    return "Quick Attack"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def go_again_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to go again."
    desc = desc % (self.get_attack_multiple(), (self.go_again_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if result == Combat.TARGET_DEAD:
      return result
    if random.random() < self.go_again_chance():
      logs.append("Quick attack succeeded")
      return Combat.ACTOR_TURN
    else:
      logs.append("Quick attack failed")
      return Combat.TARGET_ALIVE

class Blind(Skill):
  def get_name(self):
    return "Blind"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def blind_chance(self):
    return 1.0 - (0.5 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to blind."
    desc = desc % (self.get_attack_multiple(), (self.blind_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if random.random() < self.blind_chance():
      if opponent.boss:
        logs.append("Blind resisted")
      else:
        logs.append("%s is blinded" % opponent.name)
        opponent.add_debuff(effect.Blinded(10))
    return result

class Bash(Skill):
  def get_name(self):
    return "Bash"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def stun_chance(self):
    return 1.0 - (0.8 ** self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to stun."
    desc = desc % (self.get_attack_multiple(), (self.stun_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 5
  def apply_skill(self, actor, opponent, logs):
    result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                  self.get_attack_multiple())
    if random.random() < self.stun_chance():
      if opponent.boss:
        logs.append("Stun resisted")
      else:
        logs.append("%s is stunned" % opponent.name)
        opponent.add_debuff(effect.Stunned(3))
    return result

class Protection(Skill):
  def get_name(self):
    return "Protection"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Increase def/mdef by 100%% for %d time units" % self.buff_duration()
  def sp_cost(self):
    return self.level * 2
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Protection(self.buff_duration()))
    return Combat.TARGET_ALIVE

class HeavySwing(Skill):
  def get_name(self):
    return "Heavy Swing"
  def get_attack_multiple(self):
    return 2.0 + 0.3 * self.level
  def miss_chance(self):
    return 0.2 - (0.01 * self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to miss."
    desc = desc % (self.get_attack_multiple(), (self.miss_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    if random.random() < self.miss_chance():
      logs.append("Heavy Swing missed")
      return Combat.TARGET_ALIVE
    else:
      result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                    self.get_attack_multiple())
      return result

class LastStand(Skill):
  def get_name(self):
    return "Last Stand"
  def duration(self):
    return 2 + self.level
  def get_description(self):
    return "Cannot die for %d time units." % self.duration()
  def sp_cost(self):
    return 50 + 10 * self.level
  def once_per_battle(self):
    return True
  def apply_skill(self, actor, opponent, logs):
    logs.append("%s takes a Last Stand" % actor.name)
    actor.add_buff(effect.LastStand(self.duration()))
          
class Surge(Skill):
  def get_name(self):
    return "Surge"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Strength up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 3
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Surge(self.buff_duration()))
    return Combat.TARGET_ALIVE
    
class Concentrate(Skill):
  def get_name(self):
    return "Concentrate"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Intelligence up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 3
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Concentrate(self.buff_duration()))
    return Combat.TARGET_ALIVE

class Swiftness(Skill):
  def get_name(self):
    return "Swiftness"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Speed up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 4
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.Swiftness(self.buff_duration()))
    return Combat.TARGET_ALIVE

class BulkUp(Skill):
  def get_name(self):
    return "Bulk Up"
  def buff_duration(self):
    return 5 + (5 * self.level)
  def get_description(self):
    return "Stamina up by 100%% for %d time" % self.buff_duration()
  def sp_cost(self):
    return self.level * 3
  def apply_skill(self, actor, opponent, logs):
    actor.add_buff(effect.BulkUp(self.buff_duration()))
    return Combat.TARGET_ALIVE

class Cannibalize(Skill):
  def get_name(self):
    return "Cannibalize"
  def percent_converted(self):
    return 3 + self.level
  def get_description(self):
    desc = "Convert up to %d%% of max HP into half as many SP"
    return desc % self.percent_converted()
  def sp_cost(self):
    return 0
  def apply_skill(self, actor, opponent, logs):
    hp_to_convert = actor.max_hp * self.percent_converted() / 100
    hp_to_convert = min(hp_to_convert, actor.current_hp - 1)
    sp_gained = hp_to_convert / 2
    actor.current_hp -= hp_to_convert
    sp_gained = actor.restore_sp(sp_gained)
    logs.append("Converted %d HP into %d SP" % (hp_to_convert, sp_gained))
    return Combat.TARGET_ALIVE

class PoisonedBlade(Skill):
  def get_name(self):
    return "Poisoned Blade"
  def get_attack_multiple(self):
    return 1.0 + 0.1 * self.level
  def kill_chance(self):
    return 0.05 + (0.02 * self.level)
  def get_description(self):
    desc = "Physical attack with %.2f multiplier, %d%% chance to auto-kill."
    desc = desc % (self.get_attack_multiple(), (self.kill_chance() * 100))
    return desc
  def sp_cost(self):
    return self.level * 2
  def apply_skill(self, actor, opponent, logs):
    if random.random() < self.kill_chance() and not opponent.boss:
      logs.append("Assassinated!")
      return Combat.TARGET_DEAD
    else:
      result = Combat.action_attack(None, actor, opponent, logs, "Physical",
                                    self.get_attack_multiple())
      return result

SKILLS = [QuickAttack, Blind, Bash, Protection, HeavySwing, LastStand, Surge,
          Concentrate, Swiftness, BulkUp, Cannibalize, PoisonedBlade]
