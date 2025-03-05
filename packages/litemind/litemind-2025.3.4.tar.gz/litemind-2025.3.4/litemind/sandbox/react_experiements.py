from litemind import OpenAIApi
from litemind.agent.agent import Agent
from litemind.agent.messages.message import Message

# Initialize the OpenAI API
api = OpenAIApi()

# Create the ReAct agent
agent = Agent(api=api)

# Create a message with text and an image
message = Message(role="user")
message.append_text("How to register two 2D images.")
message.append_text("First, analyse the request carefully and provide a list of approaches.")
response = agent(message)

message = Message(role="user")
message.append_text("Chose the best approach and provide a detailed explanation why.")
response = agent(message)

message = Message(role="user")
message.append_text("Write code to implement the chosen approach.")
response = agent(message)


