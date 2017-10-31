# pylint: disable=missing-docstring
# TODO: Get rid of that pylint

from game_state import GameState
import time
import wx


class ButtonPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    # Buttons
    # TODO: Keybinds not in the label
    # TODO: crosspad layout
    self.button_sizer = wx.GridSizer(rows=3, cols=3, hgap=5, vgap=5)
    # TODO: Method to change button names
    self.button_names = ["Button " + str(i) for i in range(4)]
    self.buttons = []
    for i in range(4):
      self.button_sizer.Add(wx.StaticText(self))
      self.buttons.append(wx.Button(self, -1, self.button_names[i]))
      self.button_sizer.Add(self.buttons[i], 1, wx.EXPAND)

    self.SetSizer(self.button_sizer)
    self.SetAutoLayout(1)
    self.button_sizer.Fit(self)

  def set_labels(self, labels):
    for i in range(4):
      self.buttons[i].SetLabel(labels[i])

class CharacterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    self.text_field = wx.TextCtrl(self, value="",
                                  style=wx.TE_READONLY | wx.TE_MULTILINE)
    bsizer = wx.BoxSizer(wx.VERTICAL)
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update_character(self, game_state):
    pass

class LogPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    self.text_field = wx.TextCtrl(self, value="",
                                  style=wx.TE_READONLY | wx.TE_MULTILINE)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def add_entry(self, text):
    self.text_field.AppendText(time.strftime("%m/%d/%y %H:%M:%S: ",
                                             time.localtime()))
    self.text_field.AppendText(text)
    self.text_field.AppendText("\n")

class EncounterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    self.text_field = wx.TextCtrl(self, value="",
                                  style=wx.TE_READONLY | wx.TE_MULTILINE)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

class MainWindow(wx.Frame):
  # pylint: disable=too-many-instance-attributes
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title)
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

    self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)   # Top level

    # Left side, containing the encounter panel and the button panel
    self.left_sizer = wx.BoxSizer(wx.VERTICAL)
    self.button_panel = ButtonPanel(self)
    self.encounter_panel = EncounterPanel(self)
    self.left_sizer.Add(self.encounter_panel, 4, wx.EXPAND)
    self.left_sizer.Add(self.button_panel, 1, wx.EXPAND)

    self.right_sizer = wx.BoxSizer(wx.VERTICAL)
    self.char_panel = CharacterPanel(self)
    self.log_panel = LogPanel(self)
    self.right_sizer.Add(self.char_panel, 2, wx.EXPAND)
    self.right_sizer.Add(self.log_panel, 1, wx.EXPAND)

    # For now, only the log_panel is on the right side.
    # Eventually, we'd have a right_sizer containing it
    self.top_sizer.Add(self.left_sizer, 1, wx.EXPAND)
    self.top_sizer.Add(self.right_sizer, 2, wx.EXPAND)
    self.SetSizerAndFit(self.top_sizer)

    # Events
    self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
    for i in range(len(self.button_panel.buttons)):
      button = self.button_panel.buttons[i]
      button.Bind(wx.EVT_BUTTON,
                  lambda evt, number=i: self.button_press(evt, number))

    self.game_state = GameState()
    self.set_labels(self.game_state.get_choices())
    self.status_bar.SetStatusText(self.game_state.state, 0)

    self.Show()

  def button_press(self, evt, number):  # pylint: disable=unused-argument
    self.log_panel.add_entry("Debug: " + str(number))
    logs = self.game_state.apply_choice(number)
    for log in logs:
      self.log_panel.add_entry(log)
    self.status_bar.SetStatusText(self.game_state.state, 0)

  def on_exit(self, evt):  # pylint: disable=unused-argument
    self.Close(True)

  def set_labels(self, labels):
    self.button_panel.set_labels(labels)

def run_app():
  wx_app = wx.App(False)
  wx_frame = MainWindow(None, "SRS Game")  # pylint: disable=unused-variable
  wx_app.MainLoop()

if __name__ == "__main__":
  run_app()
