# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import pystray
import random
import win32gui
import win32con
import os
import sys
import atexit

# 改为实际的的大小
window_x=896
window_y=1152
icon_x=68
icon_y=68

class DesktopPet:
    def __init__(self):
        # 初始化路径处理
        self.base_path = self.get_base_path()
        
        # 创建主窗口
        self.root = tk.Tk()
        self.setup_window()
        self.load_image()
        self.setup_tray_icon()
        
        # 初始化位置和拖拽状态
        self.last_position = (0, 0)
        self.dragging = False
        self.drag_start_pos = (0, 0)
        
        # 绑定鼠标事件
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.end_drag)
        
        self.root.after(100, self.move_window)
        atexit.register(self.cleanup)

    def get_base_path(self):
        """处理开发环境和打包环境路径"""
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    def setup_window(self):
        """窗口配置"""
        self.root.overrideredirect(True)
        self.root.attributes('-alpha', 0.5)
        
        hwnd = self.root.winfo_id()
        win32gui.SetWindowLong(
            hwnd,
            win32con.GWL_EXSTYLE,
            win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) 
            | win32con.WS_EX_LAYERED 
            | win32con.WS_EX_TOOLWINDOW
        )
        win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_ALPHA)

    def load_image(self):
        """加载主图片"""
        try:
            img_path = os.path.join(self.base_path, 'assets', 'yxd.png')
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"图片路径不存在: {img_path}")
                
            img = Image.open(img_path).resize((window_x, window_y))
            self.tk_image = ImageTk.PhotoImage(img)
            label = tk.Label(self.root, image=self.tk_image, bg='black')
            label.pack()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载图片失败: {str(e)}")
            sys.exit(1)

    def start_drag(self, event):
        """鼠标按下开始拖拽"""
        self.dragging = True
        self.drag_start_pos = (event.x_root, event.y_root)
        if hasattr(self, 'scheduled_move'):
            self.root.after_cancel(self.scheduled_move)

    def on_drag(self, event):
        """鼠标拖拽过程中"""
        if self.dragging:
            delta_x = event.x_root - self.drag_start_pos[0]
            delta_y = event.y_root - self.drag_start_pos[1]
            
            current_x = self.root.winfo_x()
            current_y = self.root.winfo_y()
            
            new_x = current_x + delta_x
            new_y = current_y + delta_y
            
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            new_x = max(0, min(new_x, screen_width - window_x))
            new_y = max(0, min(new_y, screen_height - window_y))
            
            self.root.geometry(f"+{new_x}+{new_y}")
            self.drag_start_pos = (event.x_root, event.y_root)

    def end_drag(self, event):
        """鼠标释放结束拖拽"""
        self.dragging = False
        self.last_position = (self.root.winfo_x(), self.root.winfo_y())
        self.save_position()
        self.scheduled_move = self.root.after(60000, self.schedule_move)

    def schedule_move(self):
        """定时移动计划"""
        if not self.dragging:
            self.move_window()
        self.scheduled_move = self.root.after(60000, self.schedule_move)

    def move_window(self):
        """随机移动窗口"""
        if not self.dragging:
            sw = self.root.winfo_screenwidth() - window_x
            sh = self.root.winfo_screenheight() - window_y
            x = random.randint(0, sw)
            y = random.randint(0, sh)
            self.root.geometry(f"+{x}+{y}")
            self.last_position = (x, y)
            self.save_position()

    def setup_tray_icon(self):
        """创建系统托盘图标"""
        try:
            icon_path = os.path.join(self.base_path, 'assets', 'tray.png')
            image = Image.open(icon_path).resize((icon_x, icon_y))
            
            menu = pystray.Menu(
                pystray.MenuItem("退出", self.on_exit)
            )
            self.icon = pystray.Icon(
                "desktop_pet",
                image,
                "桌宠",
                menu
            )
            self.icon.run_detached()
            
        except Exception as e:
            messagebox.showerror("错误", f"创建托盘图标失败: {str(e)}")
            sys.exit(1)

    def on_exit(self, icon, item):
        """安全退出处理"""
        self.root.after(0, self.safe_exit)

    def safe_exit(self):
        """主线程退出操作"""
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        if self.root.winfo_exists():
            self.root.destroy()
#        if os.path.exists("pet_position.txt"):
#            try:
#                os.remove("pet_position.txt")
#            except:
#                pass
        sys.exit(0)

    def cleanup(self):
        """退出时清理资源（安全版）"""
        # 清理托盘图标
        if hasattr(self, 'icon') and self.icon:
            try:
                self.icon.stop()
            except Exception as e:
                print(f"清理托盘图标时出错: {e}")

        # 安全销毁窗口
        if hasattr(self, 'root'):
            try:
                # 使用winfo_exists前检查Tk是否初始化
                if self.root.winfo_exists():
                    self.root.destroy()
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    print(f"窗口销毁异常: {e}")
            except Exception as e:
                print(f"未知窗口错误: {e}")

if __name__ == "__main__":
    pet = DesktopPet()
    pet.root.after(1000, pet.schedule_move)
    pet.root.mainloop()