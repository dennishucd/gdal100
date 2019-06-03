import shapefile
from osgeo import osr

# 定义shp文件名及存储路径
shp_filename = "03/shdemo.shp"

# 创建shp文件
shp = shapefile.Writer(shp_filename)

# 设置shp的类型为多边形
shp.shapeType = 5 # POLYGON = 5

shp.field('name', 'C')

# 把多边形的点依次加入，注意：多边形的坐标为顺时针，孔的坐标为逆时针
# 注意：一个shp文件中通常可能存在多个多边形，比如表达孔的情况
shp.poly([[[104.09151077270508,30.404748814079547],[104.08854961395264,30.402268893432442],
           [ 104.09206867218016,30.40034413549041],[104.09442901611328,30.40297216090944],
           [104.09151077270508,30.404748814079547]]])
shp.record('polygon1')
shp.close()

# 创建空间参考信息
spatial_ref = osr.SpatialReference()
spatial_ref.ImportFromEPSG(4326)

file = open('03/shdemo.prj', 'w')
file.write(spatial_ref.ExportToWkt())
file.close()