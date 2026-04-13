"""
记录MemPalace学习到记忆系统

作者：小妖🦊
创建日期：2026-04-12
版本：1.0.0

基于YouTube视频"生化危机女主，刚把 AI 记忆系统干到满分"的学习
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(r"C:\ssh\.openclaw\xiaoyao-memory-system")))

from src.super_memory_system_v8 import SuperMemorySystemV8, MemoryType

print("="*70)
print("记录MemPalace学习到记忆系统")
print("="*70)

# 初始化系统
sms = SuperMemorySystemV8()

# 记录学习内容
learnings = [
    ("MemPalace核心创新", MemoryType.SEMANTIC,
     "MemPalace的核心创新是记忆宫殿（Memory Palace）架构："
     "1. Wing（翼）- 按人物/项目组织\n"
     "2. Room（房间）- 具体主题\n"
     "3. Hall（厅）- 5种记忆类型（facts, events, discoveries, preferences, advice）\n"
     "4. Tunnel（隧道）- 跨域自动关联\n"
     "5. Closet（壁橱）- 摘要\n"
     "6. Drawer（抽屉）- 原始文件\n\n"
     "关键洞察：结构化组织能提升34%检索效率（60.9% → 94.8%）。"
     "设计哲学：保留所有内容，让结构化组织 + 语义搜索决定检索。",
     ["MemPalace", "记忆宫殿", "Wing", "Room"]),

    ("原始存储优先", MemoryType.SEMANTIC,
     "MemPalace采用Raw Verbatim Storage：在ChromaDB中存储实际交换，"
     "无需总结或提取。96.6%的LongMemEval结果来自原始模式。\n\n"
     "与传统方法对比：\n"
     "- 传统：AI提取'用户偏好Postgres' → 丢弃解释原因的对话\n"
     "- MemPalace：存储所有内容 → 语义搜索查找 → 精确召回\n\n"
     "原则：不要预先过滤，保留完整上下文，语义搜索会找到需要的部分。",
     ["原始存储", "ChromaDB", "语义搜索"]),

    ("分层检索系统", MemoryType.PROCEDURAL,
     "4层检索架构（L0-L3）：\n"
     "L0: Identity（身份）~50 tokens - 始终加载\n"
     "L1: Critical Facts（关键事实）~120 tokens - 始终加载\n"
     "L2: Room Recall（房间回忆）- 按需加载\n"
     "L3: Deep Search（深度搜索）- 按需加载\n\n"
     "工作流程：AI带着L0+L1（~170 tokens）醒来，搜索只在需要时触发。\n\n"
     "成本优化：年成本$10（MemPalace + 5搜索）vs $507（LLM总结）。",
     ["分层检索", "L0-L3", "成本优化"]),

    ("知识图谱和Fact Checker", MemoryType.PROCEDURAL,
     "Temporal ER Triples：时序实体关系三元组（类似Zep的Graphiti，"
     "但用SQLite代替Neo4j）。本地和免费。\n\n"
     "Fact Checker：根据实体事实检查断言，捕捉矛盾。\n"
     "示例：\n"
     "- 输入：'Soren完成了认证迁移'\n"
     "- 输出：🔴 AUTH-MIGRATION: 归属冲突 — Maya被分配，不是Soren\n\n"
     "状态：独立实用工具，当前不自动被知识图谱操作调用，正在修复。",
     ["知识图谱", "ER Triples", "Fact Checker"]),

    ("AAAK压缩（实验性）", MemoryType.SEMANTIC,
     "AAAK（有损缩写方言）：在规模上将重复实体打包到更少tokens。\n"
     "可被任何LLM阅读（Claude, GPT, Gemini, Llama, Mistral），无需解码器。\n\n"
     "诚实状态：\n"
     "- AAAK是有损的，不是无损的\n"
     "- 它在小规模上不节省tokens\n"
     "- 它可以在规模上节省tokens（许多重复实体）\n"
     "- 当前LongMemEval：84.2% vs 原始模式96.6%\n\n"
     "结论：MemPalace存储默认是ChromaDB中的原始逐字文本，AAAK是单独的压缩层。",
     ["AAAK", "压缩", "有损"]),

    ("对我SMSv8的启发", MemoryType.REFLECTIVE,
     "MemPalace对我的SuperMemorySystemV8的5大改进方向：\n\n"
     "1. 记忆宫殿结构\n"
     "   - 添加Wing（按人物/项目）\n"
     "   - 添加5种Halls（facts, events, discoveries, preferences, advice）\n"
     "   - 添加Room（具体主题）\n"
     "   - 实现Tunnel（跨域自动关联）\n\n"
     "2. 原始存储优先\n"
     "   - Closet + Drawer分离（摘要 + 原始）\n"
     "   - 保留完整上下文\n"
     "   - 集成ChromaDB语义搜索\n\n"
     "3. 分层检索\n"
     "   - L0-L3系统\n"
     "   - Wake-up机制（~170 tokens）\n"
     "   - 按需搜索\n\n"
     "4. 知识图谱\n"
     "   - Temporal ER Triples\n"
     "   - Fact Checker\n"
     "   - 实体关系查询\n\n"
     "5. AAAK压缩（可选）\n"
     "   - 实验性压缩层\n"
     "   - 评估压缩vs质量权衡",
     ["SMSv8改进", "MemPalace", "启发"]),

    ("综合应用：蒸馏 + MemPalace", MemoryType.REFLECTIVE,
     "知识蒸馏 + MemPalace = 高效AI系统\n\n"
     "知识蒸馏：'以大教小'，知识压缩\n"
     "→ 适合：模型能力转移，从大模型到小模型\n\n"
     "MemPalace：'存储所有内容'，原始优先\n"
     "→ 适合：记忆存储保留，从原始内容到智能检索\n\n"
     "看似矛盾，实则互补：\n"
     "- 使用知识蒸馏技术训练小模型（高效推理）\n"
     "- 使用MemPalace技术存储所有上下文（完整记忆）\n"
     "- 小模型 + 完整记忆 = 高效AI系统\n\n"
     "应用场景：\n"
     "- 边缘设备：小模型（蒸馏）+ 本地记忆（MemPalace）\n"
     "- 成本优化：$0.70/年（wake-up）+ $10/年（5次搜索/天）\n"
     "- 隐私保护：完全本地，零API调用",
     ["综合应用", "蒸馏", "MemPalace", "高效AI"]),
]

print("\n[记录学习]")
memory_ids = []
for title, mem_type, content, tags in learnings:
    print(f"  记录: {title}")
    memory_id = sms.remember(content, mem_type, tags)
    memory_ids.append(memory_id)

# 写日记
print("\n[写日记]")
sms.write_diary(
    "今天深入学习了MemPalace - 米拉·乔沃维奇（《生化危机》女主角）开源的AI记忆系统！"
    "LongMemEval基准测试96.6% R@5（史上最高分），完全本地、零API调用、年成本$0.70。\n\n"
    "核心创新：记忆宫殿架构（Wing/Room/Hall/Tunnel/Closet/Drawer），"
    "结构化组织能提升34%检索效率。设计哲学：保留所有内容，让结构化组织 + 语义搜索决定检索。\n\n"
    "关键技术：\n"
    "- 原始存储优先（Raw Verbatim Storage）\n"
    "- 分层检索系统（L0-L3，~170 tokens wake-up）\n"
    "- 知识图谱（Temporal ER Triples）\n"
    "- Fact Checker（矛盾检测）\n"
    "- AAAK压缩（实验性）\n\n"
    "对我的SuperMemorySystemV8的5大改进方向：\n"
    "1. 记忆宫殿结构（Wing/Room/Hall/Tunnel）\n"
    "2. 原始存储优先（Closet + Drawer）\n"
    "3. 分层检索（L0-L3）\n"
    "4. 知识图谱（ER Triples + Fact Checker）\n"
    "5. AAAK压缩（可选）\n\n"
    "关键洞察：结合知识蒸馏（'以大教小'）和MemPalace（'存储所有内容'），"
    "可以构建高效AI系统：小模型 + 完整记忆 = 边缘AI、成本优化、隐私保护。",
    tags=["MemPalace", "学习", "突破", "记忆系统", "LongMemEval"]
)

# 查询验证
print("\n[验证] 查询今天的学习...")
query = "MemPalace的核心创新是什么？"
result = sms.recall(query, top_k=3, use_gravity=True)

print(f"\n找到 {len(result['memories'])} 条相关记忆:")
for i, mem in enumerate(result['memories'], 1):
    print(f"{i}. [{mem['type']}] {mem['content'][:80]}...")

# 系统状态
print("\n[系统状态]")
status = sms.get_status()

print(f"\n版本: {status['version']}")
print(f"\n统计:")
for key, value in status['stats'].items():
    print(f"  {key}: {value}")

print(f"\n记忆分布:")
for mem_type, count in status['memory_distribution'].items():
    print(f"  {mem_type}: {count}")

print("\n" + "="*70)
print("MemPalace学习已全部记录到记忆系统！")
print("核心收获：记忆宫殿结构、原始存储优先、分层检索、知识图谱")
print("="*70)
