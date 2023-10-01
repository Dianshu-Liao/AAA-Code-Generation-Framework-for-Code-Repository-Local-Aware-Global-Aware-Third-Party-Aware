from utils.file_util import FileUtil
from utils.llm_util import LLMUtil
from config import Config

class CodeGenerator:

    @staticmethod
    def generate(input_prompt):
        if 'Chat' in Config.prompt_type:

            generated_code = LLMUtil.ask_chat_turbo(input_prompt)
            return generated_code
        else:
            generated_code = LLMUtil.ask_turbo(input_prompt)
            return generated_code



if __name__ == '__main__':
    LocalCodeSnippet = '''
import sys
import decimal
import time
import datetime
import calendar
import json
import re
import base64
from array import array
import ctypes

if sys.version >= "3":
    long = int
    basestring = unicode = str

from py4j.protocol import register_input_converter
from py4j.java_gateway import JavaClass

from pyspark import SparkContext
from pyspark.serializers import CloudPickleSerializer

__all__ = [
    "DataType", "NullType", "StringType", "BinaryType", "BooleanType", "DateType",
    "TimestampType", "DecimalType", "DoubleType", "FloatType", "ByteType", "IntegerType",
    "LongType", "ShortType", "ArrayType", "MapType", "StructField", "StructType"]


    '''

    FunctionDef = '''def to_arrow_schema(schema):'''

    UserDemand = '''Convert a schema from Spark to Arrow'''

    ReusableFunctionsPrompt = '''
function: 1:
summary: Create a DataFrame from a given pandas.DataFrame by slicing it into partitions, converting
        to Arrow data, then sending to the JVM to parallelize. If a schema is passed in, the
        data types will be used to coerce the data in Pandas to Arrow conversion.
code: def _create_from_pandas_with_arrow(self, pdf, schema, timezone):
    # Implementation...

function: 2:
summary: Convert schema from Arrow to Spark.
code: def from_arrow_schema(arrow_schema):
    # Implementation...

function: 3:
summary: Convert pyarrow type to Spark data type.
code: def from_arrow_type(at):
    # Implementation...

function: 4:
summary: Convert Spark data type to pyarrow type
code: def to_arrow_type(dt):
    # Implementation...

function: 5:
summary: Specifies the input schema.
code: def schema(self, schema):
    # Implementation...

function: 6:
summary: Returns the contents of this :class:`DataFrame` as Pandas ``pandas.DataFrame``.
code: def toPandas(self):
    # Implementation...

function: 7:
summary: Create an RDD for DataFrame from a list or pandas.DataFrame, returns
        the RDD and schema.
code: def _createFromLocal(self, data, schema):
    # Implementation...

function: 8:
summary: Converts a binary column of avro format into its corresponding catalyst value. The specified
    schema must match the read data, otherwise the behavior is undefined: it may fail or return
    arbitrary result.
code: def from_avro(data, jsonFormatSchema, options={}):
    # Implementation...

function: 9:
summary: Creates a :class:`DataFrame` from an :class:`RDD`, a list or a :class:`pandas.DataFrame`.
code: def createDataFrame(self, data, schema=None, samplingRatio=None, verifySchema=True):
    # Implementation...

function: 10:
summary: Parses a CSV string and infers its schema in DDL format.
code: def schema_of_csv(csv, options={}):
    # Implementation...
    '''

    generated_code = CodeGenerator.generate_with_reusable_functionPrompt(LocalCodeSnippet, FunctionDef, UserDemand, ReusableFunctionsPrompt)
    print(generated_code)