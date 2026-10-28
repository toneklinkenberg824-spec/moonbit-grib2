# NyaCSV逐记录业务消费例程

这是独立MoonBit模块，主GRIB2库仍只有core依赖。例程从既有按需采样CSV迭代器取完整逻辑记录，缓存表头，每次解析表头加一条记录；检查11列结构，保留文本ID，再显式解析数值和两个JSON列。它不复制第三方解析器，不给主库增加接口。

已验证SDK：moon0.1.20260904。依赖锁定 moonbit-community/NyaCSV 源码提交 fe4448e1e45a25f6fca151320c766519e80162c9（moon.mod声明0.3.3）。当前0.3.4源码使用Int32，在此SDK下编译失败；这里不声称注册表安装已验证。以下命令用固定源工作区，需Git和可访问GitHub。

从解压后的moonbit-grib2根目录，在PowerShell中执行，使用一个新的工作目录：

    $LibraryRoot = (Get-Location).Path
    $DemoRoot = Join-Path $LibraryRoot '.nyacsv13-workspace'
    New-Item -ItemType Directory -Path (Join-Path $DemoRoot 'consumer') | Out-Null
    Copy-Item examples/nyacsv13/main.mbt,examples/nyacsv13/moon.mod,examples/nyacsv13/moon.pkg (Join-Path $DemoRoot 'consumer')
    Set-Location $DemoRoot
    git clone --no-checkout https://github.com/moonbit-community/NyaCSV.git NyaCSV
    git -C NyaCSV checkout --detach fe4448e1e45a25f6fca151320c766519e80162c9
    moon work init
    moon work use "$LibraryRoot" consumer NyaCSV
    moon -C consumer check --target js
    moon -C consumer build --target js
    moon -C consumer run . --target js

wasm-gc把最后三条命令的目标改为wasm-gc。该工作区绑定方式和相同模块源码已在两目标实际check/build/run通过；消费源码、固定依赖和工作区编译产物均记录哈希。

输出为9条业务JSON行及4条场景统计：real4、preview1、numeric4、empty0。cells数组保存原始11格字符串；value明确区分null和0，product/contributors是已解析JSON。REFERENCE.json给出独立预期。0007保持字符串，标签中的空白、引号、CRLF与emoji原样保留。预览在请求下一条数据前检查条数限制。

本例接收可信且完整的本库CSV记录；内嵌换行不等于记录边界。NyaCSV解析器无公开错误Result，本例不作为不可信CSV或任意字节分片的严格验证器，也不承担宿主文件/网络IO。按记录处理仍有当前字符串和单行表格分配；输入网格和站点列表已预备，无恒定内存、RSS或速度保证。

真实字节使用已收录的NOAA/IFS8x6简单打包派生样本，许可与变换见 ../../testdata/LICENSES.md 和 ../../testdata/SOURCES.json。synthetic-zero-analysis.grib2由forecast09前两条合成消息派生，仅把第一场的IEEE754参考值111改为0，E=D=0、位宽0和bitmap不变；不是实际预报或新的外部参考运行。第三方NyaCSV源码/许可由Git克隆保留，本包只包含调用它的例程。
