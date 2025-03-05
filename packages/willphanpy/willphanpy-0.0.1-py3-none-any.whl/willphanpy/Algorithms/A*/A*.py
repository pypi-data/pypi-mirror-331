import heapq

# Define graph features
class Graph:
    def __init__(self):
        self.adjacency_list = {}

class Vertex:
    def __init__(self, v):
        self.value = v

class Edge:
    def __init__(self, d, v):
        self.distance = d
        self.vertex = v

graph = Graph()
graph.adjacency_list = {
    'S': [Edge(2, 'A'), Edge(3, 'B')],
    'A': [Edge(3, 'C'), Edge(3, 'H')],
    'B': [Edge(3, 'D'), Edge(1, 'C')],
    'C': [Edge(1, 'D'), Edge(3, 'E')],
    'D': [Edge(2, 'F')],
    'E': [Edge(2, 'G')],
    'F': [Edge(1, 'G')],
    'H': [Edge(4, 'C'), Edge(4, 'L'), Edge(7, 'M')],
    'L': [Edge(6, 'E')],
    'M': [Edge(6, 'L')],
    'G': []
}
graph_heuristics = {
    'S': 6,
    'A': 4,
    'B': 4,
    'C': 4,
    'D': 3.5,
    'E': 1,
    'F': 1,
    'H': 5,
    'L': 7,
    'M': 12,
    'G': 0
}

def A_star(graph, heuristics, start, end):
    previous = {v: None for v in graph.adjacency_list.keys()} # space O(V), time O(V)
    visited = {v: False for v in graph.adjacency_list.keys()} # space O(V) time O(V)
    distances = {v: float("inf") for v in graph.adjacency_list.keys()} # space O(V), time O(V)
    distances[start] = 0

    priority_queue = [] # space O(V)
    heapq.heappush(priority_queue, (heuristics[start] + 0, start))

    while priority_queue:
        removed_f, removed = heapq.heappop(priority_queue)
        visited[removed] = True

        # when reaching the goal state, return
        if(removed == end ): 
            return previous, distances

        for edge in graph.adjacency_list[removed]:
            vertex = edge.vertex
            if(visited[edge.vertex]):
                continue
            new_f = (removed_f - heuristics[removed]) + edge.distance + heuristics[vertex]
            new_distance = new_f - heuristics[vertex]
            if new_distance < distances[vertex]:
                distances[vertex] = new_distance
                previous[vertex] = removed
                heapq.heappush(priority_queue, (new_f, vertex))

    # return previous, distances

prev, dist = A_star(graph, graph_heuristics, 'S', 'G')

print(prev)
print("Total cost: " + str(dist['G']))

def path(prev, start, end):
    r = []
    r.append(end)
    while(True):
        end = prev[end]
        r.append(end)
        if(end == start):
            break
    
    r.reverse()
    return r

r = path(prev, 'S', 'G')
print(r)