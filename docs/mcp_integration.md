# MCP 集成方案

## 概述

PaperCarator 可以通过 MCP (Model Context Protocol) 与外部工具和服务集成，扩展其功能。

## 已规划的 MCP 集成

### 1. 3D 建模 MCP

**目标**: 通过 MCP 控制 Blender / FreeCAD 进行高级 3D 建模

**状态**: 🔍 调研中

**方案**:
- 寻找现有的 Blender MCP Server
- 或开发自定义 Blender Python API 封装
- 通过 JSON-RPC 与 Blender 通信

**参考**:
- Blender Python API: https://docs.blender.org/api/current/
- FreeCAD Python API: https://wiki.freecad.org/Python_scripting_tutorial

### 2. 文献检索 MCP

**目标**: 自动检索和引用学术文献

**状态**: 🔍 调研中

**方案**:
- 集成 Google Scholar API
- 或 Semantic Scholar API
- 自动获取 BibTeX 引用

### 3. GitHub MCP

**目标**: 通过 MCP 管理 GitHub 仓库

**状态**: ✅ 已实现 (原生 Python)

**当前实现**:
- 使用 `httpx` 调用 GitHub REST API
- 使用 `GitPython` 进行 Git 操作

### 4. LaTeX 编译 MCP

**目标**: 远程或容器化 LaTeX 编译

**状态**: 📋 规划中

**方案**:
- 使用 Overleaf API
- 或 Docker 容器编译

## 自定义 MCP Server 开发

### Blender MCP Server (概念)

```python
# blender_mcp_server.py
import json
import bpy

class BlenderMCPServer:
    def handle_request(self, request):
        method = request.get("method")
        params = request.get("params", {})
        
        if method == "create_mesh":
            return self.create_mesh(**params)
        elif method == "apply_modifier":
            return self.apply_modifier(**params)
        elif method == "render":
            return self.render(**params)
        # ...
    
    def create_mesh(self, vertices, faces, name="Mesh"):
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        mesh.from_pydata(vertices, [], faces)
        return {"success": True, "object_name": name}
```

### 集成到 PaperCarator

```python
from papercarator.visualization import Model3DGenerator

class MCPModel3DGenerator(Model3DGenerator):
    def __init__(self, mcp_client):
        super().__init__()
        self.mcp_client = mcp_client
    
    def generate_with_blender(self, model_data):
        # 通过 MCP 调用 Blender
        result = self.mcp_client.call("blender", "create_mesh", {
            "vertices": model_data["vertices"],
            "faces": model_data["faces"],
        })
        
        # 渲染
        self.mcp_client.call("blender", "render", {
            "output_path": "/tmp/render.png",
            "resolution": [1920, 1080],
        })
        
        return result
```

## 推荐的 MCP Servers

### 现有可用

| Server | 功能 | 链接 |
|--------|------|------|
| GitHub | 仓库管理 | 原生实现 |
| Filesystem | 文件操作 | mcp__filesystem_* |
| Memory | 知识图谱 | mcp__memory_* |

### 待开发/寻找

| Server | 功能 | 优先级 |
|--------|------|--------|
| Blender | 3D建模 | 高 |
| FreeCAD | CAD建模 | 高 |
| Zotero | 文献管理 | 中 |
| Overleaf | LaTeX编译 | 中 |
| arXiv | 论文检索 | 低 |

## 配置示例

```yaml
# configs/default.yaml
mcp:
  enabled: true
  servers:
    blender:
      command: "python"
      args: ["/path/to/blender_mcp_server.py"]
      env:
        BLENDER_PATH: "/usr/bin/blender"
    
    zotero:
      command: "node"
      args: ["/path/to/zotero-mcp-server/index.js"]
    
    overleaf:
      command: "docker"
      args: ["run", "--rm", "overleaf/latex:latest"]
```

## 下一步行动

1. **调研现有 Blender MCP Server**
   - 搜索 GitHub 上的相关项目
   - 评估可行性

2. **开发最小可行版本**
   - 实现基本的 Blender 通信
   - 支持简单的几何体创建和渲染

3. **集成测试**
   - 验证端到端流程
   - 性能测试

## 参考资源

- [MCP Protocol](https://modelcontextprotocol.io/)
- [Blender Python API](https://docs.blender.org/api/current/)
- [FreeCAD Scripting](https://wiki.freecad.org/Python_scripting_tutorial)
