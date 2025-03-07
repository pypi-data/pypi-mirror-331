from pyspark.sql.types import *

_notebookutils = None
_spark = None

schemaName = None
workspaceName = None
lakehouseName = None

showLoggin = None

sourceDataPath = None
tablesRootPath = None

typeMapping = {
    "LONG": LongType(),
    "INTEGER": IntegerType(),
    "STRING": StringType(),
    "BYTE": ByteType(),
    "BOOLEAN": BooleanType(),
    "TIMESTAMP": TimestampType(),
    "FLOAT": FloatType(),
    "DOUBLE": DoubleType(),
    "DATE": DateType(),
    "BINARY": BinaryType()
}

scdColumns = [
    {"name": "SurrogateKey", "type": "LONG"},
    {"name": "CurrentFlag", "type": "BYTE"},
    {"name": "ScdStartDate", "type": "TIMESTAMP"},
    {"name": "ScdEndDate", "type": "TIMESTAMP"}
]