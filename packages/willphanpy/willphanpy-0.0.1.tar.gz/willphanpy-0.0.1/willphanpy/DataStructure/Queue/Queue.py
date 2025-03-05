class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class Queue:
    def __init__(self):
        self.__front = None
        self.__tail = None

    def getFront(self):
        if(self.__front is not None):
            return self.__front.data
        
        return False

    def enqueue(self, data):
        if(self.__front is None):
            self.__front = Node(data)
            return True
        else:
            current = self.__front
            previous = None
            while(current is not None):
                previous = current
                current = current.next

            previous.next = Node(data)
            return True
        return False

    def dequeue(self):
        frontData = self.__front.data
        self.__front = self.__front.next
        return frontData

    def pritnQueue(self):
        current = self.__front
        while(current is not None):
            print(current.data)
            current = current.next

    def size(self):
        count = 0
        current = self.__front
        while(current is not None):
            count += 1
            current = current.next
        return count
    
    def isEmpty(self):
        if(self.size() == 0):
            return True
        return False