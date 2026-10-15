import time

import requests
import urllib3
from bs4 import BeautifulSoup
import sys
import os
from typing import List, Optional, Tuple
from urllib.parse import urlencode, urlparse

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools
from sources.errors import AgenticSeekError, connection_detail
from sources.utility import pretty_print

# Reasons SearxNG reports for engines that block automated traffic.
BLOCKED_ENGINE_REASONS = ("too many requests", "captcha", "access denied", "suspended")
MAX_RETRY_AFTER = 30  # seconds; never honour a longer Retry-After

class searxSearch(Tools):
    def __init__(self, base_url: str = None):
        """
        A tool for searching a SearxNG instance and extracting URLs and titles.
        """
        super().__init__()
        self.tag = "web_search"
        self.name = "searxSearch"
        self.description = "A tool for searching a SearxNG for web search"
        self.base_url = base_url or os.getenv("SEARXNG_BASE_URL")  # Requires a SearxNG base URL
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
        # Sane network bounds: without a timeout a hung SearxNG stalls the agent loop.
        self.request_timeout = 15
        self.max_attempts = 3
        self.retry_delay = 2.0  # seconds before the first retry, doubled after each attempt
        self.paywall_keywords = [
            "Member-only", "access denied", "restricted content", "404", "this page is not working"
        ]
        if not self.base_url:
            raise AgenticSeekError(
                "Web search not configured",
                "SEARXNG_BASE_URL is not set, so the web agent has no search engine.",
                causes=["SEARXNG_BASE_URL is missing from .env, or .env was not loaded."],
                fixes=["Add SEARXNG_BASE_URL=http://127.0.0.1:8080 to .env "
                       "(use http://searxng:8080 when running in Docker).",
                       "Make sure SearxNG is running: ./start_services.sh"])

    def link_valid(self, link):
        """check if a link is valid."""
        # TODO find a better way
        if not link.startswith("http"):
            return "Status: Invalid URL"
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        try:
            response = requests.get(link, headers=headers, timeout=5)
            status = response.status_code
            if status == 200:
                content = response.text.lower()
                if any(keyword in content for keyword in self.paywall_keywords):
                    return "Status: Possible Paywall"
                return "Status: OK"
            elif status == 404:
                return "Status: 404 Not Found"
            elif status == 403:
                return "Status: 403 Forbidden"
            else:
                return f"Status: {status} {response.reason}"
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

    def check_all_links(self, links):
        """Check all links, one by one."""
        # TODO Make it asyncromous or smth
        statuses = []
        for i, link in enumerate(links):
            status = self.link_valid(link)
            statuses.append(status)
        return statuses
    
    def _parse_html_results(self, html_content: str) -> list:
        """Extract results from the SearxNG HTML results page."""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        for article in soup.find_all('article', class_='result'):
            url_header = article.find('a', class_='url_header')
            if url_header:
                url = url_header['href']
                title = article.find('h3').text.strip() if article.find('h3') else "No Title"
                description = article.find('p', class_='content').text.strip() if article.find('p', class_='content') else "No Description"
                results.append(f"Title:{title}\nSnippet:{description}\nLink:{url}")
        return results

    def _search_json_api(self, query: str) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Query the SearxNG JSON API, which is stable across UI template changes
        and reports why engines failed. Requires "json" in search.formats of the
        SearxNG settings.
        Returns:
            (results, unresponsive engines as (engine, reason)); ([], []) when the API is unavailable.
        """
        try:
            response = requests.get(
                f"{self.base_url}/search",
                params={'q': query, 'format': 'json', 'categories': 'general', 'language': 'auto', 'safesearch': '0'},
                headers={'User-Agent': self.user_agent, 'Accept': 'application/json'},
                timeout=self.request_timeout
            )
            response.raise_for_status()
            payload = response.json()
        except (requests.exceptions.RequestException, ValueError):
            return [], []
        results = []
        for r in payload.get('results', [])[:20]:
            title = r.get('title') or 'No Title'
            content = r.get('content') or 'No Description'
            results.append(f"Title:{title}\nSnippet:{content}\nLink:{r.get('url', '')}")
        engine_issues = [(str(entry[0]), str(entry[1])) for entry in payload.get('unresponsive_engines', [])
                         if isinstance(entry, (list, tuple)) and len(entry) >= 2]
        return results, engine_issues

    def execute(self, blocks: list, safety: bool = False) -> str:
        """Executes a search query against a SearxNG instance using POST and extracts URLs and titles.
        Falls back to the JSON API when the HTML template yields nothing. Rate limiting,
        timeouts and failing engines are retried with a growing delay.
        Raises:
            AgenticSeekError: SearxNG is unreachable, keeps failing, or finds nothing. Returning
            no results instead would let the LLM invent links.
        """
        if not blocks:
            return "Error: No search query provided."

        query = blocks[0].strip()
        if not query:
            return "Error: Empty search query provided."

        search_url = f"{self.base_url}/search"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.user_agent
        }
        data = urlencode({
            'q': query,
            'categories': 'general',
            'language': 'auto',
            'time_range': '',
            'safesearch': '0',
            'theme': 'simple'
        }).encode('utf-8')

        problem: Tuple[str, object] = ("timeout", None)  # (kind, detail) of the last failed attempt
        for attempt in range(1, self.max_attempts + 1):
            retry_after = None
            try:
                response = requests.post(search_url, headers=headers, data=data, timeout=self.request_timeout)
            except requests.exceptions.RequestException as e:
                if self._never_connected(e):  # nothing listens: retrying will not help
                    raise self._unreachable_error(e) from e
                if isinstance(e, requests.exceptions.Timeout):
                    problem = ("timeout", None)
                else:  # SearxNG answered, then the connection broke
                    problem = ("network", connection_detail(e) or type(e).__name__)
            else:
                status = response.status_code
                if status == 429 or status >= 500:
                    problem = ("rate_limit" if status == 429 else "server_error", status)
                    retry_after = self._retry_after(response)
                elif status >= 400:
                    raise self._rejected_error(status)
                else:
                    results = self._parse_html_results(response.text)
                    engine_issues = []
                    if not results:
                        # HTML template change or an empty result set: the JSON API also says why.
                        results, engine_issues = self._search_json_api(query)
                    if results:
                        return "\n\n".join(results)  # Return results as a single string, separated by newlines
                    if not engine_issues:
                        raise self._no_results_error(query)
                    problem = ("engines_failed", engine_issues)
            if attempt < self.max_attempts:
                delay = retry_after or self.retry_delay * 2 ** (attempt - 1)
                pretty_print(f"SearxNG: {self._describe(problem)}. Retrying in {delay:g}s "
                             f"(attempt {attempt + 1}/{self.max_attempts})...", color="warning")
                time.sleep(delay)
        raise self._gave_up_error(problem, query)

    @staticmethod
    def _never_connected(exc: requests.exceptions.RequestException) -> bool:
        """True when no TCP connection was made (refused, DNS failure, connect timeout)."""
        reason = getattr(exc.args[0], "reason", None) if exc.args else None
        # urllib3's NewConnectionError and NameResolutionError subclass ConnectTimeoutError
        return isinstance(exc, requests.exceptions.ConnectTimeout) or \
            isinstance(reason, urllib3.exceptions.ConnectTimeoutError)

    @staticmethod
    def _retry_after(response) -> Optional[float]:
        value = response.headers.get("Retry-After", "")
        return min(float(value), MAX_RETRY_AFTER) if value.strip().isdigit() else None

    @staticmethod
    def _engines_blocked(engine_issues: List[Tuple[str, str]]) -> bool:
        return any(word in reason.lower() for _, reason in engine_issues for word in BLOCKED_ENGINE_REASONS)

    def _describe(self, problem: Tuple[str, object]) -> str:
        kind, detail = problem
        if kind == "rate_limit":
            return "rate limited (HTTP 429)"
        if kind == "server_error":
            return f"server error (HTTP {detail})"
        if kind == "engines_failed":
            failures = ", ".join(f"{engine} ({reason})" for engine, reason in detail)
            return f"no results, engines failed: {failures}"
        if kind == "network":
            return f"connection dropped ({detail})"
        return f"no answer within {self.request_timeout}s"

    def _unreachable_error(self, exc: Exception) -> AgenticSeekError:
        causes = ["SearxNG is not running (start_services.sh starts it in Docker).",
                  "Docker is not running, so the SearxNG container cannot start.",
                  f"SEARXNG_BASE_URL = {self.base_url} points to the wrong host or port."]
        in_docker = bool(os.getenv("DOCKER_INTERNAL_URL")) or os.path.exists("/.dockerenv")
        if urlparse(self.base_url).hostname == "searxng" and not in_docker:
            causes.insert(0, "SEARXNG_BASE_URL uses the Docker hostname 'searxng', "
                             "but agenticSeek runs on the host, where that name does not resolve.")
        return AgenticSeekError(
            "Web search unavailable",
            f"Could not connect to SearxNG at {self.base_url}: {connection_detail(exc) or exc}",
            causes=causes,
            fixes=["Start the services: ./start_services.sh (start_services.cmd on Windows), then retry.",
                   "Check that the searxng container is up: docker ps",
                   "In .env, use SEARXNG_BASE_URL=http://127.0.0.1:8080 when agenticSeek runs on the host, "
                   "http://searxng:8080 when it runs in Docker."])

    def _rejected_error(self, status: int) -> AgenticSeekError:
        return AgenticSeekError(
            "Web search rejected",
            f"SearxNG at {self.base_url} refused the search (HTTP {status}).",
            causes=[f"SEARXNG_BASE_URL = {self.base_url} points to another web server than SearxNG.",
                    "The SearxNG settings block this kind of request."],
            fixes=["Open the URL in a browser and check that it shows SearxNG.",
                   "Compare searxng/settings.yml with the version shipped with agenticSeek."])

    def _no_results_error(self, query: str) -> AgenticSeekError:
        return AgenticSeekError(
            "No search results",
            f"SearxNG found nothing for: {query[:120]}",
            causes=["The search query is too specific or misspelled.",
                    "Every search engine enabled in searxng/settings.yml returned nothing."],
            fixes=["Rephrase your request and try again."])

    def _gave_up_error(self, problem: Tuple[str, object], query: str) -> AgenticSeekError:
        kind, detail = problem
        attempts = f"after {self.max_attempts} attempts"
        if kind == "rate_limit":
            return AgenticSeekError(
                "Web search rate limited",
                f"SearxNG kept answering HTTP 429 (too many requests) {attempts}.",
                causes=["The SearxNG bot limiter is enabled and treats agenticSeek as a bot.",
                        "Too many searches in a short time."],
                fixes=["Wait a minute, then retry.",
                       "For a private instance, set limiter: false under server: in searxng/settings.yml "
                       "and restart SearxNG."])
        if kind == "engines_failed":
            failures = ", ".join(f"{engine} ({reason})" for engine, reason in detail)
            if self._engines_blocked(detail):
                return AgenticSeekError(
                    "Search engines rate limited",
                    f"SearxNG is up, but the search engines blocked it {attempts}: {failures}",
                    causes=["Search engines temporarily block an IP after many automated searches.",
                            "A VPN or shared IP address with a bad reputation triggers CAPTCHAs."],
                    fixes=["Wait a few minutes, then retry.",
                           "Disable the VPN, or switch to another network.",
                           "Enable more engines in searxng/settings.yml so one blocked engine is not fatal."])
            return AgenticSeekError(
                "Search engines failed",
                f"SearxNG is up, but every search engine failed {attempts}: {failures}",
                causes=["The SearxNG container has no internet access.",
                        "The search engines are slow or down."],
                fixes=["Check your internet connection and Docker networking, then retry.",
                       "See why engines fail: docker logs searxng"])
        if kind == "network":
            return AgenticSeekError(
                "Web search failed",
                f"The connection to SearxNG kept breaking {attempts}: {detail}",
                causes=["SearxNG crashed or restarted while answering.",
                        "A proxy or VPN interrupts connections to it."],
                fixes=["Look at its logs: docker logs searxng",
                       "Restart the services: ./start_services.sh"])
        if kind == "server_error":
            return AgenticSeekError(
                "SearxNG error",
                f"SearxNG kept failing with HTTP {detail} {attempts}.",
                causes=["SearxNG is still starting, or crashed."],
                fixes=["Look at its logs: docker logs searxng",
                       "Restart the services: ./start_services.sh"])
        return AgenticSeekError(
            "Web search timed out",
            f"SearxNG did not answer within {self.request_timeout}s {attempts}.",
            causes=["The search engines SearxNG queries are slow to answer.",
                    "The SearxNG container is overloaded."],
            fixes=["Retry in a moment.", "Look at its logs: docker logs searxng"])

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
    search_tool = searxSearch(base_url="http://127.0.0.1:8080")
    result = search_tool.execute(["are dog better than cat?"])
    print(result)
