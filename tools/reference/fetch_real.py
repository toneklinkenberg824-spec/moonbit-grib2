from pathlib import Path
import urllib.request,json,hashlib,traceback
import eccodes as ec
ROOT=Path(__file__).parent
RAW=ROOT/'real-inputs'; RAW.mkdir(exist_ok=True)
entries=[]
def get(url, start=None, length=None):
    headers={'User-Agent':'MoonBit-GRIB2-local-validation/0.1'}
    if start is not None: headers['Range']=f'bytes={start}-{start+length-1}'
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60) as r:
        data=r.read()
        if start is not None and r.status!=206:
            if len(data)>=start+length: data=data[start:start+length]
            else: raise ValueError('server ignored range and response too short')
        return data
def archive(name,url,start,length,licence):
    path=RAW/(name+'-original.grib2')
    data=path.read_bytes() if path.exists() else get(url,start,length)
    path.write_bytes(data)
    h=ec.codes_new_from_message(data)
    original={k:ec.codes_get(h,k) for k in ['gridDefinitionTemplateNumber','productDefinitionTemplateNumber','dataRepresentationTemplateNumber','Ni','Nj','shortName']}
    ni=ec.codes_get(h,'Ni'); nj=ec.codes_get(h,'Nj')
    vals=ec.codes_get_values(h).reshape((nj,ni))[min(20,nj-6):min(20,nj-6)+6, min(30,ni-8):min(30,ni-8)+8]
    lat=ec.codes_get_array(h,'latitudes').reshape((nj,ni))[min(20,nj-6):min(20,nj-6)+6,min(30,ni-8):min(30,ni-8)+8]
    lon=ec.codes_get_array(h,'longitudes').reshape((nj,ni))[min(20,nj-6):min(20,nj-6)+6,min(30,ni-8):min(30,ni-8)+8]
    for k,v in {'Ni':8,'Nj':6,'latitudeOfFirstGridPointInDegrees':float(lat[0,0]),'latitudeOfLastGridPointInDegrees':float(lat[-1,-1]),'longitudeOfFirstGridPointInDegrees':float(lon[0,0]),'longitudeOfLastGridPointInDegrees':float(lon[-1,-1])}.items(): ec.codes_set(h,k,v)
    ec.codes_set(h,'packingType','grid_simple')
    ec.codes_set_values(h,vals.ravel())
    repacked=ec.codes_get_message(h)
    out=ROOT/'fixtures'/(name+'-repacked.grib2'); out.write_bytes(repacked)
    row={'source':url,'range':[start,start+length-1],'license':licence,'original':str(path),'original_sha256':hashlib.sha256(data).hexdigest(),
         'original_templates':original,'repacked':str(out),'repacked_sha256':hashlib.sha256(repacked).hexdigest(),'transformation':'8x6 node window from original field, ecCodes packingType=grid_simple; no interpolation; not original packing support',
         'values':ec.codes_get_values(h).tolist(),'latitudes':ec.codes_get_array(h,'latitudes').tolist(),'longitudes':ec.codes_get_array(h,'longitudes').tolist(),
         'mask':ec.codes_get_array(h,'bitmap').tolist() if ec.codes_get(h,'bitmapPresent') else [],
         'metadata':{k:ec.codes_get(h,k) for k in ['Ni','Nj','forecastTime','indicatorOfUnitOfTimeRange','discipline','parameterCategory','parameterNumber','typeOfFirstFixedSurface','scaledValueOfFirstFixedSurface']}}
    ec.codes_release(h); entries.append(row)
    print(name,original,len(data),'bytes')

for name in ['noaa-gfs','ecmwf-ifs']:
    try:
        if name=='noaa-gfs':
            url='https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20260221/00/atmos/gfs.t00z.pgrb2.1p00.f000'
            lines=get(url+'.idx').decode().splitlines()
            i=next(i for i,l in enumerate(lines) if ':TMP:2 m above ground:' in l)
            start=int(lines[i].split(':')[1]); length=int(lines[i+1].split(':')[1])-start
            archive(name,url,start,length,'NOAA/NWS public domain unless noted; https://www.weather.gov/disclaimer')
        else:
            url='https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/20260221/00z/ifs/0p25/oper/20260221000000-0h-oper-fc.grib2'
            index=[json.loads(l) for l in get(url.replace('.grib2','.index')).decode().splitlines()]
            item=next(l for l in index if l.get('param')=='2t')
            archive(name,url,int(item['_offset']),int(item['_length']),'ECMWF Open Data CC-BY-4.0 and ECMWF Terms; https://www.ecmwf.int/en/forecasts/datasets/open-data')
    except Exception as e:
        entries.append({'name':name,'error':str(e),'traceback':traceback.format_exc()})
        print(name,'FAILED',str(e))
(ROOT/'REAL-REFERENCE.json').write_text(json.dumps(entries),encoding='utf-8')
