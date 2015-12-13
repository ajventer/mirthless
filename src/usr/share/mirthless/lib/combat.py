from util import rolldice, load_yaml, debug
from math import hypot


def range_mod(player, target, weapon):
    """
    Calculated the range modifier to misile attacks based on the
    ADnD manual's rules.
    """
    ranges = {
        "long": {"short": 0, "medium": -2, "long": -5},
        "medium": {"short": 0, "medium": -2, "long": -999},
        "short": {"short": 0, "medium": -5, "long": -999}
    }
    if weapon.get('/conditional/weapon_type', 'melee') == 'misile':
        weaponrange = 'long'
    else:
        weaponrange = weapon.get('/conditional/range', 'short')
        if not weaponrange:
            weaponrange = 'short'
    ploc = player.get('/core/location', {})
    tloc = target.get('/core/location', {})
    xdiff = ploc['x'] - tloc['x']
    ydiff = ploc['y'] - tloc['y']
    distance = hypot(xdiff, ydiff)
    if distance <= 1:
        targetrange = 'short'
    elif distance <= 3:
        targetrange = 'medium'
    else:
        targetrange = 'long'
    out = '%s is attacking %s from %s range with a %s-range weapon' % (player.displayname(), target.displayname(), targetrange, weaponrange)
    if weaponrange in ["short", "medium"] and targetrange == "long":
        out += '<br> This weapon cannot hit a target that far !'
    frontend.campaign.message(out)
    return ranges[weaponrange][targetrange]


def calc_damage(player, target, custom_dmg):
    dmg_mod = player.dmg_mod() + custom_dmg
    if custom_dmg:
        frontend.campaign.message('Applying custom damage modifier of %s' % custom_dmg)
    frontend.campaign.message('Total damage modifier %s' % dmg_mod)
    weapon = player.current_weapon()
    dmg = weapon.get('/conditional/dmg', 1)
    save = weapon.get('/conditional/save_against', 'none')
    if save != 'none':
        throw = target.saving_throw(save)
        if throw[0]:
            frontend.campaign.message(throw[1])
        return throw[0]
    damage = rolldice(numdice=1, numsides=dmg, modifier=dmg_mod)
    frontend.campaign.message('Rolling for damage: %s' % damage[1])
    taken = target.take_damage(damage[0])
    frontend.campaign.message(taken[1])
    return taken[0]


def attack_roll(player, target, attack_modifiers, custom_tohit):
    custom_tohit = custom_tohit or 0
    if custom_tohit:
        frontend.campaign.message('Applying custom to-hit modifier of %s' % custom_tohit)
    if player.is_casting:
        player.interrupt_cast()
        frontend.campaign.message('%s is casting. Cast will be interrupted if you attack %s' % (player.displayname(), target.displayname))
    attack_mods = load_yaml('adnd2e', 'attack_mods')
    total_modifier = custom_tohit
    for mod in attack_modifiers:
        total_modifier += int(attack_mods[mod])
        frontend.campaign.message('Applying modifier %s: %s' % (mod, attack_mods[mod]))
    range_modifier = 0
    if range_modifier:
        frontend.campaign.message('Applying range modifier %s' % range_modifier)
        total_modifier += range_modifier
    weaponmod = player.to_hit_mod()
    frontend.campaign.message('Applying weapon modifier %s' % weaponmod)
    total_modifier += weaponmod
    frontend.campaign.message('Total modifier: %s<br><br>' % total_modifier)
    frontend.campaign.message('%s has a defense modifier of %s and armor class %s' % (target.displayname(), target.def_mod(), target.armor_class()))
    target_roll = int(player.thac0 - target.armor_class() - target.def_mod())
    target_roll = target_roll - total_modifier
    if target_roll <= 0:
        frontend.campaign.error('%s is guaranteed to hit %s - no need to roll' % (player.displayname(), target_roll, target.displayname()))
    else:
        frontend.campaign.error('%s needs to roll %s to hit %s' % (player.displayname(), target_roll, target.displayname()))
    return target_roll


def attack(player, target, attack_modifiers, custom_tohit, custom_dmg):
    custom_tohit = custom_tohit or 0
    if custom_tohit:
        frontend.campaign.message('Applying custom to-hit modifier of %s' % custom_tohit)

    frontend.campaign.message('%s is attacking %s' % (player.displayname(), target.displayname()))
    target_alive = True
    attack_number = 1
    attack_mods = load_yaml('adnd2e', 'attack_mods')
    num_attacks = player.num_attacks()
    debug("COMBAT: num_attacks:", num_attacks)
    while attack_number <= num_attacks and target_alive:
        frontend.campaign.message('<br><Br><strong>Attack %s of %s</strong><br>' % (attack_number, num_attacks))
        total_modifier = custom_tohit
        for mod in attack_modifiers:
            total_modifier += int(attack_mods[mod])
            frontend.campaign.message('Applying modifier %s: %s' % (mod, attack_mods[mod]))
        debug("Attack number", attack_number, "Out of", num_attacks, "Target alive", target_alive)
        weapon = player.current_weapon()
        frontend.campaign.message('Attacking with weapon %s' % weapon.displayname())
        range_modifier = range_mod(player, target, weapon)
        if range_modifier:
            frontend.campaign.message('Applying range modifier %s' % range_modifier)
            total_modifier += range_modifier
        frontend.campaign.message('Attack number %s out of %s' % (attack_number, num_attacks))
        attack_number += 1
        weaponmod = player.to_hit_mod()
        frontend.campaign.message('Applying weapon modifier %s' % weaponmod)
        total_modifier += weaponmod
        frontend.campaign.message('Total modifier: %s<br><br>' % total_modifier)
        attack_roll = player.attack_roll(target, total_modifier)
        frontend.campaign.message('Attack roll: %s %s %s' % (attack_roll[0], attack_roll[1], attack_roll[2]))
        if attack_roll[1] == 'Critical Hit !':
            frontend.campaign.message('Critical hit ! %s gain an extra attack.' % player.displayname())
            num_attacks += 1
        if attack_roll[1] == "Critical Miss !":
            frontend.campaign.message('Critical miss ! %s loses an attack.' % player.displayname())
            num_attacks - 1
        if "hit" in attack_roll[1].lower():
            if target.is_casting:
                target.interrupt_cast()
                frontend.campaign.message('%s was casting but it was interrupted by a successfull hit' % target.displayname)
            player.current_weapon().onstrike(player, target)
            damage_result = calc_damage(player, target, custom_dmg)
            target_alive = damage_result is True
            for char in [player, target]:
                char.autosave()
