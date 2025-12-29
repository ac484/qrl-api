infrastructure/
├─ bot/                          # 核心交易逻辑（六阶段流程、指标计算）
│   ├─ __init__.py
│   ├─ bot_core.py               # TradingBot 六阶段核心逻辑
│   └─ bot_utils.py              # 辅助函数（MA 计算、PnL 计算等）
│
├─ config/                       # 配置
│   ├─ __init__.py
│   └─ config.py                 # 全局配置（API key、环境参数等）
│
├─ external/                     # 第三方 / 外部服务客户端
│   ├─ __init__.py               # 统一导出 mexc_client、redis_client
│   ├─ mexc_client/              # MEXC API 客户端（重命名后的目录）
│   │   ├─ __init__.py
│   │   └─ client.py             # 原 mexc_client.py
│   └─ redis_client/             # Redis 客户端（重命名后的目录）
│       ├─ __init__.py
│       └─ client.py             # 原 redis_client.py
│
├─ tasks/                        # Cloud Scheduler / FastAPI 任务
│   ├─ __init__.py
│   ├─ auth.py                   # 请求验证（Cloud Scheduler / OIDC）
│   ├─ mexc_tasks.py             # 01-min / 05-min / 15-min 任务逻辑
│   └─ router.py                 # FastAPI 路由
│
├─ utils/                        # 通用工具函数
│   ├─ __init__.py
│   ├─ redis_helpers.py          # Redis 辅助函数
│   └─ utils.py                  # 其他通用工具函数
│
├─ __init__.py
├─ bot.py                        # 交易入口文件（实例化 TradingBot）
└─ cloud_tasks.py                # Cloud Tasks / FastAPI 入口文件

# 额外的 utils（架构说明档中提到）
# 如 decorators、redis_keys、redis_manager 等，落位于 infrastructure/utils/ 下，可按需扩展。
