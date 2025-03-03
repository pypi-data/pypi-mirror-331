import sys,os,re
from .QianWenLoginerFieldMixin import QianWenLoginerFieldMixin
sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from schema.loginer.MACLoginerSchema import MACLoginerSchema

class QianWenMACLoginerSchema(QianWenLoginerFieldMixin,MACLoginerSchema):

  # === create mac subclass fields ===
  def get_before_fill_atom(self):
    # Typed atom
    atom = [
      # load the main content in 60 seconds
      self.atom_factory.createClickable('Popup the login dialog','div[class^=footer] .tongyi-ui-button',timeout=60),
    ]
    return self.atom_factory.createArray('switch atom',atom)

  def get_fill_atom(self):
    '''
    Typed atom
    Fill the phone number for send sms
    '''
    atom = [
      # wait the form dialog popup in 10 seconds
      self.atom_factory.createFrame('in frame','div[role="alert-biz-modal"]:not([style]) iframe','in'),
      self.atom_factory.createInput('Phone number','#fm-sms-login-id','17607614755',timeout=10),
      #self.atom_factory.createChoice('Agree privacy','#fm-agreement-checkbox',True),
      self.atom_factory.createClickable('Agree privacy','label.fm-agreement-text'),
    ]
    return self.atom_factory.createArray('Fill phone number',atom)

  def get_send_atom(self):
    '''
    Typed atom
    Send the sms
    '''
    atom = [
      self.atom_factory.createClickable('Next step','.send-btn-link'),
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
    return self.atom_factory.createInput('Char input','#fm-smscode','')

  def get_submit_atom(self):
    atom = [
      self.atom_factory.createClickable('Submit','.fm-submit'),
    ]
    return self.atom_factory.createArray('submit',atom)
