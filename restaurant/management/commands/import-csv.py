# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
#from optparse import make_option

import csv

from restaurant.models import Restaurant

MIN_FIELD_LEN = 3

VG_TAGS = {
        'Sans gluten': 'gluten-free',
        'Végé': 'vegetarian',
        'Vegan': 'vegan',
        'Vegan-friendly': 'vegan-friendly'
        }

def parse_vg_tags(tags):
    result = set()

    for t in map(str.strip, tags.split('/')):
        # All restaurants are supposed to be at least vg friendly
        if t == 'Végé-friendly':
            continue

        try:
            result.add(VG_TAGS[t])
        except KeyError:
            print "WARNING: Unknown tag %s" % t

    return result

class Command(BaseCommand):
    args = '<csv-file>'

    def handle(self, *args, **options):
        Restaurant.objects.all().delete()

        with open(args[0], 'rb') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # clean up
                for k, v in row.items():
                    if v == '?' or len(v) < MIN_FIELD_LEN:
                        # discard
                        row[k] = None
                        continue

                    if k == 'Mail' and '@' not in v:
                        row[k] = None
                        continue

                    row[k] = v.strip()

                if not row['Nom'] or not row['Adresse']:
                    continue

                if row['Suivi'] is None or 'OK' not in row['Suivi']:
                    continue

                resto = Restaurant.create(row['Nom'], row['Adresse'], row['Site'], row['Téléphone'], row['Mail'], row['Personne de contact'], row['Suivi'], row['Personne responsable'])

                if row['Vg']:
                    tags = parse_vg_tags(row['Vg'])
                    resto.tags.add(' '.join(tags))
                    resto.save()
