# 贡献指南 (Contributing)

感谢你对xiaoyao-memory-system的兴趣！

## 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/zonghui1968/xiaoyao-memory-system.git
cd xiaoyao-memory-system

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装开发依赖
pip install -e ".[all]"
```

## 代码风格

- 遵循 PEP 8
- 使用类型注解
- 使用 `logging` 模块而非 `print()`
- 使用英文编写文档字符串

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_super_memory_v9.py -v

# 带覆盖率
pytest --cov=src --cov-report=html
```

## 项目结构

```
xiaoyao-memory-system/
├── src/              # 源代码
│   ├── __init__.py   # 包入口
│   ├── super_memory_system_v9.py  # 核心系统（推荐）
│   ├── xiaoyao_memory_system.py   # 小妖集成
│   ├── vector_store.py            # 向量存储
│   └── ...           # 其他模块
├── tests/            # 测试
├── web/              # Web UI和API
├── docs/             # 文档
└── data/             # 数据文件
```

## 提交Pull Request

1. Fork仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 版本号规范

遵循 [Semantic Versioning](https://semver.org/):
- MAJOR: 不兼容的API更改
- MINOR: 向后兼容的新功能
- PATCH: 向后兼容的Bug修复
