Smart Code Companion (Refactored)
This project provides a robust FastAPI backend for AI-powered code analysis. It has been refactored to use a modular, configurable architecture that allows for easy switching between different AI providers.

Key Changes in this Refactor
Modular AI Clients: All AI client logic is isolated in the smart_code_companion/ai_clients/ directory.

Dependency Injection: The main application (main.py) no longer imports specific clients. Instead, it uses a factory function and FastAPI's Depends system to inject the currently configured client.

Centralized Configuration: The AI provider can be changed by editing a single line in smart_code_companion/core/config.py.

How to Run on Windows
1. Create a Virtual Environment
Open Command Prompt (cmd) or PowerShell, navigate to the project's root directory:

# Create a virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

2. Install Dependencies
Install all required packages:

pip install -r requirements.txt

3. Run the FastAPI Server
Start the application with Uvicorn. The --reload flag automatically restarts the server when you make code changes.

uvicorn smart_code_companion.main:app --reload

You should see output indicating the server is running on http://127.0.0.1:8000.

4. Test the Endpoint
You can test the API using the automatically generated documentation or a tool like curl.

Option A: Using the Interactive Docs
Open your web browser and navigate to http://127.0.0.1:8000/docs.

Expand the POST /api/v1/comment endpoint.

Click "Try it out".

Fill in the example JSON body with your code and a skill level (beginner, intermediate, or advanced).

Click "Execute". You will see the response from the currently configured AI client (the mock client by default).

Option B: Using curl in Command Prompt
# Test the /comment endpoint for a beginner
curl -X POST "[http://127.0.0.1:8000/api/v1/comment](http://127.0.0.1:8000/api/v1/comment)" ^
-H "Content-Type: application/json" ^
-d "{\"code\": \"for i in range(5): print('hello')\", \"level\": \"beginner\"}"

How to Switch AI Clients
Open the file smart_code_companion/core/config.py.

Change the value of the AI_PROVIDER variable to "google", "ibm", or "mock".

Save the file. If the uvicorn server is running with --reload, it will automatically restart with the new client.