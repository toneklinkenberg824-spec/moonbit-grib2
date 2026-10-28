# Third-party provenance

## Actual source reuse
internal/upstream_context、internal/upstream_core、internal/upstream_unpack为[trkbt10/grib2_mbt](https://github.com/trkbt10/grib2_mbt)提交00c30ee9a31adca0a15157f1b93ac7269415b9d3的实际适配源码。其manifest版本0.1.0，不等于已确认Mooncakes发布。Apache-2.0许可证保留在internal/LICENSE-UPSTREAM，原始/适配哈希见UPSTREAM-LOCK.json。

context/core沿用原文件名；unpack来自typed/section7/grib2_bitstream_reader.mbt和grib2_data_unpacker_simple.mbt。消息状态机和位流算法属于复用，不计为新增原创。
局部适配：context导入命名空间；parser长度推进改用先减后比较避免整数绕过；截断组诊断改为读取有效section下标；simple packing首行公式注释纠正。另有moon fmt格式变动。保留上游旧语法产生的deprecation warnings，不把未使用的JPEG2000依赖带入运行链。

## 新增部分
根目录headers/reader/types/sampling实现固定模板头适配与验证、坐标/掩码/原点绑定、产品元数据、批量站点采样和区域提取。极点规整为本库显式标量政策，不冒充标准算法。

## 规范和参考工具
- WMO/ECMWF法规：https://codes.ecmwf.int/grib/format/grib2/regulations/
- NOAA3.0/4.0/5.0及扫描3.4：https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/
- 已核表面缩放编码：https://github.com/ecmwf/eccodes/blob/2.50.0/definitions/grib2/templates/template.4.horizontal.def
- ecCodes2.50.0为外部验证工具（Apache-2.0及ECMWF条款），不随产品分发C库。
- SciPy1.18.1、NumPy2.5.4为外部验证工具（BSD），不是运行依赖。https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.RegularGridInterpolator.html

规范文本不被本仓库重新许可；WMO registry有其OGL条款。数据独立见testdata/LICENSES.md。生成的测试来自独立工具输出与WMO边界合同，不使用产品输出制造真值。

## Zero-bit constant decimal-scale repair (2026-10-28)
The original upstream zero-bit branch directly returned R. Local repair applies
R / 10^D using the existing sign-magnitude scale conversion, consistent with this
module's WMO92.9.4 formula contract. No packing/template range or public API changed.
Nine independently encoded fixtures cover D=1/0/-1, E=3, R=10, bits=0 and bitmap
absent/mixed/all-missing. Exact Python Decimal expected values are1/10/100.
ecCodes2.50.0 also returns R in its zero-bit branch and differs for the four cases
with valid points and nonzero D; this is explicitly documented oracle divergence,
not an ecCodes parity claim. The formula basis is
https://codes.ecmwf.int/grib/format/grib2/regulations/ (92.9.4 note4).

## Deep repair05 numeric adaptation (2026-10-28)
The reused simple unpacker now falls back to locally authored normalised binary
mantissa/exponent evaluation when intermediate 2^E or 10^D cannot be materialised.
`internal/upstream_unpack/scaled_value.mbt` is a new local helper, not copied
upstream source. Existing normal-range arithmetic and the settled zero-bit
formula are retained. Exact Python Fraction expectations cover the repaired
finite extreme cases. UPSTREAM-LOCK.json records current adapted hashes and
separately identifies the local helper. Root facade repairs to longitude/poles,
exact nodes, finite-header checking and backing-state encapsulation are local
implementation changes; upstream bitstream/decoder attribution remains intact.

## Local request workflow and numeric sampling08
field_requests.mbt and the subnormal stencil headroom change are locally authored
facade contributions. The request design was compared with public MoonBit
registry metadata, the upstream generated API and ECMWF cfgrib key filtering;
research sources do not add runtime dependencies. Existing vendored decoder
attribution and hashes remain unchanged. New layer/run fixtures are synthetic
manual encodings, independently inspected with ecCodes; no forecast download.

## Local station CSV view10
station_csv.mbt is a local fixed-schema adapter over existing FieldSamples,
with a small quoting helper informed by RFC4180. Registry CSV packages were
reviewed as existing ecosystem capability; no generic CSV implementation is
vendored or imported. cmd/export embeds the existing NOAA/IFS repacked fixtures;
their data licences and derived CSV attribution remain separate from source
Apache-2.0: see testdata/export10/LICENSES.md and testdata/SOURCES.json.
