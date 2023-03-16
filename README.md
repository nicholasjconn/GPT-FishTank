# Virtual Fish Tank

This Python program simulates a virtual fish tank with fish, food, rocks, and dead fish. The fish tank is displayed in the terminal, with different colors representing various objects in the tank. Fish move around the tank to consume food and reproduce, while dead fish drift down and eventually decompose into food.

![ASCII Simulation Screenshot](screenshot.png)

## Powered by OpenAI's ChatGPT

This virtual fish tank simulation is a result of the collaboration with OpenAI's cutting-edge language model, ChatGPT. ChatGPT, a product of the advanced GPT-4 architecture, generated the code and designed the program by providing insights, suggestions, and code snippets throughout the development process.

With ChatGPT's help, the code was crafted by leveraging its vast knowledge and understanding of Python programming and concepts. By combining the power of AI with human supervision, we brought the virtual fish tank to life, showcasing the endless possibilities that can be achieved when AI takes the lead in software development.

The synergy between human supervision and AI's computational prowess has made this virtual fish tank simulation not only an engaging and fun experience but also a testament to the future of AI-driven programming. Experience the magic of AI-generated code as you explore the depths of this virtual fish tank and watch its inhabitants thrive within their dynamic, ever-changing environment.

This README.md was written solely by ChatGPT, demonstrating the capabilities of AI language models in generating comprehensive documentation.

## Features

- Terminal-based graphical display using the `colorama` library.
- Random object spawning for fish, food, and rocks.
- Fish move towards the closest food or other fish, depending on their energy level.
- Fish consume food to gain energy and reproduce when they meet certain conditions.
- Dead fish drift down towards the bottom of the tank and decompose into food after a certain time.
- Food drifts down towards the bottom of the tank, avoiding rocks and other objects.
- New food spawns at the top of the tank every set number of iterations.
- Tank size adapts to the terminal size.
- Tank statistics (number of fish, number of food, iterations, fish births, fish deaths, average fish energy) are displayed at the bottom of the tank.

## Installation

1. Clone the repository:

`git clone https://github.com/nicholasjconn/GPT-FishTank.git`

2. Change to the `GPT-FishTank` directory:

`cd GPT-FishTank`

3. Install the required dependencies:

`pip install -r requirements.txt`


## Usage

Run the virtual fish tank simulation by executing:
`python main.py`

To stop the simulation, press `Ctrl+C`.


## Future Enhancements

1. **Baby Fish Stage**: Introduce a "baby fish" stage, where newly born fish are represented by a lowercase 'f' and cannot reproduce for a certain period of time. This feature could be added either within the existing Fish class or by creating a new BabyFish class.
2. **Predator Fish**: Create a PredatorFish class that can only consume other fish, specifically non-predatory fish, and cannot eat Food. Predator fish should avoid schooling and only interact with one another for mating purposes when they have sufficient energy.
3. **User Interface**: Develop a text-based user interface that lets users interact with the simulation by pausing, resuming, or modifying parameters like fish reproduction rate, mortality rate, and food generation rate.
4. **Fish Aging**: Implement an aging mechanism for fish that affects their energy consumption, reproduction rate, and mortality based on their age, adding more realism to the simulation.
5. **Different Fish Species**: Introduce various fish species with unique characteristics, such as energy consumption, reproduction rate, and movement speed, to increase the simulation's complexity and engagement.
6. **Predator-Prey Interaction**: Add predators that hunt and consume fish to create a more dynamic environment and highlight interactions between different species.
7. **Statistics and Visualization**: Design a system that monitors and presents data on the current population, food count, and other relevant statistics over time. This feature would help users observe the evolution of the fish tank ecosystem, providing insights on the oldest fish and average fish age.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Make sure to replace https://github.com/yourusername/virtual-fish-tank.git with the correct URL for your repository.
