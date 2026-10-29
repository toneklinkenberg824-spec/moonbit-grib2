# 用外部命名查询文件生成站点 CSV

独立 Node/JS 接收器，要求 Node≥22.3（CI 为24.11.0）。它读取任意受支持的
GRIB2 文件、外部查询配方与站点 JSON，调用已有 `sample_requested_fields` 一次，
将全部请求按配方顺序写入一个11列 CSV。已有取场/采样 API 可组合实现同样流程；
本例交付文件输入、JSON 到类型化查询、统一选择失败及文件输出边界。

    GRIB_PATH REQUESTS_JSON STATIONS_JSON OUTPUT_CSV

尚未发布 Mooncakes。从源码父目录执行（源码目录假定为moonbit-grib2；Bash语法）：

```sh
mkdir request-work
cp -r moonbit-grib2/examples/node-request-file request-work/receiver
cd request-work
moon work init
moon work use ../moonbit-grib2 ./receiver
moon -C receiver build --target js
node _build/js/debug/build/local/grib2-request-file/grib2-request-file.js \
  ../moonbit-grib2/testdata/noaa-gfs-repacked.grib2 \
  /absolute/requests.json /absolute/stations.json /absolute/new.csv
```

Windows可复制同一例程并用PowerShell运行同一workspace。输出父目录须已存在。
两个JSON文件接受UTF8 BOM。配方示例：

```json
[
  {"key":"GFS温度","query":{"discipline":0,"category":0,"parameter":0,"centre":7}}
]
```

站点沿用node-file17的DTO，例如：

```json
[{"id":"港口","latitude":68.25,"longitude":31.5}]
```

请求项只能有 `key`、`query`，两者必填。key是完整字符串，不trim；空key和重复key
由根API拒绝。query必须是对象，允许以下全部原始编码过滤项，未知键报错：

| 属性 | JSON含义 |
|---|---|
| discipline、category、parameter | 必填Int数值 |
| centre、subcentre、master_table、local_table、time_unit | 可选Int；省略/null不约束 |
| forecast_time | 省略为任意时效；null仅匹配缺失时效；Int精确匹配，包括0和负值 |
| reference_time | 可选Int数组；省略/null不约束；根API要求恰好六分量 |
| first_surface、second_surface | 可选原码对象；省略/null不约束 |

Surface只能有 `kind`、`scale`、`scaled_value`：kind必填Int，scale可选Int，
scaled_value可选UInt32。对象内省略/null的后两项表示编码缺失None，整个Surface精确比较；
它们不是局部通配符。`{kind:100,scale:0,scaled_value:85000}` 与
`{kind:100,scale:1,scaled_value:850000}` 仍是不同编码，不做物理量换算。
time_unit与forecast_time也分别比较原码，不把6小时换算成360分钟，不解释地方表名称或日期。

查询整数先要求SDK解析后的JSON数值具有整数性，再用core FromJson校验类型和范围：
Int为−2147483648..2147483647，UInt32为0..4294967295；小数、布尔、数字字符串均拒绝。
`6.0`/`6e0`可以表示整数6。解析使用SDK的Double表示，不保证任意精度原始数字token校验。
站点解析不受此查询检查影响，保留原SDK的Double行为及`"NaN"`、`"Infinity"`等特殊字符串；
非法/域外/缺测坐标保留空值CSV行，不变成有效采样。普通数字字符串不是新的站点格式。

程序先解析全部请求及站点，再完整解码输入、解析全部唯一命中与采样，最后才以`wx`创建输出。
任意后续请求缺场或歧义时，均不产生前面请求的部分CSV；已有目标保持原字节。
输出按请求顺序、每请求内按站点顺序排列，保留key/ID的空白、Unicode、引号和CRLF。
11列格式及产品、来源格点/权重沿用根级`station_results_csv`；Origin相对于此次输入文件。
同一配方可跨字段顺序不同的文件使用，但正确Origin会随文件布局变化。

成功stdout只有一行JSON：`output`、`request_count`、`station_count`、`row_count`、
`unavailable`和`groups`。groups按请求顺序保留每组`key`、`origin`、`product`。
无站点时仍校验选择、保留groups；无请求时输出仅有CSV表头。计数包含空值行。

请求JSON语法/schema失败首先向stderr写
`{"phase":"requests","code":"invalid-request-file"}`，随后保留运行时错误。
取场失败首先写`selection/invalid-field-request`和根API原message，包含空/重复key、
无匹配、多匹配及reference_time长度错误。解码错误沿用原结构化decode事件。
用法、请求文件读取、站点解析及宿主IO错误保持非零原诊断，不承诺统一JSON；失败stdout为空。

本例同步物化完整输入、字段、采样结果及CSV，无流式/恒定总内存/提速承诺。
不支持模板仍按原解码器失败；没有新增科学精度或模板支持。
已有目标由wx保护；创建后发生写入IO失败可能留下新文件，不提供原子回滚或断电持久性。
本例不生成原消息span、哈希或文件读回证明。验收由外部Python实际读回CSV，
见`testdata/request-file`与`.github/scripts/check-request-file.py`。
