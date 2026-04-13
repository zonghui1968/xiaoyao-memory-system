# 小妖的AI记忆系统 - 实际应用指南

## 🚀 快速开始

### 1. 初始化

```python
from xiaoyao_memory_system import get_xiaoyao_memory

# 初始化小妖的记忆系统
xiaoyao = get_xiaoyao_memory()

# 查看状态
status = xiaoyao.get_status()
print(f"总记忆数: {status['stats']['total_memories']}")
```

### 2. 第一次使用

```python
# 记录一个决策
xiaoyao.record_decision(
    "团队决定使用Clerk认证系统",
    context="定价更优，API更简洁",
    tags=["认证", "Clerk"]
)

# Wake-up测试
wake_result = xiaoyao.wake_up("决策")
print(f"Wake-up tokens: {wake_result['total_tokens']}")
```

## 📋 日常使用场景

### 场景1: 记录项目决策

**适合时间：** 决策会议后、技术选型时

```python
# 技术选型决策
xiaoyao.record_decision(
    decision="选择Postgres作为主数据库",
    context="需要支持高并发写入，SQLite的锁机制成为瓶颈。Postgres支持多连接并发写入。",
    tags=["数据库", "Postgres", "决策"]
)

# 架构决策
xiaoyao.record_decision(
    decision="采用微服务架构",
    context="团队规模扩大后，单体架构难以维护。微服务可以提高开发效率。",
    tags=["架构", "微服务", "决策"]
)
```

### 场景2: 记录会议内容

**适合时间：** 会议结束后

```python
# 项目会议
xiaoyao.record_meeting(
    title="周一例会 - 认证方案讨论",
    content="讨论了认证系统的技术选型。Kai介绍了Clerk的优势，包括定价、API设计、文档质量。团队一致同意使用Clerk。",
    attendees=["宗晖", "Kai", "小邪"],
    tags=["认证", "会议"]
)

# 技术分享会
xiaoyao.record_meeting(
    title="技术分享 - MemPalace记忆系统",
    content="Kai分享了MemPalace系统的设计理念：1.原始存储优先 2.分层检索 3.记忆宫殿架构。LongMemEval得分96.6% R@5。",
    attendees=["宗晖", "Kai", "探路"],
    tags=["MemPalace", "学习", "分享"]
)
```

### 场景3: 记录调试经历

**适合时间：** 解决bug后

```python
# 记录调试过程
xiaoyao.record_debugging(
    issue="OAuth token刷新失败",
    solution="发现是时区配置错误。服务器使用UTC时间，客户端使用本地时间，导致token过期判断错误。统一使用UTC时间后解决。",
    duration="2小时",
    tags=["OAuth", "调试", "时区"]
)

# 记录性能优化
xiaoyao.record_debugging(
    issue="数据库查询慢",
    solution="添加了合适的索引后，查询时间从5秒降低到200ms。关键是在user_id和created_at字段上添加复合索引。",
    duration="1小时",
    tags=["数据库", "性能", "优化"]
)
```

### 场景4: 记录学习内容

**适合时间：** 学习新技术、阅读文章后

```python
# 学习新技术
xiaoyao.record_learning(
    topic="Next.js 14新特性",
    content="1. Server Actions - 可以在服务器端直接执行mutations 2. Partial Prerendering - 部分预渲染 3. Turbopack - 更快的构建工具",
    source="Next.js官方文档",
    tags=["Next.js", "React", "前端"]
)

# 阅读文章
xiaoyao.record_learning(
    topic="MemPalace记忆系统",
    content="核心创新：原始存储优先（不预先过滤）、分层检索（L0-L3）、记忆宫殿架构（Wing/Room/Hall）。LongMemEval 96.6% R@5。",
    source="https://github.com/MemPalace/mempalace",
    tags=["MemPalace", "记忆系统", "AI"]
)
```

### 场景5: 记录技术方法

**适合时间：** 学到新的技术方法时

```python
# 记录技术方法
xiaoyao.record_technique(
    name="OAuth 2.0授权码流程",
    description="1. 用户访问客户端，重定向到认证服务器 2. 用户登录并授权 3. 认证服务器返回授权码 4. 客户端用授权码换取access token 5. 使用token访问API",
    category="认证",
    tags=["OAuth", "认证", "安全"]
)

# 记录最佳实践
xiaoyao.record_technique(
    name="数据库索引最佳实践",
    description="1. 为WHERE、JOIN、ORDER BY字段创建索引 2. 避免过度索引 3. 使用复合索引时考虑字段顺序 4. 定期分析慢查询日志",
    category="数据库",
    tags=["数据库", "索引", "性能"]
)
```

### 场景6: 记录个人偏好

**适合时间：** 发现自己的偏好时

```python
# 技术偏好
xiaoyao.record_preference(
    preference="我喜欢使用TypeScript，类型安全让我更自信。",
    category="技术偏好"
)

# 工作偏好
xiaoyao.record_preference(
    preference="我喜欢在早上9点到11点处理复杂任务，因为此时精力最集中。",
    category="工作习惯"
)

# 工具偏好
xiaoyao.record_preference(
    preference="我喜欢简洁的API设计，过于复杂的框架让我困扰。Clerk比Auth0更符合我的偏好。",
    category="工具选择"
)
```

### 场景7: 记录目标

**适合时间：** 设定新目标时

```python
# 学习目标
xiaoyao.record_goal(
    goal="3个月内掌握MemPalace记忆系统的设计理念，并实现SuperMemorySystemV9",
    deadline="2026-07-13",
    tags=["学习", "MemPalace", "目标"]
)

# 工作目标
xiaoyao.record_goal(
    goal="Q2完成3个项目的认证系统迁移到Clerk",
    deadline="2026-06-30",
    tags=["工作", "Clerk", "目标"]
)
```

### 场景8: 记录反思

**适合时间：** 每周回顾、项目总结

```python
# 每周反思
xiaoyao.record_reflection(
    reflection="本周在OAuth调试上花了太多时间。应该更仔细地阅读文档，特别是时区配置部分。",
    context="调试OAuth token刷新问题花了2小时",
    tags=["反思", "时间管理"]
)

# 项目反思
xiaoyao.record_reflection(
    reflection="MemPalace项目的实施让我深刻理解了'原始存储优先'的价值。以前我总是想着如何压缩和提取信息，但保留完整内容反而更重要。",
    context="完成SuperMemorySystemV9 Phase 1-5",
    tags=["反思", "MemPalace", "项目"]
)
```

## 🔍 查询和检索

### Wake-up（推荐每天使用）

```python
# 每天启动时使用
wake_result = xiaoyao.wake_up()

# 查看关键信息
print(f"关键事实数: {len(wake_result['L1'])}")
print(f"总tokens: {wake_result['total_tokens']}")

# 带查询的Wake-up
wake_result = xiaoyao.wake_up("认证")
if wake_result['auto_search_triggered']:
    print("找到相关记忆:")
    for mem in wake_result.get('L2_results', []):
        print(f"  - {mem['content'][:60]}...")
```

### 分类搜索

```python
# 搜索工作记忆
work_result = xiaoyao.search_work("决策")
print(f"工作记忆: {work_result['count']}条")

# 搜索学习记忆
learning_result = xiaoyao.search_learning("MemPalace")
print(f"学习记忆: {learning_result['count']}条")

# 搜索个人记忆
personal_result = xiaoyao.search_personal("偏好")
print(f"个人记忆: {personal_result['count']}条")
```

### 检查矛盾

```python
# 定期检查（每周一次）
contradictions = xiaoyao.check_contradictions()

if contradictions:
    print(f"⚠️  发现 {len(contradictions)} 个矛盾:")
    for con in contradictions:
        print(f"\n矛盾:")
        print(f"  实体: {con['entity1']} vs {con['entity2']}")
        print(f"  关系1: {con['relation1']} ({con['timestamp1']})")
        print(f"  关系2: {con['relation2']} ({con['timestamp2']})")
        print(f"  置信度: {con['confidence']:.2f}")
else:
    print("✅ 没有发现矛盾")
```

## 📊 定期维护

### 每日总结

```python
# 每天晚上生成
summary = xiaoyao.daily_summary()
print(summary)
```

### 导出记忆

```python
# 每周导出一次
export_path = xiaoyao.export_memories()
print(f"已导出到: {export_path}")
```

### 系统状态检查

```python
# 每周检查一次
status = xiaoyao.get_status()

print(f"=== 系统状态 ===")
print(f"版本: {status['version']}")
print(f"总记忆: {status['stats']['total_memories']}")
print(f"关键事实: {status['stats']['critical_facts']}")
print(f"Wake-up调用: {status['stats']['wake_up_calls']}")

print(f"\n记忆分布:")
for mem_type, count in status['memory_distribution'].items():
    print(f"  {mem_type}: {count}")
```

## 💡 使用技巧

### 1. Tags命名规范

```python
# 推荐：简洁、有层次
tags = ["认证", "OAuth", "token"]  # 分类 -> 子类 -> 具体

# 避免：过于冗长
tags = ["认证系统OAuthToken刷新机制"]  # ❌
```

### 2. Content撰写技巧

```python
# 推荐：简洁、明确、包含关键信息
content = "团队决定使用Clerk而非Auth0，原因：定价更优、API更简洁。"

# 避免：过于啰嗦
content = "经过多次讨论和比较，我们团队最终一致认为..."  # ❌
```

### 3. 合理使用Wing和Room

```python
# 工作相关
xiaoyao.record_decision(...)  # 自动归类到"工作" Wing

# 学习相关
xiaoyao.record_learning(...)  # 自动归类到"学习" Wing

# 个人相关
xiaoyao.record_preference(...)  # 自动归类到"个人" Wing
```

### 4. 关键事实自动标记

```python
# 包含"决定"自动标记为关键事实
xiaoyao.record_decision("决定使用Postgres")

# 手动标记
xiaoyao.sms.remember(
    "这个原则很重要：永远不要在客户端存储secret。",
    is_critical=True
)
```

## 🎯 实战案例

### 案例1: 项目启动阶段

```python
# 记录项目决策
xiaoyao.record_decision(
    "新项目使用Next.js + TypeScript + TailwindCSS",
    context="团队熟悉度高，开发效率快",
    tags=["前端", "Next.js", "决策"]
)

xiaoyao.record_decision(
    "认证系统使用Clerk",
    context="定价和开发者体验优于Auth0",
    tags=["认证", "Clerk", "决策"]
)

# 记录会议
xiaoyao.record_meeting(
    "项目启动会",
    "讨论了技术栈和开发计划。决定采用Next.js和Clerk。",
    ["宗晖", "Kai", "小邪"],
    ["项目", "启动"]
)

# 设定目标
xiaoyao.record_goal(
    "2个月内完成MVP",
    "2026-06-13",
    ["项目", "目标"]
)
```

### 案例2: 技术问题解决

```python
# 遇到问题
xiaoyao.record_debugging(
    "Next.js SSR页面报错",
    "发现是getServerSideProps中使用了客户端API。解决方法：移到客户端组件或使用API routes。",
    "30分钟",
    ["Next.js", "SSR", "调试"]
)

# 记录学到的经验
xiaoyao.record_learning(
    "Next.js SSR限制",
    "getServerSideProps只能在服务器端运行，不能使用浏览器API。客户端交互应该使用useState等hooks。",
    "调试经验",
    ["Next.js", "SSR", "学习"]
)
```

### 案例3: 知识积累

```python
# 学习新技术
xiaoyao.record_learning(
    "MemPalace记忆系统",
    "核心创新：1.原始存储优先 2.分层检索 3.记忆宫殿架构。LongMemEval 96.6% R@5。",
    "https://github.com/MemPalace/mempalace",
    ["MemPalace", "记忆系统", "AI"]
)

# 记录技术方法
xiaoyao.record_technique(
    "OAuth授权码流程",
    "1.重定向到认证服务器 2.用户登录 3.获取授权码 4.换取token 5.访问API",
    "认证",
    ["OAuth", "认证"]
)

# 记录最佳实践
xiaoyao.record_learning(
    "数据库索引最佳实践",
    "1.为WHERE、JOIN字段创建索引 2.避免过度索引 3.使用复合索引 4.分析慢查询",
    "性能优化经验",
    ["数据库", "索引", "性能"]
)
```

## 🔧 高级用法

### 自定义Wing和Room

```python
# 使用默认API
memory_id = xiaoyao.sms.remember(
    "自定义Wing和Room",
    memory_type=MemoryType.SEMANTIC,
    tags=["测试"],
    wing="自定义Wing",
    room="自定义Room"
)
```

### 批量导入

```python
# 从文件导入
decisions = [
    ("决策1", "背景1"),
    ("决策2", "背景2"),
    ("决策3", "背景3"),
]

for decision, context in decisions:
    xiaoyao.record_decision(decision, context)
```

### 与其他工具集成

```python
# 与日记系统集成
xiaoyao.record_reflection(
    "今天的反思...",
    tags=["日记", "反思"]
)

# 与任务系统集成
xiaoyao.record_task(
    "完成SuperMemorySystemV9文档",
    status="in_progress",
    tags=["任务", "文档"]
)
```

## ⚠️ 注意事项

### 1. Token使用

- Wake-up成本：~170 tokens（L0 + L1）
- 有查询时会额外消耗L2/L3结果
- 建议每天使用1-2次Wake-up

### 2. 记忆质量

- 推荐：简洁、明确、包含关键信息
- 避免：过于冗长或过于简略
- Tags：简洁、有层次

### 3. 定期维护

- 每天生成每日总结
- 每周导出记忆备份
- 每周检查矛盾

### 4. 压缩设置

- 默认：禁用压缩（推荐）
- 生产环境：不要启用压缩
- 测试环境：可以尝试轻度压缩

## 📞 获取帮助

```python
# 查看系统状态
status = xiaoyao.get_status()
print(status)

# 查看帮助
help(xiaoyao.record_decision)
help(xiaoyao.wake_up)
help(xiaoyao.search_work)
```

---

**应用指南版本**: 1.0.0
**最后更新**: 2026-04-13
**作者**: 小妖🦊
