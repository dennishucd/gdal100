from osgeo import gdal, gdalnumeric, ogr
from PIL import Image, ImageDraw

# 将图像转为数组
def imageToArray(i):
    a = gdalnumeric.fromstring(i.tobytes(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a

# 将数组转为图像
def arrayToImage(a):
    i = Image.frombytes('L', (a.shape[1], a.shape[0]), a.astype('b'))
    return i

# 将经纬度坐标转为像素坐标
def world2Pixel(geoMatrix, x, y):
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]

    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / yDist)

    return (abs(pixel), abs(line))


# 第一步：准备好要切的tif图、shp文件及输出的文件名
tif_file = "chengdu-xinglong-lake.tif"  # 原始的tif图
shp_file = "xing/xing.shp"  # 要切的shape file
clipped_file = "clipped.tif" # 最后切出来的tif图名字

# 第二步：将tif文件读取为numpy.ndarray
srcArray = gdalnumeric.LoadFile(tif_file)

# 第三步：读取tif文件中的仿信息
in_ds = gdal.Open(tif_file)
geoTrans = in_ds.GetGeoTransform()
print (geoTrans)

# 第四步：读取shp文件中的图层从而获取要切取部分的extent
shapef = ogr.Open(shp_file)
lyr = shapef.GetLayer()
minX, maxX, minY, maxY = lyr.GetExtent()
print (111, minX, maxX, minY, maxY)

# 第五步：将要切取部分的大地坐标转为像素坐标
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

# 计算clip出来图的宽和高
pxWidth = abs(int(lrX - ulX))
pxHeight = abs(int(lrY - ulY))

# 从原图中切出来，但这个时候还是矩形的
clip = srcArray[:, ulY:lrY, ulX:lrX]

geoTrans = list(geoTrans)

# 更新左上角的坐标，相当于更新设置切后的tif图的仿射信息
geoTrans[0] = minX
geoTrans[3] = maxY

# 下面主要是构造mask
points = []
pixels = []
poly = lyr.GetNextFeature()
geom = poly.GetGeometryRef()
pts = geom.GetGeometryRef(0)
for p in range(pts.GetPointCount()):
    points.append((pts.GetX(p), pts.GetY(p)))
    print (str(pts.GetX(p))+","+str(pts.GetY(p)))

for p in points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))

rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)

rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)

mask = imageToArray(rasterPoly)

# 按照多边形来切
clip = gdalnumeric.choose(mask, (clip, 0))

# 创建切后图的tif文件
gtif_driver = gdal.GetDriverByName('GTiff')
out_ds = gtif_driver.Create(clipped_file, pxWidth, pxHeight, 3, in_ds.GetRasterBand(1).DataType)

# 设置切出来的tif图的仿射信息和参考系统
out_ds.SetGeoTransform(geoTrans)
out_ds.SetProjection(in_ds.GetProjection())

# 写入目标文件
out_ds.GetRasterBand(1).WriteArray(clip[0])
out_ds.GetRasterBand(2).WriteArray(clip[1])
out_ds.GetRasterBand(3).WriteArray(clip[2])

# 将缓存写入磁盘
out_ds.FlushCache()
print("FlushCache succeed")