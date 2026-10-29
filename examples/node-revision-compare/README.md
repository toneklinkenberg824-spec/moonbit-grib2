# 两次预报修订的逐站数值对比

Node/JS独立例程，Node≥22.3（CI24.11.0）：

    LEFT_GRIB LEFT_INDEX RIGHT_GRIB RIGHT_INDEX STATIONS_JSON

完整读取两份任意受支持的GRIB文件，选择各自数字字段索引，对同一站点列表调用公共
`left.compare_stations(right, stations)`，输出一个完整JSON。差值方向始终为right−left。
这是本项目自建接收方，不是第三方采用证明。字段可来自不同网格，程序分别采样；
它不是先相减网格或重网格，也不证明不同模式/基准具有相同物理含义。

源码依赖未发布。从源码父目录执行（源码目录假定moonbit-grib2；Bash语法）：

```sh
mkdir compare-work
cp -r moonbit-grib2/examples/node-revision-compare compare-work/receiver
cd compare-work
moon work init
moon work use ../moonbit-grib2 ./receiver
moon -C receiver build --target js
node _build/js/debug/build/local/grib2-revision-compare/grib2-revision-compare.js \
  ../moonbit-grib2/testdata/revision-comparison/left.grib2 1 \
  ../moonbit-grib2/testdata/revision-comparison/right.grib2 0 \
  ../moonbit-grib2/testdata/revision-comparison/stations.json
```

Windows也可手工复制同一目录并运行该workspace。索引从0开始，沿用当前SDK Int字符串语法；
先解析双方索引，再读UTF8站点JSON（接受BOM）及输入。站点沿用旧{id,latitude,longitude}DTO，
保留完整ID、重复坐标及SDK支持的NaN/Infinity特殊字符串；非法坐标仍报告旧采样失败。

比较前按以下优先级检查，即使站点数组为空也执行：

1. discipline/category/parameter必须相等，否则parameter-mismatch。
2. centre/subcentre/master_table/local_table必须相等，否则table-mismatch。
3. 第一/第二Surface整个原码必须相等，否则surface-mismatch。
4. 左、右分别调用已有valid_time；失败为left-time/right-time及原类型化reason。
5. 两个既有有效民用时刻须相等，否则valid-time-mismatch。

参考时间、lead与单位可以不同，例如00Z+12小时和06Z+6小时。valid_time的固定日长公历
政策和既有单位范围不变；原码查询仍区分单位，不转换层、参数或地方表名称。上述检查是
编码兼容筛选，调用者仍须选择业务上可比较的量；不作模式校准、矢量基变换或新科学模型。

成功JSON含operation、valid_time、双方index/Origin/Product、station_count、
available_count、unavailable_count和原站点顺序的rows。每行含：

- station：完整输入站点。
- left/right：`{"sample":<原Sample>}`或`{"failure":<原SampleFailure代码>}`，双方独立保留。
- difference：`{"value":<有限Double>}`；任一侧失败为`{"error":"sampling-unavailable"}`，
  双方采样成功但减法非有限则为`{"error":"nonfinite-difference"}`。

原Sample保留各自Product/Origin和全部贡献格点、权重、值。缺测不补0，不用一方成功掩盖
另一方失败。差值是普通Double减法，含IEEE舍入/下溢和有效0；不额外计算相对误差或阈值。
unavailable_count包含采样失败与差值溢出。空站点输出完整双方头及空rows。

全文件解码、索引范围及全局比较失败时非零、stdout为空。比较事件为
`{"phase":"comparison","error":<FieldComparisonError JSON>}`；索引事件为selection、
invalid-field-index/field-index-out-of-range及side（范围事件还含field_count）。
解码事件保持原形状；用法/宿主IO/站点JSON错误保留原非零诊断，不承诺统一JSON。
晚到的不支持消息仍导致完整解码失败，不返回成功前缀。

不写输出文件，shell重定向由宿主负责。输入、解码网格和结果都物化，无流式/恒定总内存
或性能保证。纯API用于JS/Wasm-GC；文件入口仅Node/JS。完整独立位流/有理数验收在
`testdata/revision-comparison`及`.github/scripts/check-revision-comparison.py`。
