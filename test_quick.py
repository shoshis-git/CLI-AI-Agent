#!/usr/bin/env python3
"""
Quick test script to verify the CLI Agent is working
"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPT_V1 = """
You are a CLI command generator.
Your task: Convert a natural-language text into a SINGLE Windows command-line instruction.

Rules:
1. Return only a command, with no explanations.
2. If the instruction is unclear, return the most reasonable CLI command.
3. If no relevant command exists, return: "UNKNOWN".
4. Do not add quotes unless required by Windows CLI.
5. Output must be a valid Windows command.

Examples:
- "מה כתובת ה-IP שלי" → ipconfig
- "מחק קבצי tmp בתיקייה downloads" → del downloads\\*.tmp
- "סדר את הקבצים מהגדול לקטן" → dir /o-s

Now convert the following instruction into a Windows CLI command:
"""

TEST_CASES = [
    ("מה כתובת ה-IP של המחשב שלי", "ipconfig"),
    ("אני רוצה למחוק את כל הקבצים עם סיומת .tmp בתיקייה downloads", "del downloads\\*.tmp"),
    ("לסדר את רשימת הקבצים לפי גודל מהגדול לקטן", "dir /o-s"),
    ("איזה תהליכים רצים כרגע במערכת", "tasklist"),
    ("הראה לי את הקבצים בתיקייה הנוכחית", "dir"),
    ("מה גרסת ה-Windows שלי", "ver"),
]

def generate_command(instruction: str) -> str:
    """Generate a CLI command from a natural language instruction"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": PROMPT_V1},
            {"role": "user", "content": instruction}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content.strip()

def main():
    print("🧪 Running Quick CLI Agent Test\n")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for instruction, expected in TEST_CASES:
        try:
            generated = generate_command(instruction)
            is_match = generated.lower() == expected.lower()
            
            status = "✅ PASS" if is_match else "❌ FAIL"
            print(f"\n{status}")
            print(f"  Instruction: {instruction}")
            print(f"  Expected:    {expected}")
            print(f"  Generated:   {generated}")
            
            if is_match:
                passed += 1
            else:
                failed += 1
                
        except Exception as e:
            print(f"\n❌ ERROR: {instruction}")
            print(f"  Error: {e}")
            failed += 1
    
    print("\n" + "=" * 80)
    accuracy = (passed / len(TEST_CASES)) * 100 if TEST_CASES else 0
    print(f"\n📊 Results: {passed}/{len(TEST_CASES)} passed ({accuracy:.1f}%)")
    print(f"   Passed: {passed} ✅")
    print(f"   Failed: {failed} ❌")
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
