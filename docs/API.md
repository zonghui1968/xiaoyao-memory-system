# SuperMemorySystemV9 - API文档

## 目录

- [核心API](#核心api)
- [记忆类型](#记忆类型)
- [枚举类型](#枚举类型)
- [数据结构](#数据结构)
- [使用示例](#使用示例)
- [错误处理](#错误处理)

## 核心API

### `SuperMemorySystemV9`

主系统类，融合所有Phase功能。

#### 初始化

```python
def __init__(
    dimension: int = 1536,
    default_compression: CompressionLevel = CompressionLevel.NONE
)
```

**参数：**
- `dimension` (int): 向量维度，默认1536（适配OpenAI embeddings）
- `default_compression` (CompressionLevel): 默认压缩级别，推荐NONE

**返回：**
- SuperMemorySystemV9实例

**示例：**
```python
from super_memory_system_v9 import SuperMemorySystemV9, CompressionLevel

# 推荐配置（生产环境）
sms = SuperMemorySystemV9(
    dimension=1536,
    default_compression=CompressionLevel.NONE
)
```

---

### `remember(content, memory_type, tags, ...)`

记录记忆（核心API）

**签名：**
```python
def remember(
    self,
    content: str,
    memory_type: MemoryType = MemoryType.SEMANTIC,
    tags: List[str] = None,
    metadata: dict = None,
    wing: str = None,
    room: str = None,
    is_critical: bool = False,
    extract_entities: bool = True,
    compress: bool = True
) -> str
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `content` | str | 必填 | 记忆内容 |
| `memory_type` | MemoryType | SEMANTIC | 记忆类型 |
| `tags` | List[str] | None | 标签列表 |
| `metadata` | dict | None | 元数据 |
| `wing` | str | None | 翼（自动创建） |
| `room` | str | None | 房间（自动提取） |
| `is_critical` | bool | False | 是否为关键事实（自动检测） |
| `extract_entities` | bool | True | 是否提取实体关系 |
| `compress` | bool | True | 是否压缩（关键事实不压缩） |

**返回：**
- `memory_id` (str): 记忆ID，格式：`mem_<timestamp>_<hash>`

**示例：**
```python
# 基础使用
memory_id = sms.remember(
    "团队决定使用Clerk而非Auth0。",
    memory_type=MemoryType.SEMANTIC,
    tags=["认证", "Clerk", "决策"]
)

# 标记为关键事实
memory_id = sms.remember(
    "选择Postgres而非SQLite，因为需要并发写入。",
    memory_type=MemoryType.SEMANTIC,
    tags=["数据库", "Postgres"],
    is_critical=True
)

# 完整配置
memory_id = sms.remember(
    content="Kai调试OAuth花了2小时，发现是时区配置错误。",
    memory_type=MemoryType.EPISODIC,
    tags=["认证", "调试", "Kai"],
    metadata={"duration": "2小时", "issue": "时区配置"},
    wing="OAuth",
    room="调试",
    is_critical=False,
    extract_entities=True,
    compress=True
)
```

---

### `wake_up(query, auto_search, search_threshold)`

Wake-up机制（~170 tokens）

**签名：**
```python
def wake_up(
    self,
    query: str = None,
    auto_search: bool = True,
    search_threshold: float = 0.7
) -> dict
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | str | None | 查询（可选） |
| `auto_search` | bool | True | 是否自动触发L2/L3搜索 |
| `search_threshold` | float | 0.7 | 搜索阈值（0-1） |

**返回：**
```python
{
    'L0': dict,              # 系统身份（~50 tokens）
    'L1': List[str],         # 关键事实（~120 tokens）
    'total_tokens': int,     # 总token数
    'query': str,            # 查询
    'auto_search_triggered': bool,  # 是否触发自动搜索
    'L2_results': List[dict],  # L2搜索结果（如果触发）
    'L3_results': List[dict]   # L3深度搜索结果（如果触发）
}
```

**示例：**
```python
# 无查询唤醒（仅返回L0 + L1）
wake_result = sms.wake_up()
print(f"Total tokens: {wake_result['total_tokens']}")  # ~170

# 带查询唤醒
wake_result = sms.wake_up("认证")
if wake_result['auto_search_triggered']:
    print(f"找到相关记忆:")
    for mem in wake_result['L2_results']:
        print(f"  - {mem['content'][:50]}...")
        print(f"    相似度: {mem['similarity']:.3f}")

# 自定义阈值
wake_result = sms.wake_up(
    query="数据库",
    search_threshold=0.8  # 更严格的阈值
)
```

---

### `query_entity_relations(entity, max_depth)`

查询实体关系

**签名：**
```python
def query_entity_relations(
    self,
    entity: str,
    max_depth: int = 1
) -> Dict[str, List[dict]]
```

**参数：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `entity` | str | 必填 | 实体名称 |
| `max_depth` | int | 1 | 最大深度（1-2） |

**返回：**
```python
{
    'entity': [
        {
            'relation': str,        # 关系
            'other_entity': str,    # 对方实体
            'confidence': float,    # 置信度（0-1）
            'count': int,           # 出现次数
            'first_seen': str,      # 首次出现时间
            'last_seen': str        # 最后出现时间
        },
        ...
    ]
}
```

**示例：**
```python
# 查询团队的关系
relations = sms.query_entity_relations("团队", max_depth=1)
print("'团队'的关系:")
for entity, rel_list in relations.items():
    print(f"  {entity}:")
    for rel in rel_list:
        print(f"    - {rel['relation']} -> {rel['other_entity']}")
        print(f"      置信度: {rel['confidence']:.2f}")
        print(f"      出现次数: {rel['count']}")

# 深度查询（2层）
relations = sms.query_entity_relations("团队", max_depth=2)
```

---

### `check_contradictions()`

检查矛盾

**签名：**
```python
def check_contradictions(self) -> List[dict]
```

**返回：**
```python
[
    {
        'type': str,            # 矛盾类型
        'entity1': str,         # 实体1
        'entity2': str,         # 实体2
        'relation1': str,       # 关系1
        'relation2': str,       # 关系2
        'timestamp1': str,      # 时间戳1
        'timestamp2': str,      # 时间戳2
        'confidence': float     # 置信度
    },
    ...
]
```

**示例：**
```python
# 检查所有矛盾
contradictions = sms.check_contradictions()
print(f"发现 {len(contradictions)} 个矛盾:")
for con in contradictions:
    print(f"\n矛盾:")
    print(f"  实体: {con['entity1']} vs {con['entity2']}")
    print(f"  关系1: {con['relation1']} ({con['timestamp1']})")
    print(f"  关系2: {con['relation2']} ({con['timestamp2']})")
    print(f"  置信度: {con['confidence']:.2f}")
```

---

### `get_status()`

获取系统状态

**签名：**
```python
def get_status(self) -> dict
```

**返回：**
```python
{
    'version': str,                    # 版本号
    'stats': {
        'total_memories': int,         # 总记忆数
        'total_reflections': int,      # 总反思数
        'gravity_sources': int,        # 引力源数
        'diary_entries': int,          # 日记条目数
        'total_wings': int,            # 翼数
        'total_rooms': int,            # 房间数
        'total_tunnels': int,          # 隧道数
        'total_vectors': int,          # 向量数
        'critical_facts': int,         # 关键事实数
        'l0_tokens': int,              # L0 tokens
        'l1_tokens': int,              # L1 tokens
        'wake_up_calls': int,          # Wake-up调用次数
        'er_triples': int,             # ER三元组数
        'unique_entities': int,        # 唯一实体数
        'contradictions': int,         # 矛盾数
        'compressed_memories': int,    # 压缩记忆数
        'compression_enabled': bool    # 压缩是否启用
    },
    'memory_distribution': {
        'episodic': int,
        'semantic': int,
        'procedural': int,
        'temporal': int,
        'reflective': int
    },
    'compression_stats': {
        'total_compressed': int,
        'total_original_bytes': int,
        'total_compressed_bytes': int,
        'overall_compression_ratio': float,
        'average_quality_score': float,
        'space_saved': int
    },
    'timestamp': str
}
```

**示例：**
```python
# 获取系统状态
status = sms.get_status()

print(f"版本: {status['version']}")
print(f"\n统计:")
for key, value in status['stats'].items():
    print(f"  {key}: {value}")

print(f"\n记忆分布:")
for mem_type, count in status['memory_distribution'].items():
    print(f"  {mem_type}: {count}")

print(f"\n压缩统计:")
stats = status['compression_stats']
print(f"  压缩数量: {stats['total_compressed']}")
print(f"  空间节省: {stats['space_saved']} bytes")
print(f"  平均质量: {stats['average_quality_score']:.3f}")
```

---

## 记忆类型

### `MemoryType`

记忆类型枚举。

**值：**

| 值 | 说明 | 自动分类到Hall |
|------|------|---------------|
| `EPISODIC` | 情景记忆（事件） | Facts/Events |
| `SEMANTIC` | 语义记忆（知识） | Discoveries/Preferences |
| `PROCEDURAL` | 程序记忆（方法） | Advice/Discoveries |
| `TEMPORAL` | 时间记忆 | Events |
| `REFLECTIVE` | 反思记忆 | Events/Discoveries |

**示例：**
```python
from super_memory_system_v9 import MemoryType

# 情景记忆
sms.remember(
    "Kai调试OAuth花了2小时。",
    memory_type=MemoryType.EPISODIC
)

# 语义记忆
sms.remember(
    "团队决定使用Clerk。",
    memory_type=MemoryType.SEMANTIC
)

# 程序记忆
sms.remember(
    "OAuth配置步骤：1.创建应用 2.配置回调 3.获取token",
    memory_type=MemoryType.PROCEDURAL
)
```

---

## 枚举类型

### `HallType`

记忆厅类型（MemPalace设计）。

**值：**
- `FACTS`: 事实（决策类）
- `EVENTS`: 事件（时间线）
- `DISCOVERIES`: 发现（学习心得）
- `PREFERENCES`: 偏好（个人喜好）
- `ADVICE`: 建议（方法流程）

### `CompressionLevel`

压缩级别（实验性功能）。

**值：**
- `NONE`: 不压缩（推荐）
- `LOW`: 轻度压缩（~20% reduction）
- `MEDIUM`: 中度压缩（~50% reduction）
- `HIGH`: 高度压缩（~80% reduction）
- `EXTREME`: 极限压缩（~95% reduction）

---

## 数据结构

### `TemporalERTriple`

时序实体关系三元组。

**字段：**
```python
@dataclass
class TemporalERTriple:
    entity1: str          # 实体1
    relation: str         # 关系
    entity2: str          # 实体2
    timestamp: str        # 时间戳
    source_memory_id: str # 来源记忆ID
    confidence: float     # 置信度（0-1）
```

**示例：**
```python
triple = TemporalERTriple(
    entity1="团队",
    relation="决定使用",
    entity2="Clerk",
    timestamp="2026-04-13",
    source_memory_id="mem_1234567890_1234",
    confidence=0.9
)
```

---

## 使用示例

### 完整工作流

```python
from super_memory_system_v9 import get_sms_v9, MemoryType

# 初始化
sms = get_sms_v9()

# 1. 记录记忆
sms.remember(
    "团队决定使用Clerk而非Auth0，因为定价和开发者体验更好。",
    memory_type=MemoryType.SEMANTIC,
    tags=["认证", "Clerk", "决策"],
    is_critical=True
)

sms.remember(
    "Kai调试OAuth花了2小时，发现是时区配置错误。",
    memory_type=MemoryType.EPISODIC,
    tags=["认证", "调试", "Kai"]
)

sms.remember(
    "我喜欢使用TypeScript，类型安全让我更自信。",
    memory_type=MemoryType.SEMANTIC,
    tags=["偏好", "TypeScript"]
)

# 2. Wake-up
wake_result = sms.wake_up("认证")
print(f"Wake-up tokens: {wake_result['total_tokens']}")

# 3. 查询实体关系
relations = sms.query_entity_relations("团队")
print(f"'团队'的关系: {relations}")

# 4. 检查矛盾
contradictions = sms.check_contradictions()
print(f"矛盾数量: {len(contradictions)}")

# 5. 系统状态
status = sms.get_status()
print(f"系统版本: {status['version']}")
print(f"总记忆数: {status['stats']['total_memories']}")
```

---

## 错误处理

### 常见错误

**1. 记忆内容为空**
```python
# 错误
sms.remember("", MemoryType.SEMANTIC)

# 正确
sms.remember("有效内容", MemoryType.SEMANTIC)
```

**2. 无效的压缩级别**
```python
# 错误
sms = SuperMemorySystemV9(default_compression="invalid")

# 正确
from super_memory_system_v9 import CompressionLevel
sms = SuperMemorySystemV9(default_compression=CompressionLevel.NONE)
```

**3. 实体不存在**
```python
# 查询不存在的实体
relations = sms.query_entity_relations("不存在的实体")
# 返回空字典: {}
```

### 异常处理

```python
try:
    memory_id = sms.remember(
        content="测试内容",
        memory_type=MemoryType.SEMANTIC
    )
    print(f"成功记录: {memory_id}")
except Exception as e:
    print(f"记录失败: {e}")
    # 处理错误
```

---

**API文档版本**: v9.5.0
**最后更新**: 2026-04-13
**作者**: 小妖🦊
