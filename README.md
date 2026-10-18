# 🤖 CLI Agent - Prompt Engineering Lab

A practical learning environment for **iterative prompt engineering** with systematic testing and measurement.

## 📋 What This Does

This project develops an agent that converts **Hebrew natural language instructions** into **executable Windows CLI commands**.

**Example:**
- 🗣️ Input: `"מה כתובת ה-IP של המחשב שלי"`
- 💻 Output: `ipconfig`

## 🎯 Learning Focus

The real work is in the **prompt engineering**, not the surrounding code:
- ✅ Design testable prompts
- ✅ Measure performance objectively
- ✅ Iterate and refine based on data
- ✅ Understand model behavior deeply

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- `uv` package manager
- OpenAI API key

### Installation

```bash
# Create .env file with your API key
echo "OPENAI_API_KEY=sk-..." > .env

# Install dependencies
uv sync
```

### Run the Application

```bash
# Start the Gradio web interface
uv run main.py
```

Then open: **http://127.0.0.1:7861**

## 📊 Features

### 🎨 Gradio Interface with 3 Tabs

#### 1️⃣ Interactive Tab
- Test individual instructions
- Try different prompt versions
- See results instantly

#### 2️⃣ Batch Testing Tab
- Systematic evaluation on 6 test cases
- Automatic accuracy calculation
- Results saved to `experiments/` folder as JSON

#### 3️⃣ Documentation Tab
- Methodology and guidelines
- Test dataset information
- Learning outcomes

## 🧪 Testing

### Quick Test (Single Run)
```bash
uv run test_quick.py
```

### View Experiments
```bash
# List all experiment results
ls experiments/

# View latest experiment
cat experiments/experiment_v1_*.json | jq .
```

## 📁 Project Structure

```
cli_agent/
├── main.py                      # Main Gradio app
├── test_quick.py                # Quick test script
├── PROMPT_ENGINEERING_LOG.md    # Detailed log & methodology
├── README.md                    # This file
├── pyproject.toml               # Project config
├── .env                         # API keys (not in git)
└── experiments/                 # Test results (auto-generated)
    ├── experiment_v1_20250119_143022.json
    └── ...
```

## 🧩 Current Prompt Versions

### V1 (Basic)
Standard system prompt with basic rules and examples.

**Expected Accuracy**: 40-60%

### V2 (Enhanced)
Improved formatting, better instructions, technical constraints.

**Expected Accuracy**: 60-75%

## 📊 Test Dataset

| Instruction | Expected | Category |
|---|---|---|
| מה כתובת ה-IP של המחשב שלי | ipconfig | network |
| אני רוצה למחוק את קבצי .tmp בdownloads | del downloads\*.tmp | file_management |
| לסדר קבצים לפי גודל | dir /o-s | file_management |
| איזה תהליכים רצים | tasklist | system_info |
| הראה קבצים בתיקייה הנוכחית | dir | file_listing |
| מה גרסת ה-Windows | ver | system_info |

## 🎓 Stage A - MVP (COMPLETED ✅)

- ✅ Basic Gradio UI
- ✅ Two prompt versions
- ✅ Batch testing system
- ✅ Experiment logging
- ✅ Accuracy metrics

## 🔬 Next Stages

### Stage B: Refinement
- Analyze v1 vs v2 results
- Create v3 with targeted improvements
- Expand test dataset to 20-30 cases

### Stage C: Safety & Edge Cases
- Test dangerous commands
- Add safety constraints
- Handle ambiguous inputs

### Stage D: Advanced Optimization
- Fine-tune temperature/parameters
- Explore few-shot vs zero-shot
- Test with different model sizes

## 📝 How to Experiment

1. **Open the UI**: `http://127.0.0.1:7861`
2. **Go to "Batch Testing" tab**
3. **Select a prompt version** (v1 or v2)
4. **Click "Run All Tests"**
5. **Check results table** - accuracy % shown
6. **Review `experiments/` folder** - detailed JSON log

## 💡 Prompt Engineering Tips

### What to Track:
- Overall accuracy %
- Per-category performance
- Types of failures
- Model consistency

### Refinement Ideas:
1. Add more specific constraints
2. Improve examples
3. Clarify edge cases
4. Add role descriptions
5. Use formatting (bullets, numbering)
6. Add reasoning markers

## 🛡️ Safety Considerations

Generated commands are **displayed only and are never executed by this application**. The app currently applies a conservative allowlist of read-only commands, blocks shell operators and selected network-changing options, and asks for clarification when a request is unclear. Run the offline safety tests with `uv run python -m unittest test_safety`.

This is a basic safeguard, not a complete security boundary. Before adding command execution, implement stricter argument validation, explicit user confirmation for each command, and audit logging. Do not rely on model output or this allowlist alone to authorize execution.

## 🔧 Technical Details

- **Model**: `gpt-4o-mini` (fast, cost-effective)
- **Temperature**: 0.1 (consistent outputs)
- **Language**: Hebrew input, English system prompt
- **Platform**: Windows CLI (CMD/PowerShell)
- **Framework**: Gradio for UI, OpenAI SDK for LLM

## 📚 Resources

- [PROMPT_ENGINEERING_LOG.md](./PROMPT_ENGINEERING_LOG.md) - Detailed methodology
- [Gradio Docs](https://www.gradio.app/)
- [OpenAI API Docs](https://platform.openai.com/docs/)

## 🤝 Contributing

Experiment with different prompts:
1. Create a new version in `main.py`
2. Add it to `PROMPTS` dict
3. Test via Batch Testing tab
4. Document results in `experiments/`

## 📞 Questions?

Check [PROMPT_ENGINEERING_LOG.md](./PROMPT_ENGINEERING_LOG.md) for detailed methodology and next steps.

---

**Last Updated**: November 19, 2025
**Status**: MVP Complete - Ready for Experiments 🚀
