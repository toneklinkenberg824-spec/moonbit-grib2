# 固定单位预报有效时刻的冻结参考

EXPECTED.json含实现前逐项手写的51个新历法案例，SHA256：
`42e6938e1f503eddfdaf5868d99f8e7b328673a04614b4b04c021faca99cf60e`。
覆盖7个固定单位、0/负/Int边界lead、分钟/天/月/年进位、1900/2000/2100世纪闰日、
前推公历1500年、年份1..9999边界、缺失/坏参考/second60、calendar/reserved/local/missing单位
及错误优先级。51是本轮历法案例数，与旧51份framing向量无关。

calendar.grib2包含43个可用原GRIB头表达的案例。来源为既有inventory24/forecast.grib2
offset180的179-byte简单打包常量消息；仅按已冻结案例改Section1参考分量和Section4
单位/符号时效，保留其网格/bitmap/数据及原出处。不是新天气数据、压缩支持或科学观测。
公有Product可表达而原头无法表达的空/长参考、负单位和Int.min由外部公共消费者直接构造。
每个原消息长179，Origin/原码与完整文件哈希在EXPECTED中冻结。

验收先用Python datetime独立核对所有手写预期，再独立读取Section1/4验证原始身份；
生成一个只导入公共模块的独立工作区消费者，JS/Wasm-GC各运行51个Product案例、43个
原文件字段及一次原码查询不变检查。每次推导前后原Product/字段元数据均须保持。
6小时与360分钟推导同历法时刻，但原码唯一选择仍分别命中各自消息。

Node接收方再读实际Unicode路径calendar文件及既有NOAA原文件的时间元数据；外部Python
逐字段核对完整JSON。空文件、缺输入、用法、unsupported及晚到unsupported/坏尾必须
非零且无成功stdout；单字段时间错误则完整保留为结果。不重跑旧科学参考或天气采样。
第一次消费者生成器缺返回类型的编译失败日志保留，不改预期过关。

政策为前推公历、年份1..9999、每天86400秒，不插入闰秒。Python只是该新政策的独立
日历算术对照，不是对物理UTC/TAI、月年步长、所有WMO单位或原压缩的认证。
单位来源：[ECMWF表4.4](https://codes.ecmwf.int/grib/format/grib2/ctables/4/4/)；
日历参考：[Python datetime](https://docs.python.org/3/library/datetime.html)。
