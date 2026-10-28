# 自有GRIB文件到站点CSV：Node/JS例程

参数顺序：

    GRIB_PATH STATIONS_JSON OUTPUT_CSV FIELD_INDEX

FIELD_INDEX仍交给项目SDK原有整数解析器处理，包括已验证的+2、02、0x2、0b10、0o2、0_2和-0写法。无法解析为SDK Int的文本（包括小数写法和Int溢出）会在读取输入文件前，以非零退出码终止，stdout为空；首条stderr事件为：

    {"phase":"selection","code":"invalid-field-index","argument":"FIELD_INDEX"}

其后仍可能有MoonBit运行时失败栈。消费者应读取首条JSON事件并检查退出码；目标CSV保持未创建或原字节不变。已解析但为负/超出字段数量的整数继续使用原field-index-out-of-range诊断。参数数量、输入I/O/JSON、解码和写入异常沿用原路径；这个事件只分类索引解析失败。

字段索引从0开始，按read_fields返回顺序。成功stdout是包含产品/来源/行数的JSON摘要；CSV写入指定文件。stderr保留站点失败原因，解码与索引错误留在外层。JSON数组中每项需要id字符串、latitude/longitude数字；UTF8和可选BOM均支持。固定SDK也解码非有限Double的特殊JSON字符串"NaN"、"Infinity"、"-Infinity"；它们仍按无效坐标处理，不表示可用采样。坐标无效/区域外仍保留对应空数值CSV行，JSON缺字段则整次失败。

需要固定项目SDK可用及Node22.3+（实际Node24.11.0通过）。这是Node/JavaScript专用宿主例程；主库依赖/API未改，不是浏览器或Wasm文件I/O程序，也不增加GRIB格式支持。

从moonbit-grib2根目录，在新的PowerShell工作目录中建立本地绑定：

    $LibraryRoot = (Get-Location).Path
    $DemoRoot = Join-Path $LibraryRoot '.node-file17-workspace'
    New-Item -ItemType Directory -Path (Join-Path $DemoRoot 'consumer') | Out-Null
    Copy-Item examples/node-file17/main.mbt,examples/node-file17/moon.mod,examples/node-file17/moon.pkg (Join-Path $DemoRoot 'consumer')
    $Noaa = [IO.File]::ReadAllBytes((Join-Path $LibraryRoot 'testdata/noaa-gfs-repacked.grib2'))
    $Ifs = [IO.File]::ReadAllBytes((Join-Path $LibraryRoot 'testdata/ecmwf-ifs-repacked.grib2'))
    [IO.File]::WriteAllBytes((Join-Path $DemoRoot 'own.grib2'), [byte[]]($Noaa + $Ifs))
    Set-Location $DemoRoot
    moon work init
    moon work use "$LibraryRoot" consumer
    moon -C consumer check --target js
    moon -C consumer build --target js
    moon -C consumer run --target js . "$DemoRoot/own.grib2" "$LibraryRoot/examples/node-file17/stations.example.json" "$DemoRoot/IFS-stations.csv" 1

示例输出3行：IFS站点约239.75051879882812，GFS位置在所选IFS窗口之外为空，纬度91无效为空。stderr分别给出outside-grid和invalid-station，并携带原始station_index=1和2。字段索引0可选择NOAA场，使用新的输出文件名；程序拒绝覆盖现有文件。也可把own.grib2替换为自己的受支持文件。输入中任一字段损坏或不支持时，read_fields整次报错，不跳过其它字段。

这些文件绑定/源码已实际check/build/run；报告还直接运行了相同编译后的Node JS程序。17轮封存的8个文件场景为两种字段选择、空站点表、站点缺字段、越界索引、损坏GRIB、缺失输入与既有输出。实际文件字节以独立CSV/JSON解析器读回。库的旧测试和16轮分流场景未重跑。

程序为同步全量例程：输入、网格、站点、样本和CSV均物化；只保证输入验证在输出写入之前，已有输出由exclusive-create保护，不提供异常退出/磁盘失败的事务写入保证。CSV仍是原11列，不添加源文件名/失败原因列；保留调用参数与摘要来关联文件。Node文件错误可直接显示运行时错误。

NOAA/IFS示例是历史8x6窗口的5.0转码，原始5.3/5.42仍不支持；许可与来源见 ../../testdata/LICENSES.md、../../testdata/SOURCES.json。站点列表示例数据，输入文件名可自选。无下载、联网服务、npm包或额外Mooncakes依赖。


## 重名／空ID的诊断关联（18轮）

sample阶段诊断新增station_index，从0开始索引原始站点数组，成功行也计数。它对应CSV逻辑数据记录（不含表头），不是物理行号；内嵌换行不影响索引。旧phase/station_id/code保留，不限制ID唯一性。严格诊断JSON键集合的消费端需允许新键。

可选Python标准库消费程序：

    python examples/node-file17/join_diagnostics.py testdata/correlation18/stations.json testdata/correlation18/result.csv testdata/correlation18/diagnostics.jsonl

从项目根目录运行以上命令，使用本轮实际执行后封存的配套样例，返回输入1、2、3、4的失败关联记录。按code=outside-grid筛选会只得到输入1和3，跳过同名但有效的输入0。它输出原始station和完整csv_record，应用可据此生成重试子集，不按ID猜测。

实际使用时传入同一次成功运行的原站点JSON、未重排CSV及以UTF8保存的原stderr日志；宿主应保留stderr原始字节。Python只用于这个可选消费者，主库和Node生产器均不依赖Python。旧日志没有station_index时程序明确报错；旧的按缺测CSV记录顺序联读仍可由应用使用。

本轮3个新关联场景（交错成功、全成功、有换行的全失败重名ID）及旧日志错误分支通过实际生产/消费验证。没有重跑17轮Unicode/BOM/既有输出保护套件。CSV格式和字节、原因合同、解码/筛选阶段均保持；索引只在本次调用中有效，不是全局身份或文件签名。

## Unicode ID 消费修复（19轮）

诊断文件仍要求UTF8，并保留本次成功运行的原始字节。消费程序按LF读取JSONL记录；CRLF和空行继续接受。ID中的U+0085、U+2028、U+2029属于字符串内容，不作记录分界，不替换或拒绝它们。

输出使用标准JSON Unicode转义，例如字符串内的U+2028写为\u2028。对输出执行JSON解析后仍得到原ID；关联对象结构、station_index和code不变。ASCII形式的JSON可经过本机默认GBK重定向管道，无需修改全局Python或控制台编码。此前ensure_ascii=False在这个实际管道下会触发UnicodeEncodeError。

从项目根目录读取本轮实际封存的3条匹配记录：

    python examples/node-file17/join_diagnostics.py testdata/jsonl19/stations.json testdata/jsonl19/result.csv testdata/jsonl19/diagnostics.jsonl

输出对应输入索引0、1、2，原因均为outside-grid；每条保留原站点和完整CSV逻辑记录。testdata/jsonl19/joined.expected.json是最终实际stdout的原始字节。该输入的GRIB仅为已有合成常量场，不是天气观测或实时预报。

这次最终验证包含实际LF日志/默认GBK管道、CRLF与空行/UTF8管道，以及截断JSON仍失败，共3项定向检查。原JSON解析和身份、坐标、缺测完整性检查保持；主库、Node生产器、CSV及失败原因均不变。18轮3个关联场景和17轮文件套件是历史证据，本轮未重跑。

## JSON 整数坐标的关联（20轮）

生产器的latitude/longitude是Double。大整数字面量超出精确表示范围时，CSV记录的是原生产器读入的Double，例如9007199254740993表示为9007199254740992。辅助消费者现按相同数值表示核对两个坐标，避免Python精确整数与CSV浮点数的错误不等比较。

这次只转换校验表达式的操作数，输出station对象仍保留原JSON整数；没有放宽为近似容差，也不恢复生产器已舍入的精度。相差一个可表示Double的经度或实际不同的纬度仍明确报错。原输入ID、原因、索引与CSV不变。

从项目根目录运行本轮实际配套样例：

    python examples/node-file17/join_diagnostics.py testdata/coordinate20/stations.json testdata/coordinate20/result.csv testdata/coordinate20/diagnostics.jsonl

结果包含输入0、1、2、3，原因依次为outside-grid、outside-grid、invalid-station、outside-grid。前两项的原经度为正负9007199254740993，第三项的原纬度也是该精确整数；它们在输出station中保持，CSV坐标按既有Double表示保留。最后一项是普通小数对照。合成区域场不是天气观测或实时预报。

本轮最终检查是配套文件成功、实际改动经度失败、实际改动纬度失败，共3项。未重跑19轮Unicode/管道检查或18轮关联套件。LF记录分界、ASCII安全JSON输出、解析错误和其他校验代码均原样保留；源码差异和独立读回在本轮报告中。

## 大来源字段的读取（21轮）

极点行可以产生较大的contributors_json单元格；生产器不会因为Python解析器的默认字段上限而删去这些来源。辅助消费者现在按当前UTF8文件的字节数临时允许完整字段，并在读取成功或失败后恢复原csv.field_size_limit。严格CSV解析及之后的原有校验不变。

从项目根目录运行本轮实际封存的配套文件：

    python examples/node-file17/join_diagnostics.py testdata/provenance21/stations.json testdata/provenance21/result.csv testdata/provenance21/diagnostics.jsonl

CSV有2条站点记录：有效极点行的单元格保留1440个贡献者，另一条输入1在覆盖域外。程序需要先完整读取CSV，随后只输出输入1的失败关联对象，code为outside-grid。164381字符的来源字段曾超过本机默认131072上限；该文件已由PowerShell的CSV/JSON消费者独立完整读回。joined.expected.json是最终实际CLI输出。

这次最终检查包括实际CLI读取、导入join调用成功后的上限恢复，以及严格CSV错误后的上限恢复。原整数/ID/原因/index/CSV和生产器保持；没有重跑20轮数值、19轮Unicode/管道或18轮关联套件。CSV与JSON解析错误继续向调用者报告。

该辅助例程仍读取并保存整份本地文件的数据，不是流式解析器。字段上限暂存于Python进程的csv模块并通过finally恢复；本例面向顺序调用，不提供其它并发CSV读者的隔离。它不修改持久Python配置或控制台编码，也不承诺任意大小文件的内存或速度。

## 标准 JSON 与原站点侧栏数字

站点除了必需的id/latitude/longitude，也可能带有调用方自己的metadata等
侧栏。CLI结果保留这些原站点内容；合法的1e400等数字不会被Python默认
编码器写成不属于标准JSON的Infinity，也不转换为字符串或null。原CSV和
失败诊断仍按原方式关联，输入文件在整个调用中须匹配且保持不变。

从项目根目录运行配套实际文件：

    python examples/node-file17/join_diagnostics.py testdata/strictjson25/stations.json testdata/strictjson25/result.csv testdata/strictjson25/diagnostics.jsonl

输出的两个失败对象仍保留原索引0、1及outside-grid原因，包含原侧栏的
1e400、-1e400、嵌套值、中文和emoji。joined.expected.json是实际最终stdout，
可直接用严格Node解析器读取：

    node -p "JSON.parse(require('node:fs').readFileSync('testdata/strictjson25/joined.expected.json','utf8')).length"

普通有限结果仍使用原ASCII转义和缩进，有限对照的输出已与旧版逐字节
比较。只有普通编码无法表示数值时，CLI才用标准JSON解码器确定原站点
元素边界，按原station_index保留其数字文本；回退排版可能与普通路径不同。
sparse-stations.json配套样例中，成功站点在输入1，返回对象使用原索引0、2。

这不提供任意精度运算。Python join()内存结果仍使用原int/float类型；下游
如需保留大数精度，应选择合适的数值解析类型。CLI保证的是有效JSON语法
与原站点数字的合法写法，不宣称每种运行时都能有限地计算这些数值。
严格CSV、JSON解析和先前的字段上限恢复、坐标比较、LF诊断边界均未改动。
主库、Node生产器和字段清单也未改动，没有新增依赖或编码设置。

## 非有限坐标的原失败行关联

固定SDK的Double FromJson已有特殊字符串NaN/Infinity/-Infinity表示；生产器
仍把它们判为invalid-station并保留空值CSV行。消费者核对原站点与该行时，
双方同为NaN代表同一类原坐标，不能用NaN不等于自身的数值算术规则误拒。
与有限值、Infinity或其它不匹配坐标的比较仍失败，NaN不是通配符。

从项目根目录运行真实配套输入：

    python examples/node-file17/join_diagnostics.py testdata/nan26/stations.json testdata/nan26/result.csv testdata/nan26/diagnostics.jsonl

结果保留输入0的NaN纬度、输入1的NaN经度及输入2的区域外普通坐标，原因
依次为invalid-station、invalid-station、outside-grid。原站点中的NaN保持
JSON字符串，CSV中的原坐标文本和空数值保持，不变成null或有效坐标。
joined.expected.json是实际最终stdout。control-*配套文件用于有限数值和
Infinity字符串的原行为对照；wrong-kind.csv故意与原NaN坐标不符，应报错。

该改动只处理关联身份，不改变采样算术、无效站点分类或原生产器接受规则。
25轮原数字词法输出函数及有限输出兼容行为保持；CSV/JSON严格错误、LF
记录边界、原输入序号及临时字段上限恢复均保持。没有新增依赖或全局设置。
