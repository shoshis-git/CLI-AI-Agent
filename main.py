import os
import json
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
2. If the instruction is unclear, return the most reasonable CLI command.
3. If no relevant command exists, return: "UNKNOWN".
4. Do not add quotes unless required by Windows CLI.
5. Output must be a valid Windows command.
6 
1. If the input is a standard Windows library folder (e.g., סרטי וידאו,הורדות, מסמכים, תמונות), return only the official English name (e.g., Downloads, Documents, Pictures).
2. If the folder name is not a standard system folder, 'write it in the same language like write in the prompt.
3.only in תקיה חדשה or תיקיה חדשהdont write it in english because its not a standard folder name write it תיקיה חדשה instead.

Examples:
- "הורדות" -> Downloads
- "מסמכים" -> Documents
- "שולחן העבודה" -> Desktop
- "מוזיקה" -> Music
- "סרטי וידאו" -> Videos
- "תמונות" -> Pictures
7. Ensure the command is syntactically correct for Windows.
Examples:
- "מה כתובת ה-IP שלי" → ipconfig
- "מחק קבצי tmp בתיקייה downloads" → del downloads\\*.tmp
- "סדר את הקבצים מהגדול לקטן" → dir /o-s

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
        "expected": "dir Documents\תכנות\אוטומציה\*.pdf",
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




def generate_command(instruction, prompt_version="v1"):
    if USE_MOCK:
        return MOCK_RESPONSES.get(instruction, f"[DEMO] {instruction[:20]}...")
    
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

        return response.choices[0].message.content.strip()
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
