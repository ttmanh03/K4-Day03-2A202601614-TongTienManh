"""
💘 CUPID AGENT — LOCAL WEB SERVER & AGENTIC VISUALIZER
Server Python phục vụ giao diện Web Dashboard & API runner cho ReAct Agent.
Sử dụng thư viện chuẩn của Python (zero-dependency backend).
"""

import http.server
import socketserver
import json
import os
import sys
import time
import urllib.parse
from dotenv import load_dotenv

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
WEB_DIR = os.path.join(BASE_DIR, "web")
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

sys.path.append(SRC_DIR)

from tools import AVAILABLE_TOOLS, calculate_zodiac_compatibility, analyze_mbti_match, suggest_date_ideas
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

PORT = 8000


def parse_action(text: str):
    """Trích xuất (tool_name, kwargs_dict) từ dòng 'Action: name({...})'"""
    import re
    m = re.search(r'Action:\s*(\w+)\s*\((.*)\)\s*$', text, re.MULTILINE | re.DOTALL)
    if not m:
        return None, None
    tool_name = m.group(1).strip()
    raw = m.group(2).strip()
    try:
        kwargs = json.loads(raw)
        if isinstance(kwargs, dict):
            return tool_name, kwargs
    except (json.JSONDecodeError, ValueError):
        pass
    parts = [p.strip().strip('"\'') for p in raw.split(',') if p.strip()]
    return tool_name, {"__pos__": parts} if parts else {}


def call_tool(tool_name: str, kwargs: dict, executed_actions: set) -> str:
    """Thực thi tool an toàn và trả về Observation"""
    signature = (tool_name, json.dumps(kwargs, sort_keys=True, ensure_ascii=False))

    if tool_name not in AVAILABLE_TOOLS:
        valid = ", ".join(AVAILABLE_TOOLS.keys())
        return f"LỖI: Tool '{tool_name}' không tồn tại. Tool hợp lệ: [{valid}]."

    if signature in executed_actions:
        return f"LỖI: Action {tool_name}({kwargs}) đã được gọi trước đó, không lặp lại."

    fn = AVAILABLE_TOOLS[tool_name]
    try:
        observation = fn(*kwargs["__pos__"]) if "__pos__" in kwargs else fn(**kwargs)
    except TypeError as e:
        return f"LỖI: Tham số không hợp lệ khi gọi '{tool_name}' — {e}"
    except Exception as e:
        return f"LỖI: Ngoại lệ khi thực thi '{tool_name}' — {e}"

    executed_actions.add(signature)
    return observation


def execute_full_flow(user_query: str):
    """Thực thi cả Chatbot Baseline lẫn ReAct Agent và trả về mảng dữ liệu JSON cấu trúc"""
    start_time = time.time()
    provider = get_llm_provider()
    provider_name = provider.__class__.__name__

    # 1. Baseline Response
    baseline_response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)

    # 2. ReAct Agent Trace Execution
    conversation = f"Question: {user_query}\n"
    executed_actions = set()
    steps = []
    final_answer = ""
    guardrail_triggered = False
    step = 0

    while step < MAX_ITERATIONS:
        step += 1
        llm_output = provider.generate(conversation, system_prompt=REACT_SYSTEM_PROMPT)

        # Parse Final Answer
        if "Final Answer:" in llm_output:
            idx = llm_output.index("Final Answer:")
            thought_part = llm_output[:idx].replace("Thought:", "").strip()
            final_answer = llm_output[idx + len("Final Answer:"):].strip()
            steps.append({
                "step": step,
                "type": "final",
                "thought": thought_part or "Đã thu thập đủ dữ liệu.",
                "final_answer": final_answer,
                "raw_output": llm_output
            })
            break

        # Parse Action
        tool_name, kwargs = parse_action(llm_output)
        if tool_name:
            thought_part = llm_output.split("Action:")[0].replace("Thought:", "").strip()
            obs = call_tool(tool_name, kwargs or {}, executed_actions)
            steps.append({
                "step": step,
                "type": "action",
                "thought": thought_part,
                "tool_name": tool_name,
                "kwargs": kwargs,
                "observation": obs,
                "raw_output": llm_output
            })
            conversation += llm_output.strip() + "\n"
            conversation += f"Observation: {obs}\n"
        else:
            thought_part = llm_output.replace("Thought:", "").strip()
            obs = "Observation: Không tìm thấy Action hợp lệ. Hãy đưa ra Final Answer hoặc thử Action khác."
            steps.append({
                "step": step,
                "type": "parse_error",
                "thought": thought_part,
                "observation": obs,
                "raw_output": llm_output
            })
            conversation += llm_output.strip() + "\n"
            conversation += f"{obs}\n"

    if step >= MAX_ITERATIONS and not final_answer:
        guardrail_triggered = True
        final_answer = "Xin lỗi, mình chưa thu thập đủ dữ liệu đáng tin cậy để kết luận trong giới hạn số bước cho phép."

    exec_time = round((time.time() - start_time) * 1000, 2)

    return {
        "query": user_query,
        "provider": provider_name,
        "execution_time_ms": exec_time,
        "baseline_answer": baseline_response,
        "react_agent": {
            "total_steps": len(steps),
            "max_iterations": MAX_ITERATIONS,
            "guardrail_triggered": guardrail_triggered,
            "steps": steps,
            "final_answer": final_answer
        }
    }


class CupidAgentHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path

        if path == "/api/test-cases":
            self.send_json_file(os.path.join(CONFIG_DIR, "test_cases.json"))
        elif path == "/api/cupid-data":
            self.send_json_file(os.path.join(CONFIG_DIR, "cupid_data.json"))
        elif path == "/api/flowchart":
            self.send_text_file(os.path.join(DOCS_DIR, "hybrid_flowchart.mermaid"), "text/plain")
        elif path == "/api/trace-eval":
            self.send_text_file(os.path.join(DOCS_DIR, "trace_eval.md"), "text/markdown")
        elif path == "/api/provider-info":
            provider = get_llm_provider()
            info = {
                "provider_class": provider.__class__.__name__,
                "provider_env": os.getenv("LLM_PROVIDER", "mock"),
                "model_name": getattr(provider, "model_name", "Mock Engine"),
                "max_iterations": MAX_ITERATIONS
            }
            self.send_json_response(info)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/run":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                query = data.get("query", "").strip()
                if not query:
                    self.send_json_response({"error": "Câu hỏi không được để rỗng"}, status=400)
                    return
                result = execute_full_flow(query)
                self.send_json_response(result)
            except Exception as e:
                self.send_json_response({"error": str(e)}, status=500)
        else:
            self.send_error(404, "Not Found")

    def send_json_response(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_json_file(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json_response({"error": "File không tồn tại"}, status=404)

    def send_text_file(self, filepath, content_type="text/plain"):
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            body = content.encode('utf-8')
            self.send_response(200)
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_json_response({"error": "File không tồn tại"}, status=404)


def run_server():
    os.makedirs(WEB_DIR, exist_ok=True)
    handler = CupidAgentHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("==================================================")
        print(" CUPID AGENT -- LOCAL WEB SERVER IS RUNNING!")
        print(f" Giao dien Web Studio: http://localhost:{PORT}")
        print("==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n Stopping web server...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
