# UE Module Generator
 Simplifies the process of creating UE modules

 **Prerequisites**

 * Unreal Engine 4 or 5
 * Python with required libraries

 **Instalation**
 1. Clone this repository into the root folder of your Unreal Engine project. It must be in the root folder, since this program uses relative paths.
 
 **Usage**

ModuleGeneration.py file must be inside your UE project root folder!

UE Module Generator can be started in 2 different states. The first one is where the program waits for your input inside the terminal. It will wait for 3 possible inputs:
1. Correct module name (string with letters only, without spaces)
2. 'gen', 'g' or 'generate' string - starts Solution files generation by calling UnrealBuildTool.exe from UE installation path
3. 'q', 'quit' or 'exit' - terminates the program

This way, it will create a new module with your name with default values defined inside 'defaults' class in .py file. You can change these values anytime.
To start the program this way, double click on .py file (if Python is set as default app for this extension) or open the console inside your UE project root folder and type 'py ModuleGenerator.py' (This requires the ModuleGenerator.py file to be inside your UE project root folder).

The second state is where the program executes instantly, but this time, overriding default values by command line arguments.
This way, you can directly change module config and generate solution files after successful module creation.

To start the program this way, open the console inside your UE project root folder and type 'py ModuleGenerator.py [module name here]' (module name goes without brackets. For example, if you want to name your module 'Gameplay', you would write py ModuleGenerator.py Gameplay)
You can also type 'py ModuleGenerator.py -h' for help. Here are all possible arguments:

- module_name: positional argument (means it must be first). Sets the name of the module you want to create. Use letters only without spaces. Suggestion: Always capitalize the first letter of each word in your module name, for example: Gameplay, UIModule, SomeReallyCoolModule etc. If you are goind to generate solution files only, you can skip this argument completely, otherwise, it's a must have.
- '-t', '--type': Sets module type. Usually 'Runtime' but can be 'Editor' also. Default is 'Runtime'
- '-p', '--phase': Sets loading phase for module. Usually set to 'Default' which is the default also.
- '-d', '--dependencies': Allows you to write what dependencies you want to include in your module. By default, program includes 'Core', 'CoreUObject' and 'Engine'
- '-g', '--generate': Starts or queues solution file generation command. If module_name argument is provided, the program will wait for succesful module creation before starting solution generation process. Otherwise, the program will start the generation instantly.

How to generate the solution files instantly without creating a module:
py ModuleGeneration.py -g

(Again, this requires .py file to be in the root directory of your UE project folder.)

Important note: Check requirements.txt file to see required libraries for this python file. It's recommended to create a virtual environment somewhere (inside or outside your UE project root), activate it and then run this .py file. You can also do a system-wide installation of libraries but it's less recommended way of doing things.

**Contributing**

Feel free to submit pull requests and raise issues.

**Licence**

This project is licenced under the MIT Licence