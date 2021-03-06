# Import standard libraries
import ast
from sys import argv
from time import time
from cv2 import imshow, waitKey, resize
# Import custom-built classes
from utils.obstacle_space import Map
from utils.explorer import Explorer
from utils.node import Node

script, start_node_coords, goal_node_coords, robot_radius, clearance = argv

if __name__ == '__main__':
    start_time = time()
    # Convert arguments into their required data types
    start_node_coords = tuple(ast.literal_eval(start_node_coords))
    goal_node_coords = tuple(ast.literal_eval(goal_node_coords))
    robot_radius = int(ast.literal_eval(robot_radius))
    clearance = int(ast.literal_eval(clearance))
    obstacle_map = Map(robot_radius, clearance)
    # Initialize the explorer class
    explorer = Explorer(start_node_coords, goal_node_coords)
    # Check validity of start and goal nodes
    if not (obstacle_map.check_node_validity(start_node_coords[0], obstacle_map.height - start_node_coords[1] - 1)
            and obstacle_map.check_node_validity(goal_node_coords[0], obstacle_map.height - goal_node_coords[1] - 1)):
        print('One of the points lie in obstacle space!!\nPlease try again')
        quit()
    # Get the start node and add it to open nodes
    start_node = Node(start_node_coords, explorer.get_final_weight(start_node_coords, 0), 0, None)
    explorer.open_nodes.append(start_node)
    explorer.generated_nodes.append(start_node)
    while len(explorer.open_nodes):
        current_node = explorer.open_nodes.pop(0)
        explorer.closed_nodes.append(current_node)
        # Check if current node is the goal node
        if current_node.data == goal_node_coords:
            break
        # Generate child nodes and iterate through them
        for child_node in current_node.generate_child_nodes((obstacle_map.width, obstacle_map.height)):
            node_repeated = False
            # Update final weight of the child node
            child_node.weight = explorer.get_final_weight(child_node.data, child_node.cost)
            if obstacle_map.check_node_validity(child_node.data[0], obstacle_map.height - child_node.data[1] - 1):
                # Check for repetition of child node in closed nodes
                for closed_node in explorer.closed_nodes:
                    if closed_node.data == child_node.data:
                        node_repeated = True
                        break
                # Check for repetition of child node in open nodes
                for i in range(len(explorer.open_nodes)):
                    if explorer.open_nodes[i].data == child_node.data:
                        if explorer.open_nodes[i].weight > child_node.weight:
                            explorer.open_nodes[i] = child_node
                        node_repeated = True
                        break
                # Append child node to the list of open nodes
                # Do no append child node if repeated
                if not node_repeated:
                    # print('Node Weight:', child_node.weight)
                    explorer.open_nodes.append(child_node)
                    explorer.generated_nodes.append(child_node)
            # Sort the open nodes using their weights
            explorer.open_nodes.sort(key=lambda x: x.weight, reverse=False)

    # Generate path
    path_data = explorer.generate_path()
    # Get image of the map
    map_img = obstacle_map.get_map()
    blue = [255, 0, 0]
    white = [255, 255, 255]
    for node in explorer.generated_nodes:
        map_img[obstacle_map.height - node.data[1] - 1, node.data[0]] = white
        imshow("Node Exploration", map_img)
        waitKey(1)
    for data in path_data:
        # print(data)
        map_img[obstacle_map.height - data[1] - 1, data[0]] = blue
    map_img = resize(map_img, (obstacle_map.width * 2, obstacle_map.height * 2))
    imshow("Node Exploration", map_img)
    print('Exploration + Display Time:', time() - start_time)
    waitKey(15000)
