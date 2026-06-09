"""
Flask Web API for SuperMemorySystemV9

提供REST API访问AI记忆系统。

启动:
    python web/app.py
    # 默认在 http://localhost:5000 启动

API端点:
    GET  /api/health          - 健康检查
    POST /api/remember        - 记录记忆
    GET  /api/wakeup          - Wake-up
    GET  /api/status          - 系统状态
    GET  /api/search          - 搜索记忆
    GET  /api/contradictions  - 检查矛盾
"""

import sys
import json
import logging
from pathlib import Path

# 设置路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from super_memory_system_v9 import (
    SuperMemorySystemV9,
    MemoryType,
    CompressionLevel,
    get_sms_v9,
)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化应用
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)

# 初始化记忆系统
sms = get_sms_v9()
logger.info("SuperMemorySystemV9 initialized (v%s)", sms.version)


# =============================================================================
# 辅助函数
# =============================================================================

def _json_response(data, status=200):
    """返回JSON响应"""
    return jsonify(data), status


def _error_response(message, status=400):
    """返回错误响应"""
    return jsonify({"error": True, "message": message}), status


# =============================================================================
# API端点
# =============================================================================

@app.route("/api/health")
def api_health():
    """健康检查"""
    return _json_response({
        "status": "ok",
        "version": sms.version,
        "stats": sms.get_status()["stats"],
    })


@app.route("/api/remember", methods=["POST"])
def api_remember():
    """记录记忆

    JSON Body:
        content (str, required): 记忆内容
        memory_type (str, optional): 记忆类型 (episodic/semantic/procedural/temporal/reflective)
        tags (list, optional): 标签列表
        is_critical (bool, optional): 是否关键事实
    """
    try:
        data = request.get_json(force=True)
    except Exception:
        return _error_response("Invalid JSON body")

    content = data.get("content", "").strip()
    if not content:
        return _error_response("content is required")

    # 解析记忆类型
    mem_type_str = data.get("memory_type", "semantic")
    try:
        mem_type = MemoryType(mem_type_str)
    except ValueError:
        valid = [m.value for m in MemoryType]
        return _error_response(f"Invalid memory_type. Must be one of: {valid}")

    tags = data.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    is_critical = data.get("is_critical", False)

    try:
        memory_id = sms.remember(
            content=content,
            memory_type=mem_type,
            tags=tags,
            is_critical=is_critical,
        )
        logger.info("Memory recorded: %s", memory_id)
        return _json_response({"memory_id": memory_id, "ok": True}, 201)
    except Exception as e:
        logger.error("Failed to record memory: %s", e)
        return _error_response(str(e), 500)


@app.route("/api/wakeup")
def api_wakeup():
    """Wake-up记忆

    Query params:
        query (str, optional): 查询关键词
    """
    query = request.args.get("query", "")
    try:
        result = sms.wake_up(query if query else None)
        return _json_response(result)
    except Exception as e:
        logger.error("Wake-up failed: %s", e)
        return _error_response(str(e), 500)


@app.route("/api/status")
def api_status():
    """获取系统状态"""
    return _json_response(sms.get_status())


@app.route("/api/search")
def api_search():
    """搜索记忆

    Query params:
        q (str, required): 搜索查询
        wing (str, optional): 按Wing过滤
        top_k (int, optional): 返回数量 (默认5)
    """
    query = request.args.get("q", "").strip()
    if not query:
        return _error_response("q parameter is required")

    wing = request.args.get("wing")
    top_k = int(request.args.get("top_k", 5))

    try:
        if wing:
            result = sms.recall_l2_room(query, wing=wing, top_k=top_k)
        else:
            result = sms.recall_l3_deep(query, top_k=top_k)
        return _json_response(result)
    except Exception as e:
        logger.error("Search failed: %s", e)
        return _error_response(str(e), 500)


@app.route("/api/contradictions")
def api_contradictions():
    """检查矛盾"""
    try:
        contradictions = sms.check_contradictions()
        return _json_response({
            "count": len(contradictions),
            "contradictions": contradictions,
        })
    except Exception as e:
        logger.error("Contradiction check failed: %s", e)
        return _error_response(str(e), 500)


@app.route("/api/memories")
def api_memories():
    """列出最近记忆

    Query params:
        limit (int, optional): 返回数量 (默认20)
        offset (int, optional): 偏移量 (默认0)
    """
    limit = int(request.args.get("limit", 20))
    offset = int(request.args.get("offset", 0))

    memories = list(sms.memories.values())
    memories.sort(key=lambda m: m.get("created_at", ""), reverse=True)
    page = memories[offset:offset + limit]

    return _json_response({
        "total": len(memories),
        "offset": offset,
        "limit": limit,
        "memories": page,
    })


# =============================================================================
# 静态文件服务
# =============================================================================

@app.route("/")
def index():
    """主页"""
    return send_from_directory(".", "index.html")


@app.route("/feedback")
def feedback():
    """反馈页面"""
    return send_from_directory(".", "feedback.html")


# =============================================================================
# 启动
# =============================================================================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SuperMemorySystemV9 Web API")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port (default: 5000)")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f" SuperMemorySystemV9 Web API")
    print(f" Version: {sms.version}")
    print(f" Listening: http://{args.host}:{args.port}")
    print(f"{'='*60}\n")

    app.run(host=args.host, port=args.port, debug=args.debug)
