import sys,os,re,time
from abc import ABC,abstractmethod
from datetime import datetime
from .LoginerForm import LoginerForm 

sys.path.append(re.sub('blues_lib.*','blues_lib',os.path.realpath(__file__)))
from sele.behavior.BehaviorChain import BehaviorChain
from pool.DBTableIO import DBTableIO
from util.BluesMailer import BluesMailer  
from util.BluesDateTime import BluesDateTime
from util.BluesConsole import BluesConsole
from util.BluesURL import BluesURL

class QRCodeLoginerForm(LoginerForm,ABC):
  
  def __init__(self,schema):
    super().__init__(schema)
    
    # { int } Verification code expiration seconds
    self.captcha_valid_period = self.schema.captcha_valid_period_atom.get_value()
    self.login_page_url = self.schema.login_page_url_atom.get_value()
    # { ShotAtom } the qrcode image
    self.code_atom = self.schema.code_atom    
    # { DBTableIO }
    self.io = DBTableIO('naps_loginer')
    #  { str } the site's main domain
    self.domain = BluesURL.get_main_domain(self.login_page_url)
  
    # { int } the last mail sent timestamp 
    self.mail_sent_ts = 0
    # shot imge local file
    self.qrcode_image = ''
  
  # template method
  def perform(self,browser):
    self.browser = browser
    self.before_fill() 
    self.shot() 
    self.mail()
    time.sleep(100)
  
  # === step methods ===
  def before_fill(self):
    if self.schema.before_fill_atom:
      handler = BehaviorChain(self.browser,self.schema.before_fill_atom)
      handler.handle()

  def shot(self):
    handler = BehaviorChain(self.browser,self.code_atom)
    outcome = handler.handle()
    print('outcome',outcome)
    if outcome.data:
      self.qrcode_image = outcome.data.get('shot')
      BluesConsole.info('Shot QRcode: %s' % self.qrcode_image)
    else:
      BluesConsole.info('Shot QRcode failurell')
      raise Exception('Shot QRcode failurell')


  def mail(self,ts=None):
    if not self.qrcode_image:
      return

    mailer = BluesMailer.get_instance()
    self.mail_sent_ts = ts if ts else BluesDateTime.get_timestamp()
    para = 'The %s account needs to be re-logged in, a auth QRCode has been sent, please scan it by WeChat within %s seconds.' % (self.domain,self.captcha_valid_period)
    url = 'http://deepbluenet.com/naps-upload-code.html?site=%s&ts=%s' % (self.domain,self.mail_sent_ts)
    url_text = 'Click here to open the upload page.'
    content = mailer.get_html_body('NAPS',para,url,url_text)
    payload={
      'subject':mailer.get_title_with_time('NAPS: Sacn QRCode by WeChat'),
      'content':content,
      'images':[self.qrcode_image],
      'addressee':['langcai10@dingtalk.com','1771548541@qq.com','118190590@qq.com'], # send to multi addressee
      'addressee_name':'BluesLiu',
    }
    result = mailer.send(payload)
    if result.get('code') == 200:
      BluesConsole.success('Notify email sent successfully')
    else:
      raise Exception('Notify email sent failure')

