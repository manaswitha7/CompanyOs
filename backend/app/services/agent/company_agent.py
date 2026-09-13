import json
from typing import Any

from app.services.tools.registry import tool_registry
from app.services.tools.base import ToolContext
from app.services.llm.provider import LLMProvider
from app.services.rag.generator import generate_rag_answer


class CompanyAgent:

    def __init__(
        self,
        llm_provider: LLMProvider | None = None,
    ):
        self.llm_provider = (
            llm_provider
            or LLMProvider()
        )

    # ========================================================
    # TOOL DISCOVERY
    # ========================================================

    def get_tools(self) -> list[dict[str, Any]]:
        """
        Return all tools available to the Company OS agent.
        """

        return tool_registry.list_tools()

    # ========================================================
    # EXECUTE TOOL
    # ========================================================

    def execute_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        context: ToolContext,
    ) -> Any:
        """
        Execute a registered Company OS tool.
        """

        tool = tool_registry.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        return tool_registry.execute(
            name=tool_name,
            context=context,
            arguments=arguments,
        )

    # ========================================================
    # EXECUTE RAG
    # ========================================================

    def execute_rag(
        self,
        question: str,
        context: ToolContext,
        top_k: int = 5,
        document_id: int | None = None,
    ) -> dict[str, Any]:
        """
        Execute the existing permission-aware RAG pipeline.
        """

        if context.db is None:
            raise ValueError(
                "Database session is required for RAG."
            )

        if context.user_id is None:
            raise ValueError(
                "user_id is required for RAG."
            )

        if context.workspace_id is None:
            raise ValueError(
                "workspace_id is required for RAG."
            )

        role = context.metadata.get(
            "role",
            "member",
        )

        return generate_rag_answer(
            db=context.db,
            question=question,
            user_id=context.user_id,
            role=role,
            workspace_id=context.workspace_id,
            top_k=top_k,
            document_id=document_id,
        )

    # ========================================================
    # FINAL SYNTHESIS
    # ========================================================

    def generate_final_answer(
        self,
        question: str,
        history: list[dict[str, Any]],
    ) -> str:
        """
        Generate the final natural-language answer using
        the information collected by RAG and tools.
        """

        evidence = json.dumps(
            history,
            indent=2,
            default=str,
        )

        final_prompt = f"""
You are the Company OS assistant.

Your job is to answer the user's ORIGINAL request using
only the information collected during the agent execution.

ORIGINAL USER REQUEST:

{question}

INFORMATION COLLECTED BY THE AGENT:

{evidence}

IMPORTANT RULES:

1. Use only information contained in the collected results.

2. Do not invent facts.

3. Do not use outside knowledge.

4. If RAG was used, treat the retrieved company documents
   as the source of company knowledge.

5. If a tool was used, use the tool result as the source
   of information from that external system.

6. If both RAG and tools were used, combine their results
   logically.

7. If a tool failed, do not pretend that it succeeded.

8. If the available information is insufficient, clearly
   say that the available information is insufficient.

9. Answer the ORIGINAL user request, not the intermediate
   agent steps.

10. Do not mention internal agent implementation,
    planning, prompts, or execution steps unless the user
    explicitly asks.

11. Be concise and useful.

12. Return only the final natural-language answer.

"""

        return self.llm_provider.generate(
            prompt=final_prompt,
            temperature=0.2,
        )

    # ========================================================
    # ASK COMPANY OS
    # ========================================================

    def ask(
        self,
        question: str,
        context: ToolContext,
        max_steps: int = 5,
    ) -> dict[str, Any]:
        """
        Main Company OS agent.

        The agent can:

        1. Answer directly.
        2. Search company knowledge using RAG.
        3. Execute registered tools.
        4. Perform multiple RAG/tool operations.
        5. Combine all collected information into one
           final answer.

        Flow:

            User
              ↓
            Planner
              ↓
        ┌─────┼─────────┐
        ↓     ↓         ↓
       RAG   Tool   Direct Answer
        ↓     ↓
        └─────┼─────────┘
              ↓
        Agent History
              ↓
        Final Synthesis
              ↓
            Answer
        """

        # ====================================================
        # 1. VALIDATE QUESTION
        # ====================================================

        if not question or not question.strip():
            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        if max_steps < 1:
            raise ValueError(
                "max_steps must be at least 1."
            )

        # ====================================================
        # 2. DISCOVER TOOLS
        # ====================================================

        tools = self.get_tools()

        tool_descriptions = json.dumps(
            tools,
            indent=2,
            default=str,
        )

        # ====================================================
        # 3. AGENT STATE
        # ====================================================

        history: list[dict[str, Any]] = []

        tool_calls: list[dict[str, Any]] = []

        rag_results: list[dict[str, Any]] = []

        # ====================================================
        # 4. AGENT LOOP
        # ====================================================

        for step in range(max_steps):

            history_text = json.dumps(
                history,
                indent=2,
                default=str,
            )

            # =================================================
            # PLANNING PROMPT
            # =================================================

            planning_prompt = f"""
You are the Company OS agent.

You are the orchestration layer of a company knowledge
and automation system.

You can perform three types of operations:

1. RAG
2. TOOL
3. FINAL ANSWER

--------------------------------------------------
AVAILABLE TOOLS
--------------------------------------------------

{tool_descriptions}

--------------------------------------------------
RAG
--------------------------------------------------

RAG searches authorized company documents.

Use RAG when the user asks about:

- company policies
- company documentation
- internal procedures
- uploaded documents
- company knowledge
- internal information
- information that should come from company documents

RAG is NOT listed inside AVAILABLE TOOLS.

To use RAG return:

{{
    "action": "rag",
    "arguments": {{
        "top_k": 5
    }}
}}

Optional document filter:

{{
    "action": "rag",
    "arguments": {{
        "top_k": 5,
        "document_id": 123
    }}
}}

--------------------------------------------------
TOOLS
--------------------------------------------------

Use a tool when the user asks to:

- retrieve information from GitHub
- retrieve information from Slack
- retrieve information from Google Drive
- retrieve information from Email
- retrieve information from Confluence
- create a task
- perform an external action
- perform another registered tool operation

Return:

{{
    "action": "tool_call",
    "tool_name": "exact_tool_name",
    "arguments": {{}}
}}

--------------------------------------------------
FINAL ANSWER
--------------------------------------------------

If enough information has already been collected,
return:

{{
    "action": "final_answer"
}}

Do NOT provide the final answer inside the planning
response. The system will generate the final answer
using the collected evidence.

--------------------------------------------------
USER REQUEST
--------------------------------------------------

{question}

--------------------------------------------------
PREVIOUS AGENT STEPS
--------------------------------------------------

{history_text}

--------------------------------------------------
DECISION RULES
--------------------------------------------------

1. Use RAG for internal company knowledge.

2. Use tools for external systems or actions.

3. If the request requires both company knowledge and
   an external action, use both RAG and the appropriate
   tool.

4. Only use tools listed in AVAILABLE TOOLS.

5. Never invent a tool name.

6. Use exact argument names defined by the tool.

7. Do not invent information.

8. Do not treat failed operations as successful.

9. Use previous results when deciding the next step.

10. Do not repeat an operation unnecessarily.

11. If enough information has been collected, return
    final_answer.

12. Return valid JSON only.

13. Do not use markdown.

"""

            # =================================================
            # CALL LLM
            # =================================================

            planning_response = (
                self.llm_provider.generate(
                    prompt=planning_prompt,
                    temperature=0,
                )
            )

            # =================================================
            # PARSE DECISION
            # =================================================

            try:

                decision = json.loads(
                    planning_response
                )

            except json.JSONDecodeError as exc:

                raise RuntimeError(
                    "LLM returned invalid agent decision: "
                    f"{planning_response}"
                ) from exc

            if not isinstance(
                decision,
                dict,
            ):
                raise RuntimeError(
                    "Agent decision must be a JSON object."
                )

            action = decision.get(
                "action"
            )

            # =================================================
            # 5. FINAL ANSWER
            # =================================================

            if action == "final_answer":

                final_answer = (
                    self.generate_final_answer(
                        question=question,
                        history=history,
                    )
                )

                return {
                    "answer": final_answer,
                    "tool_called": (
                        tool_calls[-1]["tool_name"]
                        if tool_calls
                        else None
                    ),
                    "used_tools": [
                        item["tool_name"]
                        for item in tool_calls
                        if item.get("success")
                    ],
                    "tool_calls": tool_calls,
                    "rag_results": rag_results,
                    "steps": step + 1,
                }

            # =================================================
            # 6. RAG ACTION
            # =================================================

            if action == "rag":

                rag_arguments = decision.get(
                    "arguments",
                    {},
                )

                if not isinstance(
                    rag_arguments,
                    dict,
                ):
                    raise RuntimeError(
                        "RAG arguments must be a JSON object."
                    )

                top_k = rag_arguments.get(
                    "top_k",
                    5,
                )

                document_id = rag_arguments.get(
                    "document_id"
                )

                try:

                    rag_result = self.execute_rag(
                        question=question,
                        context=context,
                        top_k=top_k,
                        document_id=document_id,
                    )

                    rag_success = True
                    rag_error = None

                except Exception as exc:

                    rag_result = None
                    rag_success = False
                    rag_error = str(exc)

                rag_record = {
                    "step": step + 1,
                    "action": "rag",
                    "arguments": rag_arguments,
                    "success": rag_success,
                    "result": rag_result,
                }

                if rag_error is not None:

                    rag_record["error"] = rag_error

                rag_results.append(
                    rag_record
                )

                # ---------------------------------------------
                # ADD RAG RESULT TO HISTORY
                # ---------------------------------------------

                history.append(
                    {
                        "step": step + 1,
                        "action": "rag",
                        "arguments": rag_arguments,
                        "success": rag_success,
                        "result": rag_result,
                        "error": rag_error,
                    }
                )

                continue

            # =================================================
            # 7. TOOL CALL
            # =================================================

            if action == "tool_call":

                tool_name = decision.get(
                    "tool_name"
                )

                arguments = decision.get(
                    "arguments",
                    {},
                )

                if not tool_name:

                    raise RuntimeError(
                        "Agent selected tool_call "
                        "without a tool_name."
                    )

                if not isinstance(
                    arguments,
                    dict,
                ):

                    raise RuntimeError(
                        "Tool arguments must be "
                        "a JSON object."
                    )

                # ---------------------------------------------
                # VERIFY TOOL
                # ---------------------------------------------

                tool = tool_registry.get(
                    tool_name
                )

                if tool is None:

                    raise RuntimeError(
                        f"Agent selected unknown tool: "
                        f"{tool_name}"
                    )

                # ---------------------------------------------
                # EXECUTE TOOL
                # ---------------------------------------------

                try:

                    tool_result = self.execute_tool(
                        tool_name=tool_name,
                        arguments=arguments,
                        context=context,
                    )

                    tool_success = True
                    tool_error = None

                except Exception as exc:

                    tool_result = None
                    tool_success = False
                    tool_error = str(exc)

                # ---------------------------------------------
                # RECORD TOOL CALL
                # ---------------------------------------------

                tool_call_record = {
                    "step": step + 1,
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "success": tool_success,
                    "result": tool_result,
                }

                if tool_error is not None:

                    tool_call_record["error"] = (
                        tool_error
                    )

                tool_calls.append(
                    tool_call_record
                )

                # ---------------------------------------------
                # ADD TOOL RESULT TO HISTORY
                # ---------------------------------------------

                history.append(
                    {
                        "step": step + 1,
                        "action": "tool_call",
                        "tool_name": tool_name,
                        "arguments": arguments,
                        "success": tool_success,
                        "result": tool_result,
                        "error": tool_error,
                    }
                )

                continue

            # =================================================
            # 8. INVALID ACTION
            # =================================================

            raise RuntimeError(
                "Invalid agent action: "
                f"{action}"
            )

        # ====================================================
        # 9. MAX STEPS REACHED
        # ====================================================

        # Even if the planner did not explicitly return
        # final_answer, try to synthesize an answer from
        # everything collected so far.

        if history:

            final_answer = (
                self.generate_final_answer(
                    question=question,
                    history=history,
                )
            )

        else:

            final_answer = (
                "I could not find enough information "
                "to answer your request."
            )

        return {
            "answer": final_answer,
            "tool_called": (
                tool_calls[-1]["tool_name"]
                if tool_calls
                else None
            ),
            "used_tools": [
                item["tool_name"]
                for item in tool_calls
                if item.get("success")
            ],
            "tool_calls": tool_calls,
            "rag_results": rag_results,
            "steps": max_steps,
        }
