# grib2 — 可追溯气象网格采样

源码仓库：[github.com/toneklinkenberg824-spec/moonbit-grib2](https://github.com/toneklinkenberg824-spec/moonbit-grib2)。源码署名与Mooncakes模块名`zhou-wei97/grib2`保留；本次发布没有改写原作者或上游归属。

纯MoonBit库：读取GRIB2字节，将值、坐标和bitmap规整为北→南、西→东矩阵，进行站点批量采样及区域节点提取。每条结果保留PDT4.0产品信息、消息/字段身份、原扫描点索引和贡献权重。
实际复用[trkbt10/grib2_mbt](https://github.com/trkbt10/grib2_mbt)固定提交的解析器与解包器；新增贡献是缺测可解释的高层采样完整链，详见THIRD_PARTY.md。

## 运行

MoonBit工具链即可，无C/Python或外部包运行依赖。本地工具链：moon0.1.20260904 / moonc0.10.12+1634b282e。

```sh
moon check --target js
moon build --target js
moon test --target js
moon check --target wasm-gc
moon build --target wasm-gc
moon test --target wasm-gc
moon run cmd/main --target js
moon run cmd/main --target wasm-gc
```

示例读取内嵌bitmap字段并输出JSON：海岸缺角为null，内陆值4.5，并列出来源权重。静态黄金测试无需联网；数据位于testdata/。

## 使用API

消费者moon.pkg导入：`import { "zhou-wei97/grib2" @grib2, }`。
本模块尚未发布Mooncakes，当前须使用本地模块/源码依赖；不表示包名已可在线安装。

### 首次接入一个独立本地消费者

将完整源码放到一个新目录的 `moonbit-grib2/` 子目录，确认
`moonbit-grib2/moon.mod` 存在。以下命令从它的父目录执行；命令使用 Bash
语法，Windows 可在 Git Bash/WSL 中执行，或用编辑器创建同名文件。
工作区把依赖绑定到本地源码，不需要先发布或复制预构建产物。

```sh
mkdir consumer
cat > consumer/moon.mod <<'EOF'
name = "local/grib2-consumer"

import {
  "zhou-wei97/grib2@0.1.0",
}
EOF
cat > consumer/moon.pkg <<'EOF'
import {
  "zhou-wei97/grib2" @grib2,
}

pkgtype(kind: "executable")
EOF
# 示例只调用公共API；其内嵌GRIB2字节不依赖文件IO或真实预报下载。
cp moonbit-grib2/cmd/main/main.mbt consumer/main.mbt
moon work init
moon work use moonbit-grib2 consumer
moon -C consumer check --target js
moon -C consumer run . --target js
```

`moon work init/use` 由已安装工具生成父目录的 `moon.work`，成员为
`./moonbit-grib2` 和 `./consumer`。消费者模块仍声明版本依赖，工作区成员
提供对应的本地实现；以后从该父目录或消费者目录执行命令，保持此目录布局。

最后一条命令输出包含两个站点的完整JSON，关键信息如下：

| station.id | value | contributors |
|---|---|---|
| coastal-gap | null | 空数组 |
| inland | 4.5 | 原值4与5，各权重0.5 |

这组本地依赖配置及JS消费者已用上述固定SDK实际check/run通过，退出码均为0。
上游组件在该SDK下仍有弃用警告；这里验证首次源码接入，不声称零警告或重新执行完整库验收。
将来发布后才能改用注册表安装流程，当前不要单独执行 `moon add zhou-wei97/grib2`
来代替此工作区绑定。

### 在应用中提供自己的字节

```mbt nocheck
let fields = @grib2.read_fields(bytes).unwrap()
let chosen = @grib2.select_fields(fields, 0, 0, 0, time_unit=1, forecast_time=6)
let samples = chosen[0].sample_stations([{ id: "port", latitude: 31.2, longitude: 121.5 }])
println(samples.to_json().stringify(indent=2))
let nodes = chosen[0].crop({ south: 30.0, north: 32.0, west: 120.0, east: 123.0 }).unwrap()
```

bytes由宿主提供。完整准确签名见pkg.generated.mbti。

- read_message要求恰好一个字段；多消息/字段用read_fields，不会静默丢字段。
- get返回原格点Double?，values返回含NaN的独立副本，mask返回独立布尔副本。
- point/crop保留坐标、原始点序号与可选值；crop是节点筛选，不是重采样。
- product保留数值参数、中心/表版本、UTC参考分量、时效原单位/可选数值及垂直层原缩放值，不猜地方表名称或日历。
- sample/sample_stations保留贡献格点与权重；缺测JSON显式null。
- 每字段默认最多10,000,000点，可用max_points调整；坏次序/长度/点数和预算超限均显式报错。

### 按需提取区域原始节点

导出或预览一个大区域时，可用 `crop_iter()` 逐个产生节点，取到所需前缀后停止，
无需先构造完整的裁剪结果数组。它与 `crop()` 使用同一筛选内核；`crop()` 仍返回完整数组。

```mbt nocheck
///|
let nodes = field
  .crop_iter({ south: 30.0, north: 32.0, west: 120.0, east: 123.0, })
  .unwrap()

///|
let first = nodes.next() // GridPoint?；需要时继续 next()，或停止消费
// 节点的 source_index 对应 field.origin() 所指消息/字段的原扫描顺序。
```

边界框在返回迭代器前完整校验；非法经纬边界或非有限数仍返回
`InvalidRequest("invalid bbox")`。节点按北→南、西→东的矩阵顺序产生，保留原坐标、
扫描索引与可选值，缺测节点也会产生；有效 `0/9999` 不会被当作缺测。
跨日界线、闭区间、零宽经线和完整360°覆盖沿用 `crop()` 规则，全球重复闭合列只产生一次；
极点节点保留原值，不应用站点采样的标量行均值。空结果或已耗尽的迭代器继续返回 `None`，
每次调用创建独立游标；提前停止只取得部分结果，不表示已返回完整区域或总节点数。

每次 `next()` 才查找并构造下一节点，游标额外状态为常量大小；它仍保留已解码字段。
输入及解码数组继续常驻内存，不承诺文件/解码流式处理、恒定总内存或特定加速比。
`moon run cmd/crop-iter --target js`（或 `wasm-gc`）运行合成公共API消费者，
包括重复经线、bitmap、原扫描身份、前缀恢复及百万点字段仅取两个节点。

## 按层和预报批次取场，再采样站点

同一参数可能同时出现在2米、850hPa、多个起报时次和预报时效中。`FieldQuery`支持参数代码、中心/子中心、表版本、6个参考时间分量、原始时效单位/整数和两组Surface筛选；`select_unique_field`要求唯一匹配，缺场或多场匹配返回`InvalidRequest`。

`sample_requested_fields`先解析全部命名请求，再批量采样。请求key必须非空且唯一；任一取场失败则整个调用报错，空间缺测仍保留为Sample.value=None/JSON null。结果按请求顺序保留key、产品、消息/字段来源及原有站点贡献权重。空站点列表仍保留选中场身份。

```mbt nocheck
let query = @grib2.FieldQuery::new(
  0, 0, 0,
  time_unit=1, forecast_time=6,
  reference_time=[2007, 3, 23, 12, 0, 0],
  first_surface={ kind: 103, scale: Some(0), scaled_value: Some(2U) },
  second_surface={ kind: 255, scale: None, scaled_value: None },
)
let rows = @grib2.sample_requested_fields(
  fields, [{ key: "temperature_2m", query }], stations,
).unwrap()
println(rows.to_json().stringify())
```

可运行示例：`moon run cmd/layers --target js`，或`--target wasm-gc`。示例用合成3.0/4.0/5.0数据演示2米与850hPa温度，结果分别为`[280,280]`和`[null,270]`，不表示真实预报。实际请求使用文件中的参考时间和层编码。

省略可选筛选项表示通配；Surface按原始kind/scale/scaled_value精确比较，85000×10^0与850000×10^-1即使物理值相同，也属于不同编码查询。无时间/层单位换算；forecast_time省略为通配；显式缺失、任意或指定整数可用下面的ForecastTimeFilter。旧`select_fields`接口保留。

### 查看完整查询候选目录

inspect_field_query(fields, query)返回FieldQueryReport：field_count、match_count和entries。每个entry含index、matches、原Origin及Product快照；无匹配或多匹配时也返回完整目录，便于查看现有层、起报和时效原码，再细化查询。非法reference_time长度仍返回原InvalidRequest。

    let report = @grib2.inspect_field_query(fields, query).unwrap()
    println(report.to_json().stringify(indent=2))

入口直接复用本库完整FieldQuery匹配规则，不省略、排序、去重或截断字段，没有输出预算。entries按传入视图顺序排列；index相对该视图，从完整read_fields数组传入时才对应全文件位置。原消息/消息内字段/byte_offset始终看origin。即使match_count=0，目录仍列出全部可用字段及false标记。

Product保留原始Surface(kind/scale/scaled_value)、起报分量、时效单位/整数；缺失forecast_time沿原Product JSON规则省略，0保留。等物理值但原缩放编码不同的层仍不匹配，不做层单位、日历或时效换算。返回的reference_time数组与字段内部状态分离。该目录只给整体匹配标记，不逐条件生成失败原因，也不替代原select_unique_field或命名批量入口；原缺场/歧义错误保持。

运行moon run cmd/query-catalog --target js或--target wasm-gc，可查看同一6字段/5消息人工文件上的缺场、唯一、歧义、missing/0、不同Surface编码及视图/非法查询。原始字节、手工身份和独立验收见testdata/query-inspection。输入仍是已完整解码的字段；该元数据快照不是文件头扫描、流式读取或全量气象认证。

### 显式区分时效缺失与分析时效0

同一参数、层和起报批次可能同时存在时效缺失、0、6或负时效。`ForecastTimeFilter`提供`AnyTime`、`MissingTime`和`ExactTime(Int)`；`with_forecast_time_filter`返回细化后的新查询，保留原查询和其它筛选条件。

```mbt nocheck
///|
let missing = query.with_forecast_time_filter(MissingTime)

///|
let analysis = query.with_forecast_time_filter(ExactTime(0))

///|
let forecast = query.with_forecast_time_filter(ExactTime(6))

///|
let unconstrained = query.with_forecast_time_filter(AnyTime)

///|
let selected = @grib2.select_unique_field(fields, missing).unwrap()
```

`forecast_time_filter()`可读取完整条件。原`FieldQuery::new`签名保留：省略forecast_time表示任意，传0仍精确匹配0。缺失条件与0互不替代；多场匹配继续报错。该筛选不计算日期或换算时效单位。

离线示例：`moon run cmd/forecast --target js`（或wasm-gc），使用4份合成字段。缺失时效、分析0、预报6的站点值分别为`[null,111]`、`[222,222]`、`[333,333]`。Product的None元数据沿用现有JSON规则省略对应键；站点Sample.value缺测始终显式null，0时效保留为数字0。

### 导出带来源信息的站点CSV

`station_results_csv(results)`把命名站点结果转换为String，每个Sample一行，按请求组和站点顺序输出。固定列为：

```text
request_key,station_id,latitude,longitude,value,algorithm,message,field,byte_offset,product_json,contributors_json
```

```mbt nocheck
///|
let text = @grib2.station_results_csv(rows)
```

所有单元格加引号并处理内部双引号，行分隔为CRLF；宿主按UTF-8保存即可。value为空表示None，实际数值0输出`0`。product_json和contributors_json沿用每个Sample自己的产品元数据、来源格点与权重，保留缺失时效和0的区别。中文、逗号、引号和内嵌换行保持原样；空站点不生成数据行，没有Sample时仅有表头。需要保留空站点组的字段身份时，继续使用原FieldSamples结果。

`moon run cmd/export --target js`（或wasm-gc）直接输出CSV，演示已收录的NOAA/IFS8×6、5.0转码字段经过唯一取场和批量站点采样后的8行结果。4个有效值及4个区域外缺口已经独立读回。它使用历史派生样本，不表示支持原始5.3/5.42压缩或实时预报。可读样例与数据来源许可见`testdata/export10/`。

### 逐记录导出，支持提前停止

`station_csv_records(results)`返回`Iter[String]`：第一项为表头，随后每项是一条完整CSV逻辑记录，按原请求／站点顺序惰性生成。每项以CRLF结束，标签中的引号或换行仍在同一记录内。

```mbt nocheck
for chunk in @grib2.station_csv_records(rows) {
  // println补LF，保留记录的最终CR。
  println(chunk[:chunk.length() - 1])
}
```

宿主可按项写出或提前停止，分别创建的迭代器状态独立。迭代期间保持输入结果及其数组不变。此接口避免额外构造整份CSV字符串，输入FieldSamples仍已在内存中；没有整个流程的内存或速度保证。空站点组跳过，无Sample时仍输出一个表头。

`moon run cmd/stream --target js`（或wasm-gc）逐记录输出已有NOAA/IFS示例，与`cmd/export`及第10轮封存CSV逐字节相同。原`station_results_csv`仍返回完整String，格式和签名保留。新接口已验证10,000站点遍历、提前读取前缀和独立CSV/JSON读回；长度统计见VALIDATION.md。

### 按需采样并逐记录导出

sample_requested_csv_records(fields, requests, stations) 返回 Result[Iter[String], GribError]。它先解析全部命名请求，缺场、歧义、空名称或重名等错误在返回迭代器前报告；即使站点列表为空也会校验。选中的字段和请求名称在创建时固定，随后每次取数据记录才采样一个站点，按请求／站点顺序输出相同的11列CSV。

    let records = @grib2.sample_requested_csv_records(
      fields, requests, stations,
    ).unwrap()
    let header = records.next().unwrap()
    let first_station = records.next()
    // 可以在此停止；尚未取出的站点不会由该迭代器采样。

空请求或空站点只输出表头，耗尽后持续返回None。分别创建的迭代器状态独立；创建后替换原请求或字段数组的条目不会改变已选身份，消费期间须保持站点列表不变。原批量采样、完整String导出和逐记录视图继续可用；字段产品、缺测值、贡献者及CSV字节格式一致。

这个入口省去为全部请求／站点先构造Sample数组，也不要求整份CSV缓冲。GRIB输入、已解码字段和站点列表仍已准备在内存中；选择状态按请求保存，当前单条极点记录的贡献者也可能覆盖整行。没有整个输入流、恒定内存、RSS或速度保证。

离线运行 moon run cmd/direct --target js（或wasm-gc）。两目标真实NOAA/IFS的8行输出与 testdata/export10/NOAA-IFS-stations.csv 逐字节一致；本轮各11项相关测试、10,000个预备站点的前缀消费及独立CSV/JSON消费者通过。未重新下载或重跑旧科学参考集合，详见VALIDATION.md。

### 用 MoonBit CSV 库逐记录消费结果

独立例程 examples/nyacsv13 展示真实下游接入：缓存表头，把每条完整逻辑记录交给 NyaCSV，校验11列表头和单行形状，再显式转换数值列、解析产品及贡献者JSON。文本ID保持字符串，因此前导0、空ID、前后空白和多行Unicode标签不会被业务层误当数值。

例程模块单独依赖 NyaCSV，主库仍只依赖core。固定SDK下已验证的依赖是声明版本0.3.3的源码提交 fe4448e1e45a25f6fca151320c766519e80162c9，通过本地moon.work绑定。当前0.3.4源码使用该SDK不识别的Int32；没有升级全局SDK，也没有证明注册表安装流程可用。完整复现命令见 examples/nyacsv13/README.md。

JS与Wasm-GC各通过4类消费场景、9条业务记录的独立读回：真实NOAA/IFS、缺测与数值0、单行预览、空结果。原库代码/API保持字节一致，未重跑已通过的12轮延迟采样或原样例字节一致性检查。

例程接收本库产生的完整CSV逻辑记录；不可按物理换行拆分，也不把它当任意字节分片或不可信CSV的严格校验器。解析时仍构造当前表头加记录及单行表格，输入网格/站点列表继续预备；不承诺全流程流式、恒定内存、RSS或速度。

### 第14轮有限审查状态

本轮只复核交替扫描的末点坐标约定。两种新构造的元数据变体均被现有校验拒绝，但尚未取得足够依据认定其为合规消息，因此未把拒绝行为记作缺陷，也未据此放宽或收紧输入校验。库源码、配置、API及原有行为保持不变。

本轮诊断程序在JS/Wasm-GC上各观察2种变体，记录位于 testdata/review14；这不是新增功能验收或全GRIB规范认证。第13轮消费者成绩仍为历史验收，未重复执行。审查边界和未证实的问题见 testdata/review14/README.md。

### 大有限数值的极点均值修复15

在支持的简单打包输入中，节点全部为有限Double.MAX时，11个极点节点的普通加权累加可能溢出，原采样因此误返回None。本轮已用公开GRIB2输入复现并修复。

仅当原计算结果非有限时，才按最大绝对值缩放贡献值，累计后按浮点权重总和归一化，限制到单位范围再恢复尺度。原有限计算及subnormal路径、缺测和极点风分量拒绝政策保持；公共API、贡献者权重、算法标签及CSV列格式均不变。

JS/Wasm-GC各18项相关测试通过（4项新增、12项小量值/普通值回归、2项极点政策回归）。新增样本用Fraction独立计算均值；极点常量精确比较，其余新增样本相对容差4e-15，不作为所有字段的精度保证。

运行 moon run cmd/extreme --target js（或wasm-gc）可查看8行合成极值压力样本：4个有限结果和4个区域外缺口。它不是气象观测或预报。实际CSV与外部JSON消费者均已独立读回；若下游自行重算极值贡献均值，应使用稳定的归一化算术，直接sum(weight*value)仍可能溢出。详见 testdata/numeric15 和VALIDATION.md。

### 可选的站点采样失败原因

当应用需要区分数据缺口与请求问题时，可调用 field.sample_result(station)，返回 Result[Sample, SampleFailure]。成功结果仍是原Sample；失败可匹配：

| SampleFailure | 含义 / JSON代码 |
|---|---|
| InvalidStation | 非有限坐标或纬度超出±90°；invalid-station |
| OutsideGrid | 合法站点坐标不在字段覆盖域；outside-grid |
| MissingData | 正权重格点缺测或标量极点行全缺测；missing-data |
| UnsupportedPolarVector | 到达现有极点风/动量限制；unsupported-polar-vector |
| NonFiniteResult | 现有最终数值保护仍未得到有限结果；nonfinite-result |

    match field.sample_result(station) {
      Ok(sample) => println(sample.to_json().stringify())
      Err(reason) => println(ToJson::to_json(reason).stringify())
    }

结果报告现有执行顺序中的首个阻断原因，不是全部原因清单。零权重缺角不触发错误；有限经度仍按原政策周期处理。NonFiniteResult保留现有保护分支，本轮没有声称以合法公共输入复现该分支的新数值问题。

解码的不支持模板、损坏输入，以及筛选未命中/歧义仍在采样之前返回GribError；不把它们混作站点MissingData。新入口只处理已解码字段，不增加模板或网格支持。

原sample继续返回None/空贡献者/outside-or-missing；Sample结构、JSON、批量接口及11列CSV保持。CSV不新增原因列；需要原因的应用应在字段上下文尚在时使用新入口。数值内核（含15轮修复）逐字节不变，15轮极值套件未重跑。

运行 moon run cmd/outcomes --target js（或wasm-gc）查看合成常量场上的6个站点事件和3个解码/筛选事件。双目标各6项相关测试及独立类型匹配消费者分流通过。具体兼容边界见 testdata/outcome16 和VALIDATION.md。

### 先查看自有文件中的字段

独立Node/JS例程examples/node-inventory24接收一个GRIB路径，列出本库实际解码得到的全部字段。每项包含index、规范网格rows/cols、is_global、原origin和product；index从0开始，严格对应read_fields返回顺序，可直接传给原文件采样例程的FIELD_INDEX。origin.field仍是消息内字段序号，byte_offset仍相对当前输入文件，不把它们混作全文件索引。

清单保留原始参数、中心/表版本、参考时间、时效单位与整数、层代码，不猜名称或做日历/单位换算；缺失时效沿用既有JSON规则省略键，分析时效0仍是数字0。它先完整读取并解码所有字段，成功后才输出一份JSON；后续字段不支持或损坏时不会给出误导的部分清单。

本地工作区命令和可运行配套样例见examples/node-inventory24/README.md。testdata/inventory24中的清单可按forecast_time=6找到index2，再由原站点CSV入口选场。主库API、原文件生产器、Python诊断消费者和CSV格式保持；Node22.3+专用宿主，不提供浏览器/Wasm文件I/O。

这是对本库索引与元数据的文件发现入口。上游grib2_mbt及ecCodes已有更广泛的库存/清单功能；本例不是通用替代品，也不是只读头信息的快速扫描器。全部网格仍物化、使用read_fields原预算与模板范围，没有全流程流式、内存或性能保证。

### 从自己的 GRIB 文件生成站点 CSV

独立例程 examples/node-file17 接收已有支持范围内的GRIB文件、站点JSON数组、CSV输出路径和从0开始的字段索引。它读完整文件后明确选择一个字段，保留所有站点行；覆盖域外或无效坐标仍写原有空数值CSV行，同时把sample_result原因写到stderr。成功stdout给出选中字段的来源、产品和行数。

FIELD_INDEX解析失败时，首条stderr事件为selection / invalid-field-index，并标明argument=FIELD_INDEX；随后仍可能有运行时失败栈，退出码非零、stdout为空、输出文件保持未创建或原字节不变。原SDK支持的整数写法继续可用；可解析但超出字段范围的整数保持field-index-out-of-range诊断。完整事件、示例与其它异常边界见examples/node-file17/README.md。

例程限定Node/JavaScript，要求Node22.3+，已在本机Node24.11.0验证；主库仍保持原有JS/Wasm-GC及core依赖合同。站点JSON沿用id/latitude/longitude，接受UTF8和可选BOM；输出保持UTF8、CRLF和原11列，目标已存在时报错，不覆盖。完整工作区命令见 examples/node-file17/README.md。

本轮8个实际文件场景通过，包括真实派生NOAA/IFS输入的两种字段选择、空表、输入错误和原输出保护。读取并独立核对了实际磁盘CSV及既有文件字节；使用历史数值预期，没有重新下载或运行科学参考，也没有重复16轮分流套件。全部旧实现、配置和API哈希保持不变。

这是同步、全量物化的文件宿主例程，不提供Wasm/浏览器文件I/O、远程文件或整条流程流式/性能保证。解码仍验证全部字段，不会跳过不支持字段；原模板和网格范围保持。

### 将失败诊断关联到原站点和 CSV 记录

Node文件例程的sample阶段stderr诊断增加 station_index：从0开始的原始站点数组索引，成功站点也计入序号。因此站点ID重名或为空时，重试程序仍能直接定位该次输入的准确站点；不要求ID唯一，不改写ID。

此索引对应CSV表头之后的逻辑数据记录索引，不是物理文本行号，也不是跨文件的全局站点ID。原phase/station_id/code及CSV、成功摘要保持；严格限定stderr键集合的消费者需允许这个附加字段。旧日志仍可按缺测CSV记录顺序联读，新的辅助程序不自动猜测缺失序号。

可选 Python 标准库例程 examples/node-file17/join_diagnostics.py 接收配套的站点JSON、未重排CSV和成功运行的UTF8 stderr日志，输出已关联的失败记录。可运行的冻结关联样例位于 testdata/correlation18；使用命令见文件例程README。主库和Node生产程序不增加Python依赖。

第18轮3个实际生产／消费关联场景通过，含交错成功、重名/空ID以及有内嵌换行的ID。混合场景CSV与冻结17版逐字节相同，域外重试只取输入1、3，没有误选同名有效站点0。未重复17轮Unicode/BOM/既有输出保护套件。

### Unicode ID 的诊断消费修复（19轮）

可选 Python 消费程序现在只按 JSONL 的 LF 记录边界拆分诊断，保留 ID 中的 U+0085、U+2028、U+2029。原来的 splitlines 会把这些合法字符串字符也当分界，实际3条生产记录被拆成6段，导致 JSONDecodeError。CRLF 记录边界与空行仍可读取，损坏 JSON 仍明确报错。

关联结果采用标准 JSON Unicode 转义输出，避免本机 Windows 默认 GBK 重定向管道因这些 ID 触发 UnicodeEncodeError；解析后的 ID、结果结构和坐标保持原值。没有更改全局编码设置。UTF8 诊断输入要求及原有身份、坐标、缺测完整性校验保持。

本轮使用未变的18轮 Node 编译产物生成1份新输入的实际文件；修复后3项定向消费检查通过：默认 GBK 管道下读取实际 LF 日志、UTF8 管道下读取 CRLF/空行变体、截断 JSON 的错误分支。原站点ID、原因、从0开始的 station_index、CSV字节和全部74份 MoonBit 源码/配置/API 均不变。没有重跑18轮关联、17轮文件或更早套件，也未重新编译未变的 MoonBit 程序。

配套实际文件及期望输出见 testdata/jsonl19；用法见 examples/node-file17/README.md。仅修复这个可选消费者，没有新增模板、网格、接口或Python主库依赖。

### JSON 整数坐标的消费校验修复（20轮）

Node 文件例程原本就把输入坐标读为 Double。JSON 中的整数9007199254740993进入该例程后表示为9007199254740992，CSV也保存这个Double值；Python则把原JSON整数字面量保留为精确整数。此前辅助消费者直接比较CSV浮点数与原整数，会把同一次成功运行的配套文件误判为坐标不一致。

辅助消费者现在仅在坐标校验时把原输入数值转换到相同的Double表示，再作精确比较，不增加容差。返回的station对象仍保留原整数；ID、失败原因、station_index、CSV、JSON解析、LF分界与转义输出均保持。真正不同的Double坐标仍会报错，不提供任意精度坐标输入或恢复精度的能力。

本轮1份新ASCII-ID输入经未变的Node编译产物实际生成4行文件，涵盖正负大整数经度、无效大整数纬度及普通小数对照。最终3项定向消费检查符合预期：配套文件全部关联成功，改动经度与纬度的两个CSV分别被拒绝。独立预期按2^53处的二进制间距与舍入规则确定，并用Decimal核对实际CSV；原输入整数在关联输出中精确保留。实际配套文件见 testdata/coordinate20。

全部74份MoonBit源码/配置/API和Node生产器保持；没有重新编译，也没有重跑19轮Unicode/GBK/UTF8、18轮关联或更早套件。仅修复可选Python消费者的一处比较，不新增格式、网格、依赖或接口。

### 完整来源字段的 CSV 消费修复（21轮）

标量极点采样会保留有效经度行的全部贡献格点。本轮使用1440列、0.25°经度间隔的普通合成常量场，实际生成的contributors_json单元格有164381字符。未变的Node生产器正常写出CSV，PowerShell独立读回全部1440个贡献者；旧Python消费者却触及默认131072单字段上限，尚未关联失败行就报错。

辅助消费者现仅在读取这份本地UTF8文件时，将CSV字段上限临时设为“原上限与文件字节数的较大值”，并用finally在成功或出错后恢复原值。UTF8文件字节数足以覆盖其中单个字段的字符数；不截断来源信息、不改用固定的新大小限制。原严格CSV解析、ID/坐标/缺测校验、JSON错误、LF分界和转义输出保持。

最终3项定向检查符合预期：实际CLI成功关联输入1的outside-grid记录；导入调用在大文件成功后恢复预设上限；派生损坏CSV仍报csv.Error并恢复预设上限。实际配套输入/CSV/诊断及独立读回见testdata/provenance21。合成常量场只用于本次文件消费链，不是天气观测或新的科学参考验收。

全部74份MoonBit源码/配置/API及Node生产器不变，没有新编译或旧套件重跑。本例仍同步物化完整文件；临时CSV上限属于调用进程内模块状态，不提供其它并发CSV读者的隔离或全流程内存/性能保证。

### 关联结果的标准 JSON 输出

站点JSON可以保留应用自己的附带信息。可选Python消费者输出关联结果时，不会把原本合法的1e400等侧栏数字改成不属于JSON语法的Infinity。普通有限结果保持原有排版；超出Python浮点表示范围时，CLI按原station_index取回原始站点JSON片段，保留数字写法，并将非ASCII字符作标准转义。数值不改为字符串或null。

这修复的是JSON交换边界；join()返回的内存对象仍遵循Python原有int/float行为，主库与Node的计算精度没有改变。配套输入在一次调用期间须保持匹配、稳定。CSV、原因、输入序号、LF诊断边界和原有严格错误仍保留。

可运行输入与实际标准JSON输出见testdata/strictjson25，命令见examples/node-file17/README.md。24轮字段清单及原采样入口、CSV格式和核心API均保持。

### 非有限坐标的失败关联

固定SDK的Double JSON解码除了普通数值，也接受特殊字符串"NaN"、"Infinity"、"-Infinity"。这些表示仍是无效坐标：原文件生产器保留空值CSV行并报告invalid-station，不把它们采样成有效数据。普通数字字符串不因此成为新的坐标输入格式。

可选Python消费者按生产器的数值表示核对来源坐标；双方同为NaN时，可关联到同一个原始失败站点。NaN不是通配符，与有限值或Infinity仍不匹配。返回的原站点字符串、ID、序号、原因和全部CSV单元格保持原样，有限数值及Infinity比较沿用原规则。命令与配套文件见examples/node-file17/README.md及testdata/nan26。

## 支持矩阵

| 部分 | 本期范围 |
|---|---|
| 容器 | GRIB2、Section0–8、可选Section2继承、串接消息、多字段 |
| 网格 | 3.0矩形非staggered、非准规则；basic-angle；16种前4扫描位组合 |
| 产品 | 4.0且无附加垂直坐标列表；其他4.x明确拒绝 |
| 数据 | 5.0简单打包、0–32位、负尺度、0位常量 |
| bitmap | 0/254/255、count核对、跨消息重置；中心预定义bitmap拒绝 |
| 后续 | 旋转/高斯/准规则/staggered、5.2/5.3/5.40/5.42、4.1/4.8等不支持 |

值使用Double，有效9999保持有效；缺测只由bitmap决定。复制的底层算法有明确归属，不计作新原创功能。

## 空间与缺测政策

经度相对西端展开；局部网格可跨日界线，越界返回None。全球独立经线满足Ni×Di≈360；重复闭合端点满足(Ni−1)×Di≈360且首尾值/mask一致，重复列不计二次权重。
常规采样为经纬坐标四角双线性，仅正权重缺角导致None，因此准确命中有效节点不受零权重NaN污染。不是球面面积保守重网格；连续性仅限有效覆盖域及相容接缝。
确有±90°标量行时取独立经线有效值均值，全缺测为None。邻接纬带也采用同一极点边界均值，使靠近极点时连续；get保留原值，Sample显示实际贡献。这是明确的数据规整政策，不是WMO通用物理算法。区域极点仅平均区域节点。discipline0/category2风/动量字段保守拒绝涉及极点的采样，不暗中平均经度相关风分量。
不向网格未覆盖的极点外推，不做风向角/矢量基变换或时间插值。

## 参考和真实样本

ecCodes C/Python2.50.0负责解码、元数据和mask；SciPy1.18.1/NumPy2.5.4独立验证站点插值，极点用解析政策验证。交替扫描另按WMO表3.4与独立NumPy置换核对：该版ecCodes坐标迭代没有体现交替行标志，不能无条件当坐标真值。
NOAA GFS与ECMWF IFS的2026-02-21 00Z真实8×6窗口附来源/许可。原压缩为5.3和5.42；测试用5.0转码，**不证明支持原压缩**。
有限值解码断言为1e-10+abs(expected)×1e-12，mask/代码精确比较，坐标按编码角度容差；不是所有物理量的普遍精度保证。实际本地结果见VALIDATION.md。
testdata/SOURCES.json及LICENSES.md记录原件/派生身份；tools/reference含固定依赖及生成脚本。在线源可能限流，静态测试无需源站。

## 许可和交付状态

源码Apache-2.0；来源与适配见THIRD_PARTY.md。NOAA和ECMWF数据保留各自许可，不能重标为源码许可。GitHub Actions配置双目标检查/构建/测试及Node文件、NyaCSV消费者；固定版本与实际命令见.github/CI.md，结论以本仓库[Actions记录](https://github.com/toneklinkenberg824-spec/moonbit-grib2/actions)对应提交为准。尚未发布到Mooncakes、未代交比赛。

### 零位常量缩放修复
零位常量按本期WMO92.9.4公式合同返回 R×10^-D，而非直接R；例如R=10、D=1得到1。独立Decimal/编码回归覆盖D正、零、负及bitmap缺测边界。ecCodes2.50.0在这个非零D特例直接返回R，因此该特例使用公式参考，不宣称与ecCodes完全一致。修复后JS/Wasm-GC各19项定向测试通过；原24字段/62项全套成绩是修复前历史记录，未重跑真实下载链。

### 深入正确性修复05（2026-10-28）

修复极端合法E/D组合的中间溢出/下溢、大有限经度余数丢失、89.999999°误判极点、准确命中节点时的浮点反算缺角误判，以及全缺测字段绕过非有限参考值校验。原有零位常量公式和模板支持范围保持不变。

封闭可变内部状态：`data`、`valid`、`source_indices`、`product_info`现在为私有字段。所有原有公共函数签名保留；直接读取这四个表示字段的外部代码会编译失败，须分别改用`values()`、`mask()`、`point(row,col).source_index`、`product()`。数值、掩码及产品元数据通过访问器返回独立副本。这是明确的字段可见性兼容变更，不宣称整个API零变化。

本轮JS/Wasm-GC各74项定向回归通过，含53项新增回归；独立工作区消费者在双目标上验证拒绝直接改写及复制隔离。新增精确Fraction数值样本观测最大相对误差2.1018510587807206e-14，仅针对这些样本。未重跑旧24字段全套或下载链。当前源身份与日志索引见`testdata/deep-repair05/`和VALIDATION.md。

### 精细网格边界修复06（2026-10-28）

精确命中`point()`返回的边缘节点时，先恢复节点索引，再进行越界判断，避免微度及更细basic-angle网格被浮点反算误拒。`crop()`使用一致的规范经度与闭区间比较，移除会在细网格上多选邻列的固定角度扩张；零宽经度框只选该经线，空的格间区间保持空。

本轮JS/Wasm-GC各22项定向检查通过（11项新增边界回归及11项相关回归），独立工作区JSON消费者在双目标通过。公共API无变化；未重跑旧24字段全套、下载链或未变化的05数值集合。详见VALIDATION.md及`testdata/boundary06/`。

### 编码与消息校验修复07（2026-10-28）

网格头在经度环绕和Double转换前，按编码整数与basic-angle比例校验经纬度和推导范围，拒绝被固定角度容差掩盖的非法范围。合法极点坐标先形成整数分子再除角度分母，避免精确90°变成90.00000000000001。查询经度继续周期环绕；每条消息都必须包含字段，拼接流中的空消息显式报错。

JS/Wasm-GC各55项定向回归通过（19项新增），独立工作区消费者双目标通过，公共API无变化。新增时间/表面层边界参考保留ecCodes2.50.0在本Windows环境对高UInt32和全一forecastTime的访问器分歧；本库按原始无符号值和WMO缺失码语义保留元数据。详见VALIDATION.md及`testdata/encoding07/REFERENCE.json`。

### 小量值采样修复08（2026-10-28）
全部贡献值为subnormal Double时，先作精确二进制尺度平移再加权求和，避免有限非零结果提前丢成0；普通范围沿用原算术路径。分阶段JS/Wasm-GC各35项修复回归及7项新请求工作流测试通过，示例和独立消费者也在双目标通过。没有重跑旧24字段下载链；当前证据见VALIDATION.md。
