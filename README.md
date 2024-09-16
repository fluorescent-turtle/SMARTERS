# Smarters

## Description

Smarters is an advanced simulator for managing robots in environments represented as tile grids. It uses the Mesa framework for detailed visualization of interactions between agents and the environment. The simulator allows testing and evaluating robot performance in complex scenarios with blocked areas, isolated areas, and different bounce and cutting modes.

## Environment Representation

### Tile Grid

The simulation environment is represented as a tile grid, managed using the Mesa framework with a `MultiGrid` object. Each tile can contain multiple agents and resources.

### Agents and Resources

- **Agents:** Mobile and interactive entities implemented as instances of the `Agent` class from Mesa. They interact with the environment and each other.
- **Resources:** Static elements distributed across tiles, such as grass, guiding lines, isolated areas, and openings.

### Tile Structure

Tiles are square and can contain various elements due to the multi-agent nature of `MultiGrid`. Resources include:
- Grass tiles
- Guiding lines
- Isolated areas
- Openings

### Blocked Areas

Blocked areas are zones inaccessible to robots, represented by `SquaredBlockedArea` and `CircledBlockedArea`. They may include buildings, pools, or other obstructive structures. These areas can be set manually or distributed randomly.

### Isolated Areas

Isolated areas are zones where robots can enter only through designated openings. Modeled with `IsolatedArea` and `Opening`, their size and position can be set manually or generated randomly.

## Customization

### Bounce Model

The bounce model manages robot collisions with obstacles:
- **Ping Pong:** The robot reflects its movement in the opposite direction after hitting an obstacle.
- **Random:** The robot always tries to move towards the upper-left tile. If blocked, it attempts other directions.

### Cutting Model

The robot simulates cutting by moving across tiles and incrementing a counter. In random mode, the robot chooses a random direction and moves in a straight line, affecting adjacent tiles.

## Simulation and Output

### Simulation Cycle

The simulation consists of:
1. Generating maps and base station positions.
2. Exploring positions based on blocked areas.
3. Simulation duration specified in the JSON configuration file.

### Autonomy Cycle

The robot operates with limited autonomy, moving until exhausted. Autonomy is reset after each cycle, and simulation continues until the set number of cycles is completed.

### Output

After each autonomy and simulation cycle, the following are produced:
- **Heatmap**
- **CSV Files:** Containing the map matrix, tile information, and details on grass, blocked areas, and guiding lines.
