# add fowwlowing code to __init__.py of browser-use package
"""
import sys
import builtins
import logging

# Redirect all print calls to stderr
original_print = builtins.print

def print_to_stderr(*args, **kwargs):
    kwargs['file'] = sys.stderr
    original_print(*args, **kwargs)

builtins.print = print_to_stderr
# Configure logging to use stderr
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)  # Set level as needed
"""


import asyncio
import os
# Configure browser_use settings
os.environ["ANONYMIZED_TELEMETRY"] = "False"
os.environ["BROWSER_USE_LOGGING_LEVEL"] = "result"  # Only show results, not debugging info
import traceback
import sys
import logging

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)  # Log to stderr for MCP server
    ]
)
logger = logging.getLogger("browser-automation-server")

# Load environment variables
load_dotenv()

# Initialize MCP server
app = FastMCP("browser-automation-server")

@app.tool()
async def browse_web(task: str) -> str:
    """Browse the web to accomplish a specific task.
    
    This tool uses browser automation to navigate the web and perform tasks. It will:
    1. Start a browser session
    2. Navigate to relevant websites based on the task
    3. Interact with elements (click, type, scroll, etc.)
    4. Extract information or perform actions
    5. Return the final result
    
    Args:
        task: A detailed description of what should be accomplished using web browsing
    """
    logger.info(f"Starting web browsing task: {task}")
   

    
    try:
        # Initialize the OpenAI LLM
        llm = ChatOpenAI(model="gpt-4o-mini")
        
        # Create an agent to browse the web
        agent = Agent(
            task=task,
            llm=llm,
        )
        
        # Run the agent
        logger.info("Running browser agent")
        history = await agent.run()
        
        # Extract final result using the ActionResult structure
        if history.is_done():
            # Get the last ActionResult from the history
            if history.history and history.history[-1].result:
                last_result = history.history[-1].result[-1]
                
                # Extract the content from the ActionResult
                if last_result.extracted_content:
                    logger.info(f"Task completed successfully with content")
                    return last_result.extracted_content
                else:
                    logger.info(f"Task completed successfully but no content was extracted")
                    return "Task completed successfully, but no specific content was extracted."
            else:
                logger.info("Task completed but no result was recorded")
                return "Task completed but no result was recorded."
        else:
            # Get error from history if available
            if history.has_errors():
                errors = history.errors()
                error_msg = next((error for error in errors if error), "Unknown error occurred")
                logger.error(f"Task failed: {error_msg}")
                return f"Task failed: {error_msg}"
            else:
                logger.error("Task failed without a specific error")
                return "Task failed without a specific error."
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = "\n".join(traceback.format_exception_only(exc_type, exc_value))
        logger.error(f"Error during web browsing: {error_details}")
        return f"Error during web browsing: {error_details}"
    
# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP Browser Automation Server")
    app.run()

# @app.tool()
# async def browse_web_with_options(
#     task: str, 
#     max_steps: int = 20, 
#     validate_output: bool = False,
#     use_vision: bool = True
# ) -> str:
#     """Browse the web with additional configuration options.
    
#     This advanced tool offers more control over the browsing process with configurable options.
    
#     Args:
#         task: A detailed description of what should be accomplished using web browsing
#         max_steps: Maximum number of steps (browser actions) to perform (default: 20)
#         validate_output: Whether to validate the output before completing (default: False)
#         use_vision: Whether to use vision capabilities for understanding page content (default: True)
#     """
#     logger.info(f"Starting advanced web browsing task: {task}")
#     logger.info(f"Options: max_steps={max_steps}, validate_output={validate_output}, use_vision={use_vision}")
    
#     # Ensure OpenAI API key is available
#     openai_api_key = os.environ.get("OPENAI_API_KEY")
#     if not openai_api_key:
#         logger.error("OpenAI API key not found in environment variables")
#         return "Error: OpenAI API key not found in environment variables. Please set the OPENAI_API_KEY environment variable."
    
#     try:
#         # Initialize the OpenAI LLM
#         llm = ChatOpenAI(api_key=openai_api_key)
        
#         # Create an agent to browse the web with custom options
#         agent = Agent(
#             task=task,
#             llm=llm,
#             validate_output=validate_output,
#             use_vision=use_vision,
#         )
        
#         # Run the agent with custom max_steps
#         logger.info("Running browser agent with custom options")
#         history = await agent.run(max_steps=max_steps)
#         steps_completed = history.number_of_steps()
        
#         # Extract final result using the ActionResult structure
#         if history.is_done():
#             # Get the last ActionResult from the history
#             if history.history and history.history[-1].result:
#                 last_result = history.history[-1].result[-1]
                
#                 # Extract the content from the ActionResult
#                 if last_result.extracted_content:
#                     logger.info(f"Task completed successfully with content in {steps_completed} steps")
#                     return last_result.extracted_content
#                 else:
#                     logger.info(f"Task completed successfully but no content was extracted (in {steps_completed} steps)")
#                     return "Task completed successfully, but no specific content was extracted."
#             else:
#                 logger.info(f"Task completed but no result was recorded (in {steps_completed} steps)")
#                 return "Task completed but no result was recorded."
#         else:
#             # Get error from history if available
#             if history.has_errors():
#                 errors = history.errors()
#                 error_msg = next((error for error in errors if error), "Unknown error occurred")
#                 logger.error(f"Task failed after {steps_completed} steps: {error_msg}")
#                 return f"Task failed after {steps_completed} steps: {error_msg}"
#             else:
#                 logger.error(f"Task failed without a specific error after {steps_completed} steps")
#                 return f"Task failed without a specific error after {steps_completed} steps."
#     except Exception as e:
#         exc_type, exc_value, exc_traceback = sys.exc_info()
#         error_details = "\n".join(traceback.format_exception_only(exc_type, exc_value))
#         logger.error(f"Error during web browsing: {error_details}")
#         return f"Error during web browsing: {error_details}"


