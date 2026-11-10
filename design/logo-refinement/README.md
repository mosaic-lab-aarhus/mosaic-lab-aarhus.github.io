# Counted DNA logo drafts

These are design previews based on the chosen open-circle concept. The website's active logo is separate.

- `quarter-ends.svg`: two complete visible loops plus a quarter-loop at each end; 1.25 full helical turns with 14 base-pair bars.
- `three-loops.svg`: three complete visible loops; 1.5 full helical turns with 16 base-pair bars.
- `comparison.png`: side-by-side-in-sequence visual comparison of the two drafts.

Each visible loop corresponds to a half-turn in this projection. A bar represents a base pair, not an individual hydrogen bond. The schematic does not depict base identities or atomic bonding. Base-pair centers are spaced by one model residue, with 10.5 residues per full turn and a 3.4 angstrom axial rise. The first and last bars are inset symmetrically from the backbone endpoints.

Both backbone curves have positive signed torsion in a right-handed coordinate system. The camera is on negative y, with screen right along positive x and screen up along positive z. Rotation and scale do not reflect the projection. Near/far strand crossings alternate correctly. The two strand polarities are opposite; chemical-direction labels and atoms are omitted from the logo. A stylized phase offset suggests unequal groove spacing without claiming atomic detail.

`geometry-checks.json` records the checked model parameters. `build_refinements.py` regenerates the SVGs and runs the geometry checks. It reuses the installed wordmark outlines. To render the comparison on macOS:

```bash
python3 design/logo-refinement/build_refinements.py
swift -module-cache-path /tmp/mosaic-swift-cache design/logo-refinement/render_preview.swift design/logo-refinement/comparison.svg design/logo-refinement/comparison.png
```

Scientific reference for the 10.5 base-pair helical periodicity: [Peck and Wang (1983), PNAS](https://doi.org/10.1073/pnas.80.20.6206).
