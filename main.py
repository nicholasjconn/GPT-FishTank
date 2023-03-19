import os, random, time, math
from itertools import product
from typing import Tuple
from colorama import Fore, Style, init


class TankObject:
    def __init__(self, x: int, y: int, icon: str, color: str):
        self.x, self.y, self.icon, self.color = x, y, icon, color
        self.age = 0

    def find_closest(self, tank_object: list['TankObject']) -> Tuple[int, int]:
        if not tank_object:
            return None, None
        closest = min(tank_object, key=lambda f: max(abs(self.x - f.x), abs(self.y - f.y)))
        return closest.x, closest.y

    def get_pos(self) -> Tuple[int, int]:
        return self.x, self.y

    def __str__(self) -> str:
        return self.color + self.icon + Style.RESET_ALL

    def run(self, tank: 'Tank'):
        self.age += 1

    def drift_down(self, tank: 'Tank'):
        possible_moves = [(0, 1), (-1, 1), (1, 1)]
        occupied_locations = tank.get_occupied_locations()

        # Check if there's a rock directly underneath
        if (self.x, self.y + 1) in tank.get_locations(tank.rocks):
            return

        # Remove occupied locations and positions outside the tank bounds from the possible_moves list
        unoccupied_moves = [
            (dx, dy) for dx, dy in possible_moves
            if 1 <= self.x + dx < tank.width - 1 and 1 <= self.y + dy < tank.height - 1
            and (self.x + dx, self.y + dy) not in occupied_locations
        ]
        if unoccupied_moves:
            dx, dy = random.choice(unoccupied_moves)
            self.x += dx
            self.y += dy

class Fish(TankObject):
    def __init__(self, x: int, y: int, icon: str, color: str, adult_age: int = 10, adult_icon: str = None):
        super().__init__(x, y, icon, color)
        self.energy = 30
        self.base_reproduction_cooldown = 10
        self.turns_since_last_eating = 0
        self.eating_cooldown = 2
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
        if self.age > self.adult_age and self.adult_icon:
            self.icon = self.adult_icon
        self.energy -= 1 + 0.01 * (self.age // 10)  # Energy consumption increases by 1% every 10 turns

    def choose_target(self, tank: 'Tank'):
        return random.randint(1, tank.width - 2), random.randint(1, tank.height - 2)

    def move_toward_target(self, tank: 'Tank', target_x: int, target_y: int):
        self.turns_since_last_eating += 1

        possible_moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        best_move = None
        best_distance = float("inf")
        occupied_locations = tank.get_occupied_locations()
        if self.turns_since_last_eating >= self.eating_cooldown:
            allowed_locations = tank.get_locations(tank.food)
        else:
            allowed_locations = set()
        for dx, dy in possible_moves:
            new_x = self.x + dx
            new_y = self.y + dy
            if 1 <= new_x < tank.width - 1 and 1 <= new_y < tank.height - 1 and (new_x, new_y) not in (occupied_locations - allowed_locations):
                distance = abs(target_x - new_x) + abs(target_y - new_y)
                fish_neighbor_count = sum([1 for fish in tank.fish if max(abs(new_x - fish.x), abs(new_y - fish.y)) <= 4])

                if distance < best_distance or (distance == best_distance and fish_neighbor_count > best_fish_neighbor_count):
                    best_move = (dx, dy)
                    best_distance = distance
                    best_fish_neighbor_count = fish_neighbor_count

        if best_move is not None:
            self.x += best_move[0]
            self.y += best_move[1]
            for f in tank.food:
                if (self.x, self.y) == f.get_pos():
                    self.energy += f.energy
                    tank.food.remove(f)
                    self.turns_since_last_eating = 0
                    break

    def can_reproduce(self) -> bool:
        reproduction_cooldown = self.base_reproduction_cooldown + self.age // 20
        return self.turns_since_last_reproduction >= reproduction_cooldown and self.energy >= self.energy_required_for_reproduction

    def reproduce(self, tank: 'Tank'):
        self.turns_since_last_reproduction += 1
        if not self.can_reproduce():
            return

        possible_spawn_locations = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        random.shuffle(possible_spawn_locations)

        for dx, dy in possible_spawn_locations:
            baby_fish_x = self.x + dx
            baby_fish_y = self.y + dy
            # Check if the baby fish's position is not occupied before adding it to the list of fish
            if 1 <= baby_fish_x < tank.width - 1 and 1 <= baby_fish_y < tank.height - 1 and (baby_fish_x, baby_fish_y) not in tank.get_occupied_locations():
                # Check for a neighboring fish to reproduce with
                neighbor_fish = None
                for fish in tank.fish:
                    if max(abs(baby_fish_x - fish.x), abs(baby_fish_y - fish.y)) == 1 and fish.can_reproduce():
                        neighbor_fish = fish
                        break

                if neighbor_fish is not None:
                    # Create a new fish of the same type as the parent fish
                    baby_fish = type(self)(baby_fish_x, baby_fish_y)
                    baby_fish.energy = math.ceil(self.energy_required_for_reproduction / 2)
                    tank.fish.append(baby_fish)
                    tank.fish_births += 1  # Increment the fish_births counter
                    self.energy -= math.ceil(baby_fish.energy / 2)
                    neighbor_fish.energy -= math.ceil(baby_fish.energy / 2)
                    self.turns_since_last_reproduction = 0
                    neighbor_fish.turns_since_last_reproduction = 0
                    break


class SchoolingFish(Fish):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "f", Fore.CYAN, adult_age=10, adult_icon="F")

    def choose_target(self, tank: 'Tank'):
        if self.energy < self.energy_required_for_reproduction:
            target_x, target_y = self.find_closest(tank.food)
            # Find nearest fish if we can't find food
            if target_x is None:
                target_x, target_y = self.find_closest(tank.fish)
        else:
            target_x, target_y = self.find_closest(tank.fish)
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
    def __init__(self, x: int, y: int, energy: int = 30):
        super().__init__(x, y, "o", Fore.YELLOW)
        self.energy = energy
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
        self.max_population = math.ceil(self.width * self.height * 0.025)
        self.new_food_interval = 20
        self.new_food_amount = math.ceil(self.width * self.height * 0.001)

        # Create a list of all possible locations and shuffle it
        all_locations = list(product(range(1, self.width - 1), range(1, self.height - 1)))
        random.shuffle(all_locations)

        # Assign locations to fish, food, and rocks, ensuring no two objects share the same location
        self.rocks = self.create_rocks(all_locations)
        self.fish = [SchoolingFish(*all_locations.pop()) for _ in range(math.ceil(self.width * self.height * 0.02)) if len(all_locations)]
        self.dead_fish = []
        self.food = [Food(*all_locations.pop()) for _ in range(math.ceil(self.width * self.height * 0.01)) if len(all_locations)]

        # Initialize statistics attributes
        self.iterations = 0
        self.fish_births = 0
        self.fish_deaths = 0
        self.oldest_fish_ever = 0

    def create_rocks(self, all_locations):
        rocks = []
        n_rocks = math.ceil(self.width * self.height * 0.05)
        # Cache the neighbor counts for all locations
        neighbor_counts = {loc: 0 for loc in all_locations}
        # Create rocks, preferring locations next to other rocks
        rock_locations = set()
        for _ in range(n_rocks):
            if len(all_locations):
                weights = [1 + 6 * neighbor_counts[loc] for loc in all_locations]
                chosen_location = random.choices(all_locations, weights, k=1)[0]
                all_locations.remove(chosen_location)
                rock_locations.add(chosen_location)
                rocks.append(Rock(*chosen_location))

                # Update neighbor counts for the chosen location's neighbors
                neighbors = [(chosen_location[0] + dx, chosen_location[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
                for neighbor in neighbors:
                    if neighbor in neighbor_counts:
                        neighbor_counts[neighbor] += 1
        return rocks

    def get_occupied_locations(self, return_set: bool = True) -> set[Tuple[int, int]]:
        locs = [tank_object.get_pos() for tank_object in self.get_all_objects()]
        if return_set:
            return set(locs)
        else:
            return locs

    def get_all_objects(self) -> list[TankObject]:
        return self.fish + self.food + self.rocks + self.dead_fish

    def average_fish_energy(self) -> float:
        if not self.fish:
            return 0.0
        return sum(f.energy for f in self.fish) / len(self.fish)

    def get_max_age(self) -> int:
        return max(fish.age for fish in self.fish) if self.fish else 0

    def get_locations(self, tank_objects: list[TankObject]) -> set[Tuple[int, int]]:
        return set([f.get_pos() for f in tank_objects])

    def display(self):
        # Check for overlapping TankObjects
        if len(self.get_occupied_locations(return_set=True)) != len(self.get_occupied_locations(return_set=False)):
            raise ValueError("Overlapping TankObjects detected.")

        # Create a grid containing the string to print for each location
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for obj in self.get_all_objects():
            x, y = obj.get_pos()
            grid[y][x] = str(obj)
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    grid[y][x] = Fore.WHITE + "+" + Style.RESET_ALL

        if self.get_max_age() > self.oldest_fish_ever:
            self.oldest_fish_ever = self.get_max_age()

        # Create a string for the tank including a status
        output = "\n".join(["".join(row) for row in grid])
        output += "\n"
        output += f"Number of fish: {len(self.fish):5}      Fish births:    {self.fish_births:5}      Max Age:          {self.get_max_age():5}\n"
        output += f"Number of food: {len(self.food):5}      Fish deaths:    {self.fish_deaths:5}      Oldest fish ever: {self.oldest_fish_ever:5}\n"
        output += f"Iterations:     {self.iterations:5}      Average energy:  {self.average_fish_energy():.1f}\n"

        # Move the cursor to the top-left corner of the screen and print it out
        print("\033[H", end="")
        print(output, end="")

    def run(self):
        all_objects = self.get_all_objects()
        random.shuffle(all_objects) # Shuffle to increase randomness in the model
        for obj in all_objects:
            obj.run(self)

        new_dead_fish = [f for f in self.fish if f.is_dead()]
        for df in new_dead_fish:
            self.fish.remove(df)
            self.fish_deaths += 1  # Increment the fish_deaths counter
            self.dead_fish.append(DeadFish(df.x, df.y))

        decomposed_fish = [df for df in self.dead_fish if df.is_decomposed()]
        for df in decomposed_fish:
            self.dead_fish.remove(df)
            self.food.append(Food(df.x, df.y, energy=15))

        # Give new food every so often, don't allow more than the max food, and don't feed the fish if there are too many
        if self.iterations % self.new_food_interval == 0 and len(self.fish) < self.max_population:
            max_food_per_clump = 10
            max_spacing_per_clump = 5

            for _ in range(self.new_food_amount):
                food_x = random.randint(1, self.width - 2)
                clump_size = random.randint(1, max_food_per_clump)
                clump_occupied = 0
                while clump_occupied < clump_size:
                    # Generate food locations within the maximum spacing of the clump
                    clump_food_x = random.randint(max(1, food_x - max_spacing_per_clump), min(self.width - 2, food_x + max_spacing_per_clump))
                    clump_food_y = random.randint(1, min(self.height - 2, 1 + max_spacing_per_clump))
                    if (clump_food_x, clump_food_y) not in self.get_occupied_locations():
                        self.food.append(Food(clump_food_x, clump_food_y))
                        clump_occupied += 1

        self.iterations += 1

def main():
    init()  # Initialize colorama
    tank = Tank()
    os.system("cls" if os.name == "nt" else "clear")
    while True:
        frame_start_time = time.time()
        tank.run()
        tank.display()
        frame_time_taken = time.time() - frame_start_time
        sleep_time = 0.1 - frame_time_taken
        if sleep_time > 0.001:
            time.sleep(sleep_time)


if __name__ == "__main__":
    main()
