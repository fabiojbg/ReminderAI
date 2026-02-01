import os
from ai_handler import AIHandler
from dotenv import load_dotenv

load_dotenv()

def test_parsing():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in .env")
        return

    ai = AIHandler(api_key)
    
    test_cases = [
        "remind me to take my medicine, starting tomorrow at 8am and repeat the same day of the week"
        "create a reminder to start at noon and repeat every 10 minutes to call to john",
        "remind me every 2 hours to walk the dog",
        "starting tomorrow at 8am remind me every day to take my medicine",
    ]

    for text in test_cases:
        print(f"\nTesting: '{text}'")
        try:
            result = ai.parse_reminder(text)
            # result is already printed inside parse_reminder
        except Exception as e:
            print(f"Error parsing case: {e}")

if __name__ == "__main__":
    test_parsing()