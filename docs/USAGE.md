# SuperMemorySystemV9 - 使用指南

## 目录

- [快速开始](#快速开始)
- [基础用法](#基础用法)
- [进阶用法](#进阶用法)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)
- [实战案例](#实战案例)

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/zonghui1968/xiaoyao-memory-system.git

# 进入目录
cd xiaoyao-memory-system

# 检查Python版本（需要3.10+）
python --version
```

### 2. 第一个记忆

```python
# 导入
from super_memory_system_v9 import get_sms_v9, MemoryType

# 初始化
sms = get_sms_v9()

# 记录第一个记忆
sms.remember(
    "团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。",
    memory_type=MemoryType.SEMANTIC,
    tags=["认证", "Clerk", "决策"]
)

# Wake-up
wake_result = sms.wake_up("认证")
print(f"找到 {len(wake_result['L1'])} 条关键事实")
```

### 3. 查看系统状态

```python
# 获取状态
status = sms.get_status()

# 打印关键信息
print(f"版本: {status['version']}")
print(f"总记忆数: {status['stats']['total_memories']}")
print(f"关键事实数: {status['stats']['critical_facts']}")
print(f"ER三元组数: {status['stats']['er_triples']}")
```

## 基础用法

### 记录不同类型的记忆

#### 1. 决策类记忆（自动标记为关键事实）

```python
# 技术决策
sms.remember(
    "团队决定使用Postgres而非SQLite，因为需要并发写入支持。",
    memory_type=MemoryType.SEMANTIC,
    tags=["数据库", "Postgres", "决策"]
)
# 自动检测到"决定"，标记为关键事实

# 架构决策
sms.remember(
    "选择Next.js而非React，因为内置SSR和路由。",
    memory_type=MemoryType.SEMANTIC,
    tags=["前端", "Next.js", "架构"]
)
```

#### 2. 事件类记忆

```python
# 调试经历
sms.remember(
    "Kai调试OAuth花了2小时，发现是时区配置错误导致token刷新失败。",
    memory_type=MemoryType.EPISODIC,
    tags=["认证", "调试", "Kai", "时区"]
)

# 会议记录
sms.remember(
    "周一例会讨论了认证方案，最终选择了Clerk。",
    memory_type=MemoryType.EPISODIC,
    tags=["会议", "认证", "Clerk"]
)
```

#### 3. 知识类记忆

```python
# 技术知识
sms.remember(
    "JWT token包含三部分：Header、Payload、Signature。",
    memory_type=MemoryType.SEMANTIC,
    tags=["JWT", "认证", "知识"]
)

# 学习心得
sms.remember(
    "MemPalace系统的核心是原始存储优先，不预先过滤内容。",
    memory_type=MemoryType.SEMANTIC,
    tags=["MemPalace", "记忆系统", "学习"]
)
```

#### 4. 方法流程类记忆

```python
# 操作步骤
sms.remember(
    "OAuth配置步骤：1.创建应用 2.配置回调URL 3.获取Client ID和Secret 4.实现token刷新逻辑",
    memory_type=MemoryType.PROCEDURAL,
    tags=["OAuth", "配置", "流程"]
)

# 调试方法
sms.remember(
    "调试token刷新问题的方法：1.检查时区配置 2.验证过期时间 3.查看网络请求日志",
    memory_type=MemoryType.PROCEDURAL,
    tags=["调试", "token", "方法"]
)
```

#### 5. 偏好类记忆

```python
# 技术偏好
sms.remember(
    "我喜欢使用TypeScript，类型安全让我更自信。",
    memory_type=MemoryType.SEMANTIC,
    tags=["偏好", "TypeScript"]
)

# 工作偏好
sms.remember(
    "我喜欢在早上9点到11点处理复杂任务，因为此时精力最集中。",
    memory_type=MemoryType.SEMANTIC,
    tags=["偏好", "时间管理"]
)
```

### Wake-up机制

```python
# 1. 基础Wake-up（仅L0 + L1，~170 tokens）
wake_result = sms.wake_up()
print(f"Tokens: {wake_result['total_tokens']}")  # ~170

# 2. 带查询的Wake-up（自动触发L2/L3）
wake_result = sms.wake_up("认证")
if wake_result['auto_search_triggered']:
    print(f"搜索已触发")
    if wake_result['L2_results']:
        print(f"L2结果: {len(wake_result['L2_results'])}条")
        for mem in wake_result['L2_results'][:3]:
            print(f"  - {mem['content'][:50]}...")
            print(f"    相似度: {mem['similarity']:.3f}")

# 3. 自定义阈值
wake_result = sms.wake_up(
    query="数据库",
    search_threshold=0.8  # 更严格
)
```

### 知识图谱查询

```python
# 1. 查询实体关系
relations = sms.query_entity_relations("团队", max_depth=1)
print(f"'团队'的关系:")
for entity, rel_list in relations.items():
    for rel in rel_list:
        print(f"  - {rel['relation']} -> {rel['other_entity']}")
        print(f"    置信度: {rel['confidence']:.2f}")

# 2. 深度查询（2层）
relations = sms.query_entity_relations("团队", max_depth=2)

# 3. 检查矛盾
contradictions = sms.check_contradictions()
if contradictions:
    print(f"发现 {len(contradictions)} 个矛盾:")
    for con in contradictions:
        print(f"  - {con['entity1']} {con['relation1']} vs {con['relation2']}")
else:
    print("没有发现矛盾")
```

## 进阶用法

### 1. 自定义Wing和Room

```python
# 指定Wing和Room
sms.remember(
    "使用Vite构建React项目，启动速度快。",
    memory_type=MemoryType.SEMANTIC,
    tags=["前端", "Vite"],
    wing="前端",  # 指定Wing
    room="构建工具"  # 指定Room
)

# 自动创建Wing "前端"，Room "构建工具"
```

### 2. 手动标记关键事实

```python
# 手动标记
sms.remember(
    "这个决策很重要：使用微服务架构。",
    memory_type=MemoryType.SEMANTIC,
    tags=["架构", "微服务"],
    is_critical=True  # 手动标记为关键事实
)

# 自动检测（包含"决定"）
sms.remember(
    "团队决定使用Kubernetes进行容器编排。",
    memory_type=MemoryType.SEMANTIC,
    tags=["架构", "Kubernetes"]
)  # 自动检测为关键事实
```

### 3. 禁用实体提取

```python
# 简单记忆不需要实体提取
sms.remember(
    "今天天气不错。",
    memory_type=MemoryType.EPISODIC,
    tags=["日常"],
    extract_entities=False  # 禁用实体提取
)
```

### 4. 添加元数据

```python
# 添加详细的元数据
sms.remember(
    "修复了token刷新bug。",
    memory_type=MemoryType.EPISODIC,
    tags=["bugfix", "token"],
    metadata={
        "issue_id": "BUG-123",
        "duration": "2小时",
        "severity": "high",
        "assignee": "Kai"
    }
)
```

### 5. 系统监控

```python
# 定期检查系统状态
def monitor_system():
    status = sms.get_status()
    
    print(f"=== 系统状态 ===")
    print(f"版本: {status['version']}")
    print(f"总记忆: {status['stats']['total_memories']}")
    print(f"关键事实: {status['stats']['critical_facts']}")
    print(f"Wake-up调用: {status['stats']['wake_up_calls']}")
    
    # 检查矛盾
    contradictions = sms.check_contradictions()
    if contradictions:
        print(f"\n⚠️  发现 {len(contradictions)} 个矛盾")
    
    # 压缩统计
    if status['stats']['compression_enabled']:
        stats = status['compression_stats']
        print(f"\n压缩统计:")
        print(f"  压缩数量: {stats['total_compressed']}")
        print(f"  空间节省: {stats['space_saved']} bytes")
        print(f"  平均质量: {stats['average_quality_score']:.3f}")

# 每天运行一次
monitor_system()
```

## 最佳实践

### 1. 记忆命名规范

**Tags命名：**
```python
# 推荐：简洁、有层次
tags = ["认证", "OAuth", "token"]  # 层次：分类 -> 子类 -> 具体

# 避免：过于冗长
tags = ["认证系统OAuthToken刷新机制"]  # ❌ 太长
```

**Content撰写：**
```python
# 推荐：简洁、明确、包含关键信息
content = "团队决定使用Clerk而非Auth0，原因：定价更优、API更简洁。"

# 避免：过于啰嗦
content = "经过多次讨论和比较，我们团队最终一致认为应该选择使用Clerk这个认证服务而不是Auth0..."  # ❌ 太长
```

### 2. 关键事实标记

**自动检测场景：**
```python
# ✅ 自动检测（包含决策关键词）
sms.remember("决定使用Postgres。")
sms.remember("选择React而不是Vue。")
sms.remember("确认使用微服务架构。")
```

**手动标记场景：**
```python
# ✅ 手动标记（重要但不包含决策关键词）
sms.remember(
    "这个原则很重要：永远不要在客户端存储secret。",
    is_critical=True
)
```

### 3. Wake-up使用策略

**低频使用（推荐）：**
```python
# 每天启动时使用一次
wake_result = sms.wake_up()
# 成本：~170 tokens
```

**按需使用：**
```python
# 需要回忆特定信息时使用
wake_result = sms.wake_up("认证")
# 自动触发L2/L3搜索
```

### 4. 知识图谱维护

**定期检查矛盾：**
```python
# 每周检查一次
contradictions = sms.check_contradictions()
if contradictions:
    for con in contradictions:
        print(f"矛盾: {con}")
        # 决定哪个记忆更准确
```

**查询实体关系：**
```python
# 了解实体的完整关系网络
relations = sms.query_entity_relations("团队", max_depth=2)
```

### 5. 压缩使用建议

**生产环境（推荐）：**
```python
# 禁用压缩，保证记忆质量
sms = SuperMemorySystemV9(
    default_compression=CompressionLevel.NONE
)
```

**实验/测试环境：**
```python
# 轻度压缩，节省空间
sms = SuperMemorySystemV9(
    default_compression=CompressionLevel.LOW
)
```

## 常见问题

### Q1: Wake-up返回多少tokens？

**A:** 
- 无查询：~170 tokens（L0 + L1）
- 有查询（触发L2）：~170 + L2结果
- 有查询（触发L3）：~170 + L3结果

### Q2: 如何提高检索准确度？

**A:**
1. 使用精准的tags
2. 指定合适的Wing和Room
3. 提高search_threshold（默认0.7）
4. 使用L2精准检索而非L3全局搜索

### Q3: 关键事实太多了怎么办？

**A:**
```python
# L1自动限制为20条
# 可以手动清理
sms.l1_critical_facts = sms.l1_critical_facts[:10]
sms._calculate_l1_tokens()
```

### Q4: 如何处理矛盾？

**A:**
```python
contradictions = sms.check_contradictions()
for con in contradictions:
    # 1. 查看相关记忆
    print(f"矛盾: {con}")
    
    # 2. 决定哪个更准确
    
    # 3. 删除不准确记忆
    # (需要实现删除API)
```

### Q5: 压缩会影响记忆质量吗？

**A:**
- `CompressionLevel.NONE`: 不影响
- `CompressionLevel.LOW`: 轻微影响（~100%质量）
- `CompressionLevel.MEDIUM`: 中等影响（~85%质量）
- `CompressionLevel.HIGH`: 显著影响（~69%质量）

**推荐：生产环境使用NONE**

## 实战案例

### 案例1: 项目决策记录系统

```python
from super_memory_system_v9 import get_sms_v9, MemoryType

# 初始化
sms = get_sms_v9()

# 记录项目决策
decisions = [
    {
        "content": "团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。",
        "tags": ["认证", "Clerk", "决策"],
        "metadata": {"date": "2026-04-13", "team": "前端组"}
    },
    {
        "content": "选择Postgres而非SQLite，因为需要并发写入支持。",
        "tags": ["数据库", "Postgres", "决策"],
        "metadata": {"date": "2026-04-13", "team": "后端组"}
    },
    {
        "content": "采用Next.js而非React，因为内置SSR和路由。",
        "tags": ["前端", "Next.js", "决策"],
        "metadata": {"date": "2026-04-13", "team": "前端组"}
    }
]

for decision in decisions:
    sms.remember(
        decision["content"],
        memory_type=MemoryType.SEMANTIC,
        tags=decision["tags"],
        metadata=decision["metadata"],
        is_critical=True  # 决策都是关键事实
    )

# 查询所有决策
wake_result = sms.wake_up("决策")
print(f"关键决策: {len(wake_result['L1'])}条")

# 查询特定领域的决策
relations = sms.query_entity_relations("团队")
print(f"团队的技术决策:")
for rel in relations['团队']:
    print(f"  - {rel['relation']} {rel['other_entity']}")
```

### 案例2: 技术问题追踪

```python
# 记录调试过程
sms.remember(
    "Kai调试OAuth花了2小时，发现是时区配置错误导致token刷新失败。" +
    "解决方法：统一使用UTC时区。",
    memory_type=MemoryType.EPISODIC,
    tags=["认证", "OAuth", "调试", "时区"],
    metadata={
        "duration": "2小时",
        "issue": "token刷新失败",
        "root_cause": "时区配置错误",
        "solution": "使用UTC时区"
    }
)

# 后续查询
wake_result = sms.wake_up("OAuth 调试")
if wake_result['auto_search_triggered']:
    print("找到相关调试记录:")
    for mem in wake_result['L2_results']:
        print(f"  - {mem['content']}")
        print(f"    相似度: {mem['similarity']:.3f}")
```

### 案例3: 知识库构建

```python
# 构建技术知识库
knowledge = [
    ("JWT包含三部分：Header、Payload、Signature。", ["JWT", "认证"]),
    ("OAuth 2.0有四种授权模式：授权码、隐式、密码、客户端凭证。", ["OAuth", "认证"]),
    ("HTTPS使用TLS加密，端口号443。", ["HTTPS", "安全"]),
    ("RESTful API使用HTTP方法：GET、POST、PUT、DELETE。", ["REST", "API"]),
]

for content, tags in knowledge:
    sms.remember(
        content,
        memory_type=MemoryType.SEMANTIC,
        tags=tags,
        extract_entities=False  # 知识点不需要实体提取
    )

# 查询知识
wake_result = sms.wake_up("认证")
print(f"认证相关知识: {len(wake_result['L1'])}条")
```

### 案例4: 个人偏好管理

```python
# 记录个人偏好
preferences = [
    "我喜欢使用TypeScript，类型安全让我更自信。",
    "我喜欢在早上9点到11点处理复杂任务。",
    "我喜欢简洁的API设计，过于复杂的框架让我困扰。",
    "我喜欢文档清晰的项目，不清楚文档会降低我的效率。",
]

for pref in preferences:
    sms.remember(
        pref,
        memory_type=MemoryType.SEMANTIC,
        tags=["偏好"],
        extract_entities=False
    )

# 查询偏好
wake_result = sms.wake_up("偏好")
print(f"我的偏好: {len(wake_result['L1'])}条")
```

---

**使用指南版本**: v9.5.0
**最后更新**: 2026-04-13
**作者**: 小妖🦊
