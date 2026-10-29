# 必要 CI 与验收边界

本计划描述必要门；结论以对应最终Git head的真实GitHub Actions run/jobs/steps为准。
workflow为`.github/workflows/ci.yml`，保留固定MoonBit工具链、Node24.11.0、Python3.14.4和只读权限。

| 必要job | 必要工作 |
|---|---|
| core (js) | 固定SDK、check、build、test、公共示例 |
| core (wasm-gc) | 同上，独立后端 |
| Node files and NyaCSV consumers | 原文件/诊断、目录查询、区域iterator、原消息framing/交付、命名配方、有效时刻、双修订比较、单例轴文件工作流及锁定NyaCSV接收 |

R09新增必要step：`Singleton regular-grid axes and existing file receiver`。
执行`.github/scripts/check-singleton-axes.py --work <fresh temporary directory>`，包含：

- JS/Wasm-GC各4个针对性blackbox回归及43字段公共消费者，逐项消费完整点/样本/贡献者/裁剪结果。
- 单行/单列各16扫描组合、0/缺失步长、单点、缺测、basic-angle、全球/极点和原正步长控制。
- 非单例missing/zero和不合端点拒绝、单点预算、线预算及多消息不得静默丢字段。
- 从当前源码重新构建未改node-file17，实际读新文件并由Python读回完整11列CSV/JSON及诊断。
- 15成功、6预期失败；公共模块和Node构建、测试进程与新字段/案例数分开记录。

预期源于冻结原始字节、手写整数节点/方向和Fraction半权重，不由新MoonBit结果反推。
原采样、metadata/时间/查询、极点/缺测和CSV合同保留；旧必要门全部继续执行。
新步只扩展当前3.0单例轴范围，不加入重网格、额外模板/压缩、科学模型或第三方采用声称。
CI不重下天气或运行ecCodes/SciPy等外部科学参考生成器。远端状态不等于下载二进制逐字节相等，
发布交付另记录最终head源码ZIP、Git/工作原字节、实际测试副本/编译/全部输出身份。

R10新增必要step：`Large ancillary JSON integer diagnostic receiver`。从当前源码新建工作区，
重建未改Node入口并真实消费附带5002位整数的站点JSON，独立读回4行11列CSV及3条完整关联结果。
正/负/嵌套整数和既有1e400原片段保真；改坏坐标及NaN仍拒绝，全局整数转换位数限制保持。
本地只修Python消费者，可复用本轮此前真实生产文件，记录原/副本SHA256；CI则完整新建、构建、生产及消费。
