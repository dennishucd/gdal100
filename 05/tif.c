#include "gdal.h"
#include "cpl_conv.h" 

int main()
{
    GDALDriverH   hDriver; 
    GDALDatasetH  hSrcDS; 
    GDALRasterBandH hSrcBand;

    char *pszSrcFilename = "030E30N.tif";
    double adfGeoTransform[6];    

    GDALAllRegister();
   
    hSrcDS = GDALOpen(pszSrcFilename, GA_ReadOnly);
    if( hSrcDS == NULL )
    {
        printf("error, file not found. \n");
    }

    int iRasterXSize = GDALGetRasterXSize(hSrcDS);
    int iRasterYSize = GDALGetRasterYSize(hSrcDS);

    printf("The input file size is %dx%d.\n", iRasterXSize, iRasterYSize);

    hDriver = GDALGetDatasetDriver(hSrcDS);

    hSrcBand = GDALGetRasterBand( hSrcDS, 1);

    GDALGetGeoTransform(hSrcDS, adfGeoTransform);

    for (int i=0; i<6; i++) 
    {
        printf("%f.\n", adfGeoTransform[i]);
    }

    printf("pixel value:\n");

    for (int i=0; i<iRasterXSize; i++) 
    {
        for (int j=0; j<iRasterYSize; j++) 
        {
            unsigned char *pValue= (unsigned char *) CPLMalloc(sizeof(unsigned char)*1*1);
            CPLErr error = GDALRasterIO(hSrcBand, GF_Read, i, j, 1, 1 ,
              pValue, 1, 1, GDT_Byte,0, 0 );

            printf("%d\t", *pValue);
        }
    }

    return 0;
}
