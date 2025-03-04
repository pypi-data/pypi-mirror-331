import logging
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional
import requests
import json
from flask import Flask, Response, request, render_template_string
import uuid
import re
from bs4 import BeautifulSoup
import html
import urllib.parse
import time
from urllib.parse import unquote

DEFAULT_OLLAMA_API_URL = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
app = Flask(__name__)
sessions = defaultdict(dict)
generation_statuses = defaultdict(lambda: {"generating": False})
session = requests.Session()

def fetch_url_content(url: str) -> Dict[str, str]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    try:
        url = urllib.parse.unquote(url)
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        content_selectors = ['article', '#content', '.post-content', '.entry-content', '.main-content', '[role="main"]', 'main', 'body']
        content = None
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        if not content:
            content = soup.body
        if content:
            for tag in content(['script', 'style', 'nav', 'footer', 'header', 'aside', '[class*="ad"]']):
                tag.decompose()
            text = content.get_text(separator=' ', strip=True)
            result = {"text": text[:65536] if text else "未提取到有效内容", "images": []}
            return result
        return {"text": "未找到有效内容区域", "images": []}
    except requests.exceptions.RequestException as e:
        logger.warning(f"URL {url} 获取失败: {str(e)}", exc_info=True)
        return {"text": f"链接获取失败: {str(e)}", "images": []}
    except Exception as e:
        logger.error(f"URL解析异常: {str(e)}", exc_info=True)
        return {"text": f"URL解析异常: {str(e)}", "images": []}

def extract_urls(text: str) -> List[str]:
    url_pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:[^\s()<>]*|\([^\s()<>]+\))*(?<![\.,:;])')
    urls = url_pattern.findall(text)
    return [f"https://{url}" if not url.startswith(('http://', 'https://')) else url for url in urls]

def normalize_context(context: List[Dict]) -> List[Dict]:
    normalized = []
    for item in context:
        role = item.get("role", "user")
        parts = item.get("parts", [{"text": item.get("content", "")}])
        message = parts[0].get("text", "") if parts and isinstance(parts, list) else ""
        normalized.append({"role": role, "message": message})
    return normalized

def chunk_text(text: str, chunk_size: int = 4096) -> List[str]:
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def generate_ollama_stream(prompt: str, session_id: str, history: List[Dict], url_content: str = "", model: str = "llama3", api_url: str = DEFAULT_OLLAMA_API_URL) -> Response:
    headers = {"Content-Type": "application/json"}
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    system_prompt = f"你是一个实用又友好的AI助手，名字叫OllamaWebUI助手，提供简洁准确的中文回复。当前时间: {current_time}"

    context_text = "\n### 当前对话上下文：\n"
    for item in history[-5:]:
        role = item.get("role", "user")
        message = item.get("message", "(无内容)")
        context_text += f"**{'用户' if role == 'user' else 'AI'}**: {message}\n"

    effective_prompt = f"{system_prompt}\n{context_text}\n### 用户提问:\n{prompt}\n{url_content}"
    previous_context = sessions[session_id].get("context", None)

    payload = {
        "model": model,
        "prompt": effective_prompt,
        "stream": True,
        "context": previous_context
    }
    logger.debug(f"Ollama Payload: {payload}")

    def stream():
        generation_statuses[session_id]["generating"] = True
        logger.info(f"Generation started for session {session_id} with model '{model}'")
        try:
            with requests.post(f"{api_url}/api/generate", headers=headers, json=payload, stream=True, timeout=120) as response:
                response.raise_for_status()
                buffer = ""
                for line in response.iter_lines():
                    if not generation_statuses[session_id]["generating"]:
                            logger.info(f"Stop signal received for session {session_id}, stopping generation.")
                            break
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                buffer += data["response"]
                                yield f"data: {json.dumps({'text': buffer}, ensure_ascii=False)}\n\n"
                            if data.get("done", False):
                                if "context" in data:
                                    sessions[session_id]["context"] = data["context"]
                                yield f"data: {json.dumps({'done': True}, ensure_ascii=False)}\n\n"
                                logger.info(f"Generation completed for session {session_id}")
                                break
                        except json.JSONDecodeError:
                            logger.error(f"JSON Decode Error: {line.decode('utf-8')}, line data: {line.decode('utf-8')[:100]}...", exc_info=True)
                            continue
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API request failed: {str(e)}, Response: {e.response}", exc_info=True)
            yield f"data: {json.dumps({'error': f'服务器响应失败: {str(e)}'}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.error(f"Generation stream error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': f'生成出错: {str(e)}'}, ensure_ascii=False)}\n\n"
        finally:
             generation_statuses[session_id]["generating"] = False

    return Response(stream(), mimetype="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json(silent=True)
        if data is None:
            logger.warning("Invalid JSON request received for /chat")
            return Response(f"data: {json.dumps({'error': '请求体不是有效的JSON格式'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")
        if not isinstance(data, dict) or 'message' not in data:
            logger.warning("Missing 'message' field in /chat request")
            return Response(f"data: {json.dumps({'error': '请求体缺少message字段或格式错误'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")

        message = data.get('message', '')
        message = unquote(message)

        session_id = data.get('session_id', str(uuid.uuid4()))
        context = data.get('context', [])
        model = data.get('model', 'llama3')
        api_url = data.get('api_url', DEFAULT_OLLAMA_API_URL)

        if not message:
            logger.warning("Empty message in /chat request")
            return Response(f"data: {json.dumps({'error': '消息不能为空'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")

        try:
            requests.get(f"{api_url}/api/tags", timeout=5)
        except requests.exceptions.RequestException:
            logger.error(f"Ollama service unavailable at: {api_url}", exc_info=True)
            return Response(f"data: {json.dumps({'error': f'Ollama 服务不可用: {api_url}，请检查地址或配置'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")

        urls = extract_urls(message)
        url_content_text = "".join(f"\n#### 来自 {url} 的内容：\n{fetch_url_content(url)['text']}\n" for url in urls)

        normalized_context = normalize_context(context)
        sessions[session_id].setdefault("messages", []).append({'role': 'user', 'parts': [{"text": message}], 'timestamp': datetime.now().isoformat()})
        return generate_ollama_stream(message, session_id, normalized_context, url_content_text, model, api_url)
    except ValueError as ve:
        logger.error(f"JSON parsing error in /chat request: {str(ve)}", exc_info=True)
        return Response(f"data: {json.dumps({'error': '请求体JSON解析失败'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")
    except Exception as e:
        logger.error(f"Request processing failed for /chat: {str(e)}", exc_info=True)
        return Response(f"data: {json.dumps({'error': f'服务器内部错误: {str(e)}'}, ensure_ascii=False)}\n\n", mimetype="text/event-stream")

@app.route('/models', methods=['POST', 'GET'])
def get_models():
    try:
        if request.method == 'POST':
            data = request.get_json(silent=True)
            api_url = data.get('api_url', DEFAULT_OLLAMA_API_URL) if data else DEFAULT_OLLAMA_API_URL
        else:
            api_url = DEFAULT_OLLAMA_API_URL
        response = requests.get(f"{api_url}/api/tags")
        response.raise_for_status()
        models_data = response.json()
        models = [model["name"] for model in models_data.get("models", [])]
        result = {"models": models}
        return json.dumps(result, ensure_ascii=False)
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch model list from Ollama API: {str(e)} at {api_url}", exc_info=True)
        return json.dumps({"error": f"获取模型列表失败: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error getting model list: {str(e)}", exc_info=True)
        return json.dumps({"error": f"获取模型列表失败: {str(e)}"}, ensure_ascii=False)

@app.route('/')
def index():
    return render_template_string(r'''<!DOCTYPE html>
<html lang="zh" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OllamaWebUI</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
    <script src="https://cdn.jsdelivr.net/npm/marked@4.3.0/lib/marked.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
    <style>
        :root {

--font-family: 'Arial', Arial, bold;
            --light-bg: #ffffff;
            --light-text: #24292e;
            --light-border: #d0d7de;
            --light-shadow: rgba(0, 0, 0, 0.05);
            --light-hover: #f6f8fa;
            --light-code-bg: #f8f9fa;
            --light-code-text: #24292e;
            --light-button-bg: #f0f2f5;
            --light-button-hover: #e0e2e5;
            --light-ai-bg: #f2f2f7;
            --light-user-bg: #e0f7fa;
            --light-markdown-bg: #f0f0f0;
            --light-link-color: #0969da;
            --light-secondary: #57606a;

            --dark-bg: #1e1e1e;
            --dark-text: #d4d4d4;
            --dark-border: #30363d;
            --dark-shadow: rgba(255, 255, 255, 0.05);
            --dark-hover: #2a2d2e;
            --dark-code-bg: #2d2d2d;
            --dark-code-text: #d4d4d4;
            --dark-button-bg: #30363d;
            --dark-button-hover: #3a3f44;
            --dark-ai-bg: #2a2a2d;
            --dark-user-bg: #29434e;
            --dark-markdown-bg: #2a2a2b;
            --dark-link-color: #ffffff;
            --dark-secondary: #8b949e;
        }
        [data-theme="light"] {
            --bg: var(--light-bg);
            --text: var(--light-text);
            --border: var(--light-border);
            --shadow: var(--light-shadow);
            --hover: var(--light-hover);
            --code-bg: var(--light-code-bg);
            --code-text: var(--light-code-text);
            --button-bg: var(--light-button-bg);
            --button-hover: var(--light-button-hover);
            --ai-bg: var(--light-ai-bg);
            --user-bg: var(--light-user-bg);
            --markdown-bg: var(--light-markdown-bg);
            --link-color:#000000;
            --secondary: var(--light-secondary);
        }
        [data-theme="dark"] {
            --bg: var(--dark-bg);
            --text: var(--dark-text);
            --border: var(--dark-border);
            --shadow: var(--dark-shadow);
            --hover: var(--dark-hover);
            --code-bg: var(--dark-code-bg);
            --code-text: var(--dark-code-text);
            --button-bg: var(--dark-button-bg);
            --button-hover: var(--dark-button-hover);
            --ai-bg: var(--dark-ai-bg);
            --user-bg: var(--dark-user-bg);
            --dark-markdown-bg: var(--dark-markdown-bg);
            --link-color: var(--dark-link-color);
            --secondary: var(--dark-secondary);
        }
        body {
            font-family: var(--font-family);
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            font-size: 16px;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            transition: background-color 0.3s, color 0.3s;
            -webkit-font-smoothing: antialiased;
        }
        .container {
            display: flex;
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            height: 100vh;
            border: 1px solid var(--border);
            background: var(--bg);
            box-shadow: 0 2px 10px var(--shadow);
            border-radius: 8px;
            overflow: hidden;
        }
        .sidebar {
            width: 25%;
            max-width: 350px;
            background: var(--light-bg);
            border-right: 1px solid var(--border);
            height: 100vh;
            overflow-y: auto;
            position: fixed;
            left: -350px;
            top: 0;
            transition: left 0.3s ease;
            z-index: 1002;
            display: flex;
            flex-direction: column;
        }
        [data-theme="dark"] .sidebar {
            background: var(--dark-bg);
        }
        .sidebar.active { left: 0; }
        .theme-toggle, .new-chat-btn, .menu-toggle, .clear-history, .history-search, .model-select, .settings-panel button, .code-actions button, #send-button, #stop-button, .settings-toggle {
            transition: background-color 0.3s, transform 0.1s, color 0.3s, border-color 0.3s;
            box-shadow: 0 1px 3px var(--shadow);
            font-weight: 500;
        }
        .theme-toggle {
            margin: 20px 8%;
            padding: 12px;
            background: var(--button-bg);
            color: var(--text);
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        .theme-toggle:hover { background: var(--button-hover); transform: translateY(-1px); }
        .menu-toggle {
            position: fixed;
            top: 10px;
            left: 10px;
            background: var(--button-bg);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            z-index: 1003;
            padding: 8px;
        }
        .menu-toggle:hover { background: var(--button-hover); }
        .menu-toggle.hidden { display: none; }
        .new-chat-btn {
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px;
            background: var(--button-bg);
            color: var(--text);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 40px;
            height: 40px;
            z-index: 1003;
        }
        .new-chat-btn:hover { background: var(--button-hover); transform: translateY(-1px); }
        .history-search {
            margin: 8% 8% 5%;
            padding: 12px;
            border: 1px solid var(--border);
            border-radius: 6px;
            width: 85%;
            font-size: 16px;
            background: var(--bg);
            color: var(--text);
            caret-color: var(--link-color);
            box-shadow: inset 0 1px 3px var(--shadow);
        }
        .history-search:focus { border-color: var(--link-color); outline: none; }
        .chat-history {
            flex: 1;
            overflow-y: auto;
            padding: 0 5%;
            scrollbar-width: thin;
            scrollbar-color: var(--secondary) var(--bg);
        }
        .chat-history::-webkit-scrollbar { width: 8px; }
        .chat-history::-webkit-scrollbar-thumb { background: var(--secondary); border-radius: 4px; }
        .history-item {
            padding: 12px;
            border-bottom: 1px solid var(--border);
            cursor: pointer;
            border-radius: 6px;
            margin: 5px 0;
            font-size: 16px;
            color: var(--text);
            overflow-wrap: break-word;
        }
        .history-item:hover { background: var(--hover); }
        .history-item.active { background: var(--ai-bg); }
        .history-item .title { font-weight: 500; font-size: 18px; color: var(--link-color); }
        .history-item .preview { font-size: 14px; color: var(--secondary); margin-top: 5px; }
        .history-item .time { font-size: 12px; color: var(--secondary); margin-top: 5px; display: block; }
        .clear-history-container {
            position: sticky;
            bottom: 0;
            padding: 10px 8%;
            background: var(--light-bg);
            border-top: 1px solid var(--border);
        }
        [data-theme="dark"] .clear-history-container {
             background: var(--dark-bg);
        }
        .clear-history {
            padding: 12px 20px;
            background: var(--button-bg);
            color: var(--text);
            border: none;
            border-radius: 6px;
            cursor: pointer;
            width: 100%;
            font-size: 18px;
            display: flex;
            justify-content: center;
        }
        .clear-history:hover { background: var(--button-hover); transform: translateY(-1px); }
        .chat-container {
            flex: 3;
            display: flex;
            flex-direction: column;
            padding: 20px;
            background: var(--bg);
            width: 100%;
            overflow-y: auto;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 0 10px;
            scrollbar-width: thin;
            scrollbar-color: var(--secondary) var(--bg);
            display: flex;
            flex-direction: column;
        }
        .chat-messages::-webkit-scrollbar { width: 8px; }
        .chat-messages::-webkit-scrollbar-thumb { background: var(--secondary); border-radius: 4px; }
        .message {
            display: flex;
            margin: 12px 0;
            max-width: 80%;
            border-radius: 8px;
            animation: fadeIn 0.3s ease;
            font-size: 16px;
            overflow-wrap: break-word;
            box-shadow: 0 1px 3px var(--shadow);
            padding: 0;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .message.user {
            margin-left: auto;
            background: #000000;
            color: #ffffff;
            border-radius: 4px 0 4px 4px;
            max-width: 70%;
        }
        .message.ai {
            margin-right: auto;
            background: var(--ai-bg);
            color: var(--text);
            border-radius: 0 4px 4px 4px;
            max-width: 70%;
        }
        .message-content {
            line-height: 1.6;
            overflow-wrap: break-word;
            word-break: break-word;
            width: 100%;
            padding: 12px 22px;
            position: relative;
            user-select: text;
        }
        .message-content p { margin: 12px 0; }
        .message-content a { color: var(--link-color); text-decoration: none; font-weight: 600; border-bottom: 1px solid var(--link-color); padding-bottom: 2px;}
        .message-content a:hover { text-decoration: underline; }
        .message-content ul, .message-content ol { padding-left: 22px; margin: 12px 0; }
        .message-content li { margin: 6px 0; }
        .message-content details { margin: 12px 0; }
        .message-content summary { cursor: pointer; font-weight: 600; padding: 6px; background-color: var(--markdown-bg); border-radius: 4px; padding: 10px; margin-bottom: 5px;}
        .message-content details[open] summary { border-bottom: 1px solid var(--border); }
        .message-content img { max-width: 100%; height: auto; margin: 12px 0; border-radius: 4px; }
        .message-content blockquote {
            margin: 12px 0;
            padding: 12px 17px;
            background: var(--markdown-bg);
            border-left: 4px solid var(--link-color);
            color: var(--text);
            font-style: italic;
            border-radius: 4px;
        }
        .message-content h1, .message-content h2, .message-content h3, .message-content h4, .message-content h5, .message-content h6 {
            margin: 17px 0 12px;
            color: var(--link-color);
            font-weight: 700;
            line-height: 1.3;
        }
        .message-content h1 { font-size: 2.2em; }
        .message-content h2 { font-size: 1.8em; }
        .message-content h3 { font-size: 1.6em; }
        .message-content h4 { font-size: 1.4em; }
        .message-content h5 { font-size: 1.2em; }
        .message-content h6 { font-size: 1.1em; }

        .message-content table {
            width: 100%;
            border-collapse: collapse;
            margin: 12px 0;
            background: var(--bg);
            border: 1px solid var(--border);
        }
        .message-content th, .message-content td { padding: 9px 14px; border: 1px solid var(--border); text-align: left; }
        .message-content th { background: var(--ai-bg); font-weight: 600; color: var(--link-color); }
        .message-content pre {
            background: var(--code-bg);
            color: var(--code-text);
            border-radius: 6px;
            max-width: 99%;
            font-size: 16px;
            line-height: 1.6;
            position: relative;
            border: 1px solid var(--border);
            padding: 10px;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        .message-content code:not(pre code) {
            background: #000000;
            color:#ffffff;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: var(--font-family-mono);
            font-size: 16px;
        }
        .message-content .katex {
            display: inline-block;
            vertical-align: middle;
            max-width: 90%;
            overflow-x: auto;
            white-space: nowrap;
            padding: 6px;
            font-size: 1em;
            color: var(--text);
        }
        .message-content .katex-display {
            display: block;
            max-width: 90%;
            overflow-x: auto;
            padding: 12px;
            margin: 12px 0;
            background: var(--markdown-bg);
            border-radius: 4px;
            color: var(--text);
            text-align: center;
            white-space: nowrap;
        }
        .code-actions {
            position: absolute;
            bottom: 9px;
            right: 9px;
            display: flex;
            gap: 7px;
        }

        .code-actions button {
            background:#f0f2f596;
            color: var(--text);
            border: none;
            border-radius: 4px;
            padding: 7px 14px;
            font-size: 15px;
            cursor: pointer;
        }
        .code-actions button:hover { background: var(--button-hover); transform: translateY(-1px); }
        .loading-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 22px;
        }
        .loading-dots {
            display: flex;
            gap: 9px;
        }
        .loading-dots span {
            width: 13px;
            height: 13px;
            background: var(--secondary);
            border-radius: 50%;
            animation: bounce 1.2s infinite ease-in-out both;
            display: inline-block;
        }
        .loading-dots span:nth-child(1) { animation-delay: -0.32s; }
        .loading-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }
        .input-container {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 17px;
            border-top: 1px solid var(--border);
            background: var(--bg);
            z-index: 1000;
            width: 100%;
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
            box-sizing: border-box;
        }
        .input-wrapper {
            display: flex;
            gap: 14px;
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 14px;
            align-items: center;
            flex: 1;
            box-shadow: 0 2px 4px var(--shadow);
        }
        .input-wrapper:focus-within { border-color: var(--link-color); }
        #message-input {
            flex: 1;
            border: none;
            outline: none;
            padding: 6px;
            resize: none;
            font-size: 16px;
            background: transparent;
            color: var(--text);
            overflow-y: auto;
            user-select: text;
            white-space: pre-wrap;
            caret-color: var(--link-color);
        }
        #send-button, #stop-button, .settings-toggle {
            background: none;
            border: none;
            cursor: pointer;
            padding: 9px;
            color: var(--link-color);
        }
        #stop-button { display: none; }
        .error-message {
            color: #ff4444;
            font-size: 16px;
            margin: 12px 0;
            text-align: center;
            font-weight: 500;
        }
        .model-select-container {
            margin: 20px 8%;
            .model-select
            width: 85%;
        }
        .model-select {
            padding: 8px 12px;
            background: var(--button-bg);
            color: var(--text);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            appearance: none;
            -webkit-appearance: none;
            -moz-appearance: none;
            width: 99%;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 0.7rem center;
            background-size: 1.5rem;
            padding-right: 2.5rem;
        }
        .model-select:hover { background: var(--button-hover); border-color: var(--link-color); }

        .settings-panel {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg);
            border: 1px solid var(--border);
            padding: 20px;
            z-index: 1004;
            display: none;
            width: 300px;
            box-shadow: 0 2px 10px var(--shadow);
            border-radius: 8px;
        }
        .settings-panel h3 { margin: 0 0 15px; font-size: 20px; font-weight: 500; color: var(--link-color); }
        .settings-panel input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            background: var(--user-bg);
            border: 1px solid var(--border);
            color: var(--text);
            font-size: 16px;
            border-radius: 6px;
            box-shadow: inset 0 1px 3px var(--shadow);
        }
        .settings-panel input:focus { border-color: var(--link-color); outline: none; }
        .settings-panel button {
            width: 100%;
            padding: 12px;
            background: var(--button-bg);
            color: var(--text);
            border: none;
            cursor: pointer;
            border-radius: 6px;
        }
        .small-text { font-size: 0.9em; color: var(--secondary); }

        @media (max-width: 600px) {
            .container { flex-direction: column; height: auto; border: none; border-radius: 0; }
            .sidebar { width: 85%; max-width: none; height: 100vh; left: -100%; border-right: none; }
            .sidebar.active { left: 0; }
            .chat-container { padding: 12px; min-height: calc(100vh - 60px); margin-top: 50px; }
            .chat-messages { max-height: calc(100vh - 150px); font-size: 15px; padding-bottom: 60px; padding: 20px; }
            .input-container { padding: 12px; padding-bottom: env(safe-area-inset-bottom); max-width: 94%; gap: 9px; padding: 10px; }
            .input-wrapper { padding: 9px; gap: 9px; width: 100%; }
            .message { max-width: 100%; font-size: 15px; }
            .menu-toggle { top: 6px; left: 6px; }
            .new-chat-btn { top: 6px; right: 6px; width: 38px; height: 38px; }
            .message-content { padding: 9px 17px; }
            .message-content pre { font-size: 13px; }
            .code-actions { bottom: 3px; right: 3px; }
            .code-actions button { padding: 5px 10px; font-size: 13px; min-width: 50px; }
            #message-input { font-size: 15px; }
            .clear-history { font-size: 17px; padding: 11px 16px; }
            .message-content .katex { font-size: 0.9em; padding: 4px; }
            .message-content .katex-display { padding: 9px; margin: 9px 0; }
            .history-item { font-size: 15px; padding: 10px; }
            .history-item .title { font-size: 17px;color :#8a8a97 }
            .history-item .preview { font-size: 13px; }
            .history-item .time { font-size: 11px; }
            .theme-toggle, .history-search, .clear-history { font-size: 17px; padding: 11px; }
            .theme-toggle { margin: 15px 8%; }
            .history-search { margin: 8% 8% 4%; padding: 10px; }
            .clear-history-container { padding: 8px 8%; }
            .settings-toggle, #send-button, #stop-button { padding: 7px; }
            .settings-panel { width: 90%; }
        }
    </style>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
</head>
<body>
    <button class="menu-toggle">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <path d="M3 12h18M3 6h18M3 18h18" stroke="var(--link-color)" stroke-width="2" stroke-linecap="round"/>
        </svg>
    </button>
    <button class="new-chat-btn" onclick="startNewChat()">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M8 3.33337V12.6667M3.33333 8H12.6667" stroke="var(--text)" stroke-width="2" stroke-linecap="round"/>
        </svg>
    </button>

    <div class="container">
        <div class="sidebar">
            <button class="theme-toggle" onclick="toggleTheme()">切换主题</button>
             <div class="model-select-container">
        <select class="model-select" id="model-select" onchange="changeModel(this.value)">
            <option value="llama3">加载模型...</option>
        </select>
    </div>
            <input type="text" class="history-search" placeholder="搜索历史记录...">
            <div class="chat-history"></div>
            <div class="clear-history-container">
                <button class="clear-history" onclick="clearHistory()">清除记录</button>
            </div>
        </div>
        <div class="chat-container">
            <div class="chat-messages"></div>
            <div class="input-container">
                <div class="input-wrapper">
                    <button class="settings-toggle" id="settings-toggle" title="设置 API" onclick="toggleSettings()">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M13.5 9.5a1.5 1.5 0 0 1-1.5 1.5h-1a1.5 1.5 0 0 1-1.5-1.5V6.5a1.5 1.5 0 0 1 1.5-1.5h1a1.5 1.5 0 0 1 1.5 1.5v3zM7 9.5a1.5 1.5 0 0 1-1.5 1.5h-1A1.5 1.5 0 0 1 3 9.5V6.5A1.5 1.5 0 0 1 4.5 5h1A1.5 1.5 0 0 1 7 6.5v3z" stroke="var(--link-color)" stroke-width="2"/>
                        </svg>
                    </button>
                    <textarea id="message-input" placeholder="输入消息..." rows="1"></textarea>
                    <button id="send-button">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M14.6667 1.33337L7.33333 8.66671M14.6667 1.33337L10 14.6667L7.33333 8.66671L1.33333 6.00004L14.6667 1.33337Z" stroke="var(--link-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button id="stop-button" onclick="stopGenerating()">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                            <path d="M4 4H12V12H4V4Z" stroke="var(--link-color)" stroke-width="2" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>
    <div id="settings-panel" class="settings-panel">
        <h3>API 设置</h3>
        <input type="text" id="api-ip" placeholder="IP (默认: localhost)">
        <input type="text" id="api-port" placeholder="端口 (默认: 11434)">
        <button onclick="saveSettings()">保存并应用</button>
    </div>
    <div id="html-preview-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.6); z-index: 1001; overflow: auto;">
        <div style="background: var(--bg); margin: 10% auto; padding: 20px; border-radius: 8px; width: 90%; max-width: 800px; position: relative; box-shadow: 0 4px 12px var(--shadow);">
            <button id="close-preview" style="position: absolute; right: 5px; top: 10px; background: none; border: none; cursor: pointer; font-size: 1.5rem; color: var(--text);" onclick="htmlPreviewModal.style.display='none';">×</button>
            <iframe id="html-preview-content" style="width: 100%; height: 500px; border: none;"></iframe>
        </div>
    </div>
    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateModelSelectArrowColor();
            sidebar.classList.remove('active');
            menuToggle.classList.remove('hidden');
        }

        function updateModelSelectArrowColor() {
            const modelSelect = document.getElementById('model-select');
        }

        function hasMath(content) {
            return /\$[\s\S]+?\$|\$\$[\s\S]+?\$\$|\\\[[\s\S]+?\\\]|\\\(.*?\\\)|\\begin\{[a-z]*\*?\}\s*[^]*?\\end\{[a-z]*\*?\}/.test(content);
        }

        function renderMath(contentDiv) {
            contentDiv.querySelectorAll('.katex').forEach(el => el.outerHTML = el.innerHTML);
            renderMathInElement(contentDiv, {
                delimiters: [
                    { left: "\\[", right: "\\]", display: true },
                    { left: "$$", right: "$$", display: true },
                    { left: "[", right: "]", display: true },
                    { left: "$", right: "$", display: false },
                    { left: "\\(", right: "\\)", display: false },
                    { left: "\\begin{equation}", right: "\\end{equation}", display: true },
                    { left: "\\begin{align*}", right: "\\end{align*}", display: true },
                    { left: "\\begin{matrix}", right: "\\end{matrix}", display: true }
                ],
                throwOnError: false,
                strict: "ignore",
                trust: true,
                macros: { "\\RR": "\\mathbb{R}", "\\NN": "\\mathbb{N}", "\\ZZ": "\\mathbb{Z}", "\\CC": "\\mathbb{C}" },
                errorColor: '#ff4444'
            });
        }

        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&")
                .replace(/</g, "<")
                .replace(/>/g, ">")
                .replace(/"/g, '""')
                .replace(/'/g, "'");
        }

        const Config = {
            MAX_CONTEXT_LENGTH: 10,
            MAX_MESSAGE_LENGTH: 65536,
            CHUNK_SIZE: 4096,
            DEFAULT_API_URL: "http://localhost:11434"
        };
        let conversations = JSON.parse(localStorage.getItem('conversations')) || [];
        let currentConversationId = localStorage.getItem('currentConversationId') || Date.now().toString();
        let generation_statuses = {};
        let currentContext = [];
        let eventSource = null;
        let isGenerating = false;
        let apiUrl = localStorage.getItem('apiUrl') || Config.DEFAULT_API_URL;
        let currentModel = localStorage.getItem('currentModel') || "llama3";

        const chatMessages = document.querySelector('.chat-messages');
        const messageInput = document.querySelector('#message-input');
        const sendButton = document.querySelector('#send-button');
        const stopButton = document.querySelector('#stop-button');
        const settingsToggle = document.querySelector('#settings-toggle');
        const sidebar = document.querySelector('.sidebar');
        const menuToggle = document.querySelector('.menu-toggle');
        const newChatBtn = document.querySelector('.new-chat-btn');
        const historySearch = document.querySelector('.history-search');
        const htmlPreviewModal = document.querySelector('#html-preview-modal');
        const htmlPreviewContent = document.querySelector('#html-preview-content');
        const settingsPanel = document.querySelector('#settings-panel');
        const apiIpInput = document.querySelector('#api-ip');
        const apiPortInput = document.querySelector('#api-port');
        const modelSelect = document.getElementById('model-select');

        function initializeChat() {
            conversations.forEach(conv => {
                conv.messages.forEach(msg => {
                    if (msg.content && !msg.parts) {
                        msg.parts = [{"text": msg.content}];
                        delete msg.content;
                    }
                    if (msg.role === "assistant") msg.role = "model";
                    if (msg.role === "system") msg.role = "user";
                });
            });
            loadConversation(currentConversationId);
            updateChatHistory();
            setupEventListeners();
            adjustInputHeight();
            adjustContainerHeight();
            setTimeout(() => messageInput.focus(), 100);
            generation_statuses[currentConversationId] = { generating: false };
            loadModelsIntoSelector();
            updateModelSelectArrowColor();
        }

        async function loadModelsIntoSelector() {
            await fetchModels();
            modelSelect.value = currentModel;
        }

        function setupEventListeners() {
            menuToggle.addEventListener('click', () => { sidebar.classList.toggle('active'); menuToggle.classList.toggle('hidden'); });
            document.addEventListener('click', e => {
                if (!sidebar.contains(e.target) && !menuToggle.contains(e.target) && sidebar.classList.contains('active')) { sidebar.classList.remove('active'); menuToggle.classList.remove('hidden'); }
                if (!settingsPanel.contains(e.target) && !settingsToggle.contains(e.target) && settingsPanel.style.display === 'block') { settingsPanel.style.display = 'none'; }
            });
            sendButton.addEventListener('click', () => debounce(sendMessage, 100)());
            messageInput.addEventListener('keydown', e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); debounce(sendMessage, 100)(); } });
            messageInput.addEventListener('input', adjustInputHeight);
            historySearch.addEventListener('input', debounce(e => updateChatHistory(e.target.value.toLowerCase()), 300));
            window.addEventListener('resize', adjustContainerHeight);
        }

        function debounce(func, wait) { let timeout; return function (...args) { clearTimeout(timeout); timeout = setTimeout(() => func.apply(this, args), wait); }; }

        function adjustInputHeight() {
            messageInput.style.height = 'auto';
            const lines = messageInput.value.split('\n').length;
            const baseHeight = 24;
            const height = Math.max(1, Math.min(lines, 5)) * baseHeight + 10;
            messageInput.style.height = `${Math.min(height, window.innerHeight * 0.2)}px`;
            sendButton.disabled = !messageInput.value.trim();
            adjustContainerHeight();
        }

        function adjustContainerHeight() {
            const inputContainer = document.querySelector('.input-container');
            const chatContainer = document.querySelector('.chat-container');
            const totalHeight = window.innerHeight;
            const inputHeight = inputContainer.offsetHeight;
            chatContainer.style.height = `${totalHeight - inputHeight - 50}px`;
            chatContainer.style.paddingBottom = `${inputHeight + 20}px`;
        }

        function updateChatHistory(searchTerm = '') {
            const chatHistory = document.querySelector('.chat-history');
            chatHistory.innerHTML = '';
            const filteredConversations = conversations
                .sort((a, b) => new Date(b.messages?.slice(-1)[0]?.timestamp || 0) - new Date(a.messages?.slice(-1)[0]?.timestamp || 0))
                .filter(c => !searchTerm || c.messages.some(m => m.parts?.[0]?.text?.toLowerCase().includes(searchTerm)));
            const initialLoad = filteredConversations.slice(0, 20);
            initialLoad.forEach(c => renderHistoryItem(c, chatHistory));
            let loadedCount = initialLoad.length;
            const handleScroll = () => { if (chatHistory.scrollTop + chatHistory.clientHeight >= chatHistory.scrollHeight - 50 && loadedCount < filteredConversations.length) { const nextBatch = filteredConversations.slice(loadedCount, loadedCount + 10); nextBatch.forEach(c => renderHistoryItem(c, chatHistory)); loadedCount += 10; } };
            chatHistory.removeEventListener('scroll', handleScroll);
            chatHistory.addEventListener('scroll', handleScroll);
        }

        function renderHistoryItem(c, chatHistory) {
            if (!c.messages?.length) return;
            const firstUserMessage = c.messages.find(m => m.role === 'user');
            const titleText = firstUserMessage?.parts?.[0]?.text?.slice(0, 30) + (firstUserMessage?.parts?.[0]?.text?.length > 30 ? '...' : '') || '新对话';
            const div = document.createElement('div');
            div.className = `history-item ${c.id === currentConversationId ? 'active' : ''}`;
            div.innerHTML = `<div class="title">${escapeHtml(titleText)}</div><div class="preview">${c.messages.slice(-2).map(m => `<div>${escapeHtml(m.parts?.[0]?.text?.slice(0, 50) || '')}${m.parts?.[0]?.text?.length > 50 ? '...' : ''}</div>`).join('')}</div><div class="time">${new Date(c.messages.slice(-1)[0].timestamp).toLocaleString()}</div>`;
            div.onclick = () => loadConversation(c.id);
            chatHistory.appendChild(div);
        }

        function loadConversation(id) {
            currentConversationId = id;
            localStorage.setItem('currentConversationId', id);
            const conversation = conversations.find(c => c.id === id);
            if (!conversation) return;
            chatMessages.innerHTML = '';
            conversation.messages.forEach(msg => { addMessage(msg.parts.find(part => part.text)?.text || '', msg.role === 'user' ? 'user' : 'ai'); });
            currentContext = conversation.messages.map(msg => ({ role: msg.role, parts: msg.parts.map(part => ({text: part.text})) }));
            updateChatHistory();
            sidebar.classList.remove('active');
            menuToggle.classList.remove('hidden');
            scrollToBottom();
            if (!generation_statuses[currentConversationId]) generation_statuses[currentConversationId] = { generating: false };
        }

        async function addMessage(text, type = 'user') {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);

            let content = text || '（无内容）';
            if (type === 'user') {
                contentDiv.innerText = content;
            } else {
                content = content;
                const markedContent = await marked.parse(content);
                contentDiv.innerHTML = markedContent || '（AI 未返回内容）';
                addCodeActions(contentDiv);
                hljs.highlightAll();
                if (hasMath(content)) {
                     renderMath(contentDiv);
                }
            }
            scrollToBottom();
        }

        function addCodeActions(contentDiv) {
            contentDiv.querySelectorAll('pre code').forEach(block => {
                if (block.parentNode.querySelector('.code-actions')) return;
                const pre = block.parentNode;
                const actions = document.createElement('div');
                actions.className = 'code-actions';
                const isHtml = block.textContent.trim().toLowerCase().startsWith('<!doctype html') || block.textContent.trim().startsWith('<html');
                actions.innerHTML = `<button onclick="copyCode(this)">复制</button>${isHtml ? '<button onclick="previewHTML(this)">预览</button>' : ''}`;
                pre.style.position = 'relative';
                pre.appendChild(actions);
            });
        }

        function copyCode(button) {
            const codeBlock = button.closest('pre').querySelector('code');
            navigator.clipboard.writeText(codeBlock.textContent).then(() => showCopyFeedback(button, '已复制')).catch(() => showCopyFeedback(button, '复制失败'));
        }
        function showCopyFeedback(button, text) { const originalText = button.textContent; button.textContent = text; button.disabled = true; setTimeout(() => { button.textContent = originalText; button.disabled = false; }, 2000); }

        function previewHTML(button) { const code = button.closest('pre').querySelector('code').textContent; htmlPreviewContent.srcdoc = code; htmlPreviewModal.style.display = 'block'; }

        function toggleSettings() { settingsPanel.style.display = settingsPanel.style.display === 'block' ? 'none' : 'block'; apiIpInput.value = localStorage.getItem('apiIp') || ''; apiPortInput.value = localStorage.getItem('apiPort') || ''; }

        function saveSettings() {
            const ip = apiIpInput.value.trim();
            const port = apiPortInput.value.trim();
            if (ip && port) { apiUrl = `http://${ip}:${port}`; localStorage.setItem('apiUrl', apiUrl); localStorage.setItem('apiIp', ip); localStorage.setItem('apiPort', port); } else { apiUrl = Config.DEFAULT_API_URL; localStorage.removeItem('apiUrl'); localStorage.removeItem('apiIp'); localStorage.removeItem('apiPort'); }
            settingsPanel.style.display = 'none';
            fetchModels();
        }

        async function fetchModels() {
            try {
                const response = await fetch('/models', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ api_url: apiUrl }) });
                const data = await response.json();
                modelSelect.innerHTML = '';
                if (data.models) { data.models.forEach(model => { const option = document.createElement('option'); option.value = model; option.text = model; if (model === currentModel) option.selected = true; modelSelect.appendChild(option); }); } else { modelSelect.innerHTML = '<option value="llama3">llama3 (默认)</option>'; }
            } catch (e) { console.error("获取模型列表失败:", e); modelSelect.innerHTML = '<option value="llama3">llama3 (默认)</option>'; addMessage(`无法连接到 Ollama 服务: ${apiUrl}，请检查 API 设置`, 'ai'); }
        }

        function changeModel(model) { currentModel = model; localStorage.setItem('currentModel', currentModel); console.log("当前模型切换为:", currentModel); }

        async function sendMessage() {
            if (!messageInput.value || isGenerating) return;

            startGeneratingState();
            if (eventSource) {
                 if (eventSource.close) {
                    eventSource.close();
                 }
                eventSource = null;
            }

            const message = messageInput.value || "";
            messageInput.value = '';
            adjustInputHeight();

            const userParts = [{"text": message}];
            currentContext.push({ role: 'user', parts: userParts });
            await addMessage(message, 'user');
            const loadingDiv = addLoadingMessage();

            try {
                const endpoint = '/chat';
                const encodedMessage = encodeURIComponent(message || " ");
                const payload = { message: encodedMessage, session_id: currentConversationId, context: currentContext, model: currentModel, api_url: apiUrl };
                console.log("发送请求:", JSON.stringify(payload));
                const response = await fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });

                if (!response.ok) throw new Error(`服务器错误: ${response.status} ${response.statusText}`);

                let accumulatedText = '';
                const aiMessageDiv = document.createElement('div');
                aiMessageDiv.className = 'message ai';
                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                aiMessageDiv.appendChild(contentDiv);
                chatMessages.replaceChild(aiMessageDiv, loadingDiv);

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                eventSource = { close: () => { stopGenerating(); if(reader && reader.cancel) reader.cancel().catch(err => console.error("取消 reader 错误:", err)); eventSource = null; } };

                async function processStream() {
                    isGenerating = true;
                    while (isGenerating) {
                        try {
                            const { done, value } = await reader.read();
                            if (done) {
                                if (!accumulatedText) accumulatedText = '（无回答）';
                                currentContext.push({ role: 'model', parts: [{"text": accumulatedText}] });
                                currentContext = currentContext.slice(-Config.MAX_CONTEXT_LENGTH);
                                saveToHistory(message, accumulatedText);
                                hljs.highlightAll();
                                if (hasMath(accumulatedText)) renderMath(contentDiv);
                                endGeneratingState();
                                eventSource = null;
                                scrollToBottom();
                                return;
                            }
                            const chunk = decoder.decode(value, { stream: true });
                            chunk.split('\n\n').forEach(async line => {
                                if (line.startsWith('data: ')) {
                                    try {
                                        const data = JSON.parse(line.slice(6));
                                        if (data.text) {
                                            accumulatedText = data.text;
                                            contentDiv.innerHTML = await marked.parse(accumulatedText);
                                            addCodeActions(contentDiv);
                                            hljs.highlightAll();
                                            if (hasMath(accumulatedText)) renderMath(contentDiv);
                                            scrollToBottom();
                                        } else if (data.error) { contentDiv.innerHTML = `<span class="error-message">发生错误: ${escapeHtml(data.error)}</span>`; endGeneratingState(); eventSource = null; scrollToBottom(); } else if (data.done) { if (!accumulatedText) accumulatedText = '（无回答）'; currentContext.push({ role: 'model', parts: [{"text": accumulatedText}] }); currentContext = currentContext.slice(-Config.MAX_CONTEXT_LENGTH); saveToHistory(message, accumulatedText); if (hasMath(accumulatedText)) renderMath(contentDiv); endGeneratingState(); eventSource = null; scrollToBottom(); }
                                    } catch (e) { console.error("解析 stream 错误:", e, "原始数据:", line); }
                                }
                            });
                        } catch (streamError) {
                            console.error("Stream reading error:", streamError);
                            reader.cancel().catch(cancelErr => console.error("Error cancelling reader:", cancelErr));
                            addMessage(`发生错误: Stream reading error - ${streamError.message || 'Unknown stream error'}`, 'ai');
                            saveToHistory(message, `[Stream Error: ${streamError.message}]`);
                            endGeneratingState();
                            eventSource = null;
                            scrollToBottom();
                            return;
                        }
                    }
                    if(reader && reader.cancel) reader.cancel();
                    endGeneratingState();
                    eventSource = null;
                    scrollToBottom();
                }
                processStream();
            } catch (error) { console.error("Fetch 错误:", error); chatMessages.removeChild(loadingDiv); addMessage(`发生错误: ${error.message || '未知错误'}`, 'ai'); saveToHistory(message, `[请求错误: ${error.message}]`); endGeneratingState(); eventSource = null; scrollToBottom(); }
        }

        function scrollToBottom() { const scrollOptions = { top: chatMessages.scrollHeight, behavior: 'smooth' }; chatMessages.scrollTop = chatMessages.scrollHeight; requestAnimationFrame(() => chatMessages.scrollTo(scrollOptions)); }

        function stopGenerating() {
            generation_statuses[currentConversationId]["generating"] = false;
            if (eventSource) {
                if (eventSource.close) {
                    eventSource.close();
                }
                eventSource = null;
            }
            isGenerating = false;
            endGeneratingState();
        }

        function startGeneratingState() { isGenerating = true; sendButton.style.display = 'none'; stopButton.style.display = 'inline-block'; }

        function endGeneratingState() { isGenerating = false; sendButton.style.display = 'inline-block'; stopButton.style.display = 'none'; }

        function addLoadingMessage() { const div = document.createElement('div'); div.className = 'message ai'; div.innerHTML = `<div class="message-content"><div class="loading-container"><div class="loading-dots"><span></span><span></span><span></span></div></div></div>`; chatMessages.appendChild(div); scrollToBottom(); return div; }

        function saveToHistory(message, response) {
            let conversation = conversations.find(c => c.id === currentConversationId);
            if (!conversation) { conversation = { id: currentConversationId, messages: [] }; conversations.push(conversation); }
            const userParts = [{"text": message}];
            conversation.messages.push( { role: 'user', parts: userParts, timestamp: new Date().toISOString() }, { role: 'model', parts: [{"text": response}], timestamp: new Date().toISOString() } );
            localStorage.setItem('conversations', JSON.stringify(conversations));
            updateChatHistory();
        }

        function startNewChat() {
            if (isGenerating) stopGenerating();
            currentConversationId = Date.now().toString();
            localStorage.setItem('currentConversationId', currentConversationId);
            chatMessages.innerHTML = '';
            messageInput.placeholder = "输入消息...";
            currentContext = [];
            conversations.push({ id: currentConversationId, messages: [] });
            localStorage.setItem('conversations', JSON.stringify(conversations));
            updateChatHistory();
            sidebar.classList.remove('active');
            menuToggle.classList.remove('hidden');
            endGeneratingState();
            generation_statuses[currentConversationId] = { generating: false };
            adjustContainerHeight();
        }

        function clearHistory() { if (confirm('确定要清除历史记录?')) { if (isGenerating) stopGenerating(); conversations = []; localStorage.setItem('conversations', JSON.stringify(conversations)); startNewChat(); } }

        marked.setOptions({ gfm: true, tables: true, breaks: true, highlight: function(code, lang) { const escapedCode = escapeHtml(code); return lang && hljs.getLanguage(lang) ? hljs.highlight(escapedCode, { language: lang }).value : escapedCode; } });

        document.addEventListener('DOMContentLoaded', () => {
            const savedTheme = localStorage.getItem('theme');
            document.documentElement.setAttribute('data-theme', savedTheme || 'light');
            fetchModels();
            initializeChat();
        });
    </script>
</body>
</html>
''')

def run_app():
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == '__main__':
    run_app()