from flask import Flask, request, render_template, redirect, url_for, flash
import os
import json
import subprocess
import atexit
import time
import ollama
from ollama_utils import (
    install_and_setup_ollama,
    kill_existing_ollama_service,
    clear_gpu_memory,
    start_ollama_service_windows,
    stop_ollama_service,
    is_windows
)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'  # Needed for flashing messages

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

DEFAULT_SYSTEM_PROMPT = "you are a verbose chat assistant"

#keep both of these here to show you can switch models
TEXT_BASED_OLLAMA_MODEL = 'llama3.1'


HISTORY_FILE_PATH = "history.json"
SYSTEM_PROMPT = DEFAULT_SYSTEM_PROMPT

def delete_history_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def save_conversation_history(file_path, message_history):
    with open(file_path, 'w') as file:
        json.dump(message_history, file, indent=2)

def load_conversation_history(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def generate_image_description(file_path, prompt, model='llava:13b'):
    try:
        result = ollama.generate(
            model=model,
            prompt=prompt,
            images=[file_path],
            stream=False
        )['response']
    except Exception as e:
        raise
    return result

def continue_conversation(message_history, user_input, initial_description, uploaded_file_path=None):
    if uploaded_file_path:
        message_history, response, initial_description = create_image_based_conversation(uploaded_file_path, user_input, initial_description)
        save_conversation_history(HISTORY_FILE_PATH, message_history)
    else:
        raise ValueError("continue_conversation should only be called for file-based interactions")
    return response, message_history, initial_description

def generate_text_response(model_name, prompt):
    response = ollama.generate(
        model=model_name,
        prompt=prompt,
        stream=False
    )['response']
    return response

def create_image_based_conversation(new_image_file_path, user_input, initial_description):
    prompt = user_input.replace(new_image_file_path, "").strip()
    initial_description = generate_image_description(new_image_file_path, f"{SYSTEM_PROMPT}\n\nDescribe this image in intricate detail.")
    new_response = generate_image_description(new_image_file_path, f"{SYSTEM_PROMPT}\n\n{prompt}")

    message_history = load_conversation_history(HISTORY_FILE_PATH)
    message_history += [
        {"role": "user", "content": "Describe this image"},
        {"role": "assistant", "content": initial_description},
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": new_response}
    ]
    return message_history, new_response, initial_description

def format_message_history(message_history):
    formatted_history = ""
    for msg in message_history:
        if msg["role"] == "user":
            formatted_history += f'<div class="message-bubble user-message">{msg["content"]}</div>'
        elif msg["role"] == "system":
            formatted_history += f'<div class="message-bubble system-message"><strong>System:</strong> {msg["content"]}</div>'
        else:
            formatted_history += f'<div class="message-bubble bot-response">{msg["content"]}</div>'
    return formatted_history

@app.route("/", methods=["GET", "POST"])
def index():
    global TEXT_BASED_OLLAMA_MODEL, SYSTEM_PROMPT
    
    if request.method == "POST" and request.form.get("system_prompt"):
        new_prompt = request.form.get("system_prompt", "").strip()
        if new_prompt:
            SYSTEM_PROMPT = new_prompt
            reset_conversation_with_prompt(new_prompt)
            trigger_initial_prompt()
            flash("System prompt updated and conversation reset.")
            return redirect(url_for("index"))

    response = ""
    initial_description = ""
    message_history = load_conversation_history(HISTORY_FILE_PATH)

    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        initial_description = request.form.get("initial_description", "")
        message_history = json.loads(request.form.get("message_history", "[]"))

        uploaded_file = request.files.get('file')
        uploaded_file_path = None
        if uploaded_file and uploaded_file.filename != '':
            filename = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(filename)
            uploaded_file_path = filename

            try:
                response, message_history, initial_description = continue_conversation(message_history, user_input, initial_description, uploaded_file_path)
            except Exception as e:
                response = f"Failed to continue the conversation: {e}"
                message_history = []
        else:
            # Add the user input to the conversation history
            message_history.append({"role": "user", "content": user_input})
            save_conversation_history(HISTORY_FILE_PATH, message_history)

            # Generate the response based on the updated conversation history
            full_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history])
            response = generate_text_response(TEXT_BASED_OLLAMA_MODEL, full_context)

            # Add the bot's response to the conversation history
            message_history.append({"role": "assistant", "content": response})
            save_conversation_history(HISTORY_FILE_PATH, message_history)

    message_history_formatted = format_message_history(message_history)

    return render_template(
        "index.html",
        user_input="",
        response=response,
        message_history=json.dumps(message_history),
        message_history_formatted=message_history_formatted,
        initial_description=initial_description,
        system_prompt=SYSTEM_PROMPT,
        selected_model=TEXT_BASED_OLLAMA_MODEL
    )

@app.route("/set_system_prompt", methods=["POST"])
def set_system_prompt():
    global SYSTEM_PROMPT
    new_prompt = request.form["system_prompt"]
    if new_prompt:
        SYSTEM_PROMPT = new_prompt
        reset_conversation_with_prompt(new_prompt)
        trigger_initial_prompt()
    return redirect(url_for("index"))

@app.route("/reset", methods=["POST"])
def clear_conversation():
    delete_history_file(HISTORY_FILE_PATH)
    reset_conversation_with_prompt(SYSTEM_PROMPT)
    return '', 204

def reset_conversation_with_prompt(prompt):
    message_history = [{"role": "system", "content": prompt}]
    save_conversation_history(HISTORY_FILE_PATH, message_history)

def trigger_initial_prompt():
    try:
        message_history = load_conversation_history(HISTORY_FILE_PATH)
        user_input = "Describe your new system prompt in detail stating how you'll now talk to me going forward based on it."
        message_history.append({"role": "user", "content": user_input})
        full_context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in message_history])
        response = generate_text_response(TEXT_BASED_OLLAMA_MODEL, full_context)
        message_history.append({"role": "assistant", "content": response})
        save_conversation_history(HISTORY_FILE_PATH, message_history)
    except Exception as e:
        print(f"Failed to trigger initial prompt: {e}")

if __name__ == "__main__":
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        atexit.register(stop_ollama_service)
        atexit.register(clear_gpu_memory)

        print("Killing existing Ollama service...")
        kill_existing_ollama_service()
        clear_gpu_memory()

        print("Resetting conversation history with the default system prompt...")
        delete_history_file(HISTORY_FILE_PATH)
        reset_conversation_with_prompt(DEFAULT_SYSTEM_PROMPT)

        print("Installing and setting up Ollama...")
        install_and_setup_ollama(TEXT_BASED_OLLAMA_MODEL)

        if is_windows():
            print("Starting Ollama service on Windows...")
            start_ollama_service_windows()

        app.run(host="0.0.0.0", port=5000, debug=True)