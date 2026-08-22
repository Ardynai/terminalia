"""Smoke tests: terrain build, placement search, schema round-trip."""
import sys, tempfile, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terminalia.schema import World, WorldSpec, Terrain, Region
from terminalia.terrain import build_terrain


def test_terrain():
    ops = [
        {"op": "voronoi", "n": 3},
        {"op": "mountains", "height_m": 150.0},
        {"op": "coast", "sea_level_m": 10.0},
        {"op": "normalize", "min_m": 0.0, "max_m": 200.0},
    ]
    g = build_terrain(ops, size=256, seed=7)
    assert g.height.shape == (256, 256)
    assert 0 <= g.height.min() and g.height.max() <= 200.5
    with tempfile.TemporaryDirectory() as td:
        p = g.save_heightmap(os.path.join(td, "hm.png"))
        assert os.path.exists(p)
    print("terrain OK")


def test_placement():
    from terminalia.place import find_placement, resolve_collisions
    g = build_terrain(
        [{"op": "fbm"}, {"op": "normalize", "min_m": 0, "max_m": 100}],
        size=256, seed=3)
    p = find_placement(g.height, 128, 128, 60, 6,
                       meters_per_pixel=2.0, n_tries=30, min_contact=0.4)
    assert p is not None, "no placement found on gentle terrain"
    assert 0 <= p.contact_ratio <= 1.0
    issues = resolve_collisions([
        {"id": "a", "pos_xy": (100, 100), "radius_m": 5},
        {"id": "b", "pos_xy": (102, 101), "radius_m": 5}], min_gap_m=2)
    assert len(issues) >= 1, "expected collision detection"
    print("placement OK")


def test_schema_roundtrip():
    w = World(spec=WorldSpec(prompt="test island"))
    w.terrain = Terrain(heightmap="hm.png", regions=[Region(name="a", mask="m.png", biome="b")])
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "world.json")
        w.save(p)
        w2 = World.load(p)
        assert w2.spec.prompt == "test island"
        assert w2.terrain.regions[0].name == "a"
    print("schema OK")


if __name__ == "__main__":
    test_terrain()
    test_placement()
    test_schema_roundtrip()
    print("\nALL TESTS PASS")
