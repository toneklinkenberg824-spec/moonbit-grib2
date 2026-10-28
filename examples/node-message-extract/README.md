# 按原消息序号交付原字节文件

Node/JS独立例程，沿用其它Node例程的Node≥22.3要求（CI为24.11.0）。

    INPUT_GRIB OUTPUT_GRIB MESSAGE_INDEX

MESSAGE_INDEX从0开始，是上游manifest给出的原消息序号，不是解码字段序号。
命令读取完整输入，使用根级index_message_spans检查所有framing，再把选中消息的
原字节写入一个新文件。支持模板与不支持模板都可原样交付，不解网格、不重打包，
多字段原消息保持为一个消息。它不是按参数/时效搜索或模板支持检测。

源码依赖尚未发布。下面从源码的父目录运行（假定源码目录名moonbit-grib2；Bash语法）：

```sh
mkdir extract-work
cp -r moonbit-grib2/examples/node-message-extract extract-work/extractor
cd extract-work
moon work init
moon work use ../moonbit-grib2 ./extractor
moon -C extractor build --target js
node _build/js/debug/build/local/grib2-message-extract/grib2-message-extract.js \
  /absolute/mixed.grib2 /absolute/selected.grib2 1
```

在Windows也可手工复制同一目录并用PowerShell创建/运行同一workspace。
输出必须是新路径，父目录须已存在。程序直接以wx独占创建，已有文件和输入文件均不覆盖；
不先用exists/access检查，也不删除文件。写完后重新读取输出逐字节比较，成功才输出一行JSON：

```json
{"input":"...","output":"...","span":{"index":1,"byte_offset":185,"length":251,"edition":2,"discipline":0},"bytes_written":251,"input_sha256":"...","output_sha256":"..."}
```

input_sha256来自实际读入的整文件字节，output_sha256来自实际读回的选片字节；它们不是文件锁或可信签名。
保留这条外部span/输入哈希记录，再把输出交给原node-inventory24或node-file17。
下游Origin仍相对选片文件，通常message0/byte_offset0，不替换为原文件全局身份。
需要选择multi-field里的字段时，下游FIELD_INDEX与本命令MESSAGE_INDEX分开使用。

无效Int在读输入前以selection/invalid-message-index诊断失败，argument为MESSAGE_INDEX；
沿用当前SDK支持的Int语法（已验证+1、01、0x1、0b1、0o1、0_1）。可解析越界值报
selection/message-index-out-of-range及message_count。framing错误报framing/code/原byte_offset。
这些校验失败均非零退出、stdout为空、不创建输出，原有目标保持原字节。
用法及宿主IO错误保留原失败信息和非零退出，不承诺统一JSON；结构化事件后也可能有运行时堆栈。

读回字节不一致报verification/output-readback-mismatch，不给成功摘要。
写入/读回IO失败或验证失败可能留下刚创建的新文件供检查；不承诺原子回滚、断电持久性。
输入/解码未流式化，不承诺恒定总内存或性能收益；不支持模板仍会被下游原解码器拒绝。

文件边界验收见testdata/message-extract和.github/scripts/check-message-extract.py。
