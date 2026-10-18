import os
import json
import re
from datetime import datetime
from pathlib import Path
from click import prompt
from dotenv import load_dotenv
import gradio as gr
import openai
import pandas as pd

load_dotenv()

# Initialize OpenAI client
USE_MOCK = True  # Default to mock mode
client = None

api_key = os.getenv("OPENAI_API_KEY", "").strip()
if api_key and len(api_key) > 20:  # Basic validation
    try:
        from openai import OpenAI
        client =openai.OpenAI(api_key=api_key,base_url="https://proxy.aiwall.org")
        USE_MOCK = False
        print("✅ OpenAI client initialized")
    except Exception as e:
        print(f"⚠️ Warning: Could not initialize OpenAI: {e}")
        print("   Using MOCK mode for demonstration")
        USE_MOCK = True
else:
    print("⚠️ No valid API key found in .env")
    print("   Using MOCK mode for demonstration")

# ============================================
# 📊 PROMPT VERSIONS - לניסוי והשוואה
# ============================================

PROMPT_V1 = """
You are a CLI command generator.
Your task: Convert a natural-language text into a SINGLE Windows command-line instruction.

Rules:
1. Return only a command, with no explanations.
2. If the instruction is ambiguous or missing required details, return "CLARIFICATION_REQUIRED: <brief question>". Do not guess.
3. If no relevant command exists, return "UNKNOWN".
4. Do not generate commands that delete, overwrite, modify, install, or shut down anything.
5. Return only a read-only Windows command, with no explanations or code fences.
6. Never chain commands, use pipes, or use input/output redirection.
7. For standard Windows folders, use their official English names (Downloads, Documents, Pictures, Desktop, Music, Videos). Keep custom folder names in the language used by the user.

Examples:
- "מה כתובת ה-IP שלי" → ipconfig
- "מחק קבצי tmp בתיקייה downloads" → UNKNOWN
- "סדר את הקבצים מהגדול לקטן" → dir /o-s
- "הצג את הקבצים" → CLARIFICATION_REQUIRED: באיזו תיקייה?

Now convert the following instruction into a Windows CLI command:
"""



PROMPTS = {
    "v1": PROMPT_V1,
}

# ============================================
# 📝 TEST DATASET - קבוצות בדיקה
# ============================================

TEST_CASES = [
    {
        "instruction": "מה כתובת ה-IP של המחשב שלי",
        "expected": "ipconfig",
        "category": "network"
    },
    {
        "instruction": "תביא את כל קבצי הpdf שקיימים בתקית אוטומציה שבתוך תקית  תכנות שבתוך תקית מסמכים",
        "expected": r"dir Documents\תכנות\אוטומציה\*.pdf",
        "category": "file_management"
    },
    {
        "instruction": "לסדר את רשימת הקבצים לפי גודל מהגדול לקטן",
        "expected": "dir /o-s",
        "category": "file_management"
    },
    {
        "instruction": "איזה תהליכים רצים כרגע במערכת",
        "expected": "tasklist",
        "category": "system_info"
    },
    {
        "instruction": "תביא לי את כל קבצי הוידאו שבתקיית עליה לבנות שבתוך תקייה חדשה שבתוןך שרטי וידאו",
        "expected": "dir",
        "category": "file_listing"
    },
    {
        "instruction": "מה גרסת ה-Windows שלי",
        "expected": "ver",
        "category": "system_info"
    }
]

# ============================================
# 🔧 EXPERIMENT LOGGING
# ============================================

EXPERIMENTS_DIR = "experiments"
os.makedirs(EXPERIMENTS_DIR, exist_ok=True)



def save_experiment(prompt_version, results):
    """שמור ניסוי לקובץ"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # ודואגים ש-prompt_version יהיה מחרוזת
    filename = f"{EXPERIMENTS_DIR}/experiment_{str(prompt_version)}_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp,
            "prompt_version": str(prompt_version), # המרה לטקסט
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    return filename






def calculate_accuracy(results):
    """חשב דיוק - האם הפקודה המוצעת תואמת לצפוי"""
    if not results:
        return 0.0
    
    exact_matches = sum(1 for r in results if r["generated"].strip().lower() == r["expected"].strip().lower())
    return (exact_matches / len(results)) * 100

# ============================================
# 🤖 CORE AGENT FUNCTION
# ============================================

# Mock responses for testing (when OpenAI API is not available)
MOCK_RESPONSES = {
    "מה כתובת ה-IP של המחשב שלי": "ipconfig",
    "אני רוצה למחוק את כל הקבצים עם סיומת .tmp בתיקייה downloads": "del downloads\\*.tmp",
    "לסדר את רשימת הקבצים לפי גודל מהגדול לקטן": "dir /o-s",
    "איזה תהליכים רצים כרגע במערכת": "tasklist",
    "הראה לי את הקבצים בתיקייה הנוכחית": "dir",
    "מה גרסת ה-Windows שלי": "ver",
}


SAFE_COMMANDS = {
    "dir",
    "ipconfig",
    "tasklist",
    "ver",
    "systeminfo",
    "whoami",
    "get-childitem",
    "get-process",
    "get-netipaddress",
}


def validate_command(command):
    """Allow only a single command from the read-only command allowlist."""
    command = (command or "").strip()
    if not command:
        return "CLARIFICATION_REQUIRED: Please enter an instruction."

    if command.upper().startswith("CLARIFICATION_REQUIRED:") or command.upper() == "UNKNOWN":
        return command

    if re.search(r"[\r\n;&|<>`$()%!^]", command):
        return "BLOCKED: Multi-command input and shell operators are not allowed."

    match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)", command)
    if not match or match.group(1).lower() not in SAFE_COMMANDS:
        return "BLOCKED: This command is not on the read-only allowlist. Review it manually; it was not executed."

    if match.group(1).lower() == "ipconfig" and re.search(
        r"/(release|renew|flushdns|registerdns|setclassid)", command, re.IGNORECASE
    ):
        return "BLOCKED: This ipconfig option changes network configuration."

    return command



def generate_command(instruction, prompt_version="v1"):
    if not instruction or not instruction.strip():
        return validate_command("")

    if USE_MOCK:
        mock_response = MOCK_RESPONSES.get(
            instruction,
            "CLARIFICATION_REQUIRED: Add this instruction to MOCK_RESPONSES or configure the API.",
        )
        return validate_command(mock_response)
    
    try:
        prompt = PROMPTS.get(prompt_version, PROMPT_V1)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": instruction}
            ],
            temperature=0.1
        )

        return validate_command(response.choices[0].message.content)
    except Exception as e:
        if "429" in str(e):
            return "❌ שגיאת מכסה (Quota): אין יתרה בחשבון OpenAI או שקצב הבקשות מהיר מדי."
        return f"[ERROR] {str(e)[:100]}"



       

# ============================================
# 🧪 GRADIO INTERFACE
# ============================================

with gr.Blocks(title="CLI Agent - Prompt Engineering") as demo:
    gr.Markdown("# 🤖 Natural Language → CLI Agent")
    gr.Markdown("### Prompt Engineering Experiments & Iterations")
    
    with gr.Tab("🚀 Interactive"):
        with gr.Row():
            with gr.Column():
                instruction_input = gr.Textbox(
                    label="הוראה בשפה טבעית",
                    placeholder="לדוגמה: מה כתובת ה-IP שלי"
                )
                prompt_version = gr.Radio(
                    choices=["v1"],
                    value="v1",
                    label="גרסת פרומפט"
                )
                generate_btn = gr.Button("🔄 Generate Command")
            
            with gr.Column():
                command_output = gr.Textbox(
                    label="פקודת CLI",
                    interactive=False
                )
        
        generate_btn.click(
            fn=generate_command,
            inputs=[instruction_input, prompt_version],
            outputs=command_output
        )
    
    
if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7865,
        share=False,
        show_error=True,
        debug=False
    )
