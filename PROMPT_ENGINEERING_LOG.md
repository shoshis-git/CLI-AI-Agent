# 📊 Prompt Engineering Log - CLI Agent

## 🎯 Project Overview

**Objective:** Develop an agent that converts natural language instructions into executable Windows CLI commands.

**Focus:** Iterative prompt engineering through systematic experimentation, measurement, and refinement.

---

## 🧩 Stage A - MVP (Initial Viable Product)

### ✅ Implementation Status: COMPLETE

#### What's Built:
1. **Gradio UI** with 3 tabs:
   - **Interactive Tab**: Test individual instructions
   - **Batch Testing Tab**: Systematic evaluation on test dataset
   - **Documentation Tab**: Guidance and methodology

2. **Prompt System**:
   - `PROMPT_V1`: Basic system prompt
   - `PROMPT_V2`: Enhanced version with better formatting and instructions

3. **Test Dataset**: 6 test cases covering:
   - Network information (ipconfig)
   - File management (del, dir)
   - System info (tasklist, ver)

4. **Experiment Logging**:
   - Automatic saving of batch test results to `experiments/` folder
   - JSON format for easy analysis

5. **Metrics**:
   - Accuracy calculation (exact string match)
   - Per-category performance tracking

---

## 📋 Test Dataset

| # | Instruction (Hebrew) | Expected Command | Category |
|---|---|---|---|
| 1 | מה כתובת ה-IP של המחשב שלי | ipconfig | network |
| 2 | אני רוצה למחוק את כל הקבצים עם סיומת .tmp בתיקייה downloads | del downloads\*.tmp | file_management |
| 3 | לסדר את רשימת הקבצים לפי גודל מהגדול לקטן | dir /o-s | file_management |
| 4 | איזה תהליכים רצים כרגע במערכת | tasklist | system_info |
| 5 | הראה לי את הקבצים בתיקייה הנוכחית | dir | file_listing |
| 6 | מה גרסת ה-Windows שלי | ver | system_info |

---

## 🧪 Experiment Tracking

### Experiment Execution Workflow:

1. **Open Gradio UI** at `http://127.0.0.1:7861`
2. **Go to "Batch Testing" tab**
3. **Select prompt version** (v1 or v2)
4. **Click "Run All Tests"**
5. **Results saved to** `experiments/experiment_{version}_{timestamp}.json`

### Key Metrics to Track:

- **Overall Accuracy %**: Exact string matches / total tests
- **Per-Category Performance**: Which categories fail?
- **Pattern Analysis**: What types of instructions does the model struggle with?

---

## 📝 Prompt Versions

### Version 1 (V1) - Basic

```
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
- "מחק קבצי tmp בתיקייה downloads" → del downloads\*.tmp
- "סדר את הקבצים מהגדול לקטן" → dir /o-s
```

**Expected Baseline Accuracy**: ~40-60%

---

### Version 2 (V2) - Enhanced

```
You are an expert Windows CLI command generator.
Your task: Convert a natural-language instruction into a SINGLE valid Windows command.

🎯 Instructions:
1. Output ONLY the command itself - no explanations, no reasoning, no quotes unless essential.
2. The command must be executable in Windows PowerShell or CMD.
3. Use forward slashes (/) for switches when possible.
4. If the request is ambiguous, choose the most reasonable interpretation.
5. If impossible to translate, respond with: "UNKNOWN"

📝 Examples:
- "מה כתובת ה-IP שלי" → ipconfig
- "מחק קבצי tmp בתיקייה downloads" → del downloads\*.tmp
- "סדר את הקבצים מהגדול לקטן" → dir /o-s
- "הראה לי את כל התהליכים" → tasklist
```

**Expected Baseline Accuracy**: ~60-75%

**Improvements**:
- Added role emphasis ("expert")
- Better formatting with emojis
- More specific technical constraints
- Added constraint about PowerShell compatibility

---

## 🔬 Next Steps (Stage B - Refinement)

### Phase 1: Initial Results Analysis
1. Run batch tests with both v1 and v2
2. Compare accuracy scores
3. Document which test cases fail in each version

### Phase 2: Prompt Refinement
1. Analyze failure patterns
2. Hypothesize improvements
3. Create v3 with targeted changes
4. Measure improvement vs v2

### Phase 3: Safety & Edge Cases
1. Add test cases for potentially dangerous commands
2. Implement safety checks or constraints
3. Test with ambiguous inputs

### Phase 4: Extended Dataset
1. Add more test cases (target: 20-30)
2. Cover more command categories
3. Include edge cases and complex scenarios

---

## 🛠️ How to Use the Application

### Interactive Tab:
```
1. Enter a Hebrew instruction
2. Select prompt version (v1 or v2)
3. Click "🔄 Generate Command"
4. See the generated CLI command
```

### Batch Testing Tab:
```
1. Choose a prompt version
2. Click "🧪 Run All Tests"
3. View results table with:
   - Input instruction
   - Expected command
   - Generated command
   - Match status (✅/❌)
   - Category
4. See overall accuracy percentage
5. Results automatically saved to experiments/
```

---

## 📊 Results Template

When you run batch tests, results are saved as JSON:

```json
{
  "timestamp": "20250119_143022",
  "prompt_version": "v1",
  "results": [
    {
      "הוראה": "מה כתובת ה-IP של המחשב שלי",
      "צפוי": "ipconfig",
      "שנוצר": "ipconfig",
      "תאימות": "✅",
      "קטגוריה": "network"
    }
    ...
  ]
}
```

---

## 🎓 Learning Outcomes

By the end of this project, you will understand:

1. ✅ **Systematic Prompt Engineering**
   - How to design testable prompts
   - How to measure performance objectively

2. ✅ **Iterative Refinement**
   - How to analyze failures
   - How to improve based on data

3. ✅ **Model Behavior Analysis**
   - How prompts affect LLM outputs
   - How to predict and test behavior

4. ✅ **Practical Safety Considerations**
   - How to add safety constraints
   - How to handle edge cases

---

## 🚀 Quick Start Commands

```bash
# Install dependencies
uv sync

# Run the app
uv run main.py

# View generated experiments
cat experiments/experiment_v1_*.json

# Check current status
Get-ChildItem experiments/
```

---

## 📝 Notes

- **Model Used**: gpt-4o-mini (fast, cost-effective for iteration)
- **Temperature**: 0.1 (low randomness for consistency)
- **Language**: Hebrew for instructions, English for system prompts
- **Platform**: Windows CLI (both CMD and PowerShell compatible)

---

**Last Updated**: November 19, 2025
