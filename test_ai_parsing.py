import os
import time
from ai_handler import AIHandler
from dotenv import load_dotenv

load_dotenv()

def test_parsing():
    api_key = os.getenv("OPENAI_API_KEY")

    ai = AIHandler(api_key)
    
    test_cases = [
        "Lembre de consultar a contabilidade a partir das 10 horas da manhã da próxima segunda feira e repetir esse lembrete a cada uma hora.",
        "Schedule a meeting every Monday and Friday at 15:00hs",
        "Remind me every Tuesday, Thursday and Saturday at 10am to water the plants",
        # "create a reminder to start at noon and repeat every 10 minutes to call to john",
        # "remind me every 2 hours to walk the dog",
        # "starting tomorrow at 8am remind me every day to take my medicine",
    ]
    duration_total = 0
    for text in test_cases:
        print(f"\nTesting: '{text}'")
        try:
            start_time = time.time()
            result = ai.parse_reminder(text)
            end_time = time.time()
            duration = end_time - start_time
            duration_total += duration
            print(f"Parsing took: {duration:.2f} seconds")
            # result is already printed inside parse_reminder
        except Exception as e:
            print(f"Error parsing case: {e}")

    average = duration_total / test_cases.__len__()
    print(f"Parsing total: {duration_total:.2f} seconds")
    print(f"Parsing average: {average:.2f} seconds")


if __name__ == "__main__":
    test_parsing()