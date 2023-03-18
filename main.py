from collections import deque
import os, random, time, math
from itertools import chain, product
from typing import Tuple
from colorama import Fore, Style, init


class TankObject:
    def __init__(self, x: int, y: int, icon: str, color: str):
        self.x, self.y, self.icon, self.color = x, y, icon, color
        self.age = 0

    def find_closest(self, grid: list[list['TankObject']], target_class: 'TankObject') -> Tuple[int, int]:
        closest = None
        min_distance = float('inf')
        for obj in chain(*grid):
            if isinstance(obj, target_class):
                distance = max(abs(self.x - obj.x), abs(self.y - obj.y))
                if distance < min_distance:
                    min_distance = distance
                    closest = obj
        return closest.x, closest.y

    def __str__(self) -> str:
        return self.color + self.icon + Style.RESET_ALL

    def run(self, tank: 'Tank'):
        self.age += 1

    def drift_down(self, tank: 'Tank'):
        # Check if there's a rock directly underneath
        if isinstance(tank.grid[self.x][self.y + 1], Rock):
            return
        # Move the fish to empty positions
        possible_moves = [(self.x + dx, self.y + dy) for dx, dy in [(0, 1), (-1, 1), (1, 1)]]
        possible_moves = [
            (x, y) for x, y in possible_moves
            if 1 <= x < tank.width - 1 and 1 <= y < tank.height - 1 and tank.grid[x][y] is None
        ]
        if possible_moves:
            tank.move_object(self, *random.choice(possible_moves))


class Fish(TankObject):
    def __init__(self, x: int, y: int, icon: str, color: str, adult_age: int = 10, adult_icon: str = None):
        super().__init__(x, y, icon, color)
        self.energy = 30
        self.base_reproduction_cooldown = 10
        self.turns_since_last_reproduction = 0
        self.energy_required_for_reproduction = 20
        self.max_energy = 60
        self.mortality_rate = 0.005
        self.adult_age = adult_age
        self.adult_icon = adult_icon

    def is_dead(self) -> bool:
        return random.random() < self.mortality_rate or self.energy <= 0

    def run(self, tank: 'Tank'):
        super().run(tank)
        target_x, target_y = self.choose_target(tank)
        if target_x is not None or target_y is not None:
            self.move_toward_target(tank, target_x, target_y)
        self.reproduce(tank)
        if self.age > self.adult_age:
            self.icon = self.adult_icon
        self.energy -= 1 + 0.01 * (self.age // 10)  # Energy consumption increases by 1% every 10 turns

    def choose_target(self, tank: 'Tank'):
        return random.randint(1, tank.width - 2), random.randint(1, tank.height - 2)

    def move_toward_target(self, tank: 'Tank', target_x: int, target_y: int):
        possible_moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        possible_moves = [(self.x + dx, self.y + dy) for dx, dy in possible_moves]
        possible_moves = [
            (x, y) for x, y in possible_moves
            if 1 <= x < tank.width - 1 and 1 <= y < tank.height - 1 and (tank.grid[x][y] is None or isinstance(tank.grid[x][y], Food))
        ]

        best_move = None
        best_distance = float("inf")
        for new_x, new_y in possible_moves:
            distance = abs(target_x - new_x) + abs(target_y - new_y)
            if distance > best_distance:
                continue
            fish_neighbor_count = 0
            for x in range(max(new_x - 4, 1), min(new_x + 4, tank.width - 2)):
                for y in range(max(new_y - 4, 1), min(new_y + 4, tank.height - 2)):
                    if isinstance(tank.grid[x][y], Fish) and max(abs(new_x - x), abs(new_y - y)) <= 4:
                        fish_neighbor_count += 1
            if distance < best_distance or fish_neighbor_count > best_fish_neighbor_count:
                best_move = new_x, new_y
                best_distance = distance
                best_fish_neighbor_count = fish_neighbor_count

        if best_move is not None:
            if isinstance(tank.grid[best_move[0]][best_move[1]], Food):
                self.energy += 20
            tank.move_object(self, best_move[0], best_move[1])

    def can_reproduce(self) -> bool:
        reproduction_cooldown = self.base_reproduction_cooldown + self.age // 20
        return self.turns_since_last_reproduction >= reproduction_cooldown and self.energy >= self.energy_required_for_reproduction

    def reproduce(self, tank: 'Tank'):
        self.turns_since_last_reproduction += 1
        if not self.can_reproduce():
            return

        possible_spawn_locations = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        possible_spawn_locations = [(self.x + dx, self.y + dy) for dx, dy in possible_spawn_locations]
        # Check if the baby fish's position is not occupied before adding it to the list of fish
        possible_spawn_locations = [
            (x, y) for x, y in possible_spawn_locations
            if 1 <= x < tank.width - 1 and 1 <= y < tank.height - 1 and tank.grid[x][y] is None
        ]
        random.shuffle(possible_spawn_locations)

        for baby_fish_x, baby_fish_y in possible_spawn_locations:
            # Check for a neighboring fish to reproduce with
            neighbor_locations = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
            neighbor_locations = [(baby_fish_x + dx, baby_fish_y + dy) for dx, dy in neighbor_locations]
            neighbor_fish: list[Fish] = [tank.grid[x][y] for x, y in neighbor_locations if isinstance(tank.grid[x][y], Fish)]
            random.shuffle(neighbor_fish)

            if neighbor_fish:
                # Create a new fish of the same type as the parent fish
                baby_fish = type(self)(baby_fish_x, baby_fish_y)
                baby_fish.energy = 10
                tank.add_object(baby_fish)
                tank.fish_births += 1  # Increment the fish_births counter
                self.energy -= 5
                neighbor_fish[0].energy -= 5
                self.turns_since_last_reproduction = 0
                neighbor_fish[0].turns_since_last_reproduction = 0
                break


class SchoolingFish(Fish):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "f", Fore.CYAN, adult_age=10, adult_icon="F")

    def choose_target(self, tank: 'Tank'):
        if self.energy < self.energy_required_for_reproduction:
            target_x, target_y = self.find_closest(tank.grid, Food)
            # Find nearest fish if we can't find food
            if target_x is None:
                target_x, target_y = self.find_closest(tank.grid, Fish)
        else:
            target_x, target_y = self.find_closest(tank.grid, Fish)
        return target_x, target_y


class DeadFish(TankObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "x", Fore.RED)
        self.decompose_time = 20
    def run(self, tank: 'Tank'):
        super().run(tank)
        self.drift_down(tank)
    def is_decomposed(self):
        return self.age >= self.decompose_time


class Food(TankObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "o", Fore.YELLOW)
    def run(self, tank: 'Tank'):
        super().run(tank)
        self.drift_down(tank)


class Rock(TankObject):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "#", Fore.GREEN)


class Tank:
    def __init__(self):
        # Get the terminal size
        terminal_size = os.get_terminal_size()
        self.width = terminal_size.columns - 4
        self.height = terminal_size.lines - 5
        # Parameters
        self.max_population = math.ceil(self.width * self.height * 0.02)
        self.new_food_interval = 10
        self.new_food_amount = math.ceil(self.width/15)

        # Create a list of all possible locations and shuffle it
        all_locations = list(product(range(1, self.width - 1), range(1, self.height - 1)))
        random.shuffle(all_locations)
        # Create a grid and add objects
        self.grid = [[None for _ in range(self.height)] for _ in range(self.width)]
        # Assign locations to fish, food, and rocks, ensuring no two objects share the same location
        self.add_rocks(all_locations)
        fish = [SchoolingFish(*all_locations.pop()) for _ in range(math.ceil(self.width * self.height * 0.02)) if len(all_locations)]
        food = [Food(*all_locations.pop()) for _ in range(math.ceil(self.width * self.height * 0.01)) if len(all_locations)]
        # Add objects to the grid
        for obj in fish + food:
            self.add_object(obj)

        # Initialize statistics attributes
        self.iterations = 0
        self.fish_births = 0
        self.fish_deaths = 0
        self.oldest_fish_ever = 0

    def add_object(self, obj: TankObject):
        self.grid[obj.x][obj.y] = obj

    def move_object(self, obj: TankObject, new_x: int, new_y: int):
        self.grid[obj.x][obj.y] = None
        self.grid[new_x][new_y] = obj
        obj.x = new_x
        obj.y = new_y

    @property
    def fish(self) -> list[Fish]:
        return [obj for obj in chain(*self.grid) if isinstance(obj, Fish)]

    @property
    def food(self) -> list[Food]:
        return [obj for obj in chain(*self.grid) if isinstance(obj, Food)]

    @property
    def dead_fish(self) -> list[DeadFish]:
        return [obj for obj in chain(*self.grid) if isinstance(obj, DeadFish)]

    def add_rocks(self, all_locations: set) -> list[Rock]:
        rocks = []
        n_rocks = math.ceil(self.width * self.height * 0.04)
        # Cache the neighbor counts for all locations
        neighbor_counts = {loc: 0 for loc in all_locations}
        # Create rocks, preferring locations next to other rocks
        rock_locations = set()
        for _ in range(n_rocks):
            if len(all_locations):
                weights = [1 + 4 * neighbor_counts[loc] for loc in all_locations]
                chosen_location = random.choices(all_locations, weights, k=1)[0]
                all_locations.remove(chosen_location)
                rock_locations.add(chosen_location)
                self.add_object(Rock(*chosen_location))

                # Update neighbor counts for the chosen location's neighbors
                neighbors = [(chosen_location[0] + dx, chosen_location[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                for neighbor in neighbors:
                    if neighbor in neighbor_counts:
                        neighbor_counts[neighbor] += 1
        return rocks

    def average_fish_energy(self) -> float:
        if not self.fish:
            return 0.0
        return sum(f.energy for f in self.fish) / len(self.fish)

    def get_max_age(self) -> int:
        return max(fish.age for fish in self.fish) if self.fish else 0

    def display(self):
        # Create a grid containing the string to print for each location
        char_grid = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    row.append(Fore.WHITE + "+" + Style.RESET_ALL)
                elif self.grid[x][y] is None:
                    row.append(" ")
                else:
                    row.append(str(self.grid[x][y]))
            char_grid.append(row)

        if self.get_max_age() > self.oldest_fish_ever:
            self.oldest_fish_ever = self.get_max_age()

        # Create a string for the tank including a status
        output = "\n".join(["".join(row) for row in char_grid])
        output += "\n"
        output += f"Number of fish: {len(self.fish):5}      Fish births:    {self.fish_births:5}      Max Age:          {self.get_max_age():5}\n"
        output += f"Number of food: {len(self.food):5}      Fish deaths:    {self.fish_deaths:5}      Oldest fish ever: {self.oldest_fish_ever:5}\n"
        output += f"Iterations:     {self.iterations:5}      Average energy:  {self.average_fish_energy():.1f}\n"

        # Move the cursor to the top-left corner of the screen and print it out
        print("\033[H", end="")
        print(output, end="")

    def run(self):
        all_objects: list[TankObject] = [obj for obj in chain(*self.grid) if obj is not None and not isinstance(obj, Rock)]
        random.shuffle(all_objects) # Shuffle to increase randomness in the model
        for obj in all_objects:
            obj.run(self)

        new_dead_fish = [f for f in self.fish if f.is_dead()]
        for df in new_dead_fish:
            self.add_object(DeadFish(df.x, df.y))
            self.fish_deaths += 1  # Increment the fish_deaths counter

        decomposed_fish = [df for df in self.dead_fish if df.is_decomposed()]
        for df in decomposed_fish:
            self.add_object(Food(df.x, df.y))

        # Give new food every so often, don't allow more than the max food, and don't feed the fish if there are too many
        if self.iterations % self.new_food_interval == 0 and len(self.fish) < self.max_population:
            x_locations = [x for x in range(1, self.width - 1) if not self.grid[x][1]]
            for _ in range(self.new_food_amount):
                if x_locations:
                    food_x = random.choice(x_locations)
                    self.add_object(Food(food_x, 1))
                    x_locations.remove(food_x)

        self.iterations += 1


def main():
    init() # Initialize colorama
    tank = Tank()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        duration = time.time()
        tank.run()
        tank.display()
        duration = time.time() - duration
        if duration < 0.1:
            time.sleep(0.1 - duration)


if __name__ == "__main__":
    main()
