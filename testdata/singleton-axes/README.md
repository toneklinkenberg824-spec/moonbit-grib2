# 单行、单列与单点的完整文件工作流

这是既有3.0/4.0/5.0支持合同内的一项有界范围扩展。只在某维Ni/Nj=1、端点表达同一位置
时，该维0或缺失步长可归为0；经度端点0/360允许表示同一点。不推断面积或未知全球覆盖。
既有正步长保持原值/原路径，非单例维仍须显式正步长。归零纬/经轴上必须命中实际坐标；
query经度仍先作原周期归一化，不在线/点上就是OutsideGrid。字段dx/dy为0表示无该维间隔。

EXPECTED.json在实现/运行前冻结，SHA256：
`deef75605bdb0ab398c3c3483cd711047d1ec9588c1e0f230a74f3e65f7b1cf5`。
all-supported.grib2共43字段/7823bytes：单行/单列各16扫描位组合，小量单点/bitmap/basic-angle/
全球单行/极点及两个原正步长控制。另4个坏输入保持非单例missing/zero及端点不合的拒绝合同。
每个独立文件也封存；它们由既有inventory24的179-byte原消息手写重编码整数节点而来，不是天气数据。
没有新模板、压缩、科学模型或SciPy参考生成。归零/域外政策是本项目明确政策，不声称所有工具等价。

基线真实node-file17拒绝column-0/column-16，仍正常接收legacy-positive-row；前置日志见单独R09报告。
扩展后公共消费者在JS/Wasm-GC核对全部数据/mask/点/来源/样本/贡献者/crop/iterator及负控制。
独立Python读原始header/bitmap/整数bits，按1维物理扫描方向及Fraction半权重求预期。
手写列中点15、行中点45、单点7、全球接缝25、标量极点25；极点风/动量仍拒绝。
非二进制权重沿用原浮点容差，不将单例轴扩成面；数据及metadata不被采样/裁剪修改。

现有文件接收器源码不改。可以直接重建并消费新输入，从源码父目录执行（目录假定moonbit-grib2；Bash语法）：

```sh
mkdir singleton-work
cp -r moonbit-grib2/examples/node-file17 singleton-work/receiver
cd singleton-work
moon work init
moon work use ../moonbit-grib2 ./receiver
moon -C receiver build --target js
cat > stations.json <<'EOF'
[
  {"id":"midpoint","latitude":1.5,"longitude":10},
  {"id":"node","latitude":1,"longitude":10},
  {"id":"off-column","latitude":1,"longitude":11}
]
EOF
node _build/js/debug/build/local/grib2-file17/grib2-file17.js \
  ../moonbit-grib2/testdata/singleton-axes/column-16.grib2 \
  stations.json new.csv 0
```

CSV三行值依次15、20、空，最后站点诊断outside-grid；仍是原11列及完整Product/Origin/贡献者。
Windows也可手工复制该例程并用PowerShell/编辑器创建同一JSON。Node≥22.3，当前源码依赖尚未发布。
真正验收消费15份成功CSV、6个预期失败（含坏尾和已有目标保护），没有冒称第三方采用。
源码/SDK/旧科学与日历/对比/framing证据都不重跑；输入/解码/结果仍物化，无全流程流式保证。
