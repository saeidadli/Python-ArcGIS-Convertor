import os
import tempfile

from pathlib import Path

import arcpy
import pandas as pd
import numpy as np
import geopandas as gpd

#constants
#WGS_1984 coordinate system
WGS_1984 = \
    "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', "+\
    "SPHEROID['WGS_1984',6378137.0,298.257223563]], "+\
    "PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]; "+\
    "-400 -400 1000000000;-100000 10000;-100000 10000; "+\
    "8.98315284119522E-09;0.001;0.001;IsHighPrecision"

#functions
def gdb_path(in_fc):
    """
    Returns the properties of a input gis data
    """
    if arcpy.Exists(in_fc):
        desc = arcpy.Describe(in_fc)
        in_fc = desc.catalogPath
        fc_name = desc.name
    else:
        fc_name = os.path.basename(in_fc)
    dirname = os.path.dirname(in_fc)
    workspace = arcpy.Describe(dirname).dataType

    if workspace == 'FeatureDataset':
        GDB = os.path.dirname(dirname)
    elif workspace == 'Workspace':
        GDB = dirname
    elif workspace == 'Folder':
        GDB = ''
    else:
        GDB = ''
    return GDB, workspace, dirname, fc_name

def get_fields(in_fc, output_type = 'list'):
    #Gets list of fileds from a feature class
    fields = arcpy.ListFields(in_fc)
    if output_type == 'list':
        output = [f.name for f in fields]
    elif output_type == 'dict':
        output = {f.name: f.type for f in fields}
    else:
        output = ''

    return output

#pandas convertor for ArcGIS

def gdf_to_fc(gdf, fc):
    """
    converts a geopandas dataframe to a layer in a ESRI file geodatabase
    """
    GDB, workspace, dirname, fc_name = gdb_path(fc)
    
    # convert fc to a gpkg in a temporary directory
    tmp_dir = tempfile.TemporaryDirectory()
    p = Path(tmp_dir.name)
    n = fc_name + '.shp'
    
    gdf.to_file(str(p/n))
    fc_cols = get_fields(str(p/n))[2:]
    
    #copy the file into a feature class
    fc = arcpy.CopyFeatures_management(str(p/n), fc)
    
    gdf_cols = gdf.columns.tolist()
    gdf_cols.remove('geometry')

    #fixing the columns
    if gdf_cols:
        col_dict = {col: gdf_cols[indx] for indx, col  in enumerate(fc_cols) }
        for col in col_dict:
            if col_dict[col] != col:
                arcpy.AlterField_management(fc, col, col_dict[col], clear_field_alias="true")
    
    # Delete temporary directory
    tmp_dir.cleanup()

    return fc

def df_to_tbl(df, tbl):
    x = np.array(np.rec.fromrecords(df.values))
    names = df.dtypes.index.tolist()
    names = [str(arcpy.ValidateTableName(name)) for name in names]
    x.dtype.names = tuple(names)
    arcpy.da.NumPyArrayToTable(x, tbl)
    return tbl

def fc_to_gdf(fc):
    #use scratch work space for temporary files
    GDB, workspace, dirname, fc_name = gdb_path(fc)
    if GDB != '':
        gdf = gpd.read_file(GDB, layer = fc_name)
    else:
        desc = arcpy.Describe(fc)
        fc_path = desc.catalogPath
        gdf = gpd.read_file(fc_path)
    
    return gdf

def tbl_to_df(tbl, fieldnames = None):
    gdf = fc_to_gdf(tbl)
    
    if fieldnames != None:
        fieldnames = [f for f in fieldnames if f in gdf.columns()]
    else:
        fieldnames = get_fields(tbl)[1:]
        
    df = pd.DataFrame(gdf)

    return df[fieldnames].copy()

def geojson_to_fc(geojson, fc):
    gdf = gpd.read_file(geojson)
    gdf_to_fc(gdf, fc)
    return fc

def fc_to_geojson(fc, geojson):
    gdf = fc_to_gdf(fc)
    gdf.to_file(geojson)
    return geojson


