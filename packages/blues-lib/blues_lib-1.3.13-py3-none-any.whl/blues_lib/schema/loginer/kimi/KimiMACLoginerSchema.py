import sys,os,re
from .KimiLoginerFieldMixin import KimiLoginerFieldMixin
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.MACLoginerSchema import MACLoginerSchema

class KimiMACLoginerSchema(KimiLoginerFieldMixin,MACLoginerSchema):

  # === create mac subclass fields ===
  def get_before_fill_atom(self):
    # Typed atom
    atom = [
      # load the main content in 60 seconds
      self.atom_factory.createClickable('Popup the login dialog','.user-info-no-login',timeout=60),
    ]
    return self.atom_factory.createArray('switch atom',atom)

  def get_fill_atom(self):
    '''
    Typed atom
    Fill the phone number for send sms
    '''
    atom = [
      # wait the form dialog popup in 10 seconds
      self.atom_factory.createInput('Phone number','.phone-login-mobile-number','17607614755',timeout=10),
      self.atom_factory.createChoice('Agree privacy','.protocol-checkbox input',True),
    ]
    return self.atom_factory.createArray('Fill phone number',atom)

  def get_send_atom(self):
    '''
    Typed atom
    Send the sms
    '''
    atom = [
      self.atom_factory.createClickable('Next step','.phone-login-verify-code button'),
    ]
    return self.atom_factory.createArray('Send the sms',atom)

  def get_before_code_atom(self):
    pass

  def get_code_atom(self):
    '''
    Typed atom
    Fill in the auth code
    Only one character can be entered in the input field at a time
    It will receive a dynamic value
    '''
    return self.atom_factory.createInput('Char input','.phone-login-verify-code input','')

  def get_submit_atom(self):
    atom = [
      self.atom_factory.createClickable('Submit','.phone-login-action'),
    ]
    return self.atom_factory.createArray('submit',atom)
