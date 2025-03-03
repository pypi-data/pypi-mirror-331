import sys,os,re
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.factory.QianWenLoginerSchemaFactory import QianWenLoginerSchemaFactory
from loginer.factory.LoginerFactory import LoginerFactory
from loginer.OnceLoginer import OnceLoginer   
from loginer.PersistentLoginer import PersistentLoginer   
from loginer.form.MACLoginerForm import MACLoginerForm   
from loginer.form.QRCodeLoginerForm import QRCodeLoginerForm   

class QianWenLoginerFactory(LoginerFactory):

  def create_once_mac(self):
    factory = QianWenLoginerSchemaFactory()
    schema = factory.create_mac()
    form = MACLoginerForm(schema)
    return OnceLoginer(schema,form)

  def create_persistent_mac(self):
    factory = QianWenLoginerSchemaFactory()
    schema = factory.create_mac()
    form = MACLoginerForm(schema)
    return PersistentLoginer(schema,form)

  def create_once_qrcode(self):
    factory = QianWenLoginerSchemaFactory()
    schema = factory.create_qrcode()
    form = QRCodeLoginerForm(schema)
    return OnceLoginer(schema,form)

  def create_persistent_qrcode(self):
    factory = QianWenLoginerSchemaFactory()
    schema = factory.create_qrcode()
    form = QRCodeLoginerForm(schema)
    return PersistentLoginer(schema,form)







