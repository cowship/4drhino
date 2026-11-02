import pytest
from fourd.geometry import Point4D, Vector4D

def test_vector4d_magnitude():
    v = Vector4D(2,3,6,6)
    magnitude = v.magnitude()
    assert magnitude == pytest.approx((2**2 + 3**2 + 6**2 + 6**2)**0.5)