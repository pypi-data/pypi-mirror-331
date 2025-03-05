from litemind.agent.messages.message import Message
from litemind.agent.react.react_agent import ReActAgent
from litemind.apis.model_features import ModelFeatures
from litemind.apis.providers.openai.openai_api import OpenAIApi

# Initialize the OpenAI API
api = OpenAIApi()

# Create the ReAct agent
agent = ReActAgent(api=api, model_features=ModelFeatures.Image)

# Create a message with text and an image
message = Message(role="user")
message.append_text("Describe the image:")
message.append_image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg/456px-Einstein_1921_by_F_Schmutzer_-_restoration.jpg")

# Run the agent
response = agent(message)
