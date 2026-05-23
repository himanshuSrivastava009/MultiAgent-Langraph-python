import os
import re
import time
from typing import TypedDict
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# =====================================================================
# 1. DEFINE THE SHARED STATE NOTEBOOK
# =====================================================================
class PipelineState(TypedDict):
    messages: list[BaseMessage]
    user_input: str              # Holds the initial prompt you type in
    jira_requirements: str       # Populated by Product Owner Agent
    test_cases: str              # Populated by QA Engineer Agent
    framework_structure: str     # Populated by Codebase Scanner Agent
    technical_blueprint: str     # Populated by Tech Lead Agent
    final_code: str              # Populated by Factory Coder Agent
    next_step: str               # Used by Supervisor to route control

# Initialize the flowchart graph canvas
workflow = StateGraph(PipelineState)

# =====================================================================
# 2. INITIALIZE THE CHEAPER GEMINI BRAIN
# =====================================================================
# gemini-2.5-flash is ultra-fast, cheap, and perfect for iterative building.
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# =====================================================================
# 3. REAL LOCAL FILESYSTEM SCANNING TOOL
# =====================================================================
def scan_local_codebase(root_dir: str) -> str:
    """Recursively crawls a local directory and maps out the file structure."""
    path = Path(root_dir)
    if not path.exists():
        return f"Error: Directory {root_dir} does not exist."
        
    tree_strings = []
    for root, dirs, files in os.walk(root_dir):
        # Filter out heavy noise and virtual environments so we don't spam the LLM
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['venv', '__pycache__', 'node_modules', '.git']]
        
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        tree_strings.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            if not f.startswith('.'):
                tree_strings.append(f"{sub_indent}{f}")
                
    return "\n".join(tree_strings)

# =====================================================================
# 4. HARD DRIVE FILE WRITER TOOL
# =====================================================================
def write_code_blocks_to_disk(llm_output: str):
    """Parses standard markdown code blocks containing file paths and writes them to disk."""
    print("\n💾 [Disk Tool]: Writing generated files to your local drive...")
    
    # Regex to extract content inside markdown blocks that specify paths in a leading comment
    block_pattern = re.compile(r"```python\s*(#\s*([^\n]+)\n.*?)(?=```)", re.DOTALL)
    matches = block_pattern.findall(llm_output)
    
    if not matches:
        print("⚠️ No explicitly flagged code blocks found to write directly to disk.")
        return

    for full_block, file_path_str in matches:
        file_path_str = file_path_str.strip()
        file_path = Path(file_path_str)
        
        # Protect our pipeline script from being blown away or modified by mistake
        if file_path.name in ["pipeline.py", "pipeline.py.backup"]:
            print(f"🛡️ Skipped protected runtime engine file: {file_path_str}")
            continue
            
        # Dynamically create nested directory paths if they don't exist yet
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean up contents and separate the path comment from functional code lines
        lines = full_block.split('\n')
        code_content = '\n'.join(lines[1:]) if lines[0].startswith('#') else full_block
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content.strip() + "\n")
        print(f"📁 Created file: {file_path}")

# =====================================================================
# 5. CREATE THE GEMINI SUPERVISOR NODE
# =====================================================================
def supervisor_node(state: PipelineState):
    print("\n👔 [Gemini Supervisor]: Assessing the pipeline state...")
    
    has_jira = bool(state.get("jira_requirements"))
    has_tests = bool(state.get("test_cases"))
    has_framework = bool(state.get("framework_structure"))
    has_blueprint = bool(state.get("technical_blueprint"))
    has_code = bool(state.get("final_code"))
    
    # Strict routing order execution
    if not has_jira:
        print("➡️ Route to: Product Owner (Requirements)")
        return {"next_step": "Researcher"}
        
    elif not has_tests:
        print("➡️ Route to: QA Engineer (Test Cases)")
        return {"next_step": "QA"}
        
    elif not has_framework:
        print("➡️ Route to: Framework Analyst (Codebase Scanner)")
        return {"next_step": "Analyst"}
        
    elif not has_blueprint:
        print("➡️ Route to: Tech Lead (Blueprint Architect)")
        return {"next_step": "Architect"}
        
    elif not has_code:
        print("➡️ Route to: Coding Agent")
        return {"next_step": "Coder"}
        
    else:
        print("🏁 All steps completed perfectly!")
        return {"next_step": "Finish"}

# =====================================================================
# 6. CREATE THE AGENT NODES (WITH APPLIED PAUSE FILTERS)
# =====================================================================

# AGENT 1: Product Owner / Requirements Gatherer
def jira_researcher_node(state: PipelineState):
    print("\n🔍 [Gemini Product Owner]: Transforming user prompt into formal requirements...")
    user_task = state.get("user_input")
    
    prompt = f"""
    You are an expert Product Owner. Translate this raw user request into a formal technical requirement document with explicit acceptance criteria.
    
    User Request:
    {user_task}
    """
    response = gemini_llm.invoke(prompt)
    
    print("⏳ [Product Owner]: Taking a short break to respect API rate limits...")
    time.sleep(18)
    return {"jira_requirements": response.content}

# AGENT 2: QA Engineer (Test Cases)
def qa_engineer_node(state: PipelineState):
    print("\n🧪 [Gemini QA Engineer]: Generating test cases & edge scenarios...")
    requirements = state.get("jira_requirements")
    
    prompt = f"""
    You are an elite QA Engineer. Based on these requirements, write a comprehensive set of functional test cases.
    Include happy path scenarios, empty/invalid inputs, and boundary constraints.
    
    Requirements:
    {requirements}
    """
    response = gemini_llm.invoke(prompt)
    
    print("⏳ [QA Engineer]: Taking a short break to respect API rate limits...")
    time.sleep(18)
    return {"test_cases": response.content}

# AGENT 3: Framework Analyst (Real Local Scanner)
def framework_analyst_node(state: PipelineState):
    print("\n🏗️ [Gemini Framework Analyst]: Scanning your ACTUAL local folder workspace...")
    target_folder = "." 
    real_directory_tree = scan_local_codebase(target_folder)
    
    prompt = f"""
    You are an expert Software Architect. Analyze this REAL directory layout of the user's project:
    
    {real_directory_tree}
    
    Identify the framework layout or lack thereof (e.g., if it is an empty workspace). Suggest exactly where new scripts/modules should go.
    """
    response = gemini_llm.invoke(prompt)
    
    print("⏳ [Framework Analyst]: Taking a short break to respect API rate limits...")
    time.sleep(18)
    return {"framework_structure": response.content}

# AGENT 4: Technical Lead Architect
def tech_lead_architect_node(state: PipelineState):
    print("\n📐 [Gemini Tech Lead]: Merging requirements, test cases, and workspace layout into a blueprint...")
    requirements = state.get("jira_requirements")
    tests = state.get("test_cases")
    framework = state.get("framework_structure")
    
    prompt = f"""
    You are the Technical Lead. Create a concrete architecture design blueprint for a developer.
    Requirements: {requirements}
    Expected Test Cases to Pass: {tests}
    Current Directory Setup: {framework}
    
    Specify exact file names, path layouts, patterns, and inputs/outputs to construct. Do not write full code blocks yet.
    """
    response = gemini_llm.invoke(prompt)
    
    print("⏳ [Tech Lead]: Taking a short break to respect API rate limits...")
    time.sleep(18)
    return {"technical_blueprint": response.content}

# AGENT 5: Factory Coder (With Local Write Actions Enabled)
def factory_coder_node(state: PipelineState):
    print("\n💻 [Gemini Coder]: Writing production-ready python code from blueprint...")
    blueprint = state.get("technical_blueprint")
    
    prompt = f"""
    You are an expert Software Engineer. Write clean, well-commented, functional Python code that perfectly fulfills this blueprint.
    You must structure multiple files if necessary.
    
    CRITICAL REQUIREMENT: For EVERY single file you generate, you MUST start the markdown code block with a comment indicating its relative file path like this:
    ```python
    # folder/filename.py
    Code goes here...
    ```
    
    Blueprint:
    {blueprint}
    """
    response = gemini_llm.invoke(prompt)
    
    # Run the disk write operations locally
    write_code_blocks_to_disk(response.content)
    
    return {"final_code": response.content}


# =====================================================================
# 7. STITCH EVERYTHING TOGETHER WITH LANGGRAPH
# =====================================================================

workflow.add_node("Supervisor", supervisor_node)
workflow.add_node("Researcher", jira_researcher_node)
workflow.add_node("QA", qa_engineer_node)
workflow.add_node("Analyst", framework_analyst_node)
workflow.add_node("Architect", tech_lead_architect_node)
workflow.add_node("Coder", factory_coder_node)

workflow.add_edge(START, "Supervisor")

workflow.add_conditional_edges(
    "Supervisor",
    lambda state: state["next_step"],
    {
        "Researcher": "Researcher",
        "QA": "QA",
        "Analyst": "Analyst",
        "Architect": "Architect",
        "Coder": "Coder",
        "Finish": END
    }
)

workflow.add_edge("Researcher", "Supervisor")
workflow.add_edge("QA", "Supervisor")
workflow.add_edge("Analyst", "Supervisor")
workflow.add_edge("Architect", "Supervisor")
workflow.add_edge("Coder", "Supervisor")

app = workflow.compile()


# =====================================================================
# 8. RUN THE PIPELINE ENGINE
# =====================================================================
# =====================================================================
# 8. RUN THE PIPELINE ENGINE
# =====================================================================
if __name__ == "__main__":
    print("🚀 Starting the Gemini Multi-Agent Software Pipeline (Powered by Gemini 2.5 Flash)...")
    
    # PASTE YOUR GOREST USER STORY HERE:
    my_custom_task = """
    User Story: GoRest User Management API Integration Testing
    As a Quality Assurance Engineer
    I want to validate the functional, security, and schema boundaries of the GoRest User Management endpoints (/public/v2/users)

    📋 Acceptance Criteria:
    1. Positive Flow (End-to-End CRUD Lifecycle: POST, GET, PATCH, DELETE)
    2. Negative Flow (Missing auth -> 401, duplicate emails -> 422)

    🛠️ Engineering Constraints:
    - Framework: Use pytest for test runner execution.
    - Data Models: Create strict Pydantic v2 models to map and validate the GoRest JSON payloads.
    - Design Pattern: Build an API Client wrapper module.
    - SECURITY: Do NOT hardcode the API token. Read it dynamically inside the code using os.environ.get("GOREST_API_TOKEN").
    
    📋 Acceptance Criteria:
    1. Positive Flow (End-to-End CRUD Lifecycle)
       - POST /public/v2/users with Bearer token creates user (201 Created)
       - GET /public/v2/users/{id} reads back record (200 OK)
       - PATCH /public/v2/users/{id} updates status to inactive (200 OK)
       - DELETE /public/v2/users/{id} removes user (204 No Content), next GET returns 404.
    2. Negative & Security Edge Cases
       - Missing Token returns 401 Unauthorized
       - Bad email/gender values return 422 Unprocessable Entity
       - Duplicate email payload returns 422 with message "has already been taken"
    """
    
    initial_state = {
        "messages": [HumanMessage(content=my_custom_task)],
        "user_input": my_custom_task,
        "jira_requirements": "",
        "test_cases": "",
        "framework_structure": "",
        "technical_blueprint": "",
        "final_code": "",
        "next_step": ""
    }
    
    final_output = app.invoke(initial_state)
    print("\n==================================================")
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY ON FLASH!")
    print("==================================================")