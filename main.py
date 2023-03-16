# Prompt
"""
TO ADD:
3. Make a baby fish be an little f for a certain period of time after birth. During that time, it cannot reproduce. This could be done either inside the Fish class or in a new class called BabyFish
4. Make a new class called PredatorFish that can only eat other fish. It should be able to eat only non predator fish and cannot eat Food. Predator fish not school and only should keep one another out if they have enough energy to mate.


User Interface: Implement a simple text-based user interface that allows users to interact with the simulation by pausing, resuming, or changing the parameters such as fish reproduction rate, mortality rate, or food generation rate.
Fish Aging: Introduce an aging mechanism for fish, where their energy consumption, reproduction rate, or chances of dying change based on their age. This would add an extra layer of realism to the simulation.
Different Fish Species: Create different types of fish with different properties such as energy consumption, reproduction rate, and movement speed. This would make the simulation more engaging and complex.
Predator-Prey Interaction: Introduce predators that can hunt and eat the fish. This would create a more dynamic environment and showcase the interactions between different species.
Statistics and Visualization: Implement a system that tracks and displays the current population, number of food items, and other relevant statistics over time. This can help users understand how the fish tank ecosystem evolves over time.
    - oldest fish, average age
"""


import os, random, time, math
from itertools import product
from typing import List, Tuple
from colorama import Fore, Style, init

# Initialize colorama
init()


class TankObject:
    def __init__(self, x: int, y: int, icon: str, color: str):
        self.x, self.y, self.icon, self.color = x, y, icon, color
        self.age = 0

    def find_closest(self, tank_object: List['TankObject']) -> Tuple[int, int]:
        if not tank_object:
            return None, None

        closest_distance = float('inf')
        closest = None

        for f in tank_object:
            # Calculate the chebyshev distance
            distance = max(abs(self.x - f.x), abs(self.y - f.y))
            if distance < closest_distance:
                closest_distance = distance
                closest = f

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
        if (self.x, self.y + 1) in tank.rock_locations:
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
    def __init__(self, x: int, y: int):
        super().__init__(x, y, "F", Fore.CYAN)
        self.energy = 30
        self.reproduction_cooldown = 10
        self.turns_since_last_reproduction = 0
        self.energy_required_for_reproduction = 20
        self.max_energy = 30
        self.mortality_rate = 0.005

    def run(self, tank: 'Tank'):
        super().run(tank)
        self.move(tank)
        self.reproduce(tank)

    def is_dead(self) -> bool:
        return random.random() < self.mortality_rate or self.energy <= 0

    def move(self, tank: 'Tank'):
        if self.energy < self.energy_required_for_reproduction:
            target_x, target_y = self.find_closest(tank.food)
            # Find nearest fish if we can't find food
            if target_x is None:
                target_x, target_y = self.find_closest(tank.fish)
        else:
            target_x, target_y = self.find_closest(tank.fish)
        if target_x is None or target_y is None:
            return

        possible_moves = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
        random.shuffle(possible_moves)

        best_move = None
        best_distance = float("inf")
        occupied_locations = tank.get_occupied_locations()
        food_locations = tank.food_locations
        for dx, dy in possible_moves:
            new_x = self.x + dx
            new_y = self.y + dy
            if 1 <= new_x < tank.width - 1 and 1 <= new_y < tank.height - 1 and (new_x, new_y) not in (occupied_locations - food_locations):
                distance = abs(target_x - new_x) + abs(target_y - new_y)
                if distance < best_distance:
                    best_move = (dx, dy)
                    best_distance = distance

        if best_move is not None:
            self.x += best_move[0]
            self.y += best_move[1]
            self.energy -= 1
            for f in tank.food:
                if self.energy < 20 and (self.x, self.y) == f.get_pos():
                    self.energy += 10
                    tank.food.remove(f)
                    break

    def reproduce(self, tank: 'Tank'):
        if self.turns_since_last_reproduction >= self.reproduction_cooldown and self.energy >= self.energy_required_for_reproduction:
            possible_spawn_locations = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (-1, -1), (1, -1)]
            random.shuffle(possible_spawn_locations)

            for dx, dy in possible_spawn_locations:
                baby_fish_x = self.x + dx
                baby_fish_y = self.y + dy

                # Check if the baby fish's position is not occupied before adding it to the list of fish
                if 1 <= baby_fish_x < tank.width - 1 and 1 <= baby_fish_y < tank.height - 1 and (baby_fish_x, baby_fish_y) not in tank.get_occupied_locations():
                    baby_fish = Fish(baby_fish_x, baby_fish_y)
                    tank.fish.append(baby_fish)
                    tank.fish_births += 1  # Increment the fish_births counter
                    self.energy -= 10
                    self.turns_since_last_reproduction = 0
                    break
                else:
                    self.turns_since_last_reproduction += 1
        else:
            self.turns_since_last_reproduction += 1


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
    def __init__(self, n_fish: int = 40, n_food: int = 20, n_rocks: int = 20):
        # Get the terminal size
        terminal_size = os.get_terminal_size()
        self.width = terminal_size.columns - 4
        self.height = terminal_size.lines - 9
        # Parameters
        self.max_population = 50
        self.max_food = 200
        self.new_food_interval = 10
        self.new_food_amount = math.ceil(self.width/20)

        # Create a list of all possible locations and shuffle it
        all_locations = list(product(range(1, self.width - 1), range(1, self.height - 1)))
        random.shuffle(all_locations)

        # Assign locations to fish, food, and rocks, ensuring no two objects share the same location
        self.fish = [Fish(*all_locations.pop()) for _ in range(n_fish) if len(all_locations)]
        self.dead_fish = []
        self.food = [Food(*all_locations.pop()) for _ in range(n_food) if len(all_locations)]
        self.rocks = [Rock(*all_locations.pop()) for _ in range(n_rocks) if len(all_locations)]

        # Initialize statistics attributes
        self.iterations = 0
        self.fish_births = 0
        self.fish_deaths = 0

    def get_occupied_locations(self, return_set: bool = True) -> set[Tuple[int, int]]:
        locs = [tank_object.get_pos() for tank_object in self.get_all_objects()]
        if return_set:
            return set(locs)
        else:
            return locs

    def get_all_objects(self) -> List[TankObject]:
        return self.fish + self.food + self.rocks + self.dead_fish

    def average_fish_energy(self) -> float:
        if not self.fish:
            return 0.0
        return sum(f.energy for f in self.fish) / len(self.fish)

    @property
    def fish_locations(self):
        return set([f.get_pos() for f in self.fish])

    @property
    def food_locations(self):
        return set([f.get_pos() for f in self.food])

    @property
    def rock_locations(self):
        return set([r.get_pos() for r in self.rocks])

    def display(self):
        # Check for overlapping TankObjects
        len(self.get_occupied_locations(return_set=True)) == len(self.get_occupied_locations(return_set=False))

        # Create a grid containing the string to print for each location
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        for obj in self.get_all_objects():
            x, y = obj.get_pos()
            grid[y][x] = str(obj)
        for y in range(self.height):
            for x in range(self.width):
                if x == 0 or x == self.width - 1 or y == 0 or y == self.height - 1:
                    grid[y][x] = Fore.WHITE + "+" + Style.RESET_ALL

        # Create a string for the tank including a status
        output = "\n".join(["".join(row) for row in grid])
        output += "\n"
        output += f"Number of fish: {len(self.fish):5}      Fish births:    {self.fish_births:5}\n"
        output += f"Number of food: {len(self.food):5}      Fish deaths:    {self.fish_deaths:5}\n"
        output += f"Iterations:     {self.iterations:5}      Average energy:  {self.average_fish_energy():.1f}\n"

        # Move the cursor to the top-left corner of the screen and print it out
        print("\033[H", end="")
        print(output, end="")

    def run(self):
        for obj in self.get_all_objects():
            obj.run(self)

        new_dead_fish = [f for f in self.fish if f.is_dead()]
        for df in new_dead_fish:
            self.fish.remove(df)
            self.fish_deaths += 1  # Increment the fish_deaths counter
            self.dead_fish.append(DeadFish(df.x, df.y))

        decomposed_fish = [df for df in self.dead_fish if df.is_decomposed()]
        for df in decomposed_fish:
            self.dead_fish.remove(df)
            self.food.append(Food(df.x, df.y))

        # Give new food every so often, don't allow more than the max food, and don't feed the fish if there are too many
        if self.iterations % self.new_food_interval == 0 and len(self.food) < self.max_food and len(self.fish) < self.max_population:
            for _ in range(self.new_food_amount):
                food_x = random.randint(1, self.width - 2)
                while (food_x, 1) in self.get_occupied_locations():
                    food_x = random.randint(1, self.width - 2)
                self.food.append(Food(food_x, 1))

        self.iterations += 1


def main():
    tank = Tank()
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        tank.run()
        tank.display()
        time.sleep(0.1)


if __name__ == "__main__":
    main()
