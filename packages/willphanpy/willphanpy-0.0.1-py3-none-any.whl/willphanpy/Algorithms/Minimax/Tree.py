import Queue

class Node:
    def __init__(self, data):
        self.data = data
        self.left = None
        self.right = None
        self.visited = False
class Tree:
    def __init__(self):
        self.__root = None

    def insert(self, data):
        if(self.__root is None):
            self.__root = Node(data)
        else:
            current = self.__root
            parent = None
            while(current is not None):
                if(data < current.data):
                    parent = current
                    current = current.left
                elif(data > current.data):
                    parent = current
                    current = current.right
                else:
                    return False #duplicated data insert

            if(data < parent.data):
                parent.left = Node(data)
                return True # inserted successfully
            elif(data > parent.data):
                parent.right = Node(data)
                return True # inserted successfully
        return False
    
    def getRoot(self):
        return self.__root

    def inorder(self, current):
        if(current is not None):
            self.inorder(current.left)
            print(current.data)
            self.inorder(current.right)

    def preorder(self, current):
        if(current is not None):
            print(current.data)
            self.preorder(current.left)
            self.preorder(current.right)

    def postorder(self, current):
        if(current is not None):
            self.postorder(current.left)
            self.postorder(current.right)
            print(current.data)

    def BFS(self):
        queue = Queue()
        queue.enqueue(self.__root)

        while(not queue.isEmpty()):
            current = queue.dequeue();
            print(current.data)

            if(current.left is not None):
                queue.enqueue(current.left)
            if(current.right is not None):
                queue.enqueue(current.right)

    # This search is similar to preorder search
    def DFS(self):
        def DFS_helper(node):
            node.visited = True
            print(node.data)
            if(node.left is not None):
                if(not node.left.visited):
                    DFS_helper(node.left)
            if(node.right is not None):
                if(not node.right.visited):
                    DFS_helper(node.right)
        DFS_helper(self.__root)

