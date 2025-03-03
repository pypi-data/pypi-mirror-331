import sys,os,re

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.factory.LoginerSchemaFactory import LoginerSchemaFactory
from schema.loginer.qianwen.QianWenMACLoginerSchema import QianWenMACLoginerSchema
from schema.loginer.qianwen.QianWenQRCodeLoginerSchema import QianWenQRCodeLoginerSchema

class QianWenLoginerSchemaFactory(LoginerSchemaFactory):

  def create_mac(self):
    return QianWenMACLoginerSchema()

  def create_qrcode(self):
    return QianWenQRCodeLoginerSchema()