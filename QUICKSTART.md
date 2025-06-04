# OdyTest Quick Start Guide

Get up and running with OdyTest in 5 minutes!

## 🚀 Installation

1. **Navigate to OdyTest directory**
   ```bash
   cd tests/odytest
   ```

2. **Run setup (creates virtual environment)**
   ```bash
   setup.bat
   ```

3. **Start testing**
   ```bash
   run.bat
   ```

## 🎯 First Test

### Option 1: Interactive Menu
```bash
run.bat
# Select option 1 for demo, or option 4 to test a model
```

### Option 2: Direct Command
```bash
run.bat demo                # See what OdyTest can do
run.bat list-models         # See available models
run.bat test qwen3_4b      # Test your first model
```

## 📋 Prerequisites

- **Python 3.7+** installed
- **Ollama** running locally
- At least one model loaded in Ollama:
  ```bash
  ollama pull qwen3-4b
  # or
  ollama pull deepseek-r1-0528-qwen3-8b
  # or  
  ollama pull llama-3.3-8b-instruct
  ```

## 🔄 Typical Workflow

1. **Load model in Ollama**
   ```bash
   ollama pull qwen3-4b
   ```

2. **Test the model**
   ```bash
   run.bat test qwen3_4b
   ```

3. **Switch to next model**
   ```bash
   ollama rm qwen3-4b
   ollama pull deepseek-r1-0528-qwen3-8b
   ```

4. **Test next model**
   ```bash
   run.bat test deepseek_r1
   ```

5. **Generate comparison report**
   ```bash
   run.bat report
   ```

## 📊 What You'll Get

- **Individual Results**: Detailed performance for each model
- **Comparative Analysis**: Side-by-side comparison
- **Recommendations**: Which model to use for production
- **Language Breakdown**: Performance per language
- **Timing Analysis**: Speed vs accuracy trade-offs

## 🆘 Need Help?

```bash
run.bat help              # Show all commands
run.bat demo              # See demonstration
```

Or check the full [README.md](README.md) for detailed documentation.

## 🎉 That's It!

You're ready to find the best LLM for your roster system!
