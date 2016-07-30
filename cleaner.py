#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=E0401
""" Pokécleaner - Turn all the runts into gelato """
import sys
sys.path.append('./pokemongo-api/pogo')

import getpass
import argparse
import keyring

from api import PokeAuthSession
from pokedex import pokedex, Rarity

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-u", "--user", help="Username")
PARSER.add_argument("-t", "--transfer", help="Transfer", action='store_true')
PARSER.add_argument("-e", "--evolve", help="Evolvable", action='store_true')
PARSER.add_argument("-l", "--live", help="WILL CHANGE!!!", action='store_true')
PARSER.add_argument("-v", "--verbose", help="Verbose", action='store_true')
ARGS = PARSER.parse_args()

if not ARGS.user:
    USER = raw_input('Username: ')
else:
    USER = ARGS.user
PASS = keyring.get_password('pkmg', USER)

if not PASS:
    PASS = getpass.getpass('Password: ')
    keyring.set_password('pkmg', USER, PASS)

POKESESSION = PokeAuthSession(USER, PASS, 'google')
SESSION = POKESESSION.authenticate(locationLookup='50 Bridge St, Sydney')

INV = SESSION.getInventory()

# #POKES = sorted(INV.party, key=lambda x: x.cp, reverse=True)
POKES = sorted(INV.party, key=lambda x: x.pokemon_id, reverse=True)
# # POKES = sorted(
# #     INV.party,
# #     key=
# #     lambda x: (x.individual_attack + x.individual_defense + x.individual_stamina),
# #     reverse=True)

GELATO = {}

for poke in POKES:
    goodness = (poke.individual_attack + poke.individual_defense +
                poke.individual_stamina) / 0.45
    if poke.pokemon_id in pokedex.rarity[
            Rarity.CRITTER
    ] or poke.pokemon_id in pokedex.rarity[Rarity.COMMON]:
        if poke.cp < 700 and goodness < 70 and not poke.nickname and not poke.favorite:
            if poke.pokemon_id in GELATO:
                GELATO[poke.pokemon_id].append(poke)
            else:
                GELATO[poke.pokemon_id] = [poke]

NUM_EVOLVE = 0

for key, poke_type in GELATO.iteritems():
    num_poke = len(poke_type)
    print '{}({}/{})'.format(pokedex[key], num_poke,
                             INV.candies[key] / pokedex.evolves[key])
    if ARGS.verbose:
        for poke in poke_type:
            goodness = (poke.individual_attack + poke.individual_defense +
                        poke.individual_stamina) / 0.45
            print "    - CP {:>4} - {:2.1f}% ({:>2}/{:>2}/{:>2}) - Candies: {}/{}".format(
                poke.cp, goodness, poke.individual_attack,
                poke.individual_defense, poke.individual_stamina,
                INV.candies[poke.pokemon_id], pokedex.evolves[poke.pokemon_id])

    if ARGS.transfer:
        evolvable = INV.candies[key] / pokedex.evolves[key]
        transferable = num_poke - evolvable
        if transferable > 0:
            check = raw_input(
                'Are you sure to want to transfer {}/{} of these {}: '.format(
                    transferable, num_poke, pokedex[key]))
            if check.upper() == 'Y':
                for poke in poke_type:
                    if transferable > 0:
                        goodness = (
                            poke.individual_attack + poke.individual_defense +
                            poke.individual_stamina) / 0.45
                        print "Transfered  - CP {:>4} - {:2.1f}% ({:>2}/{:>2}/{:>2}) - Candies: {}/{}".format(
                            poke.cp, goodness, poke.individual_attack,
                            poke.individual_defense, poke.individual_stamina,
                            INV.candies[poke.pokemon_id],
                            pokedex.evolves[poke.pokemon_id])
                        if ARGS.live:
                            SESSION.releasePokemon(poke)
                        transferable -= 1
        else:
            print 'Not enough to transfer, time to evolve?'
    if ARGS.evolve:
        NUM_EVOLVE += INV.candies[key] / pokedex.evolves[key]

if ARGS.evolve:
    print 'Evolvable: {}'.format(NUM_EVOLVE)

# for flavour in GELATO:
#     SESSION.releasePokemon(flavour)
