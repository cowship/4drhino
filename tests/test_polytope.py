import math
from itertools import product

import pytest

from fourd.geometry import Point4D, Vector4D
from fourd.matrix import Matrix4D
from fourd.polytope import Polytope, Tesseract
from fourd.rotation import Rotation4D

# polytope.py에 정의된 Polytope, Tesseract 클래스에 대한 테스트 케이스


def coords(point):
    return tuple(point.data)


def edge_lengths(polytope):
    return [a.distance_to(b) for a, b in polytope.edge_segments()]


# 테서랙트 (Tesseract) 기본 구조 테스트

# 꼭짓점 16개, 모서리 32개 (plan.md 검증 항목)
def test_tesseract_counts():
    t = Tesseract()
    assert t.vertex_count() == 16
    assert t.edge_count() == 32


# 꼭짓점이 (+-1, +-1, +-1, +-1)의 모든 조합과 정확히 일치하는지(중복 없음)
def test_tesseract_vertices_are_all_sign_combinations():
    t = Tesseract()
    actual = sorted(coords(v) for v in t.vertices)
    expected = sorted(tuple(float(c) for c in combo) for combo in product([-1, 1], repeat=4))
    assert actual == expected


# 모서리가 중복 없이 32개인지
def test_tesseract_edges_are_unique():
    t = Tesseract()
    assert len(set(t.edges)) == 32
    assert all(i < j for i, j in t.edges)


# 모든 모서리가 좌표 하나만 다른 두 꼭짓점을 잇는지(대각선 없음)
def test_tesseract_edges_differ_in_exactly_one_coordinate():
    t = Tesseract()
    for a, b in t.edge_segments():
        differences = sum(1 for k in range(4) if a.data[k] != b.data[k])
        assert differences == 1


# 좌표 하나만 다른 꼭짓점 쌍은 빠짐없이 모서리인지
def test_tesseract_has_every_adjacent_pair():
    t = Tesseract()
    edge_set = set(t.edges)
    for i in range(16):
        for j in range(i + 1, 16):
            a, b = t.vertices[i], t.vertices[j]
            adjacent = sum(1 for k in range(4) if a.data[k] != b.data[k]) == 1
            assert ((i, j) in edge_set) == adjacent


# 모든 모서리의 길이가 한 변의 길이와 같은지
@pytest.mark.parametrize("size", [2.0, 1, 3.5])
def test_tesseract_edge_lengths_equal_size(size):
    t = Tesseract(size=size)
    for length in edge_lengths(t):
        assert length == pytest.approx(size)


# 각 꼭짓점에 모서리 4개가 연결되는지 (x, y, z, w 방향 각각 하나)
def test_tesseract_each_vertex_has_four_neighbors():
    t = Tesseract()
    for i in range(16):
        assert len(t.neighbors(i)) == 4


# 모든 꼭짓점이 중심에서 같은 거리(size * sqrt(4) / 2 = size)에 있는지
def test_tesseract_vertices_equidistant_from_center():
    center = Point4D([1, -2, 0.5, 3])
    t = Tesseract(size=3.0, center=center)
    for v in t.vertices:
        assert v.distance_to(center) == pytest.approx(3.0)


# 중심 지정 시 무게중심이 그 중심과 같은지
def test_tesseract_centroid_matches_center():
    center = Point4D([1, -2, 0.5, 3])
    t = Tesseract(center=center)
    assert coords(t.centroid()) == pytest.approx(coords(center))


# 크기가 바뀌면 좌표가 +-size/2가 되는지
def test_tesseract_size_scales_coordinates():
    t = Tesseract(size=5)
    for v in t.vertices:
        for c in v.data:
            assert abs(c) == pytest.approx(2.5)


# 테서랙트와 회전

# 회전 후에도 모서리 길이가 보존되는지
@pytest.mark.parametrize("plane", ["xy", "xz", "xw", "yz", "yw", "zw"])
def test_rotation_preserves_edge_lengths(plane):
    t = Tesseract()
    rotated = t.transform(Rotation4D.coordinate_plane(plane, 0.7, 0.3).get_rotation_matrix())
    for length in edge_lengths(rotated):
        assert length == pytest.approx(2.0)


# 회전 후에도 모서리 연결 관계가 그대로인지
def test_rotation_preserves_connectivity():
    t = Tesseract()
    rotation = Rotation4D(Vector4D([1, 2, 0, 1]), Vector4D([0, 1, 3, -1]), 0.5, -1.2)
    rotated = t.transform(rotation.get_rotation_matrix())
    assert rotated.edges == t.edges
    assert rotated.vertex_count() == 16


# 회전된 꼭짓점이 각 꼭짓점을 직접 회전한 결과와 같은지
def test_transform_matches_rotate_point():
    t = Tesseract()
    rotation = Rotation4D.coordinate_plane("xw", math.pi / 6)
    rotated = t.transform(rotation.get_rotation_matrix())
    for original, moved in zip(t.vertices, rotated.vertices):
        assert coords(moved) == pytest.approx(coords(rotation.rotate_point(original)))


# xw 평면 90도 회전 후 꼭짓점 집합이 원래와 같은지(테서랙트의 대칭성)
def test_quarter_turn_maps_tesseract_onto_itself():
    t = Tesseract()
    rotated = t.transform(Rotation4D.coordinate_plane("xw", math.pi / 2).get_rotation_matrix())
    rounded = sorted(tuple(round(c, 9) + 0.0 for c in v.data) for v in rotated.vertices)
    assert rounded == sorted(coords(v) for v in t.vertices)


# 변환이 원본 도형을 바꾸지 않는지
def test_transform_does_not_modify_original():
    t = Tesseract()
    before = [coords(v) for v in t.vertices]
    t.transform(Rotation4D.coordinate_plane("xw", 1.0).get_rotation_matrix())
    t.translate(Vector4D([1, 1, 1, 1]))
    assert [coords(v) for v in t.vertices] == before


# 평행이동이 모든 꼭짓점과 무게중심을 옮기는지
def test_translate_moves_every_vertex():
    t = Tesseract()
    moved = t.translate(Vector4D([1, 2, 3, 4]))
    for a, b in zip(t.vertices, moved.vertices):
        assert (b - a).data == [1, 2, 3, 4]
    assert coords(moved.centroid()) == pytest.approx((1, 2, 3, 4))
    assert moved.edges == t.edges


# 일반 Polytope 테스트

# 직접 정의한 도형(삼각형)과 모서리 정규화
def test_polytope_custom_shape():
    vertices = [Point4D([0, 0, 0, 0]), Point4D([1, 0, 0, 0]), Point4D([0, 1, 0, 0])]
    p = Polytope(vertices, [(0, 1), (2, 1), [0, 2]])
    assert p.vertex_count() == 3
    assert p.edges == [(0, 1), (1, 2), (0, 2)]
    assert p.neighbors(1) == [0, 2]


# 생성자에 넘긴 리스트를 나중에 수정해도 도형이 바뀌지 않는지
def test_polytope_copies_input_vertices():
    vertices = [Point4D([0, 0, 0, 0]), Point4D([1, 0, 0, 0])]
    p = Polytope(vertices, [(0, 1)])
    vertices[0].data[0] = 99
    assert p.vertices[0].data[0] == 0


def test_polytope_invalid_vertices():
    with pytest.raises(TypeError):
        Polytope([[0, 0, 0, 0]], [])
    with pytest.raises(TypeError):
        Polytope("not a list", [])


def test_polytope_invalid_edges():
    vertices = [Point4D([0, 0, 0, 0]), Point4D([1, 0, 0, 0])]
    with pytest.raises(TypeError):
        Polytope(vertices, [(0, 1, 2)])
    with pytest.raises(TypeError):
        Polytope(vertices, [(0, "1")])
    with pytest.raises(TypeError):
        Polytope(vertices, [(0.0, 1)])
    with pytest.raises(IndexError):
        Polytope(vertices, [(0, 2)])
    with pytest.raises(ValueError):
        Polytope(vertices, [(1, 1)])
    with pytest.raises(ValueError):
        Polytope(vertices, [(0, 1), (1, 0)])


def test_polytope_invalid_transform_arguments():
    t = Tesseract()
    with pytest.raises(TypeError):
        t.transform(Rotation4D.coordinate_plane("xy", 0.5))
    with pytest.raises(TypeError):
        t.translate(Point4D([1, 0, 0, 0]))


def test_polytope_neighbors_out_of_range():
    with pytest.raises(IndexError):
        Tesseract().neighbors(16)


def test_empty_polytope_centroid_raises():
    with pytest.raises(ValueError):
        Polytope([], []).centroid()


def test_tesseract_invalid_arguments():
    with pytest.raises(ValueError):
        Tesseract(size=0)
    with pytest.raises(ValueError):
        Tesseract(size=-1)
    with pytest.raises(TypeError):
        Tesseract(size="2")
    with pytest.raises(TypeError):
        Tesseract(center=[0, 0, 0, 0])


def test_repr():
    assert repr(Tesseract()) == "Tesseract(16 vertices, 32 edges)"
