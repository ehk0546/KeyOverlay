"""
리듬 게임 키 오버레이
단축키: Ctrl+Alt+S (설정)  /  Ctrl+Alt+M (이동 모드)
"""
import sys, os, json, ctypes, time, random, math
from collections import deque
from copy import deepcopy

try:
    from PyQt5.QtWidgets import (
        QApplication, QWidget, QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
        QFormLayout, QLabel, QPushButton, QCheckBox, QSpinBox, QRadioButton,
        QListWidget, QColorDialog, QSystemTrayIcon, QMenu,
        QAction, QSlider, QMessageBox, QInputDialog, QScrollArea,
        QGridLayout, QLineEdit, QComboBox,
    )
    from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QPointF, pyqtSignal, QObject
    from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QIcon, QPixmap,
                              QRadialGradient, QLinearGradient, QBrush)
except ImportError:
    print("pip install PyQt5"); sys.exit(1)

try:
    from pynput import keyboard as kb
except ImportError:
    print("pip install pynput"); sys.exit(1)

# ── i18n ──────────────────────────────────────────────────────────────────────
_LANG_NAMES = [('ko','한국어'),('en','English'),('ru','Русский'),('ja','日本語'),('zh','中文')]
_LANG = {
    'ko': {
        'title':'키 오버레이 설정',
        'tab_keys':'키','tab_style':'스타일','tab_anim':'애니메이션',
        'tab_stats':'통계','tab_general':'일반',
        'btn_quit':'오버레이 끄기','btn_reset':'기본값 초기화','btn_save':'저장 및 적용',
        'keys_label':'트래킹할 키  (위 = 왼쪽)',
        'key_add':'추가','key_del':'제거',
        'key_hint':'특수키: space / shift / ctrl / alt / enter / tab / backspace',
        'dlg_add_title':'키 추가','dlg_add_prompt':'키 이름 (예: d, space, shift):',
        'kw':'키 너비:','kh':'키 높이:','spacing':'간격:','fs':'폰트 크기:',
        'sec_color':'─── 색상 ───',
        'col_on':'테두리/블록 (눌림):','col_off':'테두리 (기본):',
        'txt_on':'글자 (눌림):','txt_off':'글자 (기본):',
        'sec_fill':'─── 누를 때 박스 채우기 ───','fill_alpha':'채우기 투명도:',
        'sec_opacity':'─── 창 불투명도 ───','opacity':'불투명도:',
        'sec_block':'─── 블록 ───',
        'block_on':'블록 올라가는 효과 켜기',
        'trail_h':'블록 높이 (px):',
        'scroll_spd':'스크롤 속도:','fade_zone':'페이드 구역 (px):',
        'push_px':'키 눌림 깊이 (px):',
        'sec_particle':'─── 파티클 ───',
        'pt_on':'파티클 켜기 (키 누를 때 튀김)',
        'pt_continuous':'누르는 동안 계속 방출',
        'pt_color':'파티클 색상:','pt_cnt':'첫 방출 개수:','pt_rate':'지속 방출 (개/틱):',
        'sec_glow':'─── 빛 효과 ───',
        'glow_on':'빛 효과 켜기',
        'glow_block':'블록 주변 빛',
        'glow_pulse':'키 누를 때 섬광',
        'glow_color':'빛 색상:','glow_size':'빛 크기:','glow_alpha':'빛 강도:',
        'show_kps':'KPS (초당 키 입력 수) 표시',
        'show_key_count':'키별 누른 횟수 표시 (박스 안)',
        'show_total':'전체 누른 횟수 표시',
        'reset_stats':'통계 초기화 (카운트 리셋)','reset_done':'통계가 초기화됐어요.',
        'language':'언어:',
        'hotkey_mod':'단축키 조합 (M=이동 / S=설정):',
        'color_dialog':'색상 선택',
        'preset_label':'프리셋:',
        'key_color_label':'키 색상:','key_select_hint':'키를 목록에서 선택하세요',
        'confirm_reset':'기본값으로 되돌릴까요?','done':'완료',
        'tray_open':'설정 열기','tray_move':'이동 모드','tray_quit':'종료',
        'tray_tip':'키 오버레이  —  우클릭으로 메뉴',
        'move_hint':'[이동] 드래그  ·  {mod}+M 잠금  ·  ESC 종료',
    },
    'en': {
        'title':'Key Overlay Settings',
        'tab_keys':'Keys','tab_style':'Style','tab_anim':'Animation',
        'tab_stats':'Stats','tab_general':'General',
        'btn_quit':'Turn Off Overlay','btn_reset':'Reset Defaults','btn_save':'Save & Apply',
        'keys_label':'Tracked Keys  (top = left)',
        'key_add':'Add','key_del':'Remove',
        'key_hint':'Special: space / shift / ctrl / alt / enter / tab / backspace',
        'dlg_add_title':'Add Key','dlg_add_prompt':'Key name (e.g. d, space, shift):',
        'kw':'Key Width:','kh':'Key Height:','spacing':'Spacing:','fs':'Font Size:',
        'sec_color':'─── Colors ───',
        'col_on':'Border/Block (pressed):','col_off':'Border (default):',
        'txt_on':'Label (pressed):','txt_off':'Label (default):',
        'sec_fill':'─── Box Fill on Press ───','fill_alpha':'Fill Opacity:',
        'sec_opacity':'─── Window Opacity ───','opacity':'Opacity:',
        'sec_block':'─── Block ───',
        'block_on':'Enable rising block effect',
        'trail_h':'Block Height (px):',
        'scroll_spd':'Scroll Speed:','fade_zone':'Fade Zone (px):',
        'push_px':'Key Press Depth (px):',
        'sec_particle':'─── Particles ───',
        'pt_on':'Enable Particles (burst on press)',
        'pt_continuous':'Emit continuously while held',
        'pt_color':'Particle Color:','pt_cnt':'Burst Count:','pt_rate':'Continuous Rate (per tick):',
        'sec_glow':'─── Glow / Light ───',
        'glow_on':'Enable Glow',
        'glow_block':'Block ambient glow',
        'glow_pulse':'Flash on key press',
        'glow_color':'Glow Color:','glow_size':'Glow Size:','glow_alpha':'Glow Intensity:',
        'show_kps':'Show KPS (keys per second)',
        'show_key_count':'Show Key Count (inside box)',
        'show_total':'Show Total Count',
        'reset_stats':'Reset Stats','reset_done':'Stats have been reset.',
        'language':'Language:',
        'hotkey_mod':'Hotkey Modifier (M=move / S=settings):',
        'color_dialog':'Choose Color',
        'preset_label':'Preset:',
        'key_color_label':'Key Color:','key_select_hint':'Select a key from the list',
        'confirm_reset':'Reset to default settings?','done':'Done',
        'tray_open':'Open Settings','tray_move':'Move Mode','tray_quit':'Quit',
        'tray_tip':'Key Overlay  —  Right-click for menu',
        'move_hint':'[Move] Drag  ·  {mod}+M to lock  ·  ESC to quit',
    },
    'ru': {
        'title':'Настройки оверлея клавиш',
        'tab_keys':'Клавиши','tab_style':'Стиль','tab_anim':'Анимация',
        'tab_stats':'Статистика','tab_general':'Общие',
        'btn_quit':'Выключить оверлей','btn_reset':'Сбросить','btn_save':'Сохранить и применить',
        'keys_label':'Отслеживаемые клавиши  (вверху = слева)',
        'key_add':'Добавить','key_del':'Удалить',
        'key_hint':'Спец. клавиши: space / shift / ctrl / alt / enter / tab / backspace',
        'dlg_add_title':'Добавить клавишу','dlg_add_prompt':'Название (напр. d, space, shift):',
        'kw':'Ширина:','kh':'Высота:','spacing':'Интервал:','fs':'Размер шрифта:',
        'sec_color':'─── Цвета ───',
        'col_on':'Рамка/блок (нажато):','col_off':'Рамка (обычно):',
        'txt_on':'Текст (нажато):','txt_off':'Текст (обычно):',
        'sec_fill':'─── Заливка при нажатии ───','fill_alpha':'Прозрачность заливки:',
        'sec_opacity':'─── Прозрачность окна ───','opacity':'Прозрачность:',
        'sec_block':'─── Блок ───',
        'block_on':'Включить эффект подъёма блока',
        'trail_h':'Высота блока (px):',
        'scroll_spd':'Скорость прокрутки:','fade_zone':'Зона затухания (px):',
        'push_px':'Глубина нажатия (px):',
        'sec_particle':'─── Частицы ───',
        'pt_on':'Включить частицы (при нажатии)',
        'pt_continuous':'Непрерывный выброс при удержании',
        'pt_color':'Цвет частиц:','pt_cnt':'Количество при нажатии:','pt_rate':'Скорость (за тик):',
        'sec_glow':'─── Свечение ───',
        'glow_on':'Включить свечение',
        'glow_block':'Свечение вокруг блока',
        'glow_pulse':'Вспышка при нажатии',
        'glow_color':'Цвет:','glow_size':'Размер:','glow_alpha':'Яркость:',
        'show_kps':'Показать KPS (нажатий в секунду)',
        'show_key_count':'Счётчик нажатий (внутри блока)',
        'show_total':'Общий счётчик',
        'reset_stats':'Сбросить статистику','reset_done':'Статистика сброшена.',
        'language':'Язык:',
        'hotkey_mod':'Сочетание клавиш (M=перемещение / S=настройки):',
        'color_dialog':'Выбор цвета',
        'preset_label':'Предустановка:',
        'key_color_label':'Цвет клавиши:','key_select_hint':'Выберите клавишу из списка',
        'confirm_reset':'Сбросить до стандартных настроек?','done':'Готово',
        'tray_open':'Открыть настройки','tray_move':'Режим перемещения','tray_quit':'Выйти',
        'tray_tip':'Клавишный оверлей  —  ПКМ для меню',
        'move_hint':'[Перемещение] Перетащите  ·  {mod}+M фиксация  ·  ESC выход',
    },
    'ja': {
        'title':'キーオーバーレイ設定',
        'tab_keys':'キー','tab_style':'スタイル','tab_anim':'アニメ',
        'tab_stats':'統計','tab_general':'一般',
        'btn_quit':'オーバーレイを終了','btn_reset':'デフォルトに戻す','btn_save':'保存して適用',
        'keys_label':'トラッキングキー  (上 = 左)',
        'key_add':'追加','key_del':'削除',
        'key_hint':'特殊キー: space / shift / ctrl / alt / enter / tab / backspace',
        'dlg_add_title':'キー追加','dlg_add_prompt':'キー名 (例: d, space, shift):',
        'kw':'キー幅:','kh':'キー高さ:','spacing':'間隔:','fs':'フォントサイズ:',
        'sec_color':'─── カラー ───',
        'col_on':'枠/ブロック (押下時):','col_off':'枠 (通常):',
        'txt_on':'テキスト (押下時):','txt_off':'テキスト (通常):',
        'sec_fill':'─── 押下時の塗りつぶし ───','fill_alpha':'塗りつぶし透明度:',
        'sec_opacity':'─── ウィンドウ透明度 ───','opacity':'透明度:',
        'sec_block':'─── ブロック ───',
        'block_on':'ライジングブロック効果を有効化',
        'trail_h':'ブロック高さ (px):',
        'scroll_spd':'スクロール速度:','fade_zone':'フェードゾーン (px):',
        'push_px':'キー押下深度 (px):',
        'sec_particle':'─── パーティクル ───',
        'pt_on':'パーティクルを有効化 (押下時)',
        'pt_continuous':'押し続ける間連続放出',
        'pt_color':'パーティクルカラー:','pt_cnt':'バースト数:','pt_rate':'連続レート (毎tick):',
        'sec_glow':'─── グロー ───',
        'glow_on':'グローを有効化',
        'glow_block':'ブロック周辺グロー',
        'glow_pulse':'キー押下時フラッシュ',
        'glow_color':'グローカラー:','glow_size':'グローサイズ:','glow_alpha':'グロー強度:',
        'show_kps':'KPS を表示 (毎秒キー入力数)',
        'show_key_count':'キー別カウントを表示 (ボックス内)',
        'show_total':'総カウントを表示',
        'reset_stats':'統計リセット','reset_done':'統計がリセットされました。',
        'language':'言語:',
        'hotkey_mod':'ホットキー (M=移動 / S=設定):',
        'color_dialog':'カラー選択',
        'preset_label':'プリセット:',
        'key_color_label':'キーカラー:','key_select_hint':'リストからキーを選択',
        'confirm_reset':'デフォルト設定に戻しますか?','done':'完了',
        'tray_open':'設定を開く','tray_move':'移動モード','tray_quit':'終了',
        'tray_tip':'キーオーバーレイ  —  右クリックでメニュー',
        'move_hint':'[移動] ドラッグ  ·  {mod}+M ロック  ·  ESC 終了',
    },
    'zh': {
        'title':'键盘覆盖层设置',
        'tab_keys':'按键','tab_style':'样式','tab_anim':'动画',
        'tab_stats':'统计','tab_general':'通用',
        'btn_quit':'关闭覆盖层','btn_reset':'恢复默认','btn_save':'保存并应用',
        'keys_label':'跟踪的按键  (上 = 左)',
        'key_add':'添加','key_del':'删除',
        'key_hint':'特殊键: space / shift / ctrl / alt / enter / tab / backspace',
        'dlg_add_title':'添加按键','dlg_add_prompt':'按键名称 (例: d, space, shift):',
        'kw':'键宽:','kh':'键高:','spacing':'间距:','fs':'字体大小:',
        'sec_color':'─── 颜色 ───',
        'col_on':'边框/方块 (按下时):','col_off':'边框 (默认):',
        'txt_on':'文字 (按下时):','txt_off':'文字 (默认):',
        'sec_fill':'─── 按下时填充 ───','fill_alpha':'填充透明度:',
        'sec_opacity':'─── 窗口透明度 ───','opacity':'透明度:',
        'sec_block':'─── 方块 ───',
        'block_on':'启用上升方块效果',
        'trail_h':'方块高度 (px):',
        'scroll_spd':'滚动速度:','fade_zone':'淡化区域 (px):',
        'push_px':'按键深度 (px):',
        'sec_particle':'─── 粒子 ───',
        'pt_on':'启用粒子 (按键时喷射)',
        'pt_continuous':'按住时持续发射',
        'pt_color':'粒子颜色:','pt_cnt':'喷射数量:','pt_rate':'持续速率 (每tick):',
        'sec_glow':'─── 发光 ───',
        'glow_on':'启用发光',
        'glow_block':'方块周围发光',
        'glow_pulse':'按键时闪光',
        'glow_color':'发光颜色:','glow_size':'发光大小:','glow_alpha':'发光强度:',
        'show_kps':'显示KPS (每秒按键数)',
        'show_key_count':'显示按键次数 (方块内)',
        'show_total':'显示总按键次数',
        'reset_stats':'重置统计','reset_done':'统计已重置。',
        'language':'语言:',
        'hotkey_mod':'快捷键修饰符 (M=移动 / S=设置):',
        'color_dialog':'选择颜色',
        'preset_label':'预设:',
        'key_color_label':'键颜色:','key_select_hint':'从列表中选择按键',
        'confirm_reset':'恢复默认设置?','done':'完成',
        'tray_open':'打开设置','tray_move':'移动模式','tray_quit':'退出',
        'tray_tip':'键盘覆盖层  —  右键点击打开菜单',
        'move_hint':'[移动] 拖动  ·  {mod}+M 锁定  ·  ESC 退出',
    },
}
def tr(lang, key, **kw):
    text = _LANG.get(lang, _LANG['en']).get(key, _LANG['en'].get(key, key))
    return text.format(**kw) if kw else text

# ── platform guard ────────────────────────────────────────────────────────────
if sys.platform != 'win32':
    print("Error: This application requires Windows.")
    sys.exit(1)

# ── safe config I/O ───────────────────────────────────────────────────────────
def _load_cfg(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return deepcopy(DEFAULTS)

def _save_cfg(path, cfg):
    tmp = path + '.tmp'
    try:
        with open(tmp, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError:
        try: os.remove(tmp)
        except OSError: pass

# ── win32 ─────────────────────────────────────────────────────────────────────
GWL_EXSTYLE = -20; WS_EX_LAYERED = 0x80000; WS_EX_TRANSPARENT = 0x20
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002; SWP_NOSIZE = 0x0001; SWP_NOACTIVATE = 0x0010
def set_clickthrough(hwnd, on):
    ex = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    ex = ex | WS_EX_LAYERED | WS_EX_TRANSPARENT if on \
         else (ex | WS_EX_LAYERED) & ~WS_EX_TRANSPARENT
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex)
def force_topmost(hwnd):
    ctypes.windll.user32.SetWindowPos(
        hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE|SWP_NOSIZE|SWP_NOACTIVATE)

# ── key helpers ───────────────────────────────────────────────────────────────
_LABELS = {'space':'SPC','shift':'SHF','ctrl':'CTL','alt':'ALT',
           'enter':'ENT','backspace':'BSP','tab':'TAB','caps_lock':'CAP','delete':'DEL'}
_ALIASES = {'shift_l':'shift','shift_r':'shift','ctrl_l':'ctrl','ctrl_r':'ctrl',
            'alt_l':'alt','alt_r':'alt','alt_gr':'alt'}
def key_label(k): return _LABELS.get(k.lower(), k.upper()[:3])
def normalize(key):
    try:
        c = key.char
        if c:
            if len(c)==1 and 1<=ord(c)<=26: return chr(ord(c)+96)
            return c.lower()
    except AttributeError: pass
    try:
        vk = key.vk
        if vk and 65<=vk<=90: return chr(vk+32)
    except AttributeError: pass
    try: return _ALIASES.get(key.name.lower(), key.name.lower())
    except: return None

# ── defaults ──────────────────────────────────────────────────────────────────
DEFAULTS = {
    "keys": ["d","f","j","k"],
    "language": "en",
    "hotkey_modifier": "ctrl+alt",
    "style": {
        "key_width":50,"key_height":50,"spacing":8,"pad":8,
        "color_pressed":"#ffffff","color_released":"#555555",
        "fill_alpha":60,
        "text_on":"#ffffff","text_off":"#888888","font_size":18,"opacity":1.0,
    },
    "animation": {
        "trail_height":300,"min_height":0,"block_on":True,
        "scroll_speed":6,"fade_zone":80,"frame_ms":16,"push_px":3,
        "particle_on":True,"particle_continuous":True,
        "particle_color":"#ffffff","particle_count":12,"particle_rate":2,
        "glow_on":True,"glow_block":True,"glow_pulse":True,
        "glow_color":"#ffffff","glow_size":14,"glow_alpha":110,
    },
    "key_colors": {},
    "stats": {"show_kps":True,"show_key_count":True,"show_total":False},
    "window": {},
}

# ── animation objects ─────────────────────────────────────────────────────────
class HoldBlock:
    __slots__ = ('key_idx','y_top','y_bottom','released')
    def __init__(self, idx, y_bottom, min_h):
        self.key_idx=idx; self.y_bottom=float(y_bottom)
        self.y_top=float(y_bottom-min_h); self.released=False

class Particle:
    __slots__ = ('x','y','vx','vy','alpha','size')
    def __init__(self, x, y, vx, vy, size=4):
        self.x=float(x); self.y=float(y)
        self.vx=vx; self.vy=vy; self.alpha=255; self.size=size

class GlowPulse:
    __slots__ = ('key_idx','alpha','radius')
    def __init__(self, idx, max_r):
        self.key_idx=idx; self.alpha=255; self.radius=float(max_r*0.3)

# ── color picker ──────────────────────────────────────────────────────────────
class ColorBtn(QPushButton):
    def __init__(self, hex_color, dlg_title='색상 선택', on_change=None, parent=None):
        super().__init__(parent)
        self._c=QColor(hex_color); self._title=dlg_title; self._on_change=on_change
        self.setFixedSize(70,26); self._refresh()
    def _refresh(self):
        self.setStyleSheet(f"background:{self._c.name()};border:1px solid #aaa;border-radius:3px;")
    def mouseReleaseEvent(self, e):
        popup=ColorPickerPopup(self._c.name(), self)
        pos=self.mapToGlobal(QPoint(0, self.height()))
        scr=QApplication.primaryScreen().geometry()
        popup.adjustSize()
        popup.move(min(pos.x(), scr.width()-popup.width()-4),
                   min(pos.y(), scr.height()-popup.height()-4))
        if popup.exec_()==QDialog.Accepted:
            c=popup.result()
            if c.isValid():
                self._c=c; self._refresh()
                if self._on_change: self._on_change(c.name())
    def hex(self): return self._c.name()
    def set_color(self, hex_color):
        self._c=QColor(hex_color); self._refresh()

# ── settings stylesheet ───────────────────────────────────────────────────────
_SETTINGS_QSS = """
QDialog{background:#13131f;color:#ddd;font-family:'Segoe UI';}
QTabWidget::pane{border:1px solid #252538;background:#181828;border-radius:0 5px 5px 5px;}
QTabBar::tab{background:#0e0e1c;color:#888;padding:7px 13px;border:1px solid #252538;
             border-bottom:none;border-radius:4px 4px 0 0;min-width:54px;font-size:9pt;}
QTabBar::tab:selected{background:#181828;color:#dde;border-bottom-color:#181828;}
QTabBar::tab:hover:!selected{background:#171728;color:#aaa;}
QWidget{background:#181828;color:#ddd;font-family:'Segoe UI';font-size:10pt;}
QLabel{background:transparent;color:#ccc;}
QLabel#sec{color:#7a7acc;font-weight:bold;font-size:9pt;
           padding:8px 0 3px 0;border-bottom:1px solid #252545;}
QSpinBox{background:#1e1e34;border:1px solid #333355;border-radius:4px;
         padding:3px 6px;color:#ddd;min-width:60px;}
QSpinBox:focus{border-color:#5555aa;}
QSpinBox::up-button,QSpinBox::down-button{background:#252540;border:none;width:16px;}
QCheckBox{background:transparent;color:#ccc;spacing:7px;}
QCheckBox::indicator{width:15px;height:15px;background:#1e1e34;
                     border:1px solid #333355;border-radius:3px;}
QCheckBox::indicator:checked{background:#4a4aee;border-color:#6a6aff;}
QRadioButton{background:transparent;color:#ccc;spacing:7px;}
QRadioButton::indicator{width:14px;height:14px;background:#1e1e34;
                        border:1px solid #333355;border-radius:7px;}
QRadioButton::indicator:checked{background:#4a4aee;border-color:#6a6aff;}
QListWidget{background:#1e1e34;border:1px solid #333355;border-radius:5px;
            color:#ddd;outline:0;padding:2px;}
QListWidget::item{padding:4px 8px;border-radius:3px;}
QListWidget::item:selected{background:#333366;color:#fff;}
QListWidget::item:hover:!selected{background:#252545;}
QPushButton{background:#1e1e34;color:#bbb;border:1px solid #333355;
            border-radius:5px;padding:5px 13px;font-size:10pt;}
QPushButton:hover{background:#28285a;color:#eee;border-color:#5555aa;}
QPushButton:pressed{background:#141430;}
QPushButton#primary{background:#2a2a7a;color:#fff;border-color:#4a4aaa;font-weight:bold;}
QPushButton#primary:hover{background:#3a3aaa;}
QPushButton#danger{background:#3a1818;color:#e06060;border-color:#552222;}
QPushButton#danger:hover{background:#4a2020;}
QSlider::groove:horizontal{height:4px;background:#252545;border-radius:2px;}
QSlider::handle:horizontal{background:#5a5aee;width:14px;height:14px;
                            border-radius:7px;margin:-5px 0;}
QSlider::sub-page:horizontal{background:#4a4add;border-radius:2px;}
QScrollArea{border:none;background:#181828;}
QLineEdit{background:#1e1e34;border:1px solid #333355;border-radius:4px;
          padding:3px 7px;color:#ddd;font-family:monospace;}
QLineEdit:focus{border-color:#5555aa;}
QScrollBar:vertical{background:#13131f;width:7px;border-radius:3px;}
QScrollBar::handle:vertical{background:#2a2a5a;border-radius:3px;min-height:20px;}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{height:0;}
"""

# ── HSV 색상 피커 ─────────────────────────────────────────────────────────────
class _SVSquare(QWidget):
    def __init__(self, h, s, v, parent=None):
        super().__init__(parent)
        self._h=h; self._s=s; self._v=v
        self.setFixedSize(230, 150); self.setMouseTracking(True)

    def set_hue(self, h): self._h=h; self.update()

    def paintEvent(self, _):
        p=QPainter(self); w,h=self.width(),self.height()
        hc=QColor.fromHsvF(max(0.0,min(0.9999,self._h)),1.0,1.0)
        g1=QLinearGradient(0,0,w,0)
        g1.setColorAt(0.0,QColor(255,255,255)); g1.setColorAt(1.0,hc)
        p.fillRect(0,0,w,h,QBrush(g1))
        g2=QLinearGradient(0,0,0,h)
        g2.setColorAt(0.0,QColor(0,0,0,0)); g2.setColorAt(1.0,QColor(0,0,0,255))
        p.fillRect(0,0,w,h,QBrush(g2))
        cx=int(self._s*w); cy=int((1.0-self._v)*h)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor(0,0,0,100),2)); p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx,cy),7,7)
        p.setPen(QPen(QColor(255,255,255),2))
        p.drawEllipse(QPointF(cx,cy),5,5)
        p.end()

    def _update(self, x, y):
        self._s=max(0.0,min(1.0,x/self.width()))
        self._v=max(0.0,min(1.0,1.0-y/self.height()))
        self.update(); self.parent()._sync_sv(self._s,self._v)

    def mousePressEvent(self,e): self._update(e.x(),e.y())
    def mouseMoveEvent(self,e):
        if e.buttons(): self._update(e.x(),e.y())

class _HueBar(QWidget):
    def __init__(self, h, parent=None):
        super().__init__(parent)
        self._h=h; self.setFixedSize(230,16); self.setMouseTracking(True)

    def paintEvent(self,_):
        p=QPainter(self); w,h=self.width(),self.height()
        g=QLinearGradient(0,0,w,0)
        for i in range(13):
            hf=i/12 if i<12 else 0.9999
            g.setColorAt(i/12, QColor.fromHsvF(hf,1.0,1.0))
        p.fillRect(0,0,w,h,QBrush(g))
        mx=int(self._h*w)
        p.setPen(QPen(QColor(255,255,255),2)); p.setBrush(Qt.NoBrush)
        p.drawRect(max(0,mx-5),0,10,h-1)
        p.end()

    def _update(self, x):
        self._h=max(0.0,min(0.9999,x/self.width()))
        self.update(); self.parent()._sync_hue(self._h)

    def mousePressEvent(self,e): self._update(e.x())
    def mouseMoveEvent(self,e):
        if e.buttons(): self._update(e.x())

class ColorPickerPopup(QDialog):
    def __init__(self, hex_color, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint|Qt.Dialog)
        self.setStyleSheet(_SETTINGS_QSS+
            "QDialog{border:2px solid #333366;border-radius:8px;background:#13131f;}")
        c=QColor(hex_color); self._result=c
        h,s,v,_=c.getHsvF(); h=max(0.0,h)

        v_=QVBoxLayout(self); v_.setContentsMargins(10,10,10,10); v_.setSpacing(6)

        self._sv=_SVSquare(h,s,v,self); v_.addWidget(self._sv)
        self._hb=_HueBar(h,self); v_.addWidget(self._hb)

        # 미리보기 + 헥스 입력
        hr=QHBoxLayout(); hr.setSpacing(6)
        self._bar=QLabel(); self._bar.setFixedSize(34,24)
        self._bar.setStyleSheet(f"background:{hex_color};border-radius:4px;border:1px solid #444;")
        lbl=QLabel('#'); lbl.setStyleSheet("color:#666;")
        self._hex=QLineEdit(c.name().lstrip('#'))
        self._hex.setMaxLength(6)
        self._hex.textChanged.connect(self._on_hex)
        self._hex.returnPressed.connect(self.accept)
        _lang=self._parent_lang()
        _ok_text={'ko':'확인','en':'OK','ru':'ОК','ja':'OK','zh':'确认'}.get(_lang,'OK')
        ok=QPushButton(_ok_text); ok.setObjectName('primary')
        ok.setStyleSheet("QPushButton{padding:3px 14px;min-width:0;}")
        ok.clicked.connect(self.accept)
        hr.addWidget(self._bar); hr.addWidget(lbl)
        hr.addWidget(self._hex); hr.addStretch(); hr.addWidget(ok)
        v_.addLayout(hr)

    def _parent_lang(self):
        w=self.parent()
        while w:
            if hasattr(w,'lang'): return w.lang
            w=w.parent()
        return 'en'

    def _sync_hue(self, h):
        self._sv.set_hue(h); self._push()

    def _sync_sv(self, s, v):
        self._push()

    def _push(self):
        h=self._hb._h; s=self._sv._s; v=self._sv._v
        c=QColor.fromHsvF(h,s,v); self._result=c
        self._bar.setStyleSheet(f"background:{c.name()};border-radius:4px;border:1px solid #444;")
        self._hex.blockSignals(True)
        self._hex.setText(c.name().lstrip('#'))
        self._hex.blockSignals(False)

    def _on_hex(self, text):
        if len(text)==6:
            c=QColor('#'+text)
            if c.isValid():
                self._result=c
                h,s,v,_=c.getHsvF(); h=max(0.0,h)
                self._sv._h=h; self._sv._s=s; self._sv._v=v; self._sv.update()
                self._hb._h=h; self._hb.update()
                self._bar.setStyleSheet(f"background:#{text};border-radius:4px;border:1px solid #444;")

    def result(self): return self._result

# ── settings preview ──────────────────────────────────────────────────────────
class PreviewWidget(QWidget):
    _HOLDS = [110,130,110,130,110,400,110,130,110,130,400,110]

    KW=46; KH=46; SP=7; PAD=10  # 키 수에 비례, 스핀박스 값 무시

    def __init__(self, sw):
        super().__init__(sw); self.sw=sw
        self.setMinimumHeight(220)
        # live animation state
        self._blocks=[]; self._parts=[]; self._glows=[]
        self._pressed=set(); self._beat=0
        self._press_offsets={}; self._sim_counts={}; self._sim_times=deque()
        # animation tick ~60fps
        self._at=QTimer(self); self._at.timeout.connect(self._tick); self._at.start(16)
        # sequencer: auto-press keys in rhythm
        self._st=QTimer(self); self._st.timeout.connect(self._seq); self._st.start(320)

    # ── geometry helper ───────────────────────────────────────────────────────
    def preferred_width(self):
        n=self.sw._kl.count() if hasattr(self.sw,'_kl') else 4
        n=max(1,n)
        return n*self.KW+(n-1)*self.SP+self.PAD*2+40

    def _geo(self):
        sw=self.sw
        if not hasattr(sw,'_kl'): return None
        keys=[sw._kl.item(i).text() for i in range(sw._kl.count())]
        if not keys: return None
        n=len(keys)
        kw_s=self.KW; kh_s=self.KH; sp_s=self.SP; pad=self.PAD
        tw_s=n*kw_s+(n-1)*sp_s+pad*2; x0=(self.width()-tw_s)//2
        y_key=self.height()-kh_s-26
        return dict(keys=keys,n=n,sc=1.0,kw_s=kw_s,kh_s=kh_s,sp_s=sp_s,x0=x0,y_key=y_key,pad=pad)

    def _cx(self, g, idx):
        return g['x0']+g['pad']+idx*(g['kw_s']+g['sp_s'])+g['kw_s']//2

    # ── simulation ────────────────────────────────────────────────────────────
    def _sim_press(self, idx):
        if idx in self._pressed: return
        g=self._geo()
        if not g or idx>=g['n']: return
        self._pressed.add(idx)
        sw=self.sw
        push=max(2,int((sw._ppx.value() if hasattr(sw,'_ppx') else 3)*g['sc']))
        self._press_offsets[idx]=float(push)
        self._sim_counts[idx]=self._sim_counts.get(idx,0)+1
        self._sim_times.append(time.time())
        self._blocks.append(dict(ki=idx,y_top=float(g['y_key']),
                                 y_bot=float(g['y_key']),released=False))
        if hasattr(sw,'_pt_on') and sw._pt_on.isChecked():
            cnt=min(sw._pt_cnt.value() if hasattr(sw,'_pt_cnt') else 8, 12)
            px=self._cx(g,idx); py=float(g['y_key']); h=g['kw_s']//3
            for _ in range(cnt):
                self._parts.append(Particle(
                    px+random.uniform(-h,h), py,
                    random.uniform(-2.5,2.5), random.uniform(-4.5,-0.5),
                    size=random.randint(2,5)))
        if hasattr(sw,'_glow_on') and sw._glow_on.isChecked():
            if hasattr(sw,'_glow_pulse') and sw._glow_pulse.isChecked():
                self._glows.append(GlowPulse(idx, g['kw_s']*1.8))

    def _sim_release(self, idx):
        self._pressed.discard(idx)
        for b in self._blocks:
            if b['ki']==idx and not b['released']:
                b['released']=True; break

    def _seq(self):
        g=self._geo()
        if not g: return
        idx=self._beat % g['n']
        hold=self._HOLDS[self._beat % len(self._HOLDS)]
        self._sim_press(idx)
        QTimer.singleShot(hold, lambda i=idx: self._sim_release(i))
        self._beat+=1

    # ── animation tick ────────────────────────────────────────────────────────
    def _tick(self):
        g=self._geo()
        if not g: self.update(); return
        sw=self.sw
        spd=(sw._spd.value() if hasattr(sw,'_spd') else 6)*g['sc']
        top=22
        for b in self._blocks:
            if not b['released']:
                b['y_top']=max(float(top), b['y_top']-spd)
            else:
                b['y_top']-=spd; b['y_bot']-=spd
        self._blocks=[b for b in self._blocks if b['y_bot']>0]
        # continuous particles from block tops
        if hasattr(sw,'_pt_on') and sw._pt_on.isChecked():
            if hasattr(sw,'_pt_cont') and sw._pt_cont.isChecked():
                rate=sw._pt_rate.value() if hasattr(sw,'_pt_rate') else 2
                for b in self._blocks:
                    if not b['released'] and b['ki'] in self._pressed and b['ki']<g['n']:
                        px=self._cx(g,b['ki']); h=g['kw_s']//3
                        for _ in range(rate):
                            self._parts.append(Particle(
                                px+random.uniform(-h,h), b['y_top'],
                                random.uniform(-1.5,1.5), random.uniform(-2,0.2),
                                size=random.randint(1,3)))
        if len(self._parts)>200: self._parts=self._parts[-150:]
        for pt in self._parts:
            pt.x+=pt.vx; pt.y+=pt.vy; pt.vy+=0.25; pt.alpha=max(0,pt.alpha-18)
        self._parts=[pt for pt in self._parts if pt.alpha>0]
        for gp in self._glows:
            gp.radius+=g['kw_s']*0.06; gp.alpha=max(0,gp.alpha-22)
        self._glows=[gp for gp in self._glows if gp.alpha>0]
        # press offset spring back
        push_max=(sw._ppx.value() if hasattr(sw,'_ppx') else 3)*g['sc']
        for idx in list(self._press_offsets.keys()):
            if idx not in self._pressed:
                self._press_offsets[idx]=max(0.0,self._press_offsets[idx]-max(0.3,push_max*0.35))
                if self._press_offsets[idx]<=0: del self._press_offsets[idx]
        # KPS 감소
        cutoff=time.time()-1.0
        while self._sim_times and self._sim_times[0]<cutoff:
            self._sim_times.popleft()
        self.update()

    # ── paint ─────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        g=self._geo(); sw=self.sw
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(16,16,26))
        if not g:
            p.setFont(QFont('Segoe UI',9)); p.setPen(QColor(70,70,110))
            p.drawText(self.rect(),Qt.AlignCenter,'키를\n추가하세요')
            p.end(); return
        keys=g['keys']; kw_s=g['kw_s']; kh_s=g['kh_s']
        sp_s=g['sp_s']; x0=g['x0']; y_key=g['y_key']; pad=g['pad']; sc=g['sc']
        c_on=QColor(sw._cp.hex()) if hasattr(sw,'_cp') else QColor('#fff')
        c_off=QColor(sw._cr.hex()) if hasattr(sw,'_cr') else QColor('#555')
        t_on=QColor(sw._ton.hex()) if hasattr(sw,'_ton') else QColor('#fff')
        t_off=QColor(sw._tof.hex()) if hasattr(sw,'_tof') else QColor('#888')
        km=getattr(sw,'_key_color_map',{})
        fill_a=sw._fa.value() if hasattr(sw,'_fa') else 60
        fz=sw._fz.value() if hasattr(sw,'_fz') else 80
        block_on=sw._blk_on.isChecked() if hasattr(sw,'_blk_on') else True
        pt_on=sw._pt_on.isChecked() if hasattr(sw,'_pt_on') else True
        pt_col=QColor(sw._pt_color.hex()) if hasattr(sw,'_pt_color') else QColor('#fff')
        glow_on=sw._glow_on.isChecked() if hasattr(sw,'_glow_on') else True
        gp_on=sw._glow_pulse.isChecked() if hasattr(sw,'_glow_pulse') else True
        real_kw=sw._kw.value() if hasattr(sw,'_kw') else 55
        real_fs=sw._fs.value() if hasattr(sw,'_fs') else 18
        fs=max(7,min(12,int(real_fs*self.KW/max(1,real_kw))))

        # header label
        p.setFont(QFont('Segoe UI',8,QFont.Bold))
        p.setPen(QColor(90,90,150))
        lang=getattr(sw,'lang','en')
        _prev={'ko':'미리보기','en':'Preview','ru':'Превью','ja':'プレビュー','zh':'预览'}
        p.drawText(QRect(0,5,self.width(),14),Qt.AlignCenter,_prev.get(lang,'Preview'))

        # blocks — 메인 오버레이와 동일: 화면 상단 절대 위치 기준 그라디언트
        if block_on:
            top_y=22; fz_s=max(1.0, fz*sc)
            grad_base=QLinearGradient(0, top_y, 0, top_y+fz_s)
            p.setPen(Qt.NoPen)
            for b in self._blocks:
                ki=b['ki']
                if ki>=len(keys): continue
                kc=QColor(km.get(keys[ki], c_on.name()))
                x1=x0+pad+ki*(kw_s+sp_s); bh=b['y_bot']-b['y_top']
                if bh<=0: continue
                grad=QLinearGradient(0, top_y, 0, top_y+fz_s)
                ct=QColor(kc); ct.setAlpha(0)
                grad.setColorAt(0.0,ct); grad.setColorAt(1.0,QColor(kc))
                p.setBrush(QBrush(grad))
                p.drawRect(int(x1),int(b['y_top']),kw_s,max(1,int(bh)))
            p.setBrush(Qt.NoBrush)

        # particles
        if pt_on:
            p.setPen(Qt.NoPen)
            for pt in self._parts:
                c=QColor(pt_col); c.setAlpha(pt.alpha)
                p.setBrush(c); s=max(1,int(pt.size))
                p.drawEllipse(int(pt.x)-s//2,int(pt.y)-s//2,s,s)
            p.setBrush(Qt.NoBrush)

        # glow pulses
        if glow_on and gp_on:
            p.setPen(Qt.NoPen)
            for gp in self._glows:
                ki=gp.key_idx
                if ki>=len(keys): continue
                kc=QColor(km.get(keys[ki], c_on.name()))
                cx=float(x0+pad+ki*(kw_s+sp_s)+kw_s//2); cy=float(y_key)
                grad=QRadialGradient(QPointF(cx,cy),gp.radius)
                gc=QColor(kc); gc.setAlpha(gp.alpha)
                gc2=QColor(kc); gc2.setAlpha(0)
                grad.setColorAt(0.0,gc); grad.setColorAt(1.0,gc2)
                p.setBrush(QBrush(grad))
                p.drawEllipse(QPointF(cx,cy),gp.radius,gp.radius)
            p.setBrush(Qt.NoBrush)

        # key boxes
        fk=QFont('Segoe UI',fs); fk.setBold(True)
        fst=QFont('Segoe UI',max(5,fs-4))
        show_kc=hasattr(sw,'_sck') and sw._sck.isChecked()
        show_kps=hasattr(sw,'_sk') and sw._sk.isChecked()
        for i,key in enumerate(keys):
            off=int(self._press_offsets.get(i,0.0))
            x1=x0+pad+i*(kw_s+sp_s); y1=y_key+off
            r=QRect(x1,y1,kw_s,kh_s); ri=r.adjusted(1,1,-1,-1)
            on=(i in self._pressed)
            kc=QColor(km.get(key, c_on.name()))
            p.setPen(Qt.NoPen); p.setBrush(QColor(255,255,255,18))
            p.drawRoundedRect(ri,6,6)
            if on:
                fc=QColor(kc); fc.setAlpha(fill_a)
                p.setBrush(fc); p.drawRoundedRect(r.adjusted(2,2,-2,-2),5,5)
            p.setPen(QPen(kc if on else c_off,1.5))
            p.setBrush(Qt.NoBrush); p.drawRoundedRect(ri,6,6)
            p.setFont(fk); p.setPen(t_on if on else t_off)
            lr=r.adjusted(0,-8,0,-8) if show_kc else r
            p.drawText(lr,Qt.AlignCenter,key_label(key))
            if show_kc:
                p.setFont(fst)
                p.setPen(t_on if on else t_off)
                p.drawText(QRect(x1,y1+kh_s-16,kw_s,12),Qt.AlignCenter,str(self._sim_counts.get(i,0)))
        if show_kps:
            kps=len(self._sim_times)
            p.setFont(fst); p.setPen(QColor(160,160,160))
            p.drawText(QRect(0,y_key+kh_s+3,self.width(),14),Qt.AlignCenter,f'KPS {kps}')
        p.end()

# ── settings window ───────────────────────────────────────────────────────────
class SettingsWindow(QDialog):
    def __init__(self, overlay, cfg_path):
        super().__init__()
        self.overlay=overlay; self.cfg_path=cfg_path
        self.lang=overlay.cfg.get('language','ko')
        self._=lambda k,**kw: tr(self.lang,k,**kw)

        self.setWindowTitle(self._('title'))
        self.setFixedHeight(600)
        self.setWindowFlags(Qt.Window|Qt.WindowCloseButtonHint|Qt.WindowStaysOnTopHint)
        self.setStyleSheet(_SETTINGS_QSS)

        v=QVBoxLayout(self); v.setSpacing(8); v.setContentsMargins(10,10,10,10)
        self._tabs=QTabWidget(); self._tabs.setFixedWidth(490)
        self._tabs.addTab(self._tab_keys(),    self._('tab_keys'))
        self._tabs.addTab(self._tab_style(),   self._('tab_style'))
        self._tabs.addTab(self._tab_anim(),    self._('tab_anim'))
        self._tabs.addTab(self._tab_stats(),   self._('tab_stats'))
        self._tabs.addTab(self._tab_general(), self._('tab_general'))

        self._preview=PreviewWidget(self)
        hc=QHBoxLayout(); hc.setSpacing(10)
        hc.addWidget(self._tabs); hc.addWidget(self._preview)
        v.addLayout(hc)

        row=QHBoxLayout(); row.setSpacing(8)
        self._btn_quit=QPushButton(self._('btn_quit')); self._btn_quit.clicked.connect(self._do_quit_overlay)
        self._btn_quit.setObjectName('danger')
        self._btn_reset=QPushButton(self._('btn_reset')); self._btn_reset.clicked.connect(self._do_reset)
        self._btn_save=QPushButton(self._('btn_save'));  self._btn_save.clicked.connect(self._do_save)
        self._btn_save.setObjectName('primary'); self._btn_save.setDefault(True)
        row.addWidget(self._btn_quit); row.addWidget(self._btn_reset)
        row.addStretch(); row.addWidget(self._btn_save)
        v.addLayout(row)
        self._sync_size()

    # ── helpers ───────────────────────────────────────────────────────────────
    def _on_lang_change(self):
        new_lang=self._lang_cb.currentData()
        if not new_lang or new_lang==self.lang: return
        snap=self._collect(); snap['language']=new_lang
        km=dict(self._key_color_map)
        self.lang=new_lang
        self._=lambda k,**kw: tr(self.lang,k,**kw)
        L=self._
        # temp patch cfg so tab builders read current form values
        _orig=deepcopy(self.overlay.cfg)
        self.overlay.cfg.update(snap)
        self._tabs.clear()
        self._tabs.addTab(self._tab_keys(),    L('tab_keys'))
        self._tabs.addTab(self._tab_style(),   L('tab_style'))
        self._tabs.addTab(self._tab_anim(),    L('tab_anim'))
        self._tabs.addTab(self._tab_stats(),   L('tab_stats'))
        self._tabs.addTab(self._tab_general(), L('tab_general'))
        self.overlay.cfg.update(_orig)
        self._key_color_map.update(km)
        self._btn_quit.setText(L('btn_quit'))
        self._btn_reset.setText(L('btn_reset'))
        self._btn_save.setText(L('btn_save'))
        self._tabs.setCurrentIndex(4)  # 일반 탭으로 유지

    def _sync_size(self):
        pw=self._preview.preferred_width()
        self._preview.setFixedWidth(pw)
        w=22+490+10+pw
        self.setMinimumWidth(w); self.setMaximumWidth(w)
        self.resize(w, self.height())

    def _sec(self, text):
        l=QLabel(text); l.setObjectName('sec'); return l

    def _scrollable(self, w):
        sa=QScrollArea(); sa.setWidgetResizable(True); sa.setWidget(w)
        sa.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        return sa

    # ── tabs ──────────────────────────────────────────────────────────────────
    def _tab_keys(self):
        L=self._; cd=L('color_dialog')
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(6); v.setContentsMargins(10,10,10,10)
        v.addWidget(self._sec(L('keys_label')))
        self._kl=QListWidget()
        for k in self.overlay.cfg['keys']: self._kl.addItem(k)
        v.addWidget(self._kl)
        row=QHBoxLayout()
        for lbl,fn in [(L('key_add'),self._k_add),(L('key_del'),self._k_del),
                       ('↑',self._k_up),('↓',self._k_dn)]:
            b=QPushButton(lbl); b.clicked.connect(fn); row.addWidget(b)
        v.addLayout(row)
        # preset buttons
        pr=QHBoxLayout(); pr.addWidget(QLabel(L('preset_label')))
        for lbl,keys in [('2K',['f','j']),('4K',['d','f','j','k']),
                         ('5K',['s','d','f','j','k']),
                         ('6K',['s','d','f','j','k','l']),
                         ('7K',['s','d','f','space','j','k','l'])]:
            b=QPushButton(lbl)
            b.setStyleSheet("QPushButton{padding:3px 8px;min-width:0px;font-size:9pt;}")
            b.clicked.connect(lambda _,ks=keys: self._set_preset(ks))
            pr.addWidget(b)
        pr.addStretch(); v.addLayout(pr)
        # per-key color
        v.addWidget(QLabel(L('key_color_label')))
        self._key_color_map=dict(self.overlay.cfg.get('key_colors',{}))
        ck=QHBoxLayout()
        self._ck_lbl=QLabel(L('key_select_hint'))
        self._ck_btn=ColorBtn(self.overlay.cfg['style']['color_pressed'],cd,
                              on_change=self._on_key_color_change)
        self._ck_btn.setEnabled(False)
        ck.addWidget(self._ck_lbl); ck.addStretch(); ck.addWidget(self._ck_btn)
        v.addLayout(ck)
        self._kl.currentRowChanged.connect(self._on_key_sel)
        v.addWidget(self._sec(''))
        hint=QLabel(L('key_hint')); hint.setWordWrap(True)
        hint.setStyleSheet('color:#666688;font-size:8pt;')
        v.addWidget(hint); v.addStretch()
        return self._scrollable(w)

    def _set_preset(self, keys):
        self._kl.clear()
        for k in keys: self._kl.addItem(k)
        self._ck_btn.setEnabled(False)
        self._ck_lbl.setText(self._('key_select_hint'))
        self._sync_size()

    def _on_key_sel(self, row):
        if row<0: self._ck_btn.setEnabled(False); return
        key=self._kl.item(row).text()
        self._ck_lbl.setText(f"  {key}:")
        default=self.overlay.cfg['style']['color_pressed']
        self._ck_btn.set_color(self._key_color_map.get(key, default))
        self._ck_btn.setEnabled(True)

    def _on_key_color_change(self, hex_color):
        row=self._kl.currentRow()
        if row<0: return
        self._key_color_map[self._kl.item(row).text()]=hex_color

    def _k_add(self):
        t,ok=QInputDialog.getText(self,self._('dlg_add_title'),self._('dlg_add_prompt'))
        if ok:
            t=t.strip().lower()[:32]
            if t: self._kl.addItem(t); self._sync_size()
    def _k_del(self):
        r=self._kl.currentRow()
        if r>=0: self._kl.takeItem(r); self._sync_size()
    def _k_up(self):
        r=self._kl.currentRow()
        if r>0:
            it=self._kl.takeItem(r); self._kl.insertItem(r-1,it); self._kl.setCurrentRow(r-1)
    def _k_dn(self):
        r=self._kl.currentRow()
        if r<self._kl.count()-1:
            it=self._kl.takeItem(r); self._kl.insertItem(r+1,it); self._kl.setCurrentRow(r+1)

    def _tab_style(self):
        s=self.overlay.cfg['style']; L=self._; cd=L('color_dialog')
        w=QWidget(); f=QFormLayout(w)
        f.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        f.setSpacing(8); f.setContentsMargins(10,10,10,10)
        self._kw=QSpinBox(); self._kw.setRange(20,200); self._kw.setValue(s['key_width'])
        self._kh=QSpinBox(); self._kh.setRange(20,200); self._kh.setValue(s['key_height'])
        self._sp=QSpinBox(); self._sp.setRange(0,50);   self._sp.setValue(s['spacing'])
        self._fs=QSpinBox(); self._fs.setRange(8,48);   self._fs.setValue(s['font_size'])
        self._cp=ColorBtn(s['color_pressed'],cd); self._cr=ColorBtn(s['color_released'],cd)
        self._ton=ColorBtn(s['text_on'],cd); self._tof=ColorBtn(s['text_off'],cd)
        self._fa=QSlider(Qt.Horizontal); self._fa.setRange(0,255); self._fa.setValue(s.get('fill_alpha',60))
        fa_lb=QLabel(str(self._fa.value())); self._fa.valueChanged.connect(lambda v:fa_lb.setText(str(v)))
        fa_w=QWidget(); fa_r=QHBoxLayout(fa_w); fa_r.setContentsMargins(0,0,0,0)
        fa_r.addWidget(self._fa); fa_r.addWidget(fa_lb)
        self._op=QSlider(Qt.Horizontal); self._op.setRange(10,100); self._op.setValue(int(s.get('opacity',1.0)*100))
        op_lb=QLabel(f"{self._op.value()}%"); self._op.valueChanged.connect(lambda v:op_lb.setText(f"{v}%"))
        op_w=QWidget(); op_r=QHBoxLayout(op_w); op_r.setContentsMargins(0,0,0,0)
        op_r.addWidget(self._op); op_r.addWidget(op_lb)
        f.addRow(L('kw'),self._kw); f.addRow(L('kh'),self._kh)
        f.addRow(L('spacing'),self._sp); f.addRow(L('fs'),self._fs)
        f.addRow(self._sec(L('sec_color')))
        f.addRow(L('col_on'),self._cp); f.addRow(L('col_off'),self._cr)
        f.addRow(L('txt_on'),self._ton); f.addRow(L('txt_off'),self._tof)
        f.addRow(self._sec(L('sec_fill'))); f.addRow(L('fill_alpha'),fa_w)
        f.addRow(self._sec(L('sec_opacity'))); f.addRow(L('opacity'),op_w)
        return self._scrollable(w)

    def _tab_anim(self):
        a=self.overlay.cfg['animation']; L=self._; cd=L('color_dialog')
        w=QWidget(); f=QFormLayout(w)
        f.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        f.setSpacing(8); f.setContentsMargins(10,10,10,10)

        # block
        self._th=QSpinBox(); self._th.setRange(50,800); self._th.setValue(a['trail_height'])
        spd=a.get('scroll_speed',a.get('grow_speed',a.get('float_speed',6)))
        self._spd=QSpinBox(); self._spd.setRange(1,40);  self._spd.setValue(spd)
        self._fz=QSpinBox();  self._fz.setRange(10,400); self._fz.setValue(a.get('fade_zone',80))
        self._ppx=QSpinBox(); self._ppx.setRange(0,20);  self._ppx.setValue(a.get('push_px',3))
        self._blk_on=QCheckBox(L('block_on')); self._blk_on.setChecked(a.get('block_on',True))
        f.addRow(self._sec(L('sec_block')))
        f.addRow(self._blk_on)
        f.addRow(L('trail_h'),self._th); f.addRow(L('scroll_spd'),self._spd)
        f.addRow(L('fade_zone'),self._fz); f.addRow(L('push_px'),self._ppx)

        # particles
        self._pt_on  =QCheckBox(L('pt_on'));         self._pt_on.setChecked(a.get('particle_on',True))
        self._pt_cont=QCheckBox(L('pt_continuous')); self._pt_cont.setChecked(a.get('particle_continuous',True))
        self._pt_color=ColorBtn(a.get('particle_color','#ffffff'),cd)
        self._pt_cnt =QSpinBox(); self._pt_cnt.setRange(1,60);  self._pt_cnt.setValue(a.get('particle_count',12))
        self._pt_rate=QSpinBox(); self._pt_rate.setRange(0,10); self._pt_rate.setValue(a.get('particle_rate',2))
        f.addRow(self._sec(L('sec_particle')))
        f.addRow(self._pt_on); f.addRow(self._pt_cont)
        f.addRow(L('pt_color'),self._pt_color)
        f.addRow(L('pt_cnt'),self._pt_cnt); f.addRow(L('pt_rate'),self._pt_rate)

        # glow
        self._glow_on   =QCheckBox(L('glow_on'));    self._glow_on.setChecked(a.get('glow_on',True))
        self._glow_pulse=QCheckBox(L('glow_pulse')); self._glow_pulse.setChecked(a.get('glow_pulse',True))
        self._glow_color=ColorBtn(a.get('glow_color','#ffffff'),cd)
        self._glow_size =QSpinBox(); self._glow_size.setRange(2,60);  self._glow_size.setValue(a.get('glow_size',14))
        self._glow_alpha=QSpinBox(); self._glow_alpha.setRange(10,255); self._glow_alpha.setValue(a.get('glow_alpha',110))
        f.addRow(self._sec(L('sec_glow')))
        f.addRow(self._glow_on); f.addRow(self._glow_pulse)
        f.addRow(L('glow_color'),self._glow_color)
        f.addRow(L('glow_size'),self._glow_size); f.addRow(L('glow_alpha'),self._glow_alpha)
        return self._scrollable(w)

    def _tab_stats(self):
        st=self.overlay.cfg.get('stats',{}); L=self._
        w=QWidget(); v=QVBoxLayout(w); v.setSpacing(8); v.setContentsMargins(10,10,10,10)
        self._sk =QCheckBox(L('show_kps'));       self._sk.setChecked(st.get('show_kps',True))
        self._sck=QCheckBox(L('show_key_count')); self._sck.setChecked(st.get('show_key_count',True))
        self._st =QCheckBox(L('show_total'));     self._st.setChecked(st.get('show_total',False))
        v.addWidget(self._sk); v.addWidget(self._sck); v.addWidget(self._st); v.addStretch()
        b=QPushButton(L('reset_stats'))
        b.clicked.connect(lambda:(self.overlay.reset_stats(),
            QMessageBox.information(self,L('done'),L('reset_done'))))
        v.addWidget(b)
        return self._scrollable(w)

    def _tab_general(self):
        L=self._; w=QWidget(); f=QFormLayout(w)
        f.setSpacing(8); f.setContentsMargins(10,10,10,10)
        self._lang_cb=QComboBox()
        for code,name in _LANG_NAMES:
            self._lang_cb.addItem(name, code)
        self._lang_cb.setCurrentIndex(max(0,[c for c,_ in _LANG_NAMES].index(self.lang)
                                          if self.lang in [c for c,_ in _LANG_NAMES] else 0))
        self._lang_cb.currentIndexChanged.connect(lambda _: self._on_lang_change())
        f.addRow(L('language'), self._lang_cb)
        mod=self.overlay.cfg.get('hotkey_modifier','ctrl+alt')
        self._hk_ca=QRadioButton('Ctrl+Alt'); self._hk_cs=QRadioButton('Ctrl+Shift')
        self._hk_ca.setChecked(mod=='ctrl+alt'); self._hk_cs.setChecked(mod=='ctrl+shift')
        hk_w=QWidget(); hk_r=QHBoxLayout(hk_w); hk_r.setContentsMargins(0,0,0,0)
        hk_r.addWidget(self._hk_ca); hk_r.addWidget(self._hk_cs)
        f.addRow(L('hotkey_mod'),hk_w)
        return self._scrollable(w)

    # ── actions ───────────────────────────────────────────────────────────────
    def _collect(self):
        cfg=deepcopy(self.overlay.cfg)
        cfg['keys']=[self._kl.item(i).text() for i in range(self._kl.count())]
        cfg['key_colors']=dict(self._key_color_map)
        cfg['language']=self._lang_cb.currentData() or 'en'
        cfg['hotkey_modifier']='ctrl+alt' if self._hk_ca.isChecked() else 'ctrl+shift'
        cfg['style'].update({
            'key_width':self._kw.value(),'key_height':self._kh.value(),
            'spacing':self._sp.value(),'font_size':self._fs.value(),
            'color_pressed':self._cp.hex(),'color_released':self._cr.hex(),
            'text_on':self._ton.hex(),'text_off':self._tof.hex(),
            'fill_alpha':self._fa.value(),'opacity':self._op.value()/100.0,
        })
        cfg['animation'].update({
            'trail_height':self._th.value(),'block_on':self._blk_on.isChecked(),
            'scroll_speed':self._spd.value(),
            'fade_zone':self._fz.value(),'push_px':self._ppx.value(),
            'particle_on':self._pt_on.isChecked(),'particle_continuous':self._pt_cont.isChecked(),
            'particle_color':self._pt_color.hex(),
            'particle_count':self._pt_cnt.value(),'particle_rate':self._pt_rate.value(),
            'glow_on':self._glow_on.isChecked(),
            'glow_pulse':self._glow_pulse.isChecked(),
            'glow_color':self._glow_color.hex(),
            'glow_size':self._glow_size.value(),'glow_alpha':self._glow_alpha.value(),
        })
        cfg['stats']={
            'show_kps':self._sk.isChecked(),
            'show_key_count':self._sck.isChecked(),
            'show_total':self._st.isChecked(),
        }
        return cfg

    def _do_save(self):
        cfg=self._collect()
        cfg['window']={'x':self.overlay.x(),'y':self.overlay.y()}
        _save_cfg(self.cfg_path, cfg)
        self.overlay.apply_config(cfg)
        self.close()

    def _do_reset(self):
        if QMessageBox.question(self,self._('btn_reset'),self._('confirm_reset'),
           QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            cfg=deepcopy(DEFAULTS)
            _save_cfg(self.cfg_path, cfg)
            self.overlay.apply_config(cfg)
            self.close()

    def _do_quit_overlay(self):
        self.close(); self.overlay.sigs.quit_app.emit()

# ── signals ───────────────────────────────────────────────────────────────────
class Sigs(QObject):
    press=pyqtSignal(str); release=pyqtSignal(str)
    toggle_move=pyqtSignal(); quit_app=pyqtSignal(); open_settings=pyqtSignal()

# ── overlay ───────────────────────────────────────────────────────────────────
class Overlay(QWidget):
    def __init__(self, cfg_path):
        super().__init__()
        self.cfg_path=cfg_path
        self.cfg=_load_cfg(cfg_path)
        self.move_mode=False; self._drag_pos=None
        self.pressed=set(); self.hold_blocks=[]; self._active={}
        self.particles=[]; self.glow_pulses=[]
        self.key_counts={}; self.total_count=0; self._press_times=deque()
        self._max_kps=0

        self.sigs=Sigs()
        self.sigs.press.connect(self._press); self.sigs.release.connect(self._release)
        self.sigs.toggle_move.connect(self._toggle_move)
        self.sigs.quit_app.connect(self._do_quit)
        self.sigs.open_settings.connect(self._open_settings)

        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint|Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._build_params()
        self._place_window()
        self.show()
        set_clickthrough(int(self.winId()),True)
        self.setWindowOpacity(self.cfg['style'].get('opacity',1.0))
        self.timer=QTimer(self); self.timer.timeout.connect(self._tick)
        self.timer.start(self.cfg['animation'].get('frame_ms',16))
        self._top_timer=QTimer(self); self._top_timer.timeout.connect(self._keep_topmost)
        self._top_timer.start(1000)
        self._start_listener()

    # ── params ────────────────────────────────────────────────────────────────
    def _build_params(self):
        s,a=self.cfg['style'],self.cfg['animation']
        lang=self.cfg.get('language','ko')
        mod=self.cfg.get('hotkey_modifier','ctrl+alt')
        self.move_hint_txt=tr(lang,'move_hint',mod='Ctrl+Alt' if mod=='ctrl+alt' else 'Ctrl+Shift')
        self.keys=[k.lower() for k in self.cfg['keys']]
        self.kw=s['key_width']; self.kh=s['key_height']
        self.sp=s['spacing'];   self.pad=s.get('pad',8)
        self.fill_alpha=s.get('fill_alpha',60)
        self.trail_h=a['trail_height']; self.min_h=a.get('min_height',0)
        self.block_on=a.get('block_on',True)
        self.scroll_spd=float(a.get('scroll_speed',a.get('grow_speed',a.get('float_speed',6))))
        self.fade_zone=max(1, a.get('fade_zone',80))
        # particles
        self.pt_on=a.get('particle_on',True)
        self.pt_cont=a.get('particle_continuous',True)
        self.pt_color=QColor(a.get('particle_color','#ffffff'))
        self.pt_cnt=a.get('particle_count',12)
        self.pt_rate=a.get('particle_rate',2)
        # glow
        self.glow_on      =a.get('glow_on',True)
        self.glow_pulse_on=a.get('glow_pulse',True)
        self.glow_color=QColor(a.get('glow_color','#ffffff'))
        self.glow_size =a.get('glow_size',14)
        self.glow_alpha=a.get('glow_alpha',110)
        n=len(self.keys)
        self.cw=n*self.kw+(n-1)*self.sp+self.pad*2
        self.ch=self.trail_h+self.kh+self.pad*2+self._stats_h()
        self.c_off=QColor(s['color_released']); self.c_on=QColor(s['color_pressed'])
        self.t_off=QColor(s.get('text_off','#888888')); self.t_on=QColor(s.get('text_on','#ffffff'))
        kc_cfg=self.cfg.get('key_colors',{})
        self.key_colors=[QColor(kc_cfg.get(k, s['color_pressed'])) for k in self.keys]
        self.press_offsets=[0.0]*len(self.keys)
        self.push_px=float(a.get('push_px',3))
        self.fk=QFont('Segoe UI',s['font_size']); self.fk.setBold(True)
        self.fst=QFont('Segoe UI',max(6,s['font_size']-9))
        self.fh=QFont('Segoe UI',7)
        for k in self.keys: self.key_counts.setdefault(k,0)

    def _stats_h(self):
        st=self.cfg.get('stats',{})
        r=1 if st.get('show_kps') or st.get('show_total') else 0
        return r*22+(6 if r else 0)

    def _place_window(self):
        scr=QApplication.primaryScreen().geometry()
        w=self.cfg.get('window',{})
        wx=w.get('x',(scr.width()-self.cw)//2)
        wy=w.get('y',scr.height()-self.ch-80)
        self.setGeometry(max(0,min(wx,scr.width()-self.cw)),
                         max(0,min(wy,scr.height()-self.ch)),self.cw,self.ch)

    def apply_config(self, cfg):
        self.cfg=cfg
        self.hold_blocks.clear(); self._active.clear()
        self.particles.clear(); self.glow_pulses.clear()
        self._build_params()
        scr=QApplication.primaryScreen().geometry()
        self.setGeometry(max(0,min(self.x(),scr.width()-self.cw)),
                         max(0,min(self.y(),scr.height()-self.ch)),self.cw,self.ch)
        self.setWindowOpacity(cfg['style'].get('opacity',1.0))
        self.timer.setInterval(cfg['animation'].get('frame_ms',16))
        if hasattr(self,'_tray_actions'):
            lang=cfg.get('language','ko'); a=self._tray_actions
            a['open'].setText(tr(lang,'tray_open')); a['move'].setText(tr(lang,'tray_move'))
            a['quit'].setText(tr(lang,'tray_quit')); a['tray'].setToolTip(tr(lang,'tray_tip'))
        self.update()

    def reset_stats(self):
        self.key_counts={k:0 for k in self.keys}
        self.total_count=0; self._press_times.clear(); self._max_kps=0; self.update()

    # ── tick ──────────────────────────────────────────────────────────────────
    def _tick(self):
        changed=False

        # blocks
        for b in self.hold_blocks:
            if not b.released:
                nt=max(float(self.pad), b.y_top-self.scroll_spd)
                if nt!=b.y_top: b.y_top=nt; changed=True
            else:
                b.y_top-=self.scroll_spd; b.y_bottom-=self.scroll_spd
                changed=True
        bh=len(self.hold_blocks)
        # 블록 바닥이 화면 위로 벗어나면 제거
        self.hold_blocks=[b for b in self.hold_blocks if b.y_bottom>0]

        # continuous particles from block top
        if self.pt_on and self.pt_cont and self.pt_rate>0:
            for key,b in self._active.items():
                px=self.pad+b.key_idx*(self.kw+self.sp)+self.kw//2
                half=self.kw//3
                for _ in range(self.pt_rate):
                    self.particles.append(Particle(
                        px+random.uniform(-half,half), b.y_top,
                        random.uniform(-1.5,1.5), random.uniform(-2.5,0.2),
                        size=random.randint(2,4)))
                changed=True

        # particles
        for pt in self.particles:
            pt.x+=pt.vx; pt.y+=pt.vy; pt.vy+=0.35; pt.alpha=max(0,pt.alpha-16)
        bp=len(self.particles)
        # cap to avoid overload
        if len(self.particles)>400: self.particles=self.particles[-300:]
        self.particles=[pt for pt in self.particles if pt.alpha>0]

        # glow pulses: expand and fade
        for gp in self.glow_pulses:
            gp.radius+=self.kw*0.06; gp.alpha=max(0,gp.alpha-22)
        gph=len(self.glow_pulses)
        self.glow_pulses=[gp for gp in self.glow_pulses if gp.alpha>0]

        # press-down: 누르는 동안 유지, 뗄 때 스프링 복귀
        for i,key in enumerate(self.keys):
            if key in self.pressed:
                if self.press_offsets[i]<self.push_px:
                    self.press_offsets[i]=self.push_px; changed=True
            elif self.press_offsets[i]>0:
                self.press_offsets[i]=max(0.0,self.press_offsets[i]-self.push_px*0.35)
                changed=True

        # KPS 감소 감지 → 화면 갱신
        if self._press_times:
            cutoff=time.time()-1.0
            if self._press_times[0]<cutoff:
                while self._press_times and self._press_times[0]<cutoff:
                    self._press_times.popleft()
                changed=True

        if changed or len(self.hold_blocks)!=bh or len(self.particles)!=bp or len(self.glow_pulses)!=gph:
            self.update()

    # ── paint ─────────────────────────────────────────────────────────────────
    def paintEvent(self, _):
        p=QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        st=self.cfg.get('stats',{})

        # ── 블록 (위쪽 fade_zone 구역에 들어갈수록 투명해짐, 키별 색상)
        if self.block_on:
            p.setPen(Qt.NoPen)
            for b in self.hold_blocks:
                h=b.y_bottom-b.y_top
                if h<=0: continue
                x1=self.pad+b.key_idx*(self.kw+self.sp)
                kc=self.key_colors[b.key_idx]
                grad=QLinearGradient(0,0,0,self.fade_zone)
                c_t=QColor(kc); c_t.setAlpha(0)
                grad.setColorAt(0.0,c_t); grad.setColorAt(1.0,QColor(kc))
                p.setBrush(QBrush(grad))
                p.drawRect(int(x1),int(b.y_top),self.kw,max(1,int(h)))
            p.setBrush(Qt.NoBrush)

        # ── 파티클
        if self.pt_on:
            p.setPen(Qt.NoPen)
            for pt in self.particles:
                c=QColor(self.pt_color); c.setAlpha(pt.alpha)
                p.setBrush(c)
                s=max(1,int(pt.size))
                p.drawEllipse(int(pt.x)-s//2,int(pt.y)-s//2,s,s)
            p.setBrush(Qt.NoBrush)

        # ── glow pulse (방사형 섬광)
        if self.glow_on and self.glow_pulse_on:
            p.setPen(Qt.NoPen)
            for gp in self.glow_pulses:
                i=gp.key_idx
                cx=float(self.pad+i*(self.kw+self.sp)+self.kw//2)
                cy=float(self.trail_h+self.pad)
                r=gp.radius
                grad=QRadialGradient(QPointF(cx,cy),r)
                gc=QColor(self.key_colors[i]); gc.setAlpha(gp.alpha)
                gc2=QColor(self.key_colors[i]); gc2.setAlpha(0)
                grad.setColorAt(0.0,gc); grad.setColorAt(1.0,gc2)
                p.setBrush(QBrush(grad))
                p.drawEllipse(QPointF(cx,cy),r,r)
            p.setBrush(Qt.NoBrush)

        # ── 키 박스 (키별 색상 + press-down 오프셋)
        for i,key in enumerate(self.keys):
            x1=self.pad+i*(self.kw+self.sp)
            y1=self.trail_h+self.pad+int(self.press_offsets[i])
            r=QRect(x1,y1,self.kw,self.kh); ri=r.adjusted(1,1,-1,-1)
            kc=self.key_colors[i]
            on=key in self.pressed
            # 항상 있는 아주 약한 흰색 배경
            p.setPen(Qt.NoPen); p.setBrush(QColor(255,255,255,18))
            p.drawRoundedRect(ri,6,6)
            # 눌릴 때 채우기
            if on:
                fc=QColor(kc); fc.setAlpha(self.fill_alpha)
                p.setBrush(fc); p.drawRoundedRect(r.adjusted(2,2,-2,-2),5,5)
            # 테두리
            p.setPen(QPen(kc if on else self.c_off,2))
            p.setBrush(Qt.NoBrush); p.drawRoundedRect(ri,6,6)
            # 키 라벨
            p.setPen(self.t_on if on else self.t_off); p.setFont(self.fk)
            lr=r.adjusted(0,-10,0,-10) if st.get('show_key_count') else r
            p.drawText(lr,Qt.AlignCenter,key_label(key))
            # 카운트 (살짝 작게, 바닥에서 살짝 띄움)
            if st.get('show_key_count'):
                p.setFont(self.fst)
                p.setPen(QColor(self.t_on if on else self.t_off))
                p.drawText(QRect(x1,y1+self.kh-21,self.kw,14),
                           Qt.AlignCenter,str(self.key_counts.get(key,0)))

        # ── KPS / Total
        if st.get('show_kps') or st.get('show_total'):
            parts=[]
            if st.get('show_kps'):
                parts.append(f"KPS {len(self._press_times)}  MAX {self._max_kps}")
            if st.get('show_total'): parts.append(f"Total {self.total_count}")
            sy=self.trail_h+self.pad+self.kh+4
            p.setFont(self.fst); p.setPen(QColor(160,160,160))
            p.drawText(QRect(0,sy,self.cw,20),Qt.AlignCenter,"  ·  ".join(parts))

        # ── 이동 모드 힌트
        if self.move_mode:
            p.fillRect(0,0,self.cw,20,QColor(30,25,0,210))
            p.setPen(QColor(255,238,68)); p.setFont(self.fh)
            p.drawText(QRect(0,0,self.cw,20),Qt.AlignCenter,self.move_hint_txt)
        p.end()

    # ── press / release ───────────────────────────────────────────────────────
    def _press(self, key):
        if key in self.pressed: return
        self.pressed.add(key)
        self.key_counts[key]=self.key_counts.get(key,0)+1
        self.total_count+=1
        now=time.time(); self._press_times.append(now)
        kps=sum(1 for t in self._press_times if t>now-1.0)
        if kps>self._max_kps: self._max_kps=kps
        if key in self.keys:
            idx=self.keys.index(key)
            self.press_offsets[idx]=self.push_px
            if self.block_on:
                b=HoldBlock(idx,self.trail_h+self.pad,self.min_h)
                self.hold_blocks.append(b); self._active[key]=b
            px=self.pad+idx*(self.kw+self.sp)+self.kw//2
            py=float(self.trail_h+self.pad); half=self.kw//3
            # burst particles
            if self.pt_on:
                for _ in range(self.pt_cnt):
                    self.particles.append(Particle(
                        px+random.uniform(-half,half), py,
                        random.uniform(-3.5,3.5), random.uniform(-5.5,-0.5),
                        size=random.randint(3,6)))
            # glow pulse
            if self.glow_on and self.glow_pulse_on:
                self.glow_pulses.append(GlowPulse(idx, self.kw*1.8))
        self.update()

    def _release(self, key):
        self.pressed.discard(key)
        if key in self._active: self._active.pop(key).released=True
        self.update()

    # ── move mode ─────────────────────────────────────────────────────────────
    def _keep_topmost(self):
        try: force_topmost(int(self.winId()))
        except Exception: pass

    def _toggle_move(self):
        self.move_mode=not self.move_mode
        set_clickthrough(int(self.winId()),not self.move_mode)
        if not self.move_mode: self._save_pos()
        self.update()

    def _save_pos(self):
        self.cfg.setdefault('window',{})
        self.cfg['window']['x']=self.x(); self.cfg['window']['y']=self.y()
        _save_cfg(self.cfg_path, self.cfg)

    def _do_quit(self):
        try: self._save_pos()
        except Exception: pass
        QApplication.quit()

    def _open_settings(self):
        if getattr(self,'_settings_win',None) is not None:
            self._settings_win.raise_(); self._settings_win.activateWindow(); return
        self._settings_win=SettingsWindow(self,self.cfg_path)
        self._settings_win.exec_()
        self._settings_win=None

    def mousePressEvent(self,e):
        if self.move_mode and e.button()==Qt.LeftButton:
            self._drag_pos=e.globalPos()-self.frameGeometry().topLeft()
    def mouseMoveEvent(self,e):
        if self.move_mode and self._drag_pos and e.buttons()&Qt.LeftButton:
            self.move(e.globalPos()-self._drag_pos)
    def mouseReleaseEvent(self,e): self._drag_pos=None
    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Escape and self.move_mode: self._do_quit()

    # ── listener ──────────────────────────────────────────────────────────────
    def _start_listener(self):
        held=set()
        def on_press(key):
            held.add(key); k=normalize(key)
            hc=any(x in held for x in (kb.Key.ctrl_l,kb.Key.ctrl_r))
            ha=any(x in held for x in (kb.Key.alt_l,kb.Key.alt_r,kb.Key.alt_gr))
            hs=any(x in held for x in (kb.Key.shift_l,kb.Key.shift_r))
            mod=self.cfg.get('hotkey_modifier','ctrl+alt')
            active=(hc and ha) if mod=='ctrl+alt' else (hc and hs)
            if active and k=='m': self.sigs.toggle_move.emit(); return
            if active and k=='s': self.sigs.open_settings.emit(); return
            if k and k in self.keys: self.sigs.press.emit(k)
        def on_release(key):
            held.discard(key); k=normalize(key)
            if key==kb.Key.esc and self.move_mode: self.sigs.quit_app.emit(); return
            if k and k in self.keys: self.sigs.release.emit(k)
        listener=kb.Listener(on_press=on_press,on_release=on_release)
        listener.daemon=True; listener.start()

# ── tray ──────────────────────────────────────────────────────────────────────
def make_tray(app, overlay, cfg_path):
    pm=QPixmap(32,32); pm.fill(Qt.transparent)
    p=QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen); p.setBrush(QColor(70,120,220))
    p.drawRoundedRect(2,2,28,28,7,7)
    p.setPen(QColor(255,255,255)); p.setFont(QFont('Consolas',11,QFont.Bold))
    p.drawText(QRect(0,0,32,32),Qt.AlignCenter,'K'); p.end()
    lang=overlay.cfg.get('language','ko')
    tray=QSystemTrayIcon(QIcon(pm),app)
    menu=QMenu()
    a_set=QAction(tr(lang,'tray_open'),menu); a_set.triggered.connect(overlay._open_settings)
    a_mov=QAction(tr(lang,'tray_move'),menu); a_mov.triggered.connect(overlay.sigs.toggle_move.emit)
    a_qui=QAction(tr(lang,'tray_quit'),menu); a_qui.triggered.connect(overlay.sigs.quit_app.emit)
    menu.addAction(a_set); menu.addAction(a_mov); menu.addSeparator(); menu.addAction(a_qui)
    tray.setContextMenu(menu)
    tray.activated.connect(lambda r: overlay._open_settings() if r==QSystemTrayIcon.DoubleClick else None)
    tray.setToolTip(tr(lang,'tray_tip')); tray.show()
    overlay._tray_actions={'open':a_set,'move':a_mov,'quit':a_qui,'tray':tray}
    return tray

# ── main ──────────────────────────────────────────────────────────────────────
def main():
    app=QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    try:
        hwnd=ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd: ctypes.windll.user32.ShowWindow(hwnd,0)
    except Exception: pass
    base=os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'KeyOverlay')
    os.makedirs(base, exist_ok=True)
    cfg_path=os.path.join(base,'config.json')
    if not os.path.exists(cfg_path):
        _save_cfg(cfg_path, DEFAULTS)
    overlay=Overlay(cfg_path)
    tray=make_tray(app,overlay,cfg_path)  # noqa: F841
    sys.exit(app.exec_())

if __name__=='__main__':
    main()
