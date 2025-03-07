import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tdsbrondata
from delta.tables import DeltaTable
from pyspark.sql import functions as F
from functools import reduce

def initDeltaTable(tableName, columns, recreate):
    
    table = f"{tdsbrondata.schemaName}.{tableName}"
    tablePath = f"{tdsbrondata.tablesRootPath}/{tableName}"

    if recreate and DeltaTable.isDeltaTable(tdsbrondata._spark, tablePath):
        tdsbrondata._spark.sql(f"DROP TABLE IF EXISTS {table}")

    if not tdsbrondata._spark.catalog.tableExists(table):
        builder = DeltaTable.create(tdsbrondata._spark).tableName(tableName)

        for column in columns:
            builder = builder.addColumn(column["nameDelta"], dataType=column["type"])

        for column in tdsbrondata.scdColumns:
            builder = builder.addColumn(column["name"], dataType=column["type"])

        builder.execute()

    dt = DeltaTable.forPath(tdsbrondata._spark, tablePath)
    dt.vacuum(840)

    return dt

def applyFilters(df, filters):

    if not filters:
        return df

    conditions = reduce(
        lambda accumulator, f: accumulator & (F.col(f[0]) == f[2]) if f[1] == "==" else accumulator & (F.col(f[0]) != f[2]),
        filters,
        F.lit(True)
    )
    
    return df.filter(conditions)

def reduceExistingData(df, columns):
    
    dfCurrent = df.filter((F.col("CurrentFlag") == 1) & (F.col("ScdEndDate").isNull()))

    columnsSelected = [column["nameDelta"] for column in columns]

    return dfCurrent.select(*columnsSelected)

def reduceNewData(df, columns):
    
    columnsSelected = [column["nameSpark"] for column in columns]
    
    renameMapping = {column["nameSpark"]: column["nameDelta"] for column in columns}
    
    dfReduced = df.select(*columnsSelected)
    
    for nameOld, nameNew in renameMapping.items():
        dfReduced = dfReduced.withColumnRenamed(nameOld, nameNew)

    return dfReduced.distinct()

def extractMutations(tableName, columns, dtExisting, filters):

    dfExisting = dtExisting.toDF()
    dfExistingReduced = reduceExistingData(df=dfExisting, columns=columns)

    dfNew = tdsbrondata._spark.read.parquet(f"{tdsbrondata.sourceDataPath}/{tableName}.parquet")
    dfNew = applyFilters(df=dfNew, filters=filters)

    dfNewReduced = reduceNewData(df=dfNew, columns=columns)

    dfMutations = dfNewReduced.exceptAll(dfExistingReduced)

    if tdsbrondata.showLogging:
        print(f'{tableName} - parquet file')
        display(dfNew)
        print(f'{tableName} - existing records (reduced)')
        display(dfExistingReduced)
        print(f'{tableName} - new records (reduced)')
        display(dfNewReduced)

    return dfMutations

def extractDeletions(tableName, columns, primaryKey, dtExisting, filters):

    dfExisting = dtExisting.toDF()
    dfExistingReduced = reduceExistingData(df=dfExisting, columns=columns)

    dfNew = tdsbrondata._spark.read.parquet(f"{tdsbrondata.sourceDataPath}/{tableName}.parquet")
    dfNew = applyFilters(df=dfNew, filters=filters)

    dfNewReduced = reduceNewData(df=dfNew, columns=columns)

    dfDeletions = dfExistingReduced.join(dfNewReduced, on=primaryKey, how="left_anti")

    if tdsbrondata.showLogging:
        print(f'{tableName} - deletions')
        display(dfDeletions)

    return dfDeletions

def addSurrogateKeys(tableName, dtExisting, dfMutations):
    
    maxSurrogateKey = dtExisting.toDF().agg({"SurrogateKey": "max"}).collect()[0][0] or 0

    dfMutations = dfMutations.withColumn(
        "SurrogateKey",
        F.monotonically_increasing_id() + maxSurrogateKey + 1
    )

    dfMutations = dfMutations.select(*dfMutations.columns, "SurrogateKey")

    if tdsbrondata.showLogging:
        print(f'{tableName} - mutations')
        display(dfMutations)

    return dfMutations

def updateRecords(columns, primaryKey, dtExisting, dfMutations):

    mergeCondition = f"existing.{primaryKey} = mutations.{primaryKey} AND existing.CurrentFlag = true"
    
    updateCondition = " OR ".join([f"existing.{column['nameDelta']} != mutations.{column['nameDelta']}" for column in columns])

    dtExisting.alias("existing") \
        .merge(
            dfMutations.alias("mutations"),
            mergeCondition
        ) \
        .whenMatchedUpdate(
            condition=F.expr(updateCondition),
            set={
                "ScdEndDate": F.current_timestamp(),
                "CurrentFlag": F.lit(False)
            }
        ) \
        .execute()

def insertRecords(columns, primaryKey, dtExisting, dfMutations):
    
    mergeCondition = f"existing.{primaryKey} = mutations.{primaryKey} AND existing.CurrentFlag = true"

    insertValues = {
        column["nameDelta"]: (
            F.col(f"mutations.{column['nameDelta']}")
            if column["nameDelta"] == "SurrogateKey" or column["nameDelta"] not in [scd["name"] for scd in tdsbrondata.scdColumns]
            else (
                F.current_timestamp() if column["nameDelta"] == "ScdStartDate"
                else F.lit(None).cast("timestamp") if column["nameDelta"] == "ScdEndDate"
                else F.lit(True)
            )
        )
        for column in columns
    }

    dtExisting.alias("existing") \
        .merge(
            dfMutations.alias("mutations"),
            mergeCondition
        ) \
        .whenNotMatchedInsert(
            values=insertValues
        ) \
        .execute()

def deleteRecords(primaryKey, dtExisting, dfDeletions):
    
    mergeCondition = f"existing.{primaryKey} = deletions.{primaryKey} AND existing.CurrentFlag = true"

    dtExisting.alias("existing") \
        .merge(
            dfDeletions.alias("deletions"),
            mergeCondition
        ) \
        .whenMatchedUpdate(
            set={
                "ScdEndDate": F.current_timestamp(),
                "CurrentFlag": F.lit(False)
            }
        ) \
        .execute()

def mutateDeltaTable(columns, primaryKey, dtExisting, dfMutations, dfDeletions):

    updateRecords(columns=columns, primaryKey=primaryKey, dtExisting=dtExisting, dfMutations=dfMutations)
    insertRecords(columns=columns, primaryKey=primaryKey, dtExisting=dtExisting, dfMutations=dfMutations)
    deleteRecords(primaryKey=primaryKey, dtExisting=dtExisting, dfDeletions=dfDeletions)

def processData(tableName, columns, primaryKey, filters, recreate):
    
    dtExisting = initDeltaTable(tableName=tableName, columns=columns, recreate=recreate)

    dfMutations = extractMutations(tableName=tableName, columns=columns, dtExisting=dtExisting, filters=filters)
    dfMutations = addSurrogateKeys(tableName=tableName, dtExisting=dtExisting, dfMutations=dfMutations)

    dfDeletions = extractDeletions(tableName=tableName, columns=columns, primaryKey=primaryKey, dtExisting=dtExisting, filters=filters)

    mutateDeltaTable(columns=columns, primaryKey=primaryKey, dtExisting=dtExisting, dfMutations=dfMutations, dfDeletions=dfDeletions)