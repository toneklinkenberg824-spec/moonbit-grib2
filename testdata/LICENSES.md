# Fixture sources and licences

- scan*.grib2、bitmap/constant/negative-scale/scipy/polar.grib2：由ecCodes2.50.0 regular_ll_sfc_grib2样例构造的人工数据，保留ECMWF/ecCodes来源；不是官方预报。
- noaa-gfs-repacked.grib2：NOAA/NCEP GFS 2026-02-21 00Z 2米温度8×6节点窗口。NOAA/NWS数据除特别声明外为公共领域：https://www.weather.gov/disclaimer 。本件经过裁剪/重编码，不作为未经修改的官方产品展示，不暗示NOAA背书。
- ecmwf-ifs-repacked.grib2：ECMWF IFS 2026-02-21 00Z 2米温度8×6节点窗口。来源：ECMWF Open Data，CC-BY-4.0及ECMWF Terms：https://www.ecmwf.int/en/forecasts/datasets/open-data 。修改为节点裁剪和ecCodes简单打包，无空间插值；不暗示官方背书。许可证：https://creativecommons.org/licenses/by/4.0/ 。

SOURCES.json记录准确URL、字节范围、原件及派生哈希、模板身份。原始单字段消息保存在执行报告real-inputs/，与这些可复现的小型派生样本分开。原模板5.3/5.42不在支持范围内。
数据许可独立于项目源码Apache-2.0；不得将真实预报标为本项目原创。参考比较针对编码后还原值，不宣称等于未量化模式真值。

constant-scale/：本地人工编码的R=10零位常量及缺测掩码样本，依据WMO92.9.4的独立Decimal参考；不是官方预报。REFERENCE.json同时记录ecCodes2.50.0观察值与公式差异，不能将其混称ecCodes真值。
