#!/bin/bash
# PaperCarator CLI 演示脚本

echo "=========================================="
echo "PaperCarator CLI 演示"
echo "=========================================="
echo ""

# 1. 查看帮助
echo "1. 查看帮助"
papercarator --help
echo ""

# 2. 分析题目
echo "2. 分析题目"
papercarator analyze "基于深度学习的图像分类方法研究"
echo ""

# 3. 列出模板
echo "3. 列出可用模板"
papercarator list-templates
echo ""

# 4. 生成配置文件
echo "4. 生成默认配置"
papercarator init-config --output demo_config.yaml
echo ""

# 5. 运行完整流程（不发布到GitHub）
echo "5. 运行完整论文创作流程"
papercarator run "基于优化理论的资源配置问题研究" \
    --template custom \
    --depth standard \
    --no-github \
    --output ./demo_output
echo ""

echo "=========================================="
echo "演示完成！"
echo "=========================================="
