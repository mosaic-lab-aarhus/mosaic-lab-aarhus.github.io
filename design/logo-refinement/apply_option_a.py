"""Install the approved quarter-ended mark without altering its DNA geometry."""
from copy import deepcopy
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ASSETS = ROOT / 'assets'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)


def save(svg, path):
    path.write_text(ET.tostring(svg, encoding='unicode') + '\n')


approved = HERE / 'quarter-ends.svg'
light = ET.parse(approved).getroot()
model = json.loads(light.find(f'{{{NS}}}metadata').text)
assert model['handedness'] == 'right'
assert model['base_pair_count'] == 14
assert model['end_extensions_in_visible_loops'] == 0.25
(ASSETS / 'mosaic-logo.svg').write_bytes(approved.read_bytes())

palette = {'#252b27': '#ecf1e9', '#82936e': '#b7c6a3',
           '#9ca69c': '#98a59a', '#b1bca3': '#879776', '#7c8b70': '#a5b68d'}
dark = deepcopy(light)
for item in dark.iter():
    for attribute in ['stroke', 'fill']:
        if item.get(attribute) in palette:
            item.set(attribute, palette[item.get(attribute)])
save(dark, ASSETS / 'mosaic-logo-dark.svg')

favicon = ET.Element(f'{{{NS}}}svg', {'width': '64', 'height': '64', 'viewBox': '0 0 64 64'})
ET.SubElement(favicon, f'{{{NS}}}title').text = 'MOSAIC Lab'
ET.SubElement(favicon, f'{{{NS}}}metadata').text = json.dumps(model)
ET.SubElement(favicon, f'{{{NS}}}rect', {'width': '64', 'height': '64', 'rx': '13', 'fill': '#f7faf5'})
emblem = deepcopy(light.find(f'{{{NS}}}g[@id="emblem"]'))
assert emblem is not None
emblem.set('transform', 'translate(32,32) scale(0.21875)')
for item in emblem.iter():
    if item.get('stroke-width'):
        multiplier = 3.2 if 'data-strand' in item.attrib else 2.7
        item.set('stroke-width', str(float(item.get('stroke-width')) * multiplier))
    if item.tag == f'{{{NS}}}circle':
        item.set('r', str(float(item.get('r')) * 1.35))
favicon.append(emblem)
save(favicon, ASSETS / 'favicon.svg')

# Cache-busting URLs make the approved mark visible after the next deployment.
for page in ROOT.glob('*.html'):
    before = page.read_text()
    after = before
    pattern = r'(assets/(?:favicon\.ico|favicon\.svg|apple-touch-icon\.png|mosaic-logo\.svg|mosaic-logo-dark\.svg))(?:\?v=[^"\s]*)?(?=")'
    after = re.sub(pattern, lambda match: match.group(1) + '?v=logo-a-clearer', after)
    if after != before:
        page.write_text(after)

preview = ET.Element(f'{{{NS}}}svg', {'width': '1000', 'height': '600', 'viewBox': '0 0 1000 600'})
ET.SubElement(preview, f'{{{NS}}}rect', {'width': '1000', 'height': '300', 'fill': '#ffffff'})
ET.SubElement(preview, f'{{{NS}}}rect', {'y': '300', 'width': '1000', 'height': '300', 'fill': '#1c1c1d'})
for i, logo in enumerate([light, dark]):
    group = ET.SubElement(preview, f'{{{NS}}}g', {'transform': f'translate(50,{20 + 300*i})'})
    for child in logo:
        if child.tag == f'{{{NS}}}g':
            group.append(deepcopy(child))
save(preview, HERE / 'installed-preview.svg')

# Confirm the theme adaptation changed colours only.
for original, adapted in zip(light.iter(), dark.iter()):
    assert original.tag == adapted.tag
    for attr in ['d', 'transform', 'cx', 'cy', 'r', 'stroke-width']:
        assert original.get(attr) == adapted.get(attr)
for svg in [light, dark, favicon]:
    pairs = {item.get('data-base-pair') for item in svg.iter() if 'data-base-pair' in item.attrib}
    assert len(pairs) == 14
    assert json.loads(svg.find(f'{{{NS}}}metadata').text)['helical_turns'] == 1.25
print('Installed approved A unchanged; matched the dark logo and all browser-icon geometry.')
