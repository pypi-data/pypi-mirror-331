class KimiLoginerFieldMixin():

  # === common fields of BaiJia login ===
  def get_login_page_url_atom(self):
    '''
    @description: set the login's page url {URLAtom}
    '''
    return self.atom_factory.createURL('Log in url','https://kimi.moonshot.cn/')

  def get_loggedin_page_url_atom(self):
    '''
    @description: set the loggedin's page url {URLAtom}
    '''
    return self.atom_factory.createURL('Homepage url','https://kimi.moonshot.cn/')

  def get_login_page_identifier_atom(self):
    '''
    @description: set the css selector of the identifier in the login page{ElementAtom}
    '''
    return self.atom_factory.createElement('Login page identifier','.user-info-no-login')

  def get_max_login_waiting_time_atom(self):
    '''
    @description: set the max login waiting time {DataAtom}
    '''
    return self.atom_factory.createData('Wait for 5 seconds to confirm the login status',5)

  def get_proxy_config_atom(self):
    '''
    @description: set the browser proxy for persistent loginer {DataAtom}
    '''
    config = {
      'scopes': ['.*kimi.moonshot.cn.*'],
    }
    return self.atom_factory.createData('proxy config',config)

  def get_cookie_filter_config_atom(self):
    '''
    @description: set the logged cookie filter patterns for persistent loginer {DataAtom}
    '''
    config = {
      'url_pattern':'/api/kimiplus/history',
      'value_pattern':None
    }
    return self.atom_factory.createData('cookie filter config',config)
  
