import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.factory.LoginerSchemaFactory import LoginerSchemaFactory
from schema.loginer.kimi.KimiMACLoginerSchema import KimiMACLoginerSchema

class KimiLoginerSchemaFactory(LoginerSchemaFactory):

  def create_mac(self):
    return KimiMACLoginerSchema()
