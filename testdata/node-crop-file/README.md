# 任意文件区域原节点交付的冻结输入

`input.grib2`为513bytes、两消息/三字段：消息0内有2x3区域字段和2x5全球重复闭合列字段，
消息1是缺测单点。消息0长度333bytes，第二个字段的Origin仍是message0/field1/offset0。
另有`late-unsupported.grib2`在同样好前缀后加入不支持的3.1标记，用于确认全部解码先于输出。
它只作拒绝控制，不声称支持或科学验证该模板。

输入沿既有3.0/4.0/5.0模板，以原Section1/4和手写整数8位数据构造，不是天气观测。
R/E/D=0；区域节点0/null/30、40/50/60。global scan240原payload为
50/10/40/80/70/30/20/60/50/10，北行原索引9/6/5/2/1，南行8/7/4/3/0。
原全球cols=5、unique_columns=4，重复经度列不再次导出。缺测由bitmap决定，不把数值0当缺测。
EXPECTED.json含全部手写网格、索引、Product/Origin及每个bbox的明确节点位置列表，先于实现和运行冻结。

`bounds-cross.json`可直接用于新`examples/node-crop-file`入口。完整构建、stdout保存及Python读取见该例程README。
在源码根目录运行必要门（--work必须为不存在的新目录）：

```sh
python .github/scripts/check-node-crop-file.py --work /tmp/grib2-node-crop-file
```

它独立从原始段/bitmap/整数payload重建全部三字段，再按冻结位置列表读取7个实际成功输出，
共35条JSONL记录/21个节点；核全头、每个点和end，覆盖缺测/0、跨线/经线、空区域、重复列、
scan240、薄单点、同消息多字段选择、UTF8路径和BOM。6次坏输入必须无stdout成功前缀；
两个派生输出（缺end、错point）必须被独立接收器拒绝。保留全部实际stdout/stderr/exits。
这里完成新的文件交付，不重跑旧crop/科学参考/日历/比较/span套件，不修改主库政策或公开接口。
