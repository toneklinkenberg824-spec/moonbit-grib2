"""Independent ecCodes + SciPy reference capture, run before product implementation."""
from pathlib import Path
import json, hashlib, sys
import eccodes as ec
import numpy as np
import scipy
from scipy.interpolate import RegularGridInterpolator

ROOT = Path(__file__).parent
FIX = ROOT / 'fixtures'
FIX.mkdir(exist_ok=True)
rows = []
for scan in range(0, 256, 16):
    h = ec.codes_grib_new_from_samples('regular_ll_sfc_grib2')
    ni, nj = 4, 3
    ip, jp = bool(scan & 128), bool(scan & 64)
    keys = {'Ni':ni,'Nj':nj,'latitudeOfFirstGridPointInDegrees': -90 if jp else 90,
            'longitudeOfFirstGridPointInDegrees':270 if ip else 0,
            'latitudeOfLastGridPointInDegrees':90 if jp else -90,
            'longitudeOfLastGridPointInDegrees':0 if ip else 270,
            'iDirectionIncrementInDegrees':90,'jDirectionIncrementInDegrees':90,
            'scanningMode':scan,'productDefinitionTemplateNumber':0,'packingType':'grid_simple',
            'bitsPerValue':13, 'forecastTime':6}
    for k,v in keys.items(): ec.codes_set(h,k,v)
    values = np.arange(12, dtype=float) * 0.125 - 5.0
    if scan==240:
        ec.codes_set(h,'bitmapPresent',1)
        ec.codes_set(h,'missingValue',1e30)
        values[[2,7]]=1e30
    ec.codes_set_values(h,values)
    data=ec.codes_get_message(h)
    name=f'scan{scan:03}.grib2'
    (FIX/name).write_bytes(data)
    item={'file':name,'scan':scan,'sha256':hashlib.sha256(data).hexdigest(),
          'values':ec.codes_get_values(h).tolist(), 'kind':'ecCodes synthetic'}
    if scan==240:item['mask']=ec.codes_get_array(h,'bitmap').tolist()
    try:
        item['latitudes']=ec.codes_get_array(h,'latitudes').tolist()
        item['longitudes']=ec.codes_get_array(h,'longitudes').tolist()
    except Exception as exc: item['coordinate_oracle_error']=str(exc)
    item['metadata']={k:ec.codes_get(h,k) for k in ['Ni','Nj','gridDefinitionTemplateNumber','productDefinitionTemplateNumber','dataRepresentationTemplateNumber','parameterCategory','parameterNumber','forecastTime','indicatorOfUnitOfTimeRange','bitsPerValue','binaryScaleFactor','decimalScaleFactor','referenceValue']}
    rows.append(item)
    ec.codes_release(h)

def fixture(name, vals, **settings):
    h=ec.codes_grib_new_from_samples('regular_ll_sfc_grib2')
    keys={'Ni':3,'Nj':2,'latitudeOfFirstGridPointInDegrees':1,'longitudeOfFirstGridPointInDegrees':10,
          'latitudeOfLastGridPointInDegrees':0,'longitudeOfLastGridPointInDegrees':12,
          'iDirectionIncrementInDegrees':1,'jDirectionIncrementInDegrees':1,'scanningMode':0,
          'productDefinitionTemplateNumber':0,'packingType':'grid_simple','bitsPerValue':17}
    keys.update(settings)
    for k,v in keys.items(): ec.codes_set(h,k,v)
    if any(v is None for v in vals):
        ec.codes_set(h,'bitmapPresent',1)
        ec.codes_set(h,'missingValue',1.0e30)
        vals=[1.0e30 if v is None else v for v in vals]
    ec.codes_set_values(h,vals)
    data=ec.codes_get_message(h)
    (FIX/name).write_bytes(data)
    item={'file':name,'sha256':hashlib.sha256(data).hexdigest(),'kind':'ecCodes synthetic',
          'values':ec.codes_get_values(h).tolist(), 'latitudes':ec.codes_get_array(h,'latitudes').tolist(),
          'longitudes':ec.codes_get_array(h,'longitudes').tolist(),
          'mask':ec.codes_get_array(h,'bitmap').tolist() if ec.codes_get(h,'bitmapPresent') else [1]*len(vals),
          'metadata':{k:ec.codes_get(h,k) for k in ['Ni','Nj','bitsPerValue','binaryScaleFactor','decimalScaleFactor','referenceValue']}}
    rows.append(item)
    ec.codes_release(h)

fixture('bitmap.grib2',[1,None,9999,4,5,6])
fixture('constant.grib2',[7]*6)
fixture('negative-scale.grib2',[-3.21,-2.1,-1.02,0.01,2.37,4.01],decimalScaleFactor=2,bitsPerValue=11)
fixture('scipy.grib2',[23,24,25,26,13,14,15,16,3,4,5,6],Ni=4,Nj=3,latitudeOfFirstGridPointInDegrees=2,latitudeOfLastGridPointInDegrees=0,longitudeOfFirstGridPointInDegrees=0,longitudeOfLastGridPointInDegrees=270,iDirectionIncrementInDegrees=90)
fixture('polar.grib2',[0,2,4,6,10,12,14,16,20,22,24,26],Ni=4,Nj=3,latitudeOfFirstGridPointInDegrees=90,latitudeOfLastGridPointInDegrees=-90,longitudeOfFirstGridPointInDegrees=0,longitudeOfLastGridPointInDegrees=270,iDirectionIncrementInDegrees=90,jDirectionIncrementInDegrees=90)
# ecCodes encoder refuses this 32-bit extreme case on Windows. Construct a WMO
# byte fixture independently, then query its decoder (failure remains in log).
raw=(FIX/'constant.grib2').read_bytes(); parts=[]; pos=16
values32=[0,1,2,4294967295,2147483648,1024]
while pos<len(raw)-4:
    size=int.from_bytes(raw[pos:pos+4],'big'); section=bytearray(raw[pos:pos+size]);num=section[4]
    if num==5:
        section[11:19]=b'\0'*8;section[19]=32
    if num==7:
        section=bytearray((29).to_bytes(4,'big')+b'\x07'+b''.join(v.to_bytes(4,'big') for v in values32))
    parts.append(bytes(section));pos+=size
body=b''.join(parts)+b'7777'; data=raw[:8]+(16+len(body)).to_bytes(8,'big')+body
(FIX/'max-width.grib2').write_bytes(data)
h=ec.codes_new_from_message(data)
rows.append({'file':'max-width.grib2','kind':'manual WMO32-bit fixture checked with ecCodes decoder','sha256':hashlib.sha256(data).hexdigest(),'values':ec.codes_get_values(h).tolist(),'latitudes':ec.codes_get_array(h,'latitudes').tolist(),'longitudes':ec.codes_get_array(h,'longitudes').tolist(),'metadata':{'Ni':3,'Nj':2,'bitsPerValue':32}})
ec.codes_release(h)
ys=np.array([0.,1.,2.]); xs=np.array([0.,90.,180.,270.,360.])
grid=np.array([[3.,4.,5.,6.,3.],[13.,14.,15.,16.,13.],[23.,24.,25.,26.,23.]])
queries=[[.25,45],[1.5,315],[1.,0],[1.,360],[2.,180]]
oracle=RegularGridInterpolator((ys,xs),grid)
ref={'python':sys.version,'eccodes_python':ec.__version__,'eccodes_c_api':ec.codes_get_api_version(),
     'numpy':np.__version__,'scipy':scipy.__version__,'fields':rows,
     'interpolation':{'source':'SciPy RegularGridInterpolator independent multilinear implementation','rows_south_to_north':grid[:,:4].tolist(),'latitudes':ys.tolist(),'longitudes':xs[:4].tolist(),'queries':queries,'values':oracle(queries).tolist()}}
(ROOT/'REFERENCE.json').write_text(json.dumps(ref,indent=2),encoding='utf-8')
print(json.dumps({'eccodes_c_api':ref['eccodes_c_api'],'fields':len(rows),'coordinate_oracle_failures':[r['file'] for r in rows if 'coordinate_oracle_error' in r],'scipy_queries':len(queries)}))
