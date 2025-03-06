import sys
import os
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

def show_notification():
    """Exibe uma notificação no sistema"""
    if tray_icon.isVisible():
        tray_icon.showMessage(
            "Notificação",
            "Este é um exemplo de notificação no sistema.",
            QSystemTrayIcon.Information,
            3000  # 3 segundos
        )

app = QApplication(sys.argv)

# Verifica se a bandeja do sistema está disponível
if not QSystemTrayIcon.isSystemTrayAvailable():
    print("Bandeja do sistema não disponível. Saindo...")
    sys.exit(1)

# Tenta carregar um ícone personalizado ou usa um ícone do sistema
icon_path = "icone.png"
if not os.path.exists(icon_path):
    icon_path = QIcon.fromTheme("dialog-information")

tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=app)
tray_icon.setVisible(True)

# Cria o menu de contexto do ícone de bandeja
menu = QMenu()

# Ação para exibir a notificação
notify_action = QAction("Mostrar notificação", app)
notify_action.triggered.connect(show_notification)
menu.addAction(notify_action)

# Ação para sair do aplicativo
quit_action = QAction("Sair", app)
quit_action.triggered.connect(app.quit)
menu.addAction(quit_action)

# Associa o menu ao ícone de bandeja
tray_icon.setContextMenu(menu)

# Exibe a notificação automaticamente após 5 segundos
QTimer.singleShot(5000, show_notification)

# Mantém o app rodando
sys.exit(app.exec_())

