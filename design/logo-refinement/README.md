# Counted DNA logo drafts

Option A (`quarter-ends.svg`) is the approved website logo. The alternate draft is retained for reference. The installed light version is an exact copy of A; the dark version changes only colours. Browser icons use its emblem with thicker strokes for small sizes.

The installed helix is approximately 12% larger within the emblem and uses stronger strokes for clarity at the website's 420 px logo width. Each uninterrupted front/rear backbone curve is drawn as a continuous path to avoid the graininess caused by antialiasing many separate short strokes. The physical proportions, turn count and base-pair spacing are preserved.

- `quarter-ends.svg`: two complete visible loops plus a quarter-loop at each end; 1.25 full helical turns with 14 base-pair bars.
- `three-loops.svg`: three complete visible loops; 1.5 full helical turns with 16 base-pair bars.
- `comparison.png`: visual comparison of the two drafts.
- `installed-preview.png`: the installed logo on light and dark backgrounds.

Each visible loop corresponds to a half-turn in this projection. A bar represents a base pair, not an individual hydrogen bond. The schematic does not depict base identities or atomic bonding. Base-pair centers are spaced by one model residue, with 10.5 residues per full turn and a 3.4 angstrom axial rise. The first and last bars are inset symmetrically from the backbone endpoints.

Both backbone curves have positive signed torsion in a right-handed coordinate system. The camera is on negative y, with screen right along positive x and screen up along positive z. Rotation and scale do not reflect the projection. Near/far strand crossings alternate correctly. The two strand polarities are opposite; chemical-direction labels and atoms are omitted from the logo. A stylized phase offset suggests unequal groove spacing without claiming atomic detail.

`geometry-checks.json` records the checked model parameters. `build_refinements.py` regenerates the SVGs and runs the geometry checks. It reuses the installed wordmark outlines. To render the comparison on macOS:

```bash
python3 design/logo-refinement/build_refinements.py
swift -module-cache-path /tmp/mosaic-swift-cache design/logo-refinement/render_preview.swift design/logo-refinement/comparison.svg design/logo-refinement/comparison.png
```

Scientific reference for the 10.5 base-pair helical periodicity: [Peck and Wang (1983), PNAS](https://doi.org/10.1073/pnas.80.20.6206).

`apply_option_a.py` installs A and produces the matching dark SVG and favicon SVG. Re-render the browser PNGs and rebuild the ICO after running it.
