from Tree import Tree, Node
import random

tree = Tree();
tree.insert(0)

def minimax(current, pos, isMax):
    if(pos == 0):
        return random.randint(-10, 10)
    
    if isMax:
        maxVal = -float("inf")

        current.left = Node(0)
        eval = minimax(current.left, pos - 1, False)
        maxVal = max(maxVal, eval)

        current.right = Node(0)
        eval = minimax(current.right, pos - 1, False)
        maxVal = max(maxVal, eval)

        current.data = maxVal
        return maxVal

    else:
        minVal = float("inf")

        current.left = Node(0)
        eval = minimax(current.left, pos - 1, True)
        minVal = min(minVal, eval)

        current.right = Node(0)
        eval = minimax(current.right, pos - 1, True)
        minVal = min(minVal, eval)

        current.data = minVal
        return minVal

minimax(tree.getRoot(), 3, True)

tree.inorder(tree.getRoot())