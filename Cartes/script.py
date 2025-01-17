#!/usr/bin/env python

import csv
import os
import shutil
import weasyprint
from collections import namedtuple
from jinja2 import Template


if os.path.exists('./Rendus'):
    shutil.rmtree('./Rendus')
os.mkdir('./Rendus')

with open('_carte.html') as fd:
    html = Template(fd.read())

Card = namedtuple('Card', [
    'title', 'text', 'material', 'value', 'ma_points', 'sp_points',
    'mi_points', 'type'])


filenames = []
for filename in os.listdir('.'):
    if not filename.startswith('_') and filename.endswith('.csv'):
        symbol, name = filename.split(' ', 1)
        name = name[:-4]
        with open(filename) as fd:
            reader = csv.reader(fd)
            next(reader)
            for i, line in enumerate(reader):
                code = '%s%02i' % (symbol, i + 1)
                if line[-1] == '5':
                    line.append('Mission princière')
                elif line[-1] == '7':
                    line.append('Mission royale')
                else:
                    if line[1] and line[2]:
                        line.append('Action/Matériau')
                    elif line[2]:
                        line.append('Matériau')
                        line[2] = line[0]
                    elif line[-2] == 'x':
                        line.append('Action')
                    else:
                        line.append('Spéciale')
                card = Card(*line)
                variables = dict(
                    (key, value if value != 'x' else '')
                    for key, value in card._asdict().items())
                variables['i'] = i + 1
                variables['code'] = code
                variables['symbol'] = symbol
                output_filename = (
                    '%s - %s' % (code, variables['title'])
                    if variables['title'] else code)
                filenames.append(output_filename + '.png')
                output_file = os.path.join('Rendus', output_filename)
                print('Rendu de %s' % output_filename)
                with open(output_file + '.html', 'w') as fd:
                    fd.write(html.render(**variables))
                weasy = weasyprint.HTML(output_file + '.html')
                weasy.write_png(output_file + '.png', resolution=30)


for back_type in ('missions', 'autres'):
    print('Rendu du dos %s' % back_type)
    filename = '_dos_%s.html' % back_type
    weasy = weasyprint.HTML(filename)
    weasy.write_png(
        os.path.join('Rendus', 'dos_%s.png' % back_type), resolution=30)


cards_filename = os.path.join('Rendus', 'cartes.html')
with open('_cartes.html') as fd:
    cards_html = Template(fd.read())
with open(cards_filename, 'w') as fd:
    fd.write(cards_html.render(filenames=filenames))
weasy = weasyprint.HTML(cards_filename)
weasy.write_pdf(cards_filename.replace('.html', '.pdf'))
