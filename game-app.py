import wx

class ButtonPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    # Buttons
    # TODO: Keybinds not in the label
    # TODO: crosspad layout
    self.button_sizer = wx.GridSizer(rows=3, cols=3, hgap=5, vgap=5)
    self.buttons = []
    for i in range(4):
      self.button_sizer.Add(wx.StaticText(self))
      self.buttons.append(wx.Button(self, -1, "Button &" + str(i)))
      self.button_sizer.Add(self.buttons[i], 1, wx.EXPAND)

    self.SetSizer(self.button_sizer)
    self.SetAutoLayout(1)
    self.button_sizer.Fit(self)

class LogPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    self.text_field = wx.TextCtrl(self, value="Log Test "*100,
                                  style=wx.TE_READONLY | wx.TE_MULTILINE)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

class EncounterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    self.text_field = wx.TextCtrl(self, value="Encounter Test "*100,
                                  style=wx.TE_READONLY | wx.TE_MULTILINE)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

class MainWindow(wx.Frame):
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1000,600))   # size=(-1,-1)?
    self.status_bar = self.CreateStatusBar(3)
    self.status_bar.SetStatusText("Welcome to SRS Game")
    self.status_bar.SetStatusText("AP: 0", 1)
    self.status_bar.SetStatusText("GP: 0", 2)

    # Make menus
    # TODO: Not working
    file_menu = wx.Menu()
    menu_exit = file_menu.Append(wx.ID_EXIT, "E&xit", "Game over!")

    menu_bar = wx.MenuBar()
    menu_bar.Append(file_menu, "&File")
    self.SetMenuBar(menu_bar)

    # Events
    self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)
    #self.sizer = wx.GridSizer(rows=1, cols=2, hgap=5, vgap=5)
    self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)   # Top level

    self.left_sizer = wx.BoxSizer(wx.VERTICAL)
    self.button_panel = ButtonPanel(self)
    self.encounter_panel = EncounterPanel(self)
    self.left_sizer.Add(self.encounter_panel, 4, wx.EXPAND)
    self.left_sizer.Add(self.button_panel, 1)

    self.top_sizer.Add(self.left_sizer, 1)
    self.log_panel = LogPanel(self)
    self.top_sizer.Add(self.log_panel, 1, wx.EXPAND)
    self.SetSizerAndFit(self.top_sizer)

    self.Show()

  def OnExit(self, e):
    self.Close(True)

if __name__ == "__main__":
  app = wx.App(False)
  frame = MainWindow(None, "SRS Game")
  app.MainLoop()
