from pathlib import Path
from decimal import Decimal
import struct,json,hashlib,sys
import eccodes as ec
R=Path(__file__).parent
P=Path(__file__).resolve().parents[3]
base=(P/'testdata/constant.grib2').read_bytes()
sections=[];i=16
while i<len(base)-4:
    n=int.from_bytes(base[i:i+4],'big');sections.append(base[i:i+n]);i+=n
records=[];tests=['// WMO92.9.4 independent Decimal oracle; generated binary fixtures, not product outputs.\n']
def blob(data):return 'b"'+''.join(f'\\x{x:02x}' for x in data)+'"'
for d in [1,0,-1]:
    for kind,mask in [('no-bitmap',[True]*6),('mixed',[True,False,True,False,True,False]),('all-missing',[False]*6)]:
        parts=[]
        for source in sections:
            section=bytearray(source);num=section[4]
            if num==5:
                section[5:9]=sum(mask).to_bytes(4,'big')
                section[11:15]=struct.pack('>f',10.0)
                section[15:17]=(3).to_bytes(2,'big') # E cannot matter when X=0.
                encoded_d=(0x8000|abs(d)) if d<0 else d
                section[17:19]=encoded_d.to_bytes(2,'big');section[19]=0
            if num==6:
                section=bytearray(b'\0\0\0\6\6\xff') if kind=='no-bitmap' else bytearray(b'\0\0\0\7\6\0'+bytes([sum((1<<(7-i)) for i,v in enumerate(mask) if v)]))
            if num==7:section=bytearray(b'\0\0\0\5\7')
            parts.append(section)
        body=b''.join(parts)+b'7777';data=base[:8]+(16+len(body)).to_bytes(8,'big')+body
        name=f'constant-D{d}-{kind}.grib2';(R/name).write_bytes(data)
        expected=Decimal('10')*(Decimal(10)**(-d))
        h=ec.codes_new_from_message(data)
        observed=ec.codes_get_values(h).tolist()
        oracle_mask=ec.codes_get_array(h,'bitmap').tolist() if ec.codes_get(h,'bitmapPresent') else [1]*6
        ec.codes_release(h)
        assert oracle_mask==[int(v) for v in mask]
        records.append({'file':name,'sha256':hashlib.sha256(data).hexdigest(),'R':'10','E':3,'D':d,'bits':0,'mask':mask,'decimal_expected':str(expected),'eccodes_observed':observed,'eccodes_matches_formula':all(not valid or Decimal(str(value))==expected for valid,value in zip(mask,observed))})
        tests.append(f'''///|
test "constant scale D{d} {kind}" {{
  let f=@grib2.read_message({blob(data)}).unwrap()
  let valid={str(mask).lower()}
  let expected : Double={float(expected)!r}
  assert_eq(f.mask(),valid)
  for r in 0..<2 {{for c in 0..<3 {{
    let i=r*3+c
    if valid[i] {{
      assert_eq(f.get(r,c),Some(expected))
      assert_eq(f.values()[i],expected)
      assert_eq(f.interpolate_latlon(1.0-r.to_double(),10.0+c.to_double()),Some(expected))
    }} else {{
      assert_eq(f.get(r,c),None)
      assert_true(f.values()[i].is_nan())
    }}
  }}}}
}}
''')
(P/'constant_scale_test.mbt').write_text('\n'.join(tests),encoding='utf-8')
(R/'REFERENCE.json').write_text(json.dumps({'basis':'WMO FM92 regulation92.9.4 note4: Y*10^D=R+X*2^E, X=0 for zero bits','basis_url':'https://codes.ecmwf.int/grib/format/grib2/regulations/','independent_reference':'Python Decimal exact arithmetic on explicitly encoded headers, not product output','eccodes_version':ec.codes_get_api_version(),'python':sys.version,'cases':records,'notice':'ecCodes2.50.0 ignores D when bits=0; captures are observations, not the constant-scale expected oracle'},indent=2),encoding='utf-8')
print(json.dumps({'cases':len(records),'eccodes_formula_divergent_cases':sum(not v['eccodes_matches_formula'] for v in records),'bits':0,'expected_values':[1,10,100]}))
