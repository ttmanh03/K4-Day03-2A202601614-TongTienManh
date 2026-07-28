# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyen Van Thang
- **Student ID**: 2A202601580
- **Role**: Role 3 - Prompt Engineer
- **Date**: July 28, 2026

---

## I. Technical Contribution (15 Points)

As the **Prompt Engineer (Role 3)** for the **Cupid Agent** project, I was responsible for designing the prompts for the baseline Chatbot and the ReAct Agent. I also developed guardrail rules to ensure that the Agent calls the correct tools, handles errors safely, and terminates appropriately.

- **Module Implemented**: `src/prompts.py`
- **Main Contributions**:
  - Developed `CHATBOT_BASELINE_PROMPT`, which instructs the Chatbot to answer using only general knowledge, never simulate tool calls, and never fabricate compatibility data.
  - Developed `REACT_SYSTEM_PROMPT`, which clearly describes the three valid tools and enforces the `Thought -> Action -> Observation -> Final Answer` workflow.
  - Standardized each `Action` as a single line with JSON arguments so that the parser in `src/app.py` can process it reliably.
  - Required each turn to produce either one `Action` or one `Final Answer`, never both, and prohibited the model from creating or modifying an `Observation`.
  - Configured the `MAX_ITERATIONS = 4` and `TIMEOUT_SECONDS = 10` guardrails to limit resource usage and prevent infinite loops.
  - Added recovery rules for unknown tools, malformed JSON, repeated actions, error observations, and out-of-scope requests such as ordering a ring, scheduling an appointment, or sending a message.

- **Code Highlights**:

  ```python
  # Use one of the following two formats in each turn:
  Thought: <brief reasoning about the next step>
  Action: <tool_name>(<JSON object>)

  # Guardrails used by app.py to limit cost
  # and prevent infinite loops.
  MAX_ITERATIONS = 4
  TIMEOUT_SECONDS = 10
  ```

- **Documentation**:
  `REACT_SYSTEM_PROMPT` acts as a contract between the language model and the ReAct loop in `src/app.py`. The prompt requires the model to plan in the `Thought` block and generate exactly one `Action` for the application to parse and execute. It then uses the actual `Observation` inserted by the application to determine the next step. The Agent may return a `Final Answer` only after collecting sufficient evidence. For the INTJ/ENFP test case, the prompt also specifies that `analyze_mbti_match` must be called before `suggest_date_ideas`, which may only be called after the compatibility result has been received.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**:
  During the multi-step INTJ/ENFP test case, the Agent called the two required tools in the correct order. However, in a later turn, it produced content that did not match the `Action` format expected by the parser. Consequently, the application could not extract an Action and had to insert an error Observation into the context. This issue made the trace longer, reduced its stability, and could have caused the Agent to reach the iteration limit.

- **Log Source**: `docs/trace_eval.md` - Test Case #4 trace.

  ```text
  Thought 1: I need to analyze the compatibility between INTJ and ENFP first.
  Action 1: analyze_mbti_match({"mbti_1":"INTJ","mbti_2":"ENFP"})
  Observation 1: 95% compatibility (Diamond Complementary Pair).

  Thought 2: Next, I need to suggest a romantic date in Hanoi.
  Action 2: suggest_date_ideas({"location":"Hanoi","budget":"medium","vibe":"romantic"})
  Observation 2: A date itinerary in Hanoi.

  Observation: No valid Action was found. Please provide a Final Answer
  or try another Action.
  ```

- **Diagnosis**:
  The initial prompt version only provided an example of a JSON Action but did not strictly require the Action to appear on exactly one line. It also did not prohibit Markdown code blocks, explanations after the Action, or generating both an Action and a Final Answer in the same turn. Because the application parser depends on this output structure, even a minor formatting variation could cause parsing to fail.

- **Solution**:
  I strengthened `REACT_SYSTEM_PROMPT` with the following rules: each turn must generate exactly one `Action` or one `Final Answer`; an Action must appear on a single line; its arguments must be a valid JSON object; it must not be enclosed in a code block; the JSON must not span multiple lines; and no additional content may follow the Action. I also added recovery instructions for malformed arguments and Observations beginning with `LỖI:` (`ERROR:`): the Agent must not treat an error as successful data and must either correct the parameters or return a safe fallback. The `MAX_ITERATIONS = 4` guardrail ensures that the system still terminates safely if formatting errors continue to occur.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**:
   The `Thought` block helps the Agent separate planning from execution. For a multi-step question, the Agent can determine that it must first analyze MBTI compatibility, examine the result, and then select an appropriate date suggestion. The baseline Chatbot answers directly, so it cannot demonstrate a plan or verify its response using tools.

2. **Reliability**:
   A ReAct Agent is not always better than a Chatbot. For general relationship-advice questions, the baseline Chatbot is faster, uses fewer tokens, and does not face Action-parsing failures. The Agent may perform worse when the model produces invalid JSON, repeatedly calls the same tool, selects the wrong tool, or uses unnecessary reasoning steps. Therefore, my prompt instructs the Agent to provide a direct `Final Answer` without calling a tool when the question is simple.

3. **Observation**:
   An `Observation` provides environmental evidence that guides the Agent's next step. In the INTJ/ENFP test case, the output of `analyze_mbti_match` provides the basis for suggesting a date. When an Observation reports `LỖI:` (`ERROR:`), the Agent must stop reasoning from that data, correct the input when possible, or return a safe fallback. This mechanism reduces hallucination compared with a Chatbot that relies only on the model's internal knowledge.

---

## IV. Future Improvements (5 Points)

- **Scalability**:
  Separate the tool specifications from the static prompt and generate a relevant tool list for each query. As the number of tools grows, semantic retrieval could be used to include only the relevant tools in the context, thereby reducing prompt length.

- **Safety**:
  Add an independent validation layer before executing an Action, including JSON Schema parameter validation, a tool-name allowlist, a prompt-injection filter, and user confirmation for actions that affect external systems. The guardrails should also be evaluated with an adversarial test suite instead of relying only on natural-language instructions in the prompt.

- **Performance**:
  Apply hybrid routing: general-knowledge questions should use the Chatbot fast path, while requests requiring real data or multiple steps should use the ReAct Agent. Structured output or function calling could replace regular-expression-based Action parsing, reducing formatting errors and unnecessary iterations.
