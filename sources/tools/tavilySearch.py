import sys
import os

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tavily import TavilyClient
from sources.tools.tools import Tools

class tavilySearch(Tools):
    def __init__(self):
        """
        A tool for searching the web using the Tavily API.
        """
        super().__init__()
        self.tag = "web_search"
        self.name = "tavilySearch"
        self.description = "A tool for searching the web using Tavily"
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY must be set as an environment variable.")
        self.client = TavilyClient(api_key=api_key)

    def execute(self, blocks: list, safety: bool = False) -> str:
        """Executes a search query using the Tavily API and returns formatted results."""
        if not blocks:
            return "Error: No search query provided."

        query = blocks[0].strip()
        if not query:
            return "Error: Empty search query provided."

        try:
            response = self.client.search(
                query=query,
                max_results=10,
                search_depth="basic",
                topic="general"
            )
            results = []
            for result in response.get("results", []):
                title = result.get("title", "No Title")
                snippet = result.get("content", "No Description")
                url = result.get("url", "")
                results.append(f"Title:{title}\nSnippet:{snippet}\nLink:{url}")
            if len(results) == 0:
                return "No search results, web search failed."
            return "\n\n".join(results)
        except Exception as e:
            return f"Error during search: Tavily search failed. ({str(e)})"

    def execution_failure_check(self, output: str) -> bool:
        """
        Checks if the execution failed based on the output.
        """
        return "Error" in output or "No search results" in output

    def interpreter_feedback(self, output: str) -> str:
        """
        Feedback of web search to agent.
        """
        if self.execution_failure_check(output):
            return f"Web search failed: {output}"
        return f"Web search result:\n{output}"

if __name__ == "__main__":
    search_tool = tavilySearch()
    result = search_tool.execute(["are dogs better than cats?"])
    print(result)
