# Ollama Image and Conversation Bot

Ollama Image and Conversation Bot is an innovative application designed to generate image descriptions and engage in conversation through advanced AI models using a Flask web interface. Utilizing the Ollama platform, this bot leverages deep learning models for both image analysis and conversational AI, offering a seamless and interactive user experience.

## Directory Structure

The project is structured as follows:

```
.
|-- __pycache__
|-- screenshots
|   |-- local1.png
|   |-- local2.png
|-- templates
|   |-- index.html
|-- app.py
|-- ollama_utils.py
```

## Python Files

The application comprises two primary Python files, along with an HTML template for the web interface:

1. **app.py**:
   - **Purpose**: Serves as the main application file, setting up a Flask web server to handle user interactions and generate responses.
   - **Functionality**:
     - Initializes the Flask app and sets up configuration and routes.
     - Handles file uploads, user inputs, and system prompt updates.
     - Converts user inputs into prompts for the Ollama models and gathers responses.
     - Manages conversation history and session states to ensure coherent conversation flow.
     - Provides endpoints for resetting conversations and updating system prompts.
     - Contains utility functions to generate image descriptions and continue conversations based on user inputs and uploaded images.
     - Automatically downloads and sets up `llama3.1` model for text interaction and `llava:13b` model for image descriptions if not already installed.

2. **ollama_utils.py**:
   - **Purpose**: Contains utility functions essential for managing the Ollama service and environment setup.
   - **Functionality**:
     - Functions to check the operating system, install Ollama, and manage models.
     - Includes methods to download and setup Ollama executables and models.
     - Provides commands to start, stop, and verify the Ollama service.
     - Manages GPU memory clearance and ensures environmental path correctness for seamless execution.
     - Checks if the `ollama` service and required models (`llama3.1` for text, `llava:13b` for images) are installed, and downloads them if necessary.

3. **templates/index.html**:
   - **Purpose**: Serves as the front-end template for the Flask web application.
   - **Functionality**:
     - Provides an interactive UI for users to input messages and upload images.
     - Displays conversation history in a user-friendly chat format.
     - Includes a system prompt input field for updating the behavior of the bot.
     - Handles loading and submission animations for a smoother user experience.
     - Uses Bootstrap for styling and Prism for syntax highlighting.

## How to Run the Application

To run the application, follow these steps:

1. **Install Required Packages**: Ensure all the required Python packages are installed. You can install dependencies using the following command:
   ```sh
   pip install -r requirements.txt
   ```

2. **Set Up Ollama**: Ensure Ollama is installed and properly set up on your system. The `ollama_utils.py` file provides functions to install and manage Ollama.

3. **Run the Flask Application**: Start the Flask web server by running the `app.py` script.
   ```sh
   python app.py
   ```

4. **Interact with the Bot**: Open your web browser and navigate to `http://localhost:5000`. Use the web interface to interact with the bot by entering messages, uploading images, and updating system prompts.

## Model Setup and Installation

The application will automatically download and set up the necessary models if they are not already installed:

- **Text-Based Model**: `llama3.1`
- **Image Description Model**: `llava:13b`

These models will be pulled during the initial setup, ensuring seamless execution without manual intervention.

## Screenshots

Below are screenshots demonstrating the bot's interactions:

### Initial Setup and System Prompt Update
![Initial Setup and System Prompt Update](./screenshots/local1.png)

### User Interaction and Image Upload
![User Interaction and Image Upload](./screenshots/local2.png)

These screenshots showcase the bot's ability to describe images and engage in conversational interactions based on user inputs.

## Conclusion

Ollama Image and Conversation Bot is a cutting-edge application that demonstrates the potential of AI in image analysis and interactive dialogue. With its robust architecture and intuitive web interface, it stands as a versatile tool for both developers and end-users seeking advanced conversational agents.
