# 故障排除指南 (Troubleshooting)

## 常见问题

### 导入错误

**问题**: `ModuleNotFoundError: No module named 'super_memory_system_v9'`

**解决**: 确保src目录在PYTHONPATH中：
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))
```

或安装为包：
```bash
pip install -e .
```

### LanceDB连接失败

**问题**: `lancedb not installed` 或连接错误

**解决**: 
1. 确保安装了lancedb: `pip install lancedb pyarrow`
2. 系统会自动回退到SimpleVectorStore（MD5哈希），功能不受影响
3. 检查数据目录权限: `data/lancedb_store/`

### Wake-up返回空结果

**问题**: `wake_up()` 返回的L2/L3结果为空

**可能原因**:
1. 没有记录任何记忆 — 先调用 `remember()`
2. 搜索阈值太高 — 降低 `search_threshold` 参数
3. 向量维度不匹配 — 检查 `dimension` 参数

### 记忆丢失

**问题**: 之前记录的记忆不见了

**说明**: 
- 当前版本使用内存存储，重启后记忆会丢失
- 长期记忆需要配置LanceDB持久化
- 使用 `export_memories()` 导出备份

## 性能优化

### 减少Wake-up token消耗

```python
# 不触发自动搜索
result = sms.wake_up(query=None, auto_search=False)

# 提高搜索阈值减少结果
result = sms.wake_up("关键词", search_threshold=0.9)
```

### 大批量记忆导入

```python
# 关闭实体提取以提高速度
for item in items:
    sms.remember(item, extract_entities=False, compress=False)
```

## 调试技巧

### 查看系统状态

```python
import json
status = sms.get_status()
print(json.dumps(status, indent=2, ensure_ascii=False))
```

### 检查记忆内容

```python
for mid, mem in sms.memories.items():
    print(f"{mid}: {mem['content'][:50]}...")
```

### 查看实体关系图

```python
relations = sms.query_entity_relations("重要实体", max_depth=2)
print(json.dumps(relations, indent=2, ensure_ascii=False))
```
