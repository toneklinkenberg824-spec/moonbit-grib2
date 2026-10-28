# 自有GRIB文件的字段清单：Node/JS例程

参数：GRIB_PATH。成功stdout是一份JSON：field_count和fields数组。每项包含
index、rows、cols、is_global、origin、product。index是从0开始的全文件字段
序号，可直接用作../node-file17的FIELD_INDEX；origin.message/field仍表示
消息与消息内字段，byte_offset相对本次输入文件。更换输入后应重新列场。

需要项目固定SDK及Node22.3+；实际环境为Node24.11.0。主库仍只依赖core，
本例不引入npm、Python或额外Mooncakes包。没有将模块发布到注册表。

从moonbit-grib2根目录在新的本地工作目录建立绑定：

    $LibraryRoot = (Get-Location).Path
    $DemoRoot = Join-Path $LibraryRoot '.node-inventory24-workspace'
    New-Item -ItemType Directory -Path (Join-Path $DemoRoot 'consumer') | Out-Null
    Copy-Item examples/node-inventory24/main.mbt,examples/node-inventory24/moon.mod,examples/node-inventory24/moon.pkg (Join-Path $DemoRoot 'consumer')
    Set-Location $DemoRoot
    moon work init
    moon work use "$LibraryRoot" consumer
    moon -C consumer check --target js
    moon -C consumer build --target js
    moon -C consumer run --target js . "$LibraryRoot/testdata/inventory24/forecast.grib2"

该合成文件有4个字段，均为2x3区域网格；清单中原时效依次是缺失、0、6、-6。
缺失时效不输出forecast_time键，0则明确输出数字0。时效6的index为2，
origin是message2/field0/byte_offset359。它与全文件索引2不可互换命名。
这些数据不是天气观测或实时预报。

把同一GRIB路径、原站点JSON、一个新的CSV路径和index2交给
../node-file17/README.md中的生产程序，即可选中该场；本库例程实际生成的
2行配套结果位于../../testdata/inventory24/selected.csv，值为333和空值。
清单JSON及失败诊断样例也在该目录，可按原产品代码筛选，禁止假定名称或
日历换算。原始文件上下文仍由调用方保留，清单不是全局身份或文件签名。

程序使用原read_fields完整验证并解码全部字段，之后一次输出JSON；不支持
或损坏的后续字段使整次失败，stdout为空。stderr保留解码原因并以非零码
退出，文件IO问题仍显示运行时错误。刻意的失败样例：

    moon -C consumer run --target js . "$LibraryRoot/testdata/inventory24/later-unsupported.grib2"
    moon -C consumer run --target js . "$LibraryRoot/testdata/inventory24/later-truncated.grib2"

它不是头信息扫描器，不绕过不支持字段，不提供额外网格/压缩/PDT能力、
浏览器/Wasm文件IO、流式或性能保证。默认每字段点数预算仍为read_fields
的10000000。原主库API、采样器、CSV生产器和可选Python消费者均未修改。

上游已有类似库存能力；本例的用途是明确给出此采样库的索引与原Product/
Origin，而不复制新解析器。比较依据：
[MoonBit上游清单接口](https://github.com/trkbt10/grib2_mbt/blob/main/wgrib2_facade.mbt)，
[ecCodes官方字段检查教程](https://confluence.ecmwf.int/spaces/ECC/pages/362415536/Introduction+Tutorial+on+GRIB+decoding+with+ecCodes+inspecting+GRIB+files+with+the+GRIB+tools)。
