
from typing import Tuple, Callable, List
from pydantic import BaseModel, Field
from sources.utility import pretty_print

class QueryRequest(BaseModel):
    query: str
    tts_enabled: bool = True

    def __str__(self):
        return f"Query: {self.query}, Language: {self.lang}, TTS: {self.tts_enabled}, STT: {self.stt_enabled}"

    def jsonify(self):
        return {
            "query": self.query,
            "tts_enabled": self.tts_enabled,
        }

class QueryResponse(BaseModel):
    done: str
    answer: str
    reasoning: str
    agent_name: str
    success: str
    blocks: dict
    status: str
    uid: str

    def __str__(self):
        return f"Done: {self.done}, Answer: {self.answer}, Agent Name: {self.agent_name}, Success: {self.success}, Blocks: {self.blocks}, Status: {self.status}, UID: {self.uid}"

    def jsonify(self):
        return {
            "done": self.done,
            "answer": self.answer,
            "reasoning": self.reasoning,
            "agent_name": self.agent_name,
            "success": self.success,
            "blocks": self.blocks,
            "status": self.status,
            "uid": self.uid
        }


class CommunityCommentCreate(BaseModel):
    content: str
    author: str = "Anonymous"


class CommunityComment(BaseModel):
    id: str
    content: str
    author: str
    created_at: float


class CommunityPostCreate(BaseModel):
    content: str
    author: str = "Anonymous"


class CommunityPost(BaseModel):
    id: str
    content: str
    author: str
    likes: int = 0
    comments: List[CommunityComment] = Field(default_factory=list)
    created_at: float

class executorResult:
    """
    A class to store the result of a tool execution.
    """
    def __init__(self, block: str, feedback: str, success: bool, tool_type: str):
        """
        Initialize an agent with execution results.

        Args:
            block: The content or code block processed by the agent.
            feedback: Feedback or response information from the execution.
            success: Boolean indicating whether the agent's execution was successful.
            tool_type: The type of tool used by the agent for execution.
        """
        self.block = block
        self.feedback = feedback
        self.success = success
        self.tool_type = tool_type
    
    def __str__(self):
        return f"Tool: {self.tool_type}\nBlock: {self.block}\nFeedback: {self.feedback}\nSuccess: {self.success}"
    
    def jsonify(self):
        return {
            "block": self.block,
            "feedback": self.feedback,
            "success": self.success,
            "tool_type": self.tool_type
        }

    def show(self):
        pretty_print('▂'*64, color="status")
        pretty_print(self.feedback, color="success" if self.success else "failure")
        pretty_print('▂'*64, color="status")