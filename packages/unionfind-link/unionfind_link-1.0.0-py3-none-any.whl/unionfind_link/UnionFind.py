# -*- coding: utf-8 -*-
#############################################
# File Name: UnionFind.py
# Author: Basti.YourDeveloper
# Mail: Basti.YourDeveloper@gmail.com
# Created Time:  2025-02-21
#
# Version-History:
# ================
# 2025-02-22    1.0.0    Basti  START: using parent linking as reverse-tree
#                               ADD: return None in find(), if not yet inserted
#                                 Cause then can test if not yet inside at all. No need for parallel list.
#                                 Use findOrCreate() if this feature is not necessary. 
#############################################

class UnionFind(object):
    def __init__(self):
        self.parents = dict()
        self.rank = dict()

    def copy(self):
        ret:UnionFind = UnionFind()
        ret.parents = self.parents.copy()
        ret.rank = self.rank.copy()
        return ret

    def isInserted(self, x):
        return x not in self.parents

    def add(self, x):
        if x not in self.parents:
            self.parents[x] = x
            self.rank[x] = 0
            return True
        else:
            return False

    def find(self, x):
        if x not in self.parents:
            return None
        if self.parents[x] == x:
            return x
        self.parents[x] = self.find(self.parents[x])
        return self.parents[x]

    def findOrCreate(self, x):
        root = self.find(x)
        if (root == None):
            self.add(x)
            root = x
        return root

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root == None: 
            raise SystemError("x is mandatory to be inside, please use add(x) for adding root-set initial before!")

        if y_root == None:
            self.parents[y] = x_root
            return x_root

        if x_root == y_root:
            return x_root

        self.parents[y_root] = x_root

        return x_root

        # FIXME: impl rank-ordering for equaly ordered tree
        # FIXME: use increasing children

        
    def connected(self, x, y):
        return self.find(x) == self.find(y)


    # the obj's in the unionfind need to impl print() as string-return
    def print(self, root):
        ret = ""
        ret += root.print()
        for x in self.parents:
            if (x == root): continue
            if (root == self.find(x)):
                ret += "; "
                ret += x.print()
        return ret

