# 超长附带整数的真实诊断关联

输入仍是已经支持的`../singleton-axes/column-0.grib2`。这里不扩展坐标、网格、精度或采样模型。
站点应用附带信息包含`10^5001+1`（5002位）的正数、嵌套负数，以及既有1e400形式。
Node入口忽略附带字段，按原坐标产生4行CSV：值依次15/空/空/空；诊断依次原索引1、2的outside-grid
和索引3的invalid-station。CSV的Product/Origin、两个半权重贡献点和全部11列均独立核对。

旧Python辅助消费者在读取整数字面量时触及默认4300位限制，退出而无关联输出。修复只为站点JSON和
原片段解码器提供本地精确整数解析；join()仍保留Python int，不修改全局转换上限。
CLI沿原片段路径保留所有数字、正负和嵌套位置，不把附带数值改成Double/字符串/null。
原严格坐标比较及非JSON NaN拒绝保留；未把超大整数坐标或任意精度采样加入支持范围。

在源码根目录，装有已固定MoonBit、Node24.11.0和Python3.14.4时运行：

```sh
python .github/scripts/check-ancillary-integer.py --work /tmp/grib2-ancillary-integer
```

工作目录必须不存在。该门从当前源码构建既有Node文件例程、读取真实站点文件、写新CSV，
再调用`examples/node-file17/join_diagnostics.py`。它独立读回每列及三条完整标准JSON关联记录，
通过Decimal和整数幂核对全部5002位；另核坏坐标CSV和非JSON NaN输入确实拒绝。
Windows可把--work改为一个新的绝对目录。直接调用关联器的三个文件参数沿原例程README。

站点输入、预期值/诊断/整数token在基线运行前冻结；完整预期文件组合发生于基线之后、实现之前，
其共享Product/Origin/贡献者取自同一GRIB在更早运行前的独立冻结预期。时间顺序如实保留于R10报告。
本地修复验收复用本轮未改Node实际生成的原文件，逐字节核原/副本身份，避免重复生产；远端门完整新建。
这是同步物化、本地稳定配套文件的消费工作流，不声称第三方采用、内存/性能界限或新的格式/科学支持。
