import rasterio
from pathlib import Path 
import geopandas as gpd
import pandas as pd

## 0. Data Load and Check
tp_up = gpd.GeoDataFrame.from_file("tree_points/manup_treepoint.shp")
tp_down = gpd.GeoDataFrame.from_file("tree_points/mandown_treepoint.shp")
tp_br1 = gpd.GeoDataFrame.from_file("tree_points/br_rest1_treepoint.shp")
tp_br2 = gpd.GeoDataFrame.from_file("tree_points/br_rest2_treepoint.shp")
tp_brleft = gpd.GeoDataFrame.from_file("tree_points/brleft.shp")
tp_br = gpd.GeoDataFrame( pd.concat( [tp_br1, tp_br2], ignore_index=True) )

tp_brtest = gpd.GeoDataFrame.from_file("tree_points/br_test_treepoint.shp")



## function define
## 1. subclass change
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

## 2. NDVI point smapling and Delete under 0.2
def NDVIpoint02(tp, file, src):
    coord_list = [(x,y) for x,y in zip(tp['geometry'].x , tp['geometry'].y)] 
    tp[Path(file).stem] = [x for x in src.sample(coord_list)] # 포인트 샘플링
    tp[Path(file).stem] = tp[Path(file).stem].astype('float64')
    tp.drop(tp[tp['NDVI'] < 0.2].index, inplace=True)
    
    return tp

## 3. 3by3 Point Sampling
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


## 4. NDVI kernels < 0.2 delete
def NDVIkn02(tp):
    for i in range(9):
        tp.drop(tp[tp['NDVI'+str(i)]<0.2].index, inplace=True)
    return tp

## 5. brleft, manup, mandown 의 subclass 1, 2 지우기
def scdel(tp):
    tp['subclass'] = tp['subclass'].astype(str)
    tem = tp.drop(tp[tp['subclass'] == '1'].index)
    tem = tem.drop(tem[tem['subclass'] == '2'].index)
    return tem




# run
## [1] 1. subclass change
manup = sc_change(tp_up)
mandown = sc_change(tp_down)
br = sc_change(tp_br)
brleft = sc_change(tp_brleft)
brtest = sc_change(tp_brtest)

## [2] 
# file에 영상 넣기 # NDVIup_file, NDVIdown_file, NDVIbr_file
# 'NDVI', 'GCI', 'AVI', 'SIPI', 'ARVI', 'EVI' / 'NDVI', 'SBI', 'GVI', 'YVI', 'WBI'
for i in ['NDVI', 'GCI', 'AVI', 'SIPI', 'ARVI', 'EVI']:
    for j in ['brleft', 'br', 'mandown', 'manup']:
        globals()[f'{i}{j}_file'] = '../KOMPSAT 위성영상/데이터 전처리/4. data/'+j+'/'+i+'.tif'
        globals()[f'{i}{j}_src'] = rasterio.open(globals()[f'{i}{j}_file'])
        
# 2. NDVI point smapling and Delete under 0.2
manup = NDVIpoint02(manup, NDVImanup_file, NDVImanup_src)
mandown = NDVIpoint02(mandown, NDVImandown_file, NDVImandown_src)
brleft = NDVIpoint02(brleft, NDVIbrleft_file, NDVIbrleft_src)
br = NDVIpoint02(br, NDVIbr_file, NDVIbr_src)
brtest = NDVIpoint02(brtest, NDVIbr_file, NDVIbr_src)

## 3. 3by3 Point Sampling
PointSampling(NDVIbr_file, NDVIbr_src, brtest, 'NDVI')
PointSampling(GCIbr_file, GCIbr_src, brtest, 'GCI')
PointSampling(AVIbr_file, AVIbr_src, brtest, 'AVI')
PointSampling(SIPIbr_file, SIPIbr_src, brtest, 'SIPI')
PointSampling(ARVIbr_file, ARVIbr_src, brtest, 'ARVI')
PointSampling(EVIbr_file, EVIbr_src, brtest, 'EVI')

# up
PointSampling(NDVImanup_file, NDVImanup_src, manup, 'NDVI')
PointSampling(GCImanup_file, GCImanup_src, manup, 'GCI')
PointSampling(AVImanup_file, AVImanup_src, manup, 'AVI')
PointSampling(SIPImanup_file, SIPImanup_src, manup, 'SIPI')
PointSampling(ARVImanup_file, ARVImanup_src, manup, 'ARVI')
PointSampling(EVImanup_file, EVImanup_src, manup, 'EVI')

# down
PointSampling(NDVImandown_file, NDVImandown_src, mandown, 'NDVI')
PointSampling(GCImandown_file, GCImandown_src, mandown, 'GCI')
PointSampling(AVImandown_file, AVImandown_src, mandown, 'AVI')
PointSampling(SIPImandown_file, SIPImandown_src, mandown, 'SIPI')
PointSampling(ARVImandown_file, ARVImandown_src, mandown, 'ARVI')
PointSampling(EVImandown_file, EVImandown_src, mandown, 'EVI')

# br
PointSampling(NDVIbrleft_file, NDVIbrleft_src, brleft, 'NDVI')
PointSampling(GCIbrleft_file, GCIbrleft_src, brleft, 'GCI')
PointSampling(AVIbrleft_file, AVIbrleft_src, brleft, 'AVI')
PointSampling(SIPIbrleft_file, SIPIbrleft_src, brleft, 'SIPI')
PointSampling(ARVIbrleft_file, ARVIbrleft_src, brleft, 'ARVI')
PointSampling(EVIbrleft_file, EVIbrleft_src, brleft, 'EVI')

PointSampling(NDVIbr_file, NDVIbr_src, br, 'NDVI')
PointSampling(GCIbr_file, GCIbr_src, br, 'GCI')
PointSampling(AVIbr_file, AVIbr_src, br, 'AVI')
PointSampling(SIPIbr_file, SIPIbr_src, br, 'SIPI')
PointSampling(ARVIbr_file, ARVIbr_src, br, 'ARVI')
PointSampling(EVIbr_file, EVIbr_src, br, 'EVI')

## 4. NDVI kernels < 0.2 delete
brtest = NDVIkn02(brtest)
manup = NDVIkn02(manup)
mandown = NDVIkn02(mandown)
brleft = NDVIkn02(brleft)
br = NDVIkn02(br)

brtest.to_csv('./dataCSV/br_test_ver2.csv', index=False)
manup.to_csv('./dataCSV/manup_training_ver2.csv', index=False)
mandown.to_csv('./dataCSV/mandown_training_ver2.csv', index=False)
brleft.to_csv('./dataCSV/brleft_training_ver2.csv', index=False)
br.to_csv('./dataCSV/br_training_ver2.csv', index=False)




