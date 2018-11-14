import gdal

# 读取要切的原图
in_ds = gdal.Open("chengdu-xinglong-lake.tif")
print("open tif file succeed")

# 读取原图中的每个波段
in_band1 = in_ds.GetRasterBand(1)
in_band2 = in_ds.GetRasterBand(2)
in_band3 = in_ds.GetRasterBand(3)

# 定义切图的起始点坐标(相比原点的横坐标和纵坐标偏移量)
offset_x = 100  # 这里是随便选取的，可根据自己的实际需要设置
offset_y = 100

# 定义切图的大小（矩形框）
block_xsize = 400  # 行
block_ysize = 400  # 列

# 从每个波段中切需要的矩形框内的数据(注意读取的矩形框不能超过原图大小)
out_band1 = in_band1.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
out_band2 = in_band2.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)
out_band3 = in_band3.ReadAsArray(offset_x, offset_y, block_xsize, block_ysize)

# 获取Tif的驱动，为创建切出来的图文件做准备
gtif_driver = gdal.GetDriverByName("GTiff")

# 创建切出来的要存的文件（3代表3个不都按，最后一个参数为数据类型，跟原文件一致）
out_ds = gtif_driver.Create('clip.tif', block_xsize, block_ysize, 3, in_band1.DataType)
print("create new tif file succeed")

# 获取原图的原点坐标信息
ori_transform = in_ds.GetGeoTransform()
if ori_transform:
    print (ori_transform)
    print("Origin = ({}, {})".format(ori_transform[0], ori_transform[3]))
    print("Pixel Size = ({}, {})".format(ori_transform[1], ori_transform[5]))

# 读取原图仿射变换参数值
top_left_x = ori_transform[0]  # 左上角x坐标
w_e_pixel_resolution = ori_transform[1] # 东西方向像素分辨率
top_left_y = ori_transform[3] # 左上角y坐标
n_s_pixel_resolution = ori_transform[5] # 南北方向像素分辨率

# 根据反射变换参数计算新图的原点坐标
top_left_x = top_left_x + offset_x * w_e_pixel_resolution
top_left_y = top_left_y + offset_y * n_s_pixel_resolution

# 将计算后的值组装为一个元组，以方便设置
dst_transform = (top_left_x, ori_transform[1], ori_transform[2], top_left_y, ori_transform[4], ori_transform[5])

# 设置裁剪出来图的原点坐标
out_ds.SetGeoTransform(dst_transform)

# 设置SRS属性（投影信息）
out_ds.SetProjection(in_ds.GetProjection())

# 写入目标文件
out_ds.GetRasterBand(1).WriteArray(out_band1)
out_ds.GetRasterBand(2).WriteArray(out_band2)
out_ds.GetRasterBand(3).WriteArray(out_band3)

# 将缓存写入磁盘
out_ds.FlushCache()
print("FlushCache succeed")

# 计算统计值
# for i in range(1, 3):
#     out_ds.GetRasterBand(i).ComputeStatistics(False)
# print("ComputeStatistics succeed")

del out_ds

print("End!")


