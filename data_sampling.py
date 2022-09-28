import rasterio
from pathlib import Path 
import geopandas as gpd
import pandas as pd

## 0. Data Load and Check
tp_up = gpd.GeoDataFrame.from_file("tree_points/manup_treepoint.shp")
tp_down = gpd.GeoDataFrame.from_file("tree_points/mandown_treepoint.shp")
tp_br1 = gpd.GeoDataFrame.from_file("tree_points/br_rest1_treepoint.shp")
tp_br2 = gpd.GeoDataFrame.from_file("tree_points/br_rest2_treepoint.shp")
tp_br = gpd.GeoDataFrame( pd.concat( [tp_br1, tp_br2], ignore_index=True) )


# run
## 0. subclass change
up = sc_change(tp_up)
down = sc_change(tp_down)
br = sc_change(tp_br)

## 1. Point Sampling
# file에 영상 넣기 # NDVIup_file, NDVIdown_file, NDVIbr_file
for i in ['NDVI', 'SBI', 'GVI', 'YVI', 'WBI']:
    for j in ['up', 'down', 'br']:
        globals()[f'{i}{j}_file'] = '../KOMPSAT 위성영상/데이터 전처리/4. data/'+j+'/'+i+'.tif'
        globals()[f'{i}{j}_src'] = rasterio.open(globals()[f'{i}{j}_file'])
        
# NDVI point smapling and Delete under 0.2
up = NDVIpoint02(up, NDVIup_file, NDVIup_src)
down = NDVIpoint02(down, NDVIdown_file, NDVIdown_src)
br = NDVIpoint02(br, NDVIbr_file, NDVIbr_src)

## run 3by3 PS
# up
PointSampling(NDVIup_file, NDVIup_src, up, 'NDVI')
PointSampling(SBIup_file, SBIup_src, up, 'SBI')
PointSampling(GVIup_file, GVIup_src, up, 'GVI')
PointSampling(YVIup_file, YVIup_src, up, 'YVI')
PointSampling(WBIup_file, WBIup_src, up, 'WBI')
# down
PointSampling(NDVIdown_file, NDVIdown_src, down, 'NDVI')
PointSampling(SBIdown_file, SBIdown_src, down, 'SBI')
PointSampling(GVIdown_file, GVIdown_src, down, 'GVI')
PointSampling(YVIdown_file, YVIdown_src, down, 'YVI')
PointSampling(WBIdown_file, WBIdown_src, down, 'WBI')
# br
PointSampling(NDVIbr_file, NDVIbr_src, br, 'NDVI')
PointSampling(SBIbr_file, SBIbr_src, br, 'SBI')
PointSampling(GVIbr_file, GVIbr_src, br, 'GVI')
PointSampling(YVIbr_file, YVIbr_src, br, 'YVI')
PointSampling(WBIbr_file, WBIbr_src, br, 'WBI')

# NDVI kernels < 0.2 delete
up = NDVIkn02(up)
down = NDVIkn02(down)
br = NDVIkn02(br)

tpall = pd.concat([up, down, br], axis=1)

tpall.drop(['geometry'], axis = 1, inplace=True)
print(tpall)




## function define
## subclass change
## 그냥 하나의 지역을 기준으로 만들기
def sc_change(tp):
    # replace with *
    tp_sc = tp['subclass'].fillna('*')
    
    # subclass string to int
    tp_sc = tp_sc.to_frame()
    sc_list = {'subclass':{'Rosidae':'1', 'Hamamelididae':'2', 'Asteridae':'3',
                           'Dilleniidae':'4', 'Magnoliidae':'5', '*':'6'}}
    tp_sc = tp_sc.replace(sc_list)
    
    # change
    tp.drop(["subclass", "GenusSpeci", "OBJECTID", "Lat", "Long"], axis = 1, inplace=True)
    tp = pd.concat([tp, tp_sc], axis=1)
    
    return tp


## 1. Point Sampling
# NDVI point smapling and Delete under 0.2
def NDVIpoint02(tp, file, src):
    coord_list = [(x,y) for x,y in zip(tp['geometry'].x , tp['geometry'].y)] 
    tp[Path(file).stem] = [x for x in src.sample(coord_list)] # 포인트 샘플링
    tp[Path(file).stem] = tp[Path(file).stem].astype('float64')
    tp.drop(tp[tp['NDVI'] < 0.2].index, inplace=True)
    
    return tp


# 3by3 Point Sampling
def PointSampling(file, src, tp, feature):
    WIDTH = 0.00000599299783809013749338974087784241
    HEIGHT = 0.0000059299783809007439469768700121737
    coord_list0= [(x,y) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list1= [(x-WIDTH, y+HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list2= [(x, y+HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list3= [(x+WIDTH,y+HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list4= [(x+WIDTH,y) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list5= [(x+WIDTH,y-HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list6= [(x,y-HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list7= [(x-WIDTH,y-HEIGHT) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list8= [(x-WIDTH,y) for x,y in zip(tp['geometry'].x , tp['geometry'].y)]
    coord_list = [coord_list0, coord_list1, coord_list2, coord_list3, coord_list4, coord_list5, coord_list6, coord_list7, coord_list8]
    
    for i in range(9):
        globals()[f'tp{i}'] = tp
    
    for i in range(9):
        globals()[f'tp{i}'][Path(file).stem] = [x for x in src.sample(coord_list[i])] # 포인트 샘플링
        globals()[f'tp{i}'][Path(file).stem] = globals()[f'tp{i}'][Path(file).stem].astype('float64')
        globals()[f'tp{i}'].rename(columns = {feature : feature+str(i)} , inplace=True)

# NDVI kernels < 0.2 delete
def NDVIkn02(tp):
    for i in range(9):
        tp.drop(tp[tp['NDVI'+str(i)]<0.2].index, inplace=True)
    return tp


