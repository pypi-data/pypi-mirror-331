from stefan.execution_context import ExecutionContext
from stefan.tool.tool_definition import ToolDefinition
from stefan.tool.tool_executor import ToolExecutor
from stefan.tool.tool_formatter import ToolFormatter

def create_tools_use_prompt(tools: list[ToolDefinition], context: ExecutionContext) -> str:
    tools_str = "\n".join([ToolFormatter().format_tool(tool, context) for tool in tools])
    return _TOOLS_USE_PROMPT.format(tools_str=tools_str)

_TOOLS_USE_PROMPT = """
TOOL USE

You have access to a set of tools and you can use one tool per message, and will receive the result of that tool use in the user's response. You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use.

# Tool Use Formatting

Tool use is formatted using XML-style tags wrapped with <answer>...</answer> tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<answer>
  <tool_name>
    <parameter1_name>value1</parameter1_name>
    <parameter2_name>value2</parameter2_name>
    ...
  </tool_name>
</answer>

For example:

<answer>
  <read_file>
    <path>src/main.js</path>
  </read_file>
</answer>

Always adhere to this format for the tool use to ensure proper parsing and execution.

# Tools

{tools_str}

# Tool Use Guidelines

1. In <thinking> tags, assess what information you already have and what information you need to proceed with the task.
2. Choose the most appropriate tool based on the task and the tool descriptions provided. Assess if you need additional information to proceed, and which of the available tools would be most effective for gathering this information. For example using the list_files tool is more effective than running a command like \`ls\` in the terminal. It's critical that you think about each available tool and use the one that best fits the current step in the task.
3. If multiple actions are needed, use one tool at a time per message to accomplish the task iteratively, with each tool use being informed by the result of the previous tool use. Do not assume the outcome of any tool use. Each step must be informed by the previous step's result.
4. Formulate your tool use using the XML format specified for each tool.
5. After each tool use, the user will respond with the result of that tool use. This result will provide you with the necessary information to continue your task or make further decisions. This response may include:
  - Information about whether the tool succeeded or failed, along with any reasons for failure.
  - Linter errors that may have arisen due to the changes you made, which you'll need to address.
  - New terminal output in reaction to the changes, which you may need to consider or act upon.
  - Any other relevant feedback or information related to the tool use.
6. ALWAYS wait for user confirmation after each tool use before proceeding. Never assume the success of a tool use without explicit confirmation of the result from the user.

It is crucial to proceed step-by-step, waiting for the user's message after each tool use before moving forward with the task. This approach allows you to:
1. Confirm the success of each step before proceeding.
2. Address any issues or errors that arise immediately.
3. Adapt your approach based on new information or unexpected results.
4. Ensure that each action builds correctly on the previous ones.

By waiting for and carefully considering the user's response after each tool use, you can react accordingly and make informed decisions about how to proceed with the task. This iterative process helps ensure the overall success and accuracy of your work.

# Output Format

The output should be the last thing in your response and should be valid xml format wrapped with <answer>...</answer> tags.

<answer>
    <selected_tool>...</selected_tool>
</answer>
"""