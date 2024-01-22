import tkinter as tk
from tkinter import ttk
import openai
from tkinter import filedialog
import base64
from tkinter import PhotoImage

history_limit = 4  # Default history limit
max_tokens = 150  # Default tokens
text_chat_history = []
image_chat_history = []
is_image_context = False  # Flag to track conversation context

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
        
def select_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        encoded_image = encode_image(file_path)
        api_key = entry_api_key.get()
        response = send_request_to_gpt(api_key, "", image_data=encoded_image)
        chat_history.insert(tk.END, "Image Analysis: " + response + "\n\n")

def send_request_to_gpt(api_key, user_input, image_url=None, image_data=None):
    global text_chat_history, image_chat_history, is_image_context, history_limit, max_tokens
    openai.api_key = api_key

    # Determine which history and model to use based on the input type
    if image_data:
        is_image_context = True
        history = image_chat_history
        model = "gpt-4-vision-preview"
        content = [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}]
    elif image_url:
        is_image_context = True
        history = image_chat_history
        model = "gpt-4-vision-preview"
        content = [{"type": "image_url", "image_url": {"url": image_url}}]
    else:
        history = text_chat_history
        model = "gpt-4-1106-preview"
        content = user_input

    # Prepare messages for GPT
    messages = [{"role": "user", "content": message} for message in history]
    messages.append({"role": "user", "content": content})

    # Retrieve and validate max_tokens from user input
    try:
        max_tokens = int(entry_max_tokens.get())
    except ValueError:
        max_tokens = 150  # Default value if input is invalid

    # Call the OpenAI API
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens
    )

    # Get GPT response and update chat history
    gpt_response = response.choices[0].message['content'].strip()
    history.append(gpt_response)

    # Limit the history size based on history_limit
    history = history[-history_limit:]

    return gpt_response

def handle_send():
    global is_image_context
    user_input = entry_text.get()
    api_key = entry_api_key.get()
    image_url = entry_image_url.get()

    # Send the request to GPT and get the response
    response = send_request_to_gpt(api_key, user_input, image_url)

    # Append only the new interaction to the chat window
    chat_history.insert(tk.END, "You: " + (user_input or image_url) + "\n")
    chat_history.insert(tk.END, "GPT: " + response + "\n\n")

    # Clear the input fields
    entry_text.delete(0, tk.END)
    entry_image_url.delete(0, tk.END)

    # Reset image context if no image URL is provided
    if not image_url and is_image_context:
        is_image_context = False  # Reset context to text
        
def open_help_window():
    help_window = tk.Toplevel(root)
    help_window.title("Help")
    help_window.geometry("400x300")  # Adjust size as needed

    tk.Label(help_window, text="API Key: Used for authenticating with OpenAI's API.\n You can get your own key from OpenAI.").pack()
    tk.Label(help_window, text="History Limit: Sets how many messages are kept in history.\n Larger history more token use.").pack()
    tk.Label(help_window, text="Max Tokens: Determines the length of the GPT response.\n You can buy Tokens from OpenAI.").pack()
    tk.Label(help_window, text="Image URL: Upload image via URL.").pack()
    tk.Label(help_window, text="Upload image: Local upload.").pack()
    tk.Label(help_window, text="\n\n\n").pack()
    tk.Label(help_window, text="Made by Ross Masyukov.").pack()
    tk.Label(help_window, text="Github: https://github.com/RossEcho").pack()
    tk.Label(help_window, text="Email: masyukov.ross@gmail.com").pack()

root = tk.Tk()
root.title("GPT Chat Interface - by Ross Ornias")
root.geometry("600x600")
style = ttk.Style()
style.configure('TButton', font=('Helvetica', 10))
style.configure('TLabel', font=('Helvetica', 10))
style.configure('TEntry', font=('Helvetica', 10))

# Load the logo image
logo_image = PhotoImage(file="logo.png")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X)

# Help button
help_button = ttk.Button(top_frame, text="Help", command=open_help_window)
help_button.pack(side=tk.LEFT, padx=10)

# Logo
logo_label = tk.Label(top_frame, image=logo_image)
logo_label.pack(side=tk.LEFT, padx=10, pady=10)

# Frame for controls
controls_frame = tk.Frame(top_frame)
controls_frame.pack(side=tk.LEFT, padx=10, pady=10)

# API Key
label_api_key = ttk.Label(controls_frame, text="API Key:")
label_api_key.pack(side=tk.TOP, fill=tk.X)
entry_api_key = ttk.Entry(controls_frame, width=50, show="*")
entry_api_key.pack(side=tk.TOP, fill=tk.X)

# Image URL
label_image_url = ttk.Label(controls_frame, text="Image URL:")
label_image_url.pack(side=tk.TOP, fill=tk.X)
entry_image_url = ttk.Entry(controls_frame, width=50)
entry_image_url.pack(side=tk.TOP, fill=tk.X)

# Image Upload Button
image_upload_button = ttk.Button(controls_frame, text="Upload Image", command=select_image)
image_upload_button.pack(side=tk.TOP, fill=tk.X)

# Sub-frame for history limit and max tokens inside controls_frame
settings_frame = tk.Frame(controls_frame)
settings_frame.pack(fill=tk.X)

# History Limit
label_history_limit = ttk.Label(settings_frame, text="History Limit:")
label_history_limit.pack(side=tk.LEFT)
entry_history_limit = ttk.Entry(settings_frame, width=10)
entry_history_limit.insert(0, "4")  # Default value
entry_history_limit.pack(side=tk.LEFT)

# Max Tokens
label_max_tokens = ttk.Label(settings_frame, text="Max Tokens:")
label_max_tokens.pack(side=tk.LEFT)
entry_max_tokens = ttk.Entry(settings_frame, width=10)
entry_max_tokens.insert(0, "150")  # Default value
entry_max_tokens.pack(side=tk.LEFT)

# Output Text Area
label_output = ttk.Label(root, text="Output:")
label_output.pack(fill=tk.X, padx=10, pady=5)
chat_history = tk.Text(root, height=15, bd=2, relief="groove")
chat_history.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Text Input Field
label_text = ttk.Label(root, text="Text Input:")
label_text.pack(fill=tk.X, padx=10, pady=5)
entry_text = ttk.Entry(root)
entry_text.pack(fill=tk.X, padx=10, pady=5)

# Send Button
send_button = ttk.Button(root, text="Send", command=handle_send)
send_button.pack()

root.mainloop()
