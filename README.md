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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Make sure to replace https://github.com/yourusername/virtual-fish-tank.git with the correct URL for your repository.
