# 部署说明

目标：把插件部署到测试库，并确认设置页可以打开。

1. 运行命令：

   ```bash
   node scripts/deploy.mjs --vault /tmp/example
   ```

2. 打开 Obsidian 设置页。
3. 确认结果：插件名称和版本均可见。

失败时保留日志，不要把未验证状态写成成功。
