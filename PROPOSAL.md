# GRIB2 可追溯分层站点采样库
当前维护与申报账户：toneklinkenberg824-spec；模块：toneklinkenberg824-spec/grib2。原源码署名：zhou-wei97。
将GRIB2参数、层和批次转为可追溯站点/区域结果，供MoonBit报表、可视化和科研前处理使用。

- 支持串接消息/多字段、3.0矩形非staggered网格、4.0产品、5.0简单打包0–32位；单例轴端点相符时允许0/缺失步长且不外推。损坏或不支持输入显式报错。
- 根级span只检framing，不复制raw或建段上下文。Node按原消息序号写新文件并读回核span/哈希；不证明模板/完整语义，解码Origin仍相对选片。
- 规整16种扫描及bitmap0/254/255为北→南、西→东矩阵，保留原扫描索引；Double值由bitmap判缺测，有效0不丢。
- 按参数/中心/表/层/起报原码唯一取场并列候选，缺场/歧义报错。任意/缺失/0时效独立；固定单位公历有效时刻支持闰日、负时效与越界诊断，拒绝月年和闰秒。
- 命名站点双线性采样支持经度环绕，仅正权重缺角阻断结果；标量极点采用显式有效行均值政策，涉及极点的风/动量采样保守拒绝。
- 结果保留Product/Origin、格点贡献及权重，类型化区分坏坐标、域外、缺测、极点限制；缺测为None/JSON null并保留CSV行。
- 同有效时刻两场逐站计算right−left，核参数/表/层原码，保留双方来源、失败及差值溢出；不作模式校准或网格相减。
- 区域原节点保留坐标/缺测/扫描索引，可迭代早停；Node按文件/bbox交付完整JSONL，非面积重网格。
- 导出11列CSV并处理引号/换行，支持整串/逐记录/按需采样。文件入口按索引或命名JSON配方取场；Python关联原站点与失败，保留大整数附带信息。

主库仅依赖MoonBit core，支持JS/Wasm-GC；宿主提供字节。Node≥22.3承担文件IO，Python辅助关联，NyaCSV消费者另锁兼容依赖。输入/解码网格仍物化，不承诺全流程流式或恒定内存。
离线运行 `moon run cmd/main --target js`：coastal-gap为null，inland为4.5（原值4/5，各权重0.5）。源码工作区及自有文件接入见README。
实际复用[trkbt10/grib2_mbt](https://github.com/trkbt10/grib2_mbt)固定提交的解析/解包组件，底层算法归属上游。独立贡献是原始语义取场、采样/缺测解释、来源追踪、区域提取、文件导出链和已复现编码/数值修正，不把解析器或通用CSV冒充原创。
验证包含双目标构建、独立消费者、ecCodes/SciPy/精确算术对照及已记录分歧；真实NOAA/IFS小窗口经5.0转码，不代表支持原5.3/5.42压缩。远端结论以同提交Actions为准。
不支持旋转/高斯/准规则网格、其它压缩/产品模板、时间插值、层单位/矢量基变换；详细政策见README。
源码：[GitHub仓库](https://github.com/toneklinkenberg824-spec/moonbit-grib2)。Apache-2.0及原作者/上游归属保留。NOAA样本遵守[公共领域条件](https://www.weather.gov/disclaimer)，ECMWF样本遵守[CC-BY-4.0及ECMWF条款](https://www.ecmwf.int/en/forecasts/datasets/open-data)；样本裁剪/转码及人工编码来源见THIRD_PARTY.md、testdata/LICENSES.md。
