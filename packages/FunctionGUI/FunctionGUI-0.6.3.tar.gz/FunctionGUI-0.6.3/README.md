## Sentience 

Sentience is a basic AI library made to simplify the usage of the genai library by providing basic functions for chat at a higher level.


## Installation

To install Sentience, you can simply use:

```bash
pip install Sentience 
```

## Usage
```python
#Set your api (does not return in a variable)
API(your_api_key)
#Make the model, settings can be altered (returns the model in a variable), code example provides default settings
model = Model(model = "gemini-1.5-pro", temperature = 1, top_p = 0.95, top_k = 40, max_output_tokens = 8192)

#Uses model created above to make a chat (returns chat in a variable)
chat = Chat(model)

#Sends a message to your chat, replace chat with the varible you have named your chat
response = Send(chat, "Hello, how are you?")

print(response)
```

# Bugs

If you are finding bugs in the code, please report them to me @aaroh.charne@gmail.com.
Please include a snippet of your code as well the problem. Thank You


```