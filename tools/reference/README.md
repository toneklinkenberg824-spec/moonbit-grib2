# Reference regeneration (optional, online)
Static moon tests use already captured independent values and need no Python/network.
To regenerate in a disposable checkout, create a Python3.14 venv outside the product,
pip install -r tools/reference/requirements.txt, then run in order:
python tools/reference/generate_reference.py
python tools/reference/fetch_real.py
python tools/reference/emit_tests.py
python tools/reference/emit_edges.py
python tools/reference/emit_sampling_edges.py
moon info
moon fmt
Then run both targets' check/build/test and examples from the root README.
This writes reference files under tools/reference and regenerates test sources.
Official historical servers may return errors/limit access; retain failure logs and do
not treat a failed source download as a product failure or fabricate a replacement.
References pin ecCodes2.50.0, NumPy2.5.4 and SciPy1.18.1 plus their captured dependencies.
Expected values come from ecCodes/SciPy and WMO-specific independent matrix transforms,
not from this product. WMO32-bit fixture construction and ecCodes-iterator limits are
explicit in generate_reference.py. Raw original and cropped/repacked files stay distinct.

零位常量补充参考：python tools/reference/constant_scale_fix/generate_constant_regression.py。该脚本人工编码9份样本，用Decimal/WMO公式作真值，ecCodes观察值只用于记录差异。
