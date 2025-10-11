import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QPixmap, QTransform, QShortcut, QKeySequence
import pygetwindow as gw
import os
#import ctypes
#user32 = ctypes.windll.user32
#user32.SetProcessDPIAware()  # Pythonプロセス自体を DPI 対応

import pvv_mcp_server.avatar.mod_load_pixmaps
import pvv_mcp_server.avatar.mod_update_frame
import pvv_mcp_server.avatar.mod_update_position
import pvv_mcp_server.avatar.mod_right_click_context_menu

class AvatarWindow(QWidget):
    def __init__(self, image_dict, default_anime_key, flip=False, scale_percent=50, app_title="Claude", position="right_out"):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        #QShortcut(QKeySequence("Escape"), self, QApplication.quit)
        QShortcut(QKeySequence("Escape"), self, self.hide)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)

        self.image_dict = image_dict
        self.anime_key = default_anime_key
        self.anime_index = 0
        self.scale_percent = scale_percent
        self.app_title = app_title
        self.position = position
        self.flip = flip  # 左右反転フラグ

        # ここで pixmap の辞書を作る
        self.pixmap_dict = self.load_pixmaps(image_dict, scale_percent)

        # 初期表示
        self.update_frame()

        # タイマー
        self.frame_timer_interval = 150
        self.frame_timer = QTimer()
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(self.frame_timer_interval)

        self.follow_timer_interval = 150
        self.follow_timer = QTimer()
        self.follow_timer.timeout.connect(self.update_position)
        self.follow_timer.start(self.follow_timer_interval)

        # マウスドラッグ
        self._drag_pos = None  # ドラッグ開始位置

        # 右クリックメニューを有効化
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_context_menu)


    # 右クリックメニュー
    def right_click_context_menu(self, position: QPoint) -> None:
        pvv_mcp_server.avatar.mod_right_click_context_menu.right_click_context_menu(self, position)
        return

    # マウス押下時にドラッグ開始位置を記録
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.follow_timer.stop()
            event.accept()

    # マウス移動時にウィンドウを追従
    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    # マウスボタン離したらドラッグ終了
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = None
            event.accept()

    # PNG を一括で読み込み、スケーリングして辞書化
    def load_pixmaps(self, image_dict, scale_percent):
        ret = pvv_mcp_server.avatar.mod_load_pixmaps.load_pixmaps(self, image_dict, scale_percent)
        return ret

    # 口パク更新
    def update_frame(self):
        pvv_mcp_server.avatar.mod_update_frame.update_frame(self)
        return

    # Claude ウィンドウに追従
    def update_position(self):
        pvv_mcp_server.avatar.mod_update_position.update_position(self)
        return

    # セッター
    def set_anime_key(self, anime_key):
        if anime_key in self.pixmap_dict:
            self.anime_key = anime_key
            self.anime_index = 0

    # セッター
    def set_frame_timer_interval(self, val): 
        self.frame_timer_interval = val
        self.frame_timer.setInterval(self.frame_timer_interval)

    # セッター
    def set_position(self, val):
        self.position = val

    # セッター
    def set_flip(self, val):
        self.flip = val

# ----------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    images = {
        "立ち絵": ["josei_20_a.png"],
        "口パク": ["josei_20_a.png", "josei_20_b.png"]
    }

    window = AvatarWindow(images, default_anime_key="立ち絵", flip=True, scale_percent=50, app_title="Claude", position="right_out")
    window.update_position()
    window.show()

    # 切り替えテスト（3秒ごと）
    # from PySide6.QtCore import QTimer
    # sequence = [("立ち絵", 0), ("口パク", 3000), ("立ち絵", 6000), 
    #             ("口パク", 9000), ("立ち絵", 12000), ("口パク", 15000), ("立ち絵", 18000)]
    # for anime_key, delay in sequence:
    #     QTimer.singleShot(delay, lambda k=anime_key: window.set_anime_key(k))

    sys.exit(app.exec())
