from abc import ABC,abstractmethod
from .LoginerSchema import LoginerSchema

class QRCodeLoginerSchema(LoginerSchema,ABC):

  def __init__(self):

    super().__init__()

    # { ArrayAtom } : the behaviors that show the loginer form
    self.before_fill_atom = self.get_before_fill_atom()
    # { InputAtom } : the behavior that input the code
    self.code_atom = self.get_code_atom()
    self.captcha_valid_period_atom = self.get_captcha_valid_period_atom()

  # define the mini steps 
  def get_before_fill_atom(self):
    pass

  def get_code_atom(self):
    pass

  def get_captcha_valid_period_atom(self):
    return self.atom_factory.createData('Captcha valid period',5*60)