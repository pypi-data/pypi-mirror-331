import tkinter as tk

from easyTkinter.easy_auto_window import EasyAutoWindow
from easyTkinter.easy_button import EasyButton
from easyTkinter.easy_drop_list import EasyDropList
from easyTkinter.easy_label import EasyLabel
from easyTkinter.easy_progressbar import EasyProgressbar
from easyTkinter.easy_warning_windows import EasyWarningWindows


def trigger():
    EasyWarningWindows(window, "信息", "这是按钮被点击时触发的代码, 可以改动参数 cmd 来实现").show_warning()


def start_progressbar():
    for _ in range(100):
        progressbar.increase_progressbar()


def quit_window():
    window.destroy()


def author():
    EasyWarningWindows(window, "信息", "作者: Yan Xinle").show_warning()


window = tk.Tk()

EasyAutoWindow(window, window_title="easyTkinter 库的小部件", window_width_value=1200, window_height_value=800,
               adjust_y=False, adjust_x=False)
EasyLabel(window, text="这个窗口是由 easyTkinter 库的 EasyAutoWindow 类创建的, 你可以通过调各种参数来控制窗口",
          font_size=20, side=tk.TOP, expand=tk.YES)
EasyLabel(window, text="这几行文本是由 easyTkinter 库的 EasyLabel 类创建的, 可以调整颜色, 字体等样式", font_size=20,
          side=tk.TOP, expand=tk.YES)
EasyLabel(window, text="接下来, 我们来看下 easyTkinter 库可以创建的几个小部件, 这些小部件都可以调整各种样式",
          font_size=20, side=tk.TOP, expand=tk.YES)

EasyLabel(window, text="1. 按钮", font_size=20, side=tk.TOP, expand=tk.YES)
EasyButton(window, text="点一下我", expand=tk.YES, width=6, height=1, font_size=12, cmd=trigger)

EasyLabel(window, text="2. 下拉列表", font_size=20, side=tk.TOP, expand=tk.YES)
EasyDropList(window)

EasyLabel(window, text="3. 进度条", font_size=20, side=tk.TOP, expand=tk.YES)
progressbar = EasyProgressbar(window, expand=tk.YES, side=tk.TOP)
EasyButton(window, text="开始", font_size=12, side=tk.TOP, expand=tk.YES, width=6, height=1, cmd=start_progressbar)

EasyLabel(window, text="除了这些, 还有其他小部件可以创建出来, 可以探索一下", font_size=20, side=tk.TOP, expand=tk.YES)

EasyButton(window, text="退出", font_size=12, width=6, height=1, side=tk.RIGHT, cmd=quit_window)

EasyButton(window, text="作者", font_size=12, width=6, height=1, side=tk.RIGHT, cmd=author)

window.mainloop()
