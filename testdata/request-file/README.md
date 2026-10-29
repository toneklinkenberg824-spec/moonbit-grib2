# 外部查询配方的文件接收验收

`weather-requests.json`和`weather-stations.json`是可由用户维护的外部JSON文件。
key/ID刻意含完整空白、引号、CRLF、Unicode和空ID，CSV读回必须保持原字符串。
EXPECTED.json在实现前冻结，SHA256为
`a701120af92c875b467c14482642acab4419cde46d575f62a2a4876be60085b4`。

脚本使用仓库既有NOAA GFS251-byte及ECMWF IFS268-byte原件，按GFS+IFS和IFS+GFS
生成两个新输入文件。相同外部命名配方两次产生同序值253.6234765625/null/null/
239.85598754882812，来源message/byte_offset随实际布局变化。旧numeric FIELD_INDEX0
分别取首字段，因此结果依赖文件顺序，这是原命令合同，未声称旧实现有缺陷。
天气值复用已验收consumer13/REFERENCE.json，不下载天气或重跑科学参考生成器。

既有query-inspection/catalogue.grib2提供手写原码/常量身份，用于新的JSON解释边界：
省略/null/0时效、全部可选原码过滤项、不同缩放Surface、原单位360分钟与6小时，
命中101/202/303/404/606及其原始身份。inventory24/forecast.grib2的−6时效常量444
另验证负整数输入。不重跑旧目录/时间/科学套件，不把已有查询API能力计为新功能。

`.github/scripts/check-request-file.py --work /new/temporary/directory`实际构建并运行
新接收器及未变旧file17命令。外部CSV parser读回11列及嵌入CRLF，核对请求/站点顺序、
值、Origin、Product、贡献者JSON及计数。用不存在的GRIB路径验证schema错误先于数据IO；
整数性/范围、未知键、坏JSON、空/重复key、晚到的缺场/歧义、reference长度、原错误、
空请求/站点、NaN坐标、已有目标保护及IO/用法均有真实进程检查。
脚本保留每次调用stdout/stderr和COMMANDS.json；失败目录保留，必须使用新work目录。

接收器完整解码/选择/采样成功后才以wx创建CSV；这是写前选择完整性，不是文件事务。
新增运行目标仅Node/JS。输入/字段/结果/CSV仍物化，不声称全流程流式、性能改进或支持新模板。
根库、旧例程、科学参考、作者/模块/许可和旧支持范围保持。
