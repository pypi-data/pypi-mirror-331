# CoffeeAI Library

CoffeeAI is a Python library for neural network applications. The library requires an API key to operate, which can be generated via a Flask server.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/coffeeai.git
    cd coffeeai
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the Flask server to generate and validate API keys:
    ```bash
    python server/server.py
    ```

4. Use the CoffeeAI library:
    ```python
    from coffeeai.coffeeai import CoffeeAI

    # Insert your generated API key
    ai = CoffeeAI(api_key='your_generated_key')

    # Train and predict
    ```

## License
MIT License
