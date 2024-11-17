# my_llama_index_playground

This repository provides implemented tutorials on building workflows using **LlamaIndex** and deploying multi-agent systems with **llama_deploy**. The implemented tutorials are taken for [Llama Index Examples](https://docs.llamaindex.ai/en/stable/examples/).

## Repository Structure  

- **`src/workflow/`**: Contains all the workflow definitions.  
- **`main.py`**: The entry point for running workflows. Workflows must be imported into `main.py` to execute.  

## Features  

1. **LlamaIndex Workflows**: Step-by-step examples to build custom workflows.  
2. **Multi-Agent Deployment**: Includes setups for deploying multi-agent systems using `llama_deploy`.  

## Getting Started  

### 1. Clone the Repository  

```bash
git clone https://github.com/HammamWahab/my_llama_index_playground.git
cd my_llama_index_playground
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```


### 3. Install Dependencies
Install all required Python packages using requirements.txt:
```bash
pip install -r requirements.txt

```

### 4. Running Workflows
Develop or edit workflows under the src/workflow/ directory.
Import the desired workflow(s) into main.py.
Run the workflow:

```bash
python main.py
```