# 预报有效时刻的完整文件接收方

Node/JS独立例程，要求Node≥22.3（CI为24.11.0），只接收一个参数：

    INPUT_GRIB

它完整解码任意受支持文件，对每个字段调用新增公共`Product::valid_time()`，
将原始index/Origin/Product和时间推导结果一起输出为一个JSON。
这是本项目自建接收方，不表示第三方采用或部署。

源码依赖尚未发布。从源码父目录执行（源码目录名moonbit-grib2；Bash语法）：

```sh
mkdir validity-work
cp -r moonbit-grib2/examples/node-valid-time validity-work/receiver
cd validity-work
moon work init
moon work use ../moonbit-grib2 ./receiver
moon -C receiver build --target js
node _build/js/debug/build/local/grib2-valid-time/grib2-valid-time.js \
  ../moonbit-grib2/testdata/valid-time/calendar.grib2
```

Windows也可手工复制同一目录并运行同一workspace。成功stdout是一个对象：
`field_count`以及按原字段顺序的`fields`数组。每行含`index`、`origin`、原`product`及`time`。
time是以下二者之一：

```json
{"valid_time":{"year":2024,"month":2,"day":29,"hour":0,"minute":0,"second":30}}
```

```json
{"error":"unsupported-time-unit","unit":3}
```

其它时间错误码为`missing-forecast-time`、`invalid-reference-time`、
`unsupported-leap-second`、`out-of-range`。单字段时间推导失败是保留该字段的结果，
不会删除其它字段或使全文件失败；原Product仍完整保留，缺失时效也不冒充0。

推导采用显式的前推公历民用时间政策：参考和结果年份1..9999、六分量、每天86400秒。
固定单位为GRIB表4.4中的0分钟、1小时、2天、10三小时、11六小时、12十二小时、13秒。
参考日期须合法；合法日期中的second60专门报不支持闰秒。月/年/十年/normal/世纪、
reserved/local/missing单位不换算，即便lead0也失败。负lead保留，所有乘法先扩大为Int64，
结果越出支持年份报错。错误优先级为缺失lead→不支持单位→坏参考→闰秒→结果越界。

此政策把GRIB的UTC参考分量当作固定日长公历分量计算，不插入或累计闰秒；跨2016年末的
23:59:59加1秒得到次日00:00:00。它不是闰秒感知的物理UTC/TAI间隔计算，无时区/DST转换。
原码查询继续区分6小时与360分钟，二者仅在显式推导结果中可指向相同历法时刻。
旧解码器仍接受的日期/单位不因新增方法而被拒绝，原选择、采样、CSV、错误均不变。

完整解码失败时沿用原结构化`decode`事件、非零退出且stdout为空，后面才坏的消息也不会
留下看似完整的前缀JSON。用法和宿主IO错误保留原非零诊断；不承诺统一JSON错误。
程序不写输出文件；shell重定向由宿主处理。输入/解码/结果全部物化，不承诺流式、恒定
总内存或新模板/科学精度支持。纯时间API可用于JS/Wasm-GC；本文件IO入口仅Node/JS。

新案例、原码与独立Python日期核对见`testdata/valid-time`和`.github/scripts/check-valid-time.py`。
