import json
from dotenv import load_dotenv
from langchain.globals import set_verbose, set_debug
from langchain_groq.chat_models import ChatGroq
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from agent.prompts import *
from agent.states import *
from agent.tools import write_file, read_file, get_current_directory, list_files

_ = load_dotenv()

set_debug(True)
set_verbose(True)

llm = ChatGroq(model="openai/gpt-oss-20b")


def planner_agent(state: dict) -> dict:
    """Converts user prompt into a structured Plan."""
    user_prompt = state["user_prompt"]
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Get raw response from LLM
            response = llm.invoke(planner_prompt(user_prompt))
            response_text = response.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON object if surrounded by other text
            if not response_text.startswith("{"):
                start_idx = response_text.find("{")
                if start_idx != -1:
                    end_idx = response_text.rfind("}") + 1
                    response_text = response_text[start_idx:end_idx]
            
            # Parse JSON
            plan_dict = json.loads(response_text)
            plan = Plan(**plan_dict)
            
            if plan is None:
                raise ValueError("Planner did not return a valid response.")
            print(f"✓ Planner succeeded on attempt {attempt + 1}")
            return {"plan": plan}
        except Exception as e:
            last_error = e
            print(f"✗ Planner attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                continue
    
    raise ValueError(f"Planner failed after {max_retries} attempts: {last_error}")


def architect_agent(state: dict) -> dict:
    """Creates TaskPlan from Plan."""
    plan: Plan = state["plan"]
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            # Get raw response from LLM
            response = llm.invoke(architect_prompt(plan=plan.model_dump_json()))
            response_text = response.content.strip()
            
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to find JSON object if surrounded by other text
            if not response_text.startswith("{"):
                start_idx = response_text.find("{")
                if start_idx != -1:
                    end_idx = response_text.rfind("}") + 1
                    response_text = response_text[start_idx:end_idx]
            
            # Parse JSON
            task_plan_dict = json.loads(response_text)
            resp = TaskPlan(**task_plan_dict)
            
            if resp is None:
                raise ValueError("Architect did not return a valid response.")
            
            resp.plan = plan
            print(f"✓ Architect succeeded on attempt {attempt + 1}")
            print(resp.model_dump_json())
            return {"task_plan": resp}
        except Exception as e:
            last_error = e
            print(f"✗ Architect attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                continue
    
    raise ValueError(f"Architect failed after {max_retries} attempts: {last_error}")


def coder_agent(state: dict) -> dict:
    """LangGraph tool-using coder agent."""
    coder_state: CoderState = state.get("coder_state")
    if coder_state is None:
        coder_state = CoderState(task_plan=state["task_plan"], current_step_idx=0)

    steps = coder_state.task_plan.implementation_steps
    if coder_state.current_step_idx >= len(steps):
        return {"coder_state": coder_state, "status": "DONE"}

    current_task = steps[coder_state.current_step_idx]
    existing_content = read_file.run(current_task.filepath)

    system_prompt = coder_system_prompt()
    user_prompt = (
        f"Task: {current_task.task_description}\n"
        f"File: {current_task.filepath}\n"
        f"Existing content:\n{existing_content}\n"
        "Use write_file(path, content) to save your changes. "
        "Important: When calling write_file, ensure the content is properly JSON-escaped."
    )

    coder_tools = [read_file, write_file, list_files, get_current_directory]
    
    max_retries = 3
    last_error = None
    
    for attempt in range(max_retries):
        try:
            react_agent = create_react_agent(llm, coder_tools)
            react_agent.invoke({"messages": [{"role": "system", "content": system_prompt},
                                             {"role": "user", "content": user_prompt}]})
            break
        except Exception as e:
            last_error = e
            print(f"Coder attempt {attempt + 1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                # Retry with simplified prompt
                user_prompt = (
                    f"Task: {current_task.task_description}\n"
                    f"File: {current_task.filepath}\n"
                    "Write complete file content using write_file tool."
                )
                continue
            else:
                # If all retries fail, manually handle the file write
                print(f"All retries failed, attempting direct file write...")
                try:
                    # Try to get content from LLM with a simpler approach
                    simple_prompt = f"Generate the complete code for: {current_task.task_description}. Output ONLY the code, no markdown."
                    response = llm.invoke(simple_prompt)
                    write_file.run(current_task.filepath, response.content)
                except Exception as fallback_error:
                    print(f"Fallback write also failed: {fallback_error}")
                    raise ValueError(f"Coder failed after {max_retries} attempts: {last_error}")

    coder_state.current_step_idx += 1
    return {"coder_state": coder_state}


graph = StateGraph(dict)

graph.add_node("planner", planner_agent)
graph.add_node("architect", architect_agent)
graph.add_node("coder", coder_agent)

graph.add_edge("planner", "architect")
graph.add_edge("architect", "coder")
graph.add_conditional_edges(
    "coder",
    lambda s: "END" if s.get("status") == "DONE" else "coder",
    {"END": END, "coder": "coder"}
)

graph.set_entry_point("planner")
agent = graph.compile()
if __name__ == "__main__":
    result = agent.invoke({"user_prompt": "Build a colourful modern todo app in html css and js"},
                          {"recursion_limit": 100})
    print("Final State:", result)
