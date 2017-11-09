# TODO: Get rid of pylint disables in pylintrc and fix

import time
from game_state import GameState
import wx
import wx.richtext

def write_color_text(rtc, string):
  # Takes a wx.richtext.RichTextCtrl and writes my wacky custom color-coded
  # text out to it.
  # Colors are specified via `r,g,b` in the text
  # TODO: There might be some better way to do this via the control's XML?
  # Note: Assumes there are no "`" in the text.
  tokens = string.split("`")
  rtc.BeginTextColour((0, 0, 0))
  rtc.BeginParagraphSpacing(0, 0)
  rtc.WriteText(tokens.pop(0))
  while tokens:
    color_string = tokens.pop(0)
    r, g, b = map(int, color_string.split(","))  # pylint: disable=invalid-name
    rtc.BeginTextColour((r, g, b))
    rtc.WriteText(tokens.pop(0))
  rtc.ShowPosition(rtc.GetLastPosition())

class ButtonPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    # Buttons
    # TODO: Keybinds not in the label
    self.button_sizer = wx.GridSizer(rows=3, cols=3, hgap=5, vgap=5)
    self.button_names = [" " * 30 for _ in range(4)]
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
      if labels[i] == "":
        self.buttons[i].Enable(False)
      else:
        self.buttons[i].Enable(True)

# TODO: Aren't these three panels all similar? We should be able to clean that
#       up
class CharacterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer(wx.VERTICAL)
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update_character(self, game_state):
    self.text_field.SetValue("")
    write_color_text(self.text_field, str(game_state.character))

class LogPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def add_entry(self, text):
    line = time.strftime("%m/%d/%y %H:%M:%S: ", time.localtime()) + text + "\n"
    write_color_text(self.text_field, line)

class EncounterPanel(wx.Panel):
  def __init__(self, parent):
    wx.Panel.__init__(self, parent, wx.NewId())
    style = wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER
    self.text_field = wx.richtext.RichTextCtrl(self, value="", style=style)
    bsizer = wx.BoxSizer()
    bsizer.Add(self.text_field, 1, wx.EXPAND)
    self.SetSizerAndFit(bsizer)

  def update(self, game_state):
    self.text_field.SetValue("")
    write_color_text(self.text_field, str(game_state.panel_text()))

class MainWindow(wx.Frame):
  # pylint: disable=too-many-instance-attributes
  def __init__(self, parent, title):
    wx.Frame.__init__(self, parent, title=title, size=(1000, 600))
    self.status_bar = self.CreateStatusBar(4)
    self.status_bar.SetStatusText("Welcome to SRS Game")
    self.status_bar.SetStatusText("Energy: 0", 1)
    self.status_bar.SetStatusText("GP: 0", 2)
    self.status_bar.SetStatusText("Time: 0", 3)

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
    #self.SetSizerAndFit(self.top_sizer)
    self.SetSizer(self.top_sizer)

    # Events
    # Bind the four buttons to the button_press method
    self.Bind(wx.EVT_MENU, self.on_exit, menu_exit)
    for i in range(len(self.button_panel.buttons)):
      button = self.button_panel.buttons[i]
      button.Bind(wx.EVT_BUTTON,
                  lambda evt, number=i: self.button_press(evt, number))

    # TODO: This accepts multiple key presses from one key press when held,
    #       which is not great.
    # Bind u/d/l/r for our four buttons
    bindings = [(wx.ACCEL_NORMAL, wx.WXK_UP, 0),
                (wx.ACCEL_NORMAL, wx.WXK_DOWN, 3),
                (wx.ACCEL_NORMAL, wx.WXK_LEFT, 1),
                (wx.ACCEL_NORMAL, wx.WXK_RIGHT, 2)]
    entries = []
    for binding in bindings:
      event_id = wx.NewId()
      entries.append((binding[0], binding[1], event_id))
      self.Bind(wx.EVT_BUTTON,
                lambda evt, temp=binding[2]:
                self.button_press(evt, temp), id=event_id)
    accel_table = wx.AcceleratorTable(entries)
    self.SetAcceleratorTable(accel_table)

    # Update UI with initial game state
    self.game_state = GameState()
    self.set_labels(self.game_state.get_choices())
    self.status_bar.SetStatusText(self.game_state.current_state(), 0)
    self.encounter_panel.update(self.game_state)

    self.Show()

  def button_press(self, evt, number):  # pylint: disable=unused-argument
    if not self.button_panel.buttons[number].IsEnabled():
      self.log_panel.add_entry("Debug: " + str(number) + " not enabled")
      return   # TODO: Do I need a Skip()?
    #self.log_panel.add_entry("Debug: " + str(number))
    logs = self.game_state.apply_choice(number)
    for log in logs:
      self.log_panel.add_entry(log)
    #self.status_bar.SetStatusText(self.game_state.current_state(), 0)
    # TODO: Revert to above
    self.status_bar.SetStatusText(str(self.game_state.state), 0)
    # TODO: unify names here. Also break out to general "Update" function?
    self.char_panel.update_character(self.game_state)
    self.set_labels(self.game_state.get_choices())
    self.encounter_panel.update(self.game_state)
    self.status_bar.SetStatusText("Energy: %d" % self.game_state.energy, 1)
    self.status_bar.SetStatusText("GP: %d" % self.game_state.character.gold, 2)
    time_spent = self.game_state.time_spent
    time_left = self.game_state.time_to_refresh()
    update_ready = "*" if self.game_state.tower_update_ready else ""
    self.status_bar.SetStatusText("Time: %d (%s%d)" % (time_spent,
                                                       update_ready,
                                                       time_left), 3)

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
