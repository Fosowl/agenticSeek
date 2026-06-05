import re
import time
import configparser
from datetime import date
from typing import List, Tuple, Type, Dict
from enum import Enum
import asyncio

from sources.utility import pretty_print, animate_thinking
from sources.agents.agent import Agent
from sources.tools.searxSearch import searxSearch
from sources.tools.tavilySearch import tavilySearch
from sources.browser import Browser
from sources.logger import Logger
from sources.memory import Memory

class Action(Enum):
    REQUEST_EXIT = "REQUEST_EXIT"
    FORM_FILLED = "FORM_FILLED"
    GO_BACK = "GO_BACK"
    NAVIGATE = "NAVIGATE"
    SEARCH = "SEARCH"
    
class BrowserAgent(Agent):
    def __init__(self, name, prompt_path, provider, verbose=False, browser=None):
        """
        The Browser agent is an agent that navigate the web autonomously in search of answer
        """
        super().__init__(name, prompt_path, provider, verbose, browser)
        self.tools = {
            "web_search": self._init_search_tool(),
        }
        self.role = "web"
        self.type = "browser_agent"
        self.browser = browser
        self.current_page = ""
        self.search_history = []
        self.navigable_links = []
        self.last_action = Action.NAVIGATE.value
        self.notes = []
        self.date = self.get_today_date()
        self.logger = Logger("browser_agent.log")
        self.memory = Memory(self.load_prompt(prompt_path),
                        recover_last_session=False, # session recovery in handled by the interaction class
                        memory_compression=False,
                        model_provider=provider.get_model_name() if provider else None)
    
    def _init_search_tool(self):
        """Select search tool based on config.ini search_provider setting."""
        config = configparser.ConfigParser()
        config.read('./config.ini')
        provider = config.get('MAIN', 'search_provider', fallback='searxng').strip().lower()
        if provider == 'tavily':
            return tavilySearch()
        return searxSearch()

    def get_today_date(self) -> str:
        """Get the date"""
        date_time = date.today()
        return date_time.strftime("%B %d, %Y")

    def extract_links(self, search_result: str) -> List[str]:
        """Extract all links from a sentence."""
        pattern = r'(https?://\S+|www\.\S+)'
        matches = re.findall(pattern, search_result)
        trailing_punct = ".,!?;:)"
        cleaned_links = [link.rstrip(trailing_punct) for link in matches]
        self.logger.info(f"Extracted links: {cleaned_links}")
        return self.clean_links(cleaned_links)
    
    def extract_form(self, text: str) -> List[str]:
        """Extract form written by the LLM in format [input_name](value)"""
        inputs = []
        matches = re.findall(r"\[\w+\]\([^)]+\)", text)
        return matches
        
    def clean_links(self, links: List[str]) -> List[str]:
        """Ensure no '.' at the end of link"""
        links_clean = []
        for link in links:
            link = link.strip()
            if not (link[-1].isalpha() or link[-1].isdigit()):
                links_clean.append(link[:-1])
            else:
                links_clean.append(link)
        return links_clean

    def get_unvisited_links(self) -> List[str]:
        return "\n".join([f"[{i}] {link}" for i, link in enumerate(self.navigable_links) if link not in self.search_history])

    def make_newsearch_prompt(self, prompt: str, search_result: dict) -> str:
        search_choice = self.stringify_search_results(search_result)
        self.logger.info(f"Search results: {search_choice}")
        return f"""
        Based on the search result:
        {search_choice}
        Your goal is to find accurate and complete information to satisfy the user’s request.
        User request: {prompt}
        To proceed, choose a relevant link from the search results. Announce your choice by saying: "I will navigate to <link>"
        Do not explain your choice.
        """
    
    def make_navigation_prompt(self, user_prompt: str, page_text: str) -> str:
        remaining_links = self.get_unvisited_links() 
        remaining_links_text = remaining_links if remaining_links is not None else "No links remaining, do a new search." 
        inputs_form = self.browser.get_form_inputs()
        inputs_form_text = '\n'.join(inputs_form)
        notes = '\n'.join(self.notes)
        self.logger.info(f"Making navigation prompt with page text: {page_text[:100]}...\nremaining links: {remaining_links_text}")
        self.logger.info(f"Inputs form: {inputs_form_text}")
        self.logger.info(f"Notes: {notes}")

        return f"""
        You are navigating the web.

        **Current Context**

        Webpage ({self.current_page}) content:
        {page_text}

        Allowed Navigation Links:
        {remaining_links_text}

        Inputs forms:
        {inputs_form_text}

        End of webpage ({self.current_page}.

        # Instruction

        1. **Evaluate if the page is relevant for user’s query and document finding:**
          - If the page is relevant, extract and summarize key information in concise notes (Note: <your note>)
          - If page not relevant, state: "Error: <specific reason the page does not address the query>" and either return to the previous page or navigate to a new link.
          - Notes should be factual, useful summaries of relevant content, they should always include specific names or link. Written as: "On <website URL>, <key fact 1>. <Key fact 2>. <Additional insight>." Avoid phrases like "the page provides" or "I found that."
        2. **Navigate to a link by either: **
          - Saying I will navigate to (write down the full URL) www.example.com/cats
          - Going back: If no link seems helpful, say: {Action.GO_BACK.value}.
        3. **Fill forms on the page:**
          - Fill form only when relevant.
          - Use Login if username/password specified by user. For quick task create account, remember password in a note.
          - You can fill a form using [form_name](value). Don't {Action.GO_BACK.value} when filling form.
          - If a form is irrelevant or you lack informations (eg: don't know user email) leave it empty.
        4. **Decide if you completed the task**
          - Check your notes. Do they fully answer the question? Did you verify with multiple pages?
          - Are you sure it’s correct?
          - If yes to all, say {Action.REQUEST_EXIT}.
          - If no, or a page lacks info, go to another link.
          - Never stop or ask the user for help.
        
        **Rules:**
        - Do not write "The page talk about ...", write your finding on the page and how they contribute to an answer.
        - Put note in a single paragraph.
        - When you exit, explain why.
        
        # Example:
        
        Example 1 (useful page, no need go futher):
        Note: According to karpathy site LeCun net is ...
        No link seem useful to provide futher information.
        Action: {Action.GO_BACK.value}

        Example 2 (not useful, see useful link on page):
        Error: reddit.com/welcome does not discuss anything related to the user’s query.
        There is a link that could lead to the information.
        Action: navigate to http://reddit.com/r/locallama

        Example 3 (not useful, no related links):
        Error: x.com does not discuss anything related to the user’s query and no navigation link are usefull.
        Action: {Action.GO_BACK.value}

        Example 3 (clear definitive query answer found or enought notes taken):
        I took 10 notes so far with enought finding to answer user question.
        Therefore I should exit the web browser.
        Action: {Action.REQUEST_EXIT.value}

        Example 4 (loging form visible):

        Note: I am on the login page, I will type the given username and password. 
        Action:
        [username_field](David)
        [password_field](edgerunners77)

        Remember, user asked:
        {user_prompt}
        You previously took these notes:
        {notes}
        Do not Step-by-Step explanation. Write comprehensive Notes or Error as a long paragraph followed by your action.
        You must always take notes.
        """
    
    async def llm_decide(self, prompt: str, show_reasoning: bool = False) -> Tuple[str, str]:
        animate_thinking("Thinking...", color="status")
        self.memory.push('user', prompt)
        answer, reasoning = await self.llm_request()
        self.last_reasoning = reasoning
        if show_reasoning:
            pretty_print(reasoning, color="failure")
        pretty_print(answer, color="output")
        return answer, reasoning
    
    def select_unvisited(self, search_result: List[str]) -> List[str]:
        results_unvisited = []
        for res in search_result:
            if res["link"] not in self.search_history:
                results_unvisited.append(res) 
        self.logger.info(f"Unvisited links: {results_unvisited}")
        return results_unvisited

    def jsonify_search_results(self, results_string: str) -> List[str]:
        result_blocks = results_string.split("\n\n")
        parsed_results = []
        for block in result_blocks:
            if not block.strip():
                continue
            lines = block.split("\n")
            result_dict = {}
            for line in lines:
                if line.startswith("Title:"):
                    result_dict["title"] = line.replace("Title:", "").strip()
                elif line.startswith("Snippet:"):
                    result_dict["snippet"] = line.replace("Snippet:", "").strip()
                elif line.startswith("Link:"):
                    result_dict["link"] = line.replace("Link:", "").strip()
            if result_dict:
                parsed_results.append(result_dict)
        return parsed_results 
    
    def stringify_search_results(self, results_arr: List[str]) -> str:
        return '\n\n'.join([f"Link: {res['link']}\nPreview: {res['snippet']}" for res in results_arr])
    
    def parse_answer(self, text):
        lines = text.split('\n')
        saving = False
        buffer = []
        links = []
        for line in lines:
            if line == '' or 'action:' in line.lower():
                saving = False
            if "note" in line.lower():
                saving = True
            if saving:
                buffer.append(line.replace("notes:", ''))
            else:
                links.extend(self.extract_links(line))
        self.notes.append('. '.join(buffer).strip())
        return links
    
    def select_link(self, links: List[str]) -> str | None:
        """
        Select the first unvisited link that is not the current page.
        Preference is given to links not in search_history.
        """
        for lk in links:
            if lk == self.current_page or lk in self.search_history:
                self.logger.info(f"Skipping already visited or current link: {lk}")
                continue
            self.logger.info(f"Selected link: {lk}")
            return lk
        self.logger.warning("No suitable link selected.")
        return None
    
    def get_page_text(self, limit_to_model_ctx = False) -> str:
        """Get the text content of the current page."""
        page_text = self.browser.get_text()
        if limit_to_model_ctx:
            #page_text = self.memory.compress_text_to_max_ctx(page_text)
            page_text = self.memory.trim_text_to_max_ctx(page_text)
        return page_text
    
    def conclude_prompt(self, user_query: str) -> str:
        annotated_notes = [f"{i+1}: {note.lower()}" for i, note in enumerate(self.notes)]
        search_note = '\n'.join(annotated_notes)
        pretty_print(f"AI notes:\n{search_note}", color="success")
        return f"""
        Following a human request:
        {user_query}
        A web browsing AI made the following finding across different pages:
        {search_note}

        Expand on the finding or step that lead to success, and provide a conclusion that answer the request. Include link when possible.
        Do not give advices or try to answer the human. Just structure the AI finding in a structured and clear way.
        You should answer in the same language as the user.
        """
    
    def search_prompt(self, user_prompt: str) -> str:
        return f"""
        Current date: {self.date}
        Make a efficient search engine query to help users with their request:
        {user_prompt}
        Example:
        User: "go to twitter, login with username toto and password pass79 to my twitter and say hello everyone "
        You: search: Twitter login page. 

        User: "I need info on the best laptops for AI this year."
        You: "search: best laptops 2025 to run Machine Learning model, reviews"

        User: "Search for recent news about space missions."
        You: "search: Recent space missions news, {self.date}"

        Do not explain, do not write anything beside the search query.
        Except if query does not make any sense for a web search then explain why and say {Action.REQUEST_EXIT.value}
        Do not try to answer query. you can only formulate search term or exit.
        """
    
    def handle_update_prompt(self, user_prompt: str, page_text: str, fill_success: bool) -> str:
        prompt = f"""
        You are a web browser.
        You just filled a form on the page.
        Now you should see the result of the form submission on the page:
        Page text:
        {page_text}
        The user asked: {user_prompt}
        Does the page answer the user’s query now? Are you still on a login page or did you get redirected?
        If it does, take notes of the useful information, write down result and say {Action.FORM_FILLED.value}.
        if it doesn’t, say: Error: Attempt to fill form didn't work {Action.GO_BACK.value}.
        If you were previously on a login form, no need to take notes.
        """
        if not fill_success:
            prompt += f"""
            According to browser feedback, the form was not filled correctly. Is that so? you might consider other strategies.
            """
        return prompt
    
    def show_search_results(self, search_result: List[str]):
        pretty_print("\nSearch results:", color="output")
        for res in search_result:
            pretty_print(f"Title: {res['title']} - ", color="info", no_newline=True)
            pretty_print(f"Link: {res['link']}", color="status")
    
    def stuck_prompt(self, user_prompt: str, unvisited: List[str]) -> str:
        """
        Prompt for when the agent repeat itself, can happen when fail to extract a link.
        """
        prompt = self.make_newsearch_prompt(user_prompt, unvisited)
        prompt += f"""
        You previously said:
        {self.last_answer}
        You must consider other options. Choose other link.
        """
        return prompt
    
    async def process(self, user_prompt: str, speech_module: type) -> Tuple[str, str]:
        """
        Process the user prompt to conduct an autonomous web search.
        Start with a google search with searxng using web_search tool.
        Then enter a navigation logic to find the answer or conduct required actions.
        Args:
          user_prompt: The user's input query
          speech_module: Optional speech output module
        Returns:
            tuple containing the final answer and reasoning
        """
        complete = False

        animate_thinking(f"Thinking...", color="status")
        mem_begin_idx = self.memory.push('user', self.search_prompt(user_prompt))
        ai_prompt, reasoning = await self.llm_request()
        if Action.REQUEST_EXIT.value in ai_prompt:
            pretty_print(f"Web agent requested exit.\n{reasoning}\n\n{ai_prompt}", color="failure")
            return ai_prompt, "" 
        animate_thinking(f"Searching...", color="status")
        self.status_message = "Searching..."
        search_result_raw = self.tools["web_search"].execute([ai_prompt], False)
        search_result = self.jsonify_search_results(search_result_raw)[:16]
        self.show_search_results(search_result)
        prompt = self.make_newsearch_prompt(user_prompt, search_result)
        unvisited = [None]
        while not complete and len(unvisited) > 0 and not self.stop:
            self.memory.clear()
            unvisited = self.select_unvisited(search_result)
            answer, reasoning = await self.llm_decide(prompt, show_reasoning = False)
            if self.stop:
                pretty_print(f"Requested stop.", color="failure")
                break
            if self.last_answer == answer:
                prompt = self.stuck_prompt(user_prompt, unvisited)
                continue
            self.last_answer = answer
            pretty_print('▂'*32, color="status")

            extracted_form = self.extract_form(answer)
            if len(extracted_form) > 0:
                self.status_message = "Filling web form..."
                pretty_print(f"Filling inputs form...", color="status")
                fill_success = self.browser.fill_form(extracted_form)
                page_text = self.get_page_text(limit_to_model_ctx=True)
                answer = self.handle_update_prompt(user_prompt, page_text, fill_success)
                answer, reasoning = await self.llm_decide(prompt)

            if Action.FORM_FILLED.value in answer:
                pretty_print(f"Filled form. Handling page update.", color="status")
                page_text = self.get_page_text(limit_to_model_ctx=True)
                self.navigable_links = self.browser.get_navigable()
                prompt = self.make_navigation_prompt(user_prompt, page_text)
                continue

            links = self.parse_answer(answer)
            link = self.select_link(links)
            if link == self.current_page:
                pretty_print(f"Already visited {link}. Search callback.", color="status")
                prompt = self.make_newsearch_prompt(user_prompt, unvisited)
                self.search_history.append(link)
                continue

            if Action.REQUEST_EXIT.value in answer:
                self.status_message = "Exiting web browser..."
                pretty_print(f"Agent requested exit.", color="status")
                complete = True
                break

            if (link == None and len(extracted_form) < 3) or Action.GO_BACK.value in answer or link in self.search_history:
                pretty_print(f"Going back to results. Still {len(unvisited)}", color="status")
                self.status_message = "Going back to search results..."
                request_prompt = user_prompt
                if link is None:
                    request_prompt += f"\nYou previously choosen:\n{self.last_answer} but the website is unavailable. Consider other options."
                prompt = self.make_newsearch_prompt(request_prompt, unvisited)
                self.search_history.append(link)
                self.current_page = link
                continue

            animate_thinking(f"Navigating to {link}", color="status")
            if speech_module: speech_module.speak(f"Navigating to {link}")
            nav_ok = self.browser.go_to(link)
            self.search_history.append(link)
            if not nav_ok:
                pretty_print(f"Failed to navigate to {link}.", color="failure")
                prompt = self.make_newsearch_prompt(user_prompt, unvisited)
                continue
            self.current_page = link
            page_text = self.get_page_text(limit_to_model_ctx=True)
            self.navigable_links = self.browser.get_navigable()
            prompt = self.make_navigation_prompt(user_prompt, page_text)
            self.status_message = "Navigating..."
            self.browser.screenshot()

        pretty_print("Exited navigation, starting to summarize finding...", color="status")
        prompt = self.conclude_prompt(user_prompt)
        mem_last_idx = self.memory.push('user', prompt)
        self.status_message = "Summarizing findings..."
        answer, reasoning = await self.llm_request()
        pretty_print(answer, color="output")
        self.status_message = "Ready"
        self.last_answer = answer
        return answer, reasoning

if __name__ == "__main__":
    pass
