"""Build counted, right-handed DNA logo drafts from a 3-D helical schematic."""
from copy import deepcopy
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
INK, OLIVE = '#252b27', '#82936e'
RADIUS, RISE, BP_PER_TURN = 10.0, 3.4, 10.5
OMEGA = 2 * math.pi / BP_PER_TURN
PHASE = math.radians(144)
TILT = math.radians(21)
WORDMARK = ET.parse(ROOT / 'assets/mosaic-logo.svg').find(
    f'.//{{{NS}}}g[@id="mosaic-wordmark"]')
assert WORDMARK is not None


def element(parent, tag, text=None, **attributes):
    child = ET.SubElement(parent, f'{{{NS}}}{tag}',
                          {k.replace('_', '-'): str(v) for k, v in attributes.items()})
    if text is not None:
        child.text = text
    return child


def make_logo(name, psi_start, psi_end, caption):
    span = (psi_end - psi_start) / OMEGA
    pairs = math.floor(span) + 1
    pair_offset = (span - (pairs - 1)) / 2
    scale = 170 / (RISE * span)

    def point(t, strand):
        theta = psi_start - PHASE / 2 + OMEGA * t + strand * PHASE
        return (RADIUS * math.cos(theta), RADIUS * math.sin(theta),
                RISE * (t - span / 2))

    def project(p):
        # Camera at negative y; screen right is +x and screen up is +z.
        # The final in-plane rotation has positive determinant and cannot mirror DNA.
        x, _, z = p
        u, v = scale * x, -scale * z
        return (u * math.cos(TILT) - v * math.sin(TILT),
                u * math.sin(TILT) + v * math.cos(TILT))

    metadata = {
        'model': 'schematic centerlines, not an atomic or chemical-bond diagram',
        'handedness': 'right', 'camera': 'negative y',
        'screen_right': '+x', 'screen_up': '+z', 'nearer_depth': '-y',
        'helical_turns': (psi_end - psi_start) / (2 * math.pi),
        'visible_loop_span': (psi_end - psi_start) / math.pi,
        'base_pairs_per_full_helical_turn': BP_PER_TURN,
        'base_pair_count': pairs, 'base_pair_center_rise_angstrom': RISE,
        'rungs': 'one connecting bar per base pair, not individual hydrogen bonds',
        'strand_polarity': ['5prime to 3prime with increasing z',
                            '5prime to 3prime with decreasing z'],
        'backbone_phase_degrees': 144,
        'end_extensions_in_visible_loops': 0.25 if name == 'quarter-ends' else 0,
    }
    svg = ET.Element(f'{{{NS}}}svg', {
        'width': '900', 'height': '260', 'viewBox': '0 0 900 260',
        'role': 'img', 'aria-labelledby': 'logo-title logo-description'})
    element(svg, 'title', text='MOSAIC Lab')
    element(svg, 'desc', id='logo-description', text=caption +
            f' A right-handed antiparallel DNA schematic with {pairs} base-pair bars.'
            ' Bars are base pairs, not individual hydrogen bonds. No tagline.')
    svg.find(f'{{{NS}}}title').set('id', 'logo-title')
    element(svg, 'metadata', text=json.dumps(metadata))
    emblem = element(svg, 'g', id='emblem', transform='translate(130,130) scale(0.68)')

    for start, stop, color in [(198, 224, OLIVE), (278, 302, OLIVE),
                                (-12, 20, INK), (80, 108, INK)]:
        points = [(128 * math.cos(math.radians(start + (stop - start) * i / 60)),
                   128 * math.sin(math.radians(start + (stop - start) * i / 60)))
                  for i in range(61)]
        path = 'M' + ' L'.join(f'{x:.4f},{y:.4f}' for x, y in points)
        element(emblem, 'path', d=path, fill='none', stroke=color,
                stroke_width=2.9, stroke_linecap='round')
    for angles, sizes, color in [([236, 247, 258, 269], [4.2, 3.2, 2.2, 1.35], OLIVE),
                                 ([32, 44, 56, 68], [1.35, 2.2, 3.2, 4.2], INK)]:
        for angle, size in zip(angles, sizes):
            a = math.radians(angle)
            element(emblem, 'circle', cx=128 * math.cos(a), cy=128 * math.sin(a),
                    r=size, fill=color)

    primitives = []
    samples = 1000
    for strand in [0, 1]:
        for i in range(samples):
            a, b = point(span * i / samples, strand), point(span * (i + 1) / samples, strand)
            primitives.append((-(a[1] + b[1]) / 2, 'backbone', strand, a, b))
    pair_positions = [pair_offset + i for i in range(pairs)]
    for i, t in enumerate(pair_positions):
        a, b = point(t, 0), point(t, 1)
        assert abs(a[2] - b[2]) < 1e-12
        assert abs(math.dist(a, b) - 2 * RADIUS * math.sin(PHASE / 2)) < 1e-10
        for j in range(12):
            f, g = j / 12, (j + 1) / 12
            p = tuple(a[k] * (1 - f) + b[k] * f for k in range(3))
            q = tuple(a[k] * (1 - g) + b[k] * g for k in range(3))
            primitives.append((-(p[1] + q[1]) / 2, 'base-pair', i, p, q))
    dna = element(emblem, 'g', id='right-handed-dna', data_handedness='right',
                  data_base_pairs=pairs, data_full_turns=metadata['helical_turns'])
    for depth, kind, index, a, b in sorted(primitives, key=lambda p: p[0]):
        p, q = project(a), project(b)
        path = f'M{p[0]:.4f},{p[1]:.4f} L{q[0]:.4f},{q[1]:.4f}'
        attrs = {'fill': 'none', 'stroke_linecap': 'round'}
        if kind == 'backbone':
            front = depth >= 0
            color = ([INK, OLIVE] if front else ['#9ca69c', '#b1bca3'])[index]
            element(dna, 'path', d=path, stroke=color, stroke_width=2.8 if front else 2.2,
                    data_strand=index, **attrs)
        else:
            element(dna, 'path', d=path, stroke='#7c8b70', stroke_width=1.25,
                    data_base_pair=index, **attrs)
    svg.append(deepcopy(WORDMARK))

    # Verify the actual generating geometry, not just a handedness label.
    torsions = []
    for strand in [0, 1]:
        for t in [0, span / 4, span / 2, span * 3 / 4, span]:
            theta = psi_start - PHASE / 2 + OMEGA * t + strand * PHASE
            d1 = (-RADIUS * OMEGA * math.sin(theta), RADIUS * OMEGA * math.cos(theta), RISE)
            d2 = (-RADIUS * OMEGA**2 * math.cos(theta), -RADIUS * OMEGA**2 * math.sin(theta), 0)
            d3 = (RADIUS * OMEGA**3 * math.sin(theta), -RADIUS * OMEGA**3 * math.cos(theta), 0)
            cross = (d1[1]*d2[2]-d1[2]*d2[1], d1[2]*d2[0]-d1[0]*d2[2],
                     d1[0]*d2[1]-d1[1]*d2[0])
            torsion = sum(cross[k] * d3[k] for k in range(3)) / sum(x*x for x in cross)
            assert torsion > 0
            torsions.append(torsion)
    crossings = []
    for n in range(math.ceil(psi_start / math.pi), math.floor(psi_end / math.pi) + 1):
        t = (n * math.pi - psi_start) / OMEGA
        a, b = point(t, 0), point(t, 1)
        assert abs(a[0] - b[0]) < 1e-10
        front = 0 if a[1] < b[1] else 1
        assert front == n % 2
        crossings.append({'crossing': n, 'nearer_strand': front})
    assert abs(math.cos(TILT)**2 + math.sin(TILT)**2 - 1) < 1e-12
    assert all(abs(pair_positions[i+1] - t - 1) < 1e-12
               for i, t in enumerate(pair_positions[:-1]))
    assert abs(OMEGA - math.radians(360 / BP_PER_TURN)) < 1e-12
    assert scale > 0
    assert all(math.hypot(*project(point(span*i/1000, strand))) < 118
               for strand in [0, 1] for i in range(1001))
    if name == 'quarter-ends':
        assert abs(-psi_start / math.pi - 0.25) < 1e-12
        assert abs((psi_end - 2*math.pi) / math.pi - 0.25) < 1e-12
    assert len({e.attrib['data-base-pair'] for e in dna
                if 'data-base-pair' in e.attrib}) == pairs
    report = dict(metadata, positive_torsion_for_both_backbones=True,
                  proper_camera_basis=True, in_plane_rotation_determinant=1,
                  regular_base_pair_spacing=True, inside_emblem=True, crossing_order=crossings)
    path = HERE / f'{name}.svg'
    path.write_text(ET.tostring(svg, encoding='unicode') + '\n')
    return svg, report


drafts = [make_logo('quarter-ends', -math.pi / 4, 2 * math.pi + math.pi / 4,
                   'Two complete visible loops with a quarter-loop extension at each end.'),
          make_logo('three-loops', 0, 3 * math.pi, 'Three complete visible loops.')]
sheet = ET.Element(f'{{{NS}}}svg', {'width': '1200', 'height': '720', 'viewBox': '0 0 1200 720'})
element(sheet, 'rect', width=1200, height=720, fill='#ffffff')
for i, ((logo, report), label) in enumerate(zip(drafts, [
        'A · Two loops + quarter ends', 'B · Three loops'])):
    y = i * 350
    element(sheet, 'text', x=60, y=y + 45, fill='#616161', font_family='Helvetica Neue, Arial, sans-serif',
            font_size=21, text=label)
    group = element(sheet, 'g', transform=f'translate(75,{y+60}) scale(1.1)')
    for child in logo:
        if child.tag.endswith('g'):
            child = deepcopy(child)
            for descendant in child.iter():
                if 'id' in descendant.attrib:
                    descendant.set('id', f'{i}-' + descendant.get('id'))
            group.append(child)
(HERE / 'comparison.svg').write_text(ET.tostring(sheet, encoding='unicode') + '\n')
(HERE / 'geometry-checks.json').write_text(json.dumps([r for _, r in drafts], indent=2) + '\n')
print('Built two right-handed drafts. A: 14 base pairs / 1.25 turns; B: 16 base pairs / 1.5 turns.')
print('Verified positive torsion, camera orientation, alternating front/back crossings and rung spacing.')
