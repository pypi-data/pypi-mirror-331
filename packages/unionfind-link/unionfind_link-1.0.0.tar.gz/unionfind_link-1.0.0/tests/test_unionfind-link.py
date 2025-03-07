import unittest
from unionfind_link import UnionFind

class TestCore(unittest.TestCase):
    def test_simple(self):
        # = test union path
        uf = UnionFind()
        uf.union(1, 2)
        uf.union(3, 4)
        uf.union(5, 6)
        uf.union(1, 3)
        uf.union(6, 4)

        assert uf.connected(1, 6)


    def test_withNone(self):
        uf = UnionFind()
        root = uf.find(1)
        assert root == None

        try:
            uf.union(1, 2)
        except:
            uf.add(1)

        assert not uf.connected(1,2)
        uf.union(1,2)
        assert uf.connected(1,2)


    def test_withoutNone(self):
        uf = UnionFind()
        uf.findOrCreate(1)
        uf.union(1,2)
        assert uf.connected(1,2)



if __name__ == "__main__":
    unittest.main()

