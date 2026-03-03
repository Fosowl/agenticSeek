import os, sys
import requests
import dotenv

dotenv.load_dotenv()

if __name__ == "__main__": # if running as a script for individual testing
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sources.tools.tools import Tools

class FlightSearch(Tools):
    def __init__(self, api_key: str = None):
        """
        A tool to search for flight information using a flight number via SerpApi.
        """
        super().__init__()
        self.tag = "flight_search"
        self.name = "Flight Search"
        self.description = "Search for flight information using a flight number via SerpApi."
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")

    def execute(self, blocks: str, safety: bool = True) -> str:
        if self.api_key is None:
            return "Error: No SerpApi key provided."
        
        for block in blocks:
            flight_number = block.strip().upper().replace('\n', '')
            if not flight_number:
                return "Error: No flight number provided."

            try:
                url = "https://serpapi.com/search"
                params = {
                    "engine": "google_flights",
                    "api_key": self.api_key,
                    "q": flight_number,
                    "type": "2"  # Flight status search
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if "flights" in data and len(data["flights"]) > 0:
                    flight = data["flights"][0]
                    
                    # Extract key information
                    departure = flight.get("departure_airport", {})
                    arrival = flight.get("arrival_airport", {})
                    
                    departure_code = departure.get("id", "Unknown")
                    departure_time = flight.get("departure_time", "Unknown")
                    arrival_code = arrival.get("id", "Unknown") 
                    arrival_time = flight.get("arrival_time", "Unknown")
                    airline = flight.get("airline", "Unknown")
                    status = flight.get("flight_status", "Unknown")

                    return (
                        f"Flight: {flight_number}\n"
                        f"Airline: {airline}\n"
                        f"Status: {status}\n"
                        f"Departure: {departure_code} at {departure_time}\n"
                        f"Arrival: {arrival_code} at {arrival_time}"
                    )
                else:
                    return f"No flight information found for {flight_number}"
                    
            except requests.RequestException as e:
                return f"Error during flight search: {str(e)}"
            except Exception as e:
                return f"Unexpected error: {str(e)}"
        
        return "No flight search performed"

    def execution_failure_check(self, output: str) -> bool:
        return output.startswith("Error") or "No flight information found" in output

    def interpreter_feedback(self, output: str) -> str:
        if self.execution_failure_check(output):
            return f"Flight search failed: {output}"
        return f"Flight information:\n{output}"


if __name__ == "__main__":
    flight_tool = FlightSearch()
    flight_number = "AA123"
    result = flight_tool.execute([flight_number], safety=True)
    feedback = flight_tool.interpreter_feedback(result)
    print(feedback)