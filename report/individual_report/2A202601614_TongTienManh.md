# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Tống Tiến Mạnh
- **Student ID**: 2A202601614
- **Date**: July 28, 2026

---

## I. Technical Contribution (15 Points)

My main responsibility in this lab was **Role 5: Observability & Reviewer**. Instead of building the tools or the ReAct loop directly, I focused on evaluating whether the selected problem was suitable for an agent, recording baseline chatbot behavior, extracting ReAct traces, and documenting the differences between the two approaches in a clean report format.

- **Modules Implementated**: `docs/trace_eval.md`, `docs/hybrid_flowchart.mermaid`
- **Code Highlights**:
  - Completed the **Agentic Fit Scoring Matrix** for the Cupid Agent use case in `docs/trace_eval.md`.
  - Recorded and evaluated **Chatbot Baseline** responses on representative test cases, including a general knowledge case, a multi-step case, and an edge case.
  - Extracted structured ReAct traces in the format `Thought -> Action -> Observation -> Final Answer` for test cases involving MBTI analysis and invalid zodiac inputs.
  - Cleaned the report file to remove raw terminal logs and reorganized it into a proper submission-ready document.
  - Created the **Hybrid Flowchart** in `docs/hybrid_flowchart.mermaid` to show when the system should follow the Chatbot path and when it should follow the ReAct Agent path.
- **Documentation**:
  - My report work interacts with the ReAct loop indirectly. I observed outputs produced by `src/app.py`, compared the baseline path with the ReAct path, and transformed those raw outputs into structured evidence for scoring, debugging, and reflection.
  - This role was important because it turned the group’s implementation into something measurable and explainable, especially for Mốc 1-4 evaluation.

---

## II. Debugging Case Study (10 Points)

- **Problem Description**: During the ReAct run for the multi-step MBTI dating scenario, the agent successfully called the first tools, but a later model output became unstable and could not be parsed cleanly as a valid `Action`. This made the trace noisy and reduced confidence in the ReAct loop formatting.
- **Log Source**: The issue was documented in `docs/trace_eval.md` under the ReAct trace for **TEST CASE #4**. The trace showed that the agent produced useful observations first, but later generated an output that did not follow the expected strict pattern.
- **Diagnosis**: I concluded that the issue was not caused by the tool implementations themselves, but mainly by **output-format instability between the prompt and the parser**. The loop in `src/app.py` expects a predictable `Thought` / `Action` structure, so if the model drifts into a more free-form explanation too early, parsing becomes unreliable.
- **Solution**: I recorded this as a concrete observability finding and recommended tightening the `REACT_SYSTEM_PROMPT` so the agent keeps a stricter output contract. I also documented that the trace should be evaluated not only by whether the answer sounds good, but by whether the intermediate steps remain machine-readable throughout the loop.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning**: The `Thought` block made the agent’s decision process visible. A normal chatbot can give a smooth final answer, but we do not know why it chose that answer. With ReAct, I could see that the system first analyzed MBTI compatibility, then used that observation to decide whether it should propose a date plan. This made the system more inspectable and easier to evaluate.

2. **Reliability**: The agent did not always perform better than the chatbot. In simple knowledge questions, the baseline chatbot was actually more stable because it answered directly and did not risk parser failure. In contrast, the ReAct path could become worse when the model output format drifted or when a fallback rule in the tool was too permissive.

3. **Observation**: Environment feedback was the key difference. Observations changed what the agent did next. For example, after receiving the MBTI result for `INTJ` and `ENFP`, the agent moved on to `suggest_date_ideas`. In the invalid zodiac case, the observation should have helped the agent stop hallucinating and move into a safer refusal path. This showed me that observations are what turn a text generator into a more grounded system.

---

## IV. Future Improvements (5 Points)

- **Scalability**: Replace the current hardcoded compatibility data with a structured profile dataset and a clearer separation between user profiles, matching rules, and recommendation outputs.
- **Safety**: Add stricter input validation in tools such as `calculate_zodiac_compatibility` so invalid zodiac names return an explicit error instead of a generic compatibility fallback.
- **Performance**: Improve the ReAct loop by enforcing a more rigid action schema and optionally validating model output before execution, so malformed responses do not break the reasoning flow.

---

> [!NOTE]
> This report was written based on my role as **Role 5: Observability & Reviewer**, focusing on evaluation artifacts, trace analysis, and hybrid decision documentation rather than primary tool or application implementation.
