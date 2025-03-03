import sys,os,re
from .QianWenLoginerFieldMixin import QianWenLoginerFieldMixin
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.QRCodeLoginerSchema import QRCodeLoginerSchema

class QianWenQRCodeLoginerSchema(QianWenLoginerFieldMixin,QRCodeLoginerSchema):

  def get_before_fill_atom(self):
    # Typed atom
    atom = [
      # load the main content in 60 seconds
      self.atom_factory.createClickable('Popup the login dialog','div[class^=footer] .tongyi-ui-button',timeout=10),
    ]
    return self.atom_factory.createArray('switch atom',atom)

  def get_code_atom(self):
    atoms = [
      # the title will be the return dict's key
      self.atom_factory.createShot('shot','div[role="alert-biz-modal"]:not([style]) div[class^=codeBox]'),
    ]
    return self.atom_factory.createArray('get shot image',atoms)


