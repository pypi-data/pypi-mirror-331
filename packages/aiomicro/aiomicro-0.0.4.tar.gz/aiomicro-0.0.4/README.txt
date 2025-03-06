# MicroA (aiomicro)

MicroA 是一个基于 Python asyncio 的轻量级微服务框架，它是 nameko 框架的异步重写版本。通过使用 asyncio 替代 eventlet，MicroA 提供了更符合 Python 现代异步编程模式的开发体验。

## 特性

- 完全异步：基于 asyncio 构建，支持现代 Python 异步编程
- RPC 通信：基于 AMQP 的服务间远程调用
- 事件系统：支持发布/订阅模式的事件处理
- 依赖注入：简化服务间的依赖管理
- 定时任务：支持定时执行的任务
- 可扩展：易于添加新的功能模块

## 安装

pip install aiomicro

## 快速开始

### 1. 创建一个简单的 RPC 服务

from mia.rpc import rpc

class GreetingService:
    name = "greeting_service"
    
    @rpc
    async def hello(self, name):
        return f"Hello, {name}!"

### 2. 创建一个事件监听服务

from mia.rpc.events import event_handler
from mia.abc import EventHandlerType

class NotificationService:
    name = "notification_service"
    
    @event_handler("greeting_service", "user_greeted", handler_type=EventHandlerType.BROADCAST)
    async def handle_greeting(self, name):
        print(f"Greeting event received for {name}")

### 3. 创建定时任务

from mia.timer import timer

class TimerService:
    name = "timer_service"
    
    @timer(interval=60)  # 每60秒执行一次
    async def periodic_task(self):
        print("Executing periodic task")

### 4. 运行服务

创建配置文件 config.yaml:

AMQP_URI: 'amqp://guest:guest@localhost:5672'

运行服务:

mia run module.service --config config.yaml

## RPC 客户端使用

from mia.rpc.proxy import ProxyRpc

async def main():
    async with ProxyRpc("amqp://guest:guest@localhost:5672") as rpc:
        result = await rpc.greeting_service.hello.wait("World")
        print(result)  # 输出: Hello, World!

if __name__ == '__main__':
    asyncio.run(main())

## 主要组件

- **RPC (Remote Procedure Call)**
  - 支持服务间的远程调用
  - 自动序列化/反序列化
  - 异步调用和响应

- **事件系统**
  - 支持发布/订阅模式
  - 支持广播和工作池模式
  - 事件持久化

- **依赖注入**
  - 自动管理服务依赖
  - 支持自定义依赖提供者
  - 生命周期管理

- **定时任务**
  - 支持定期执行的任务
  - 可配置执行间隔
  - 支持立即执行选项

## 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| AMQP_URI | RabbitMQ 连接地址 | - |
| SERIALIZER | 序列化方式 (pickle/json) | pickle |
| RPC_EXCHANGE | RPC 交换机名称 | mia-rpc |

## 与 nameko 的区别

1. **异步支持**
   - 使用 asyncio 替代 eventlet
   - 原生支持 async/await 语法
   - 更好的性能和可扩展性

2. **现代化特性**
   - 类型提示支持
   - 更好的错误处理
   - 更清晰的代码组织

## 命令行参数

mia run [-h] [-C CONFIG] [-R RABBIT_URL] module [module ...]

参数说明:
  module                运行一个或多个服务类的Python路径
  -C, --config         yaml配置文件路径
  -R, --rabbit         RabbitMQ连接地址 (格式: amqp://guest:guest@localhost:port)
  -H, --host          主机地址，默认为127.0.0.1

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 依赖要求

- Python 3.7+
- aio-pika>=9.3.0
- uvloop>=0.16
- pyyaml>=6.0.0
- six==1.16.0