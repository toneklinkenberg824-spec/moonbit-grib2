# 从任意受支持文件导出区域原始节点

这是Node/JS文件宿主例程：`GRIB_PATH BOUNDS_JSON FIELD_INDEX`。它使用既有
`read_fields()`与`crop_iter()`，把一个字段内选定区域的原始节点交付为stdout JSONL，
供地图、质检或后续程序逐记录读取。它不创建站点、不插值，不改变主库算法或支持模板。
Node要求22.3+；固定验收使用Node24.11.0。库源码依赖尚未发布，按以下工作区绑定当前源码。

从源码父目录执行，目录名假定为moonbit-grib2（Bash语法）：

```sh
mkdir raw-node-work
cp -r moonbit-grib2/examples/node-crop-file raw-node-work/producer
cd raw-node-work
moon work init
moon work use ../moonbit-grib2 ./producer
moon -C producer build --target js
node _build/js/debug/build/local/grib2-crop-file/grib2-crop-file.js \
  ../moonbit-grib2/testdata/node-crop-file/input.grib2 \
  ../moonbit-grib2/testdata/node-crop-file/bounds-cross.json 0 > nodes.jsonl
```

Windows可手工创建同一工作区。保存stdout原UTF8字节时可用Python
`subprocess.run([...], stdout=open('nodes.jsonl', 'wb'), check=True)`，其中参数列表
就是上面node及其四个路径/索引参数；此方式与实际验收一致，不依赖shell重定向的文本编码。

bounds是包含south/north/west/east的JSON对象，支持UTF8和可选BOM；使用既有Double解码及
bbox校验政策。FIELD_INDEX从0按完整`read_fields()`字段数组选择，**不是原消息序号**。
配套输入有两条消息、三个字段：索引1仍在消息0/字段1，索引2才在消息1，来源offset为333。

成功输出依次为一条field头、零到多条point、最后一条end，每条都是完整JSON且以LF分界：

- field：schema=`grib2-node-crop/1`、selected_index、field_count、原请求bounds、grid、Origin及完整Product。
- grid：原rows/cols/north/west/dx/dy/cyclic/unique_columns。重复全球闭合列的原cols仍包含重复列，输出只含独立列。
- point：包裹完整GridPoint，保留row/col/source_index/latitude/longitude/value，缺测显式null，有效0保留。
- end：points总数及missing总数。空区域也有field与end，两个计数均为0。

节点保持规整矩阵的北→南、西→东顺序，不按bbox起始经线重新排序。跨经线、零宽经线、
全360°、重复闭合列、单例轴等均复用原crop_iter政策；不把点/线推断为区域覆盖。
Origin以传入GRIB文件为参照，source_index仍属该原消息/字段扫描顺序。没有重采样或极点行均值。

完整读取的Python标准库例子（在生成nodes.jsonl的目录执行）：

```python
import json

with open("nodes.jsonl", encoding="utf-8") as source:
    records = [json.loads(line) for line in source]
assert records[0]["type"] == "field"
assert records[-1]["type"] == "end"
points = [record["point"] for record in records[1:-1]]
assert records[-1]["points"] == len(points)
assert records[-1]["missing"] == sum(point["value"] is None for point in points)
print([(point["source_index"], point["value"]) for point in points])
```

配套cross输入应输出`[(0, 0), (1, None), (3, 40), (4, 50)]`。独立验收还从原始Section/bitmap/
整数bits及手写索引核对每条完整记录，确认截断end或改坏节点值会被拒绝；不是第三方采用声称。

输入JSON解析、完整GRIB解码、字段选择、bbox校验都在首条stdout前完成；尾部坏字段也不输出
前面的成功前缀。识别到的解码/选择/bbox失败先写单行JSON事件到stderr，随后可能带SDK堆栈；
JSON/文件IO异常以原异常退出。全部失败退出非0。宿主stdout写入中断可能留下不完整交付，
接收方应核end及计数；不承诺IO原子回滚。重定向文件由调用者/shell管理。

节点逐个由crop_iter产生，不先collect成节点数组。输入字节、解码字段和宿主stdout缓冲仍在内存中，
不承诺全流程流式、恒定总内存、背压隔离或速度。主库仍支持原JS/Wasm-GC；本文件宿主仅Node/JS。
