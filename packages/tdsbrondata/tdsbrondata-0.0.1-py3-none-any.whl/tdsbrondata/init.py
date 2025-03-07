import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tdsbrondata
import pytz
from datetime import datetime

def modules(notebookutils, spark):
    tdsbrondata._notebookutils = notebookutils
    tdsbrondata._spark = spark
    tdsbrondata._spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "false")
    tdsbrondata._spark.conf.set("spark.sql.parquet.vorder.enabled", "true")
    tdsbrondata._spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
    tdsbrondata._spark.conf.set("spark.microsoft.delta.optimizeWrite.binSize", "134217728")
    tdsbrondata._spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")

def lakehouse(schemaName, showLogging):

    tdsbrondata.schemaName = schemaName
    tdsbrondata.showLogging = showLogging

    timezone = pytz.timezone('Europe/Amsterdam')
    today = datetime.now(timezone).strftime('%Y%m%d')

    tdsbrondata.workspaceName = workspaceName = tdsbrondata._spark.conf.get("trident.workspace.name", "")
    tdsbrondata.lakehouseName = lakehouseName = tdsbrondata._spark.conf.get("trident.lakehouse.name", "")

    tdsbrondata._spark.sql(f"USE database {lakehouseName}.{schemaName}")

    tdsbrondata.sourceDataPath = f"abfss://{workspaceName}@onelake.dfs.fabric.microsoft.com/{lakehouseName}.Lakehouse/Files/SourceData/{schemaName}/{today}"
    tdsbrondata.tablesRootPath = f"abfss://{workspaceName}@onelake.dfs.fabric.microsoft.com/{lakehouseName}.Lakehouse/Tables/{schemaName}"