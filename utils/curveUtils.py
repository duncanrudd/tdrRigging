import pymel.core as pm

def curveThroughPoints(name, positions=None, degree=3, bezier=0, rebuild=1):
    if not positions:
        positions = [pm.xform(p, q=1, ws=1, t=1) for p in pmc.selected()]

    if len(positions) < (degree + 1):
        return 'Please supply at least 4 points'

    # create the curve
    knots = range(len(positions) + degree - 1)

    crv = pm.curve(p=positions, k=knots, d=degree, name=name)
    if rebuild:
        pm.rebuildCurve(crv, ch=0, rpo=1, kr=0, kcp=1, d=degree)
    return crv