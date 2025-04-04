def resolve_combat(attacker, defender):
    attacker_strength = attacker.count
    defender_strength = defender.count

    if attacker_strength > defender_strength:
        attacker.count -= defender_strength // 2
        defender.is_dead = True
        return attacker
    elif attacker_strength < defender_strength:
        defender.count -= attacker_strength // 2
        attacker.is_dead = True
        return defender
    else:
        attacker.is_dead = True
        defender.is_dead = True
        return None