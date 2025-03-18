import os
import sys
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sources.agents.agent import Agent
from sources.agents.code_agent import CoderAgent
from sources.agents.casual_agent import CasualAgent
from sources.agents.planner_agent import PlannerAgent
from sources.utility import pretty_print

class AgentRouter:
    """
    AgentRouter is a class that selects the appropriate agent based on the user query.
    """
    def __init__(self, agents: list, model_name: str = "facebook/bart-large-mnli"):
        self.model = model_name
        self.pipeline = None
        if config.getboolean('MAIN', 'is_local') and config["MAIN"]["provider_name"] != "openai":
            import torch
            self.device = "mps" if torch.backends.mps.is_available() else "cuda:0" if torch.cuda.is_available() else "cpu"
            from transformers import pipeline
            self.pipeline = pipeline("zero-shot-classification",
                          model=self.model, device = self.device)
        self.agents = agents
        self.labels = [agent.role for agent in agents]

    def get_device(self) -> str:
        if config.getboolean('MAIN', 'is_local') and config["MAIN"]["provider_name"] != "openai":
            return self.device
        else:
            return "cpu"

    def classify_text(self, text: str, threshold: float = 0.5) -> list:
        """
        Classify the text into labels (agent roles).
        Args:
            text (str): The text to classify
            threshold (float, optional): The threshold for the classification.
        Returns:
            list: The list of agents and their scores
        """
        # if not config.getboolean('MAIN', 'is_local'):
        #     print("Warning: Agent Router is not running locally, classification is disabled.")
        #     return {"labels": [self.labels[0]], "scores": [1.0]}

        first_sentence = None
        for line in text.split("\n"):
                first_sentence = line.strip()
                break
        if first_sentence is None:
            first_sentence = text
        
        if config["MAIN"]["provider_name"] == "openai":
            from openai import OpenAI
            client = OpenAI(base_url=f"http://{config['MAIN']['provider_server_address']}", api_key="none")
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a zero-shot classifier.  Given a sentence, you must classify it into one of these categories: " + ", ".join(self.labels)},
                        {"role": "user", "content": first_sentence}
                    ],
                    temperature=0.0
                )
                classification = response.choices[0].message.content.strip()
                scores = [0.0] * len(self.labels)
                if classification in self.labels:
                    index = self.labels.index(classification)
                    scores[index] = 1.0
                else:
                    print(f"Warning: Classification '{classification}' not found in labels.")
                return {"labels": [classification], "scores": scores}
            except Exception as e:
                print(f"Error during OpenAI classification: {e}")
                return {"labels": [self.labels[0]], "scores": [0.0]}
        else:
            result = self.pipeline(first_sentence, self.labels, threshold=threshold)
            return result
    
    def select_agent(self, text: str) -> Agent:
        """
        Select the appropriate agent based on the text.
        Args:
            text (str): The text to select the agent from
        Returns:
            Agent: The selected agent
        """
        if len(self.agents) == 0 or len(self.labels) == 0:
            return self.agents[0]
        result = self.classify_text(text)
        selected_agent = None
        for agent in self.agents:
            if result["labels"][0] == agent.role:
                selected_agent = agent
                break
        if selected_agent is None:
            pretty_print(f"No agent found for classification '{result['labels'][0]}', using default agent.", color="warning")
            selected_agent = self.agents[0]  # Use the first agent as the default
        pretty_print(f"Selected agent: {selected_agent.agent_name}", color="warning")
        return selected_agent

if __name__ == "__main__":
    agents = [
        CoderAgent(config["MAIN"]["provider_model"], "agent1", "../prompts/coder_agent.txt", "server"),
        CasualAgent(config["MAIN"]["provider_model"], "agent2", "../prompts/casual_agent.txt", "server"),
        PlannerAgent(config["MAIN"]["provider_model"], "agent3", "../prompts/planner_agent.txt", "server")
    ]
    router = AgentRouter(agents)
    
    texts = ["""
    Write a python script to check if the device on my network is connected to the internet
    """,
    """
    Hey could you search the web for the latest news on the stock market ?
    """,
    """
    hey can you give give a list of the files in the current directory ?
    """,
    """
    Make a cool game to illustrate the current relation between USA and europe
    """
    ]

    for text in texts:
        print(text)
        results = router.classify_text(text)
        for result in results:
            print(result["label"], "=>", result["score"])
        agent = router.select_agent(text)
        print("Selected agent role:", agent.role)
