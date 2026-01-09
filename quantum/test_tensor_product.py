from quantum.yatra_core import S60
from quantum.yatra_math import S60Math

def test_tensor_product_1d():
    print("🧪 Testing 1D Tensor Product...")
    v1 = [S60(1), S60(0)]
    v2 = [S60(0), S60(1)]
    
    # |0> x |1> = |01> = [0, 1, 0, 0]
    expected = [S60(0), S60(1), S60(0), S60(0)]
    result = S60Math.tensor_product(v1, v2)
    
    for r, e in zip(result, expected):
        assert r == e, f"Expected {e}, got {r}"
    print("✅ 1D Tensor Product OK")

def test_tensor_product_2d():
    print("🧪 Testing 2D Tensor Product...")
    # I matrix (2x2)
    I = [[S60(1), S60(0)], [S60(0), S60(1)]]
    # X matrix (2x2)
    X = [[S60(0), S60(1)], [S60(1), S60(0)]]
    
    # I x X = [ [0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0] ]
    expected = [
        [S60(0), S60(1), S60(0), S60(0)],
        [S60(1), S60(0), S60(0), S60(0)],
        [S60(0), S60(0), S60(0), S60(1)],
        [S60(0), S60(0), S60(1), S60(0)]
    ]
    
    result = S60Math.tensor_product(I, X)
    
    for i in range(4):
        for j in range(4):
            assert result[i][j] == expected[i][j], f"At [{i}][{j}]: expected {expected[i][j]}, got {result[i][j]}"
    print("✅ 2D Tensor Product OK")

if __name__ == "__main__":
    try:
        test_tensor_product_1d()
        test_tensor_product_2d()
        print("\n🏆 ALL TENSOR PRODUCT TESTS PASSED")
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
