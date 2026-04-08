"""カスタムウィジェット: データレンジ(カラーランプ変化量)スライダー

PyQt5のQSliderを拡張し、データレンジ値のマッピングを自動的に管理します。
スライダーのインデックス(0-5)に対応する実際の値[10, 20, 50, 100, 200, 500]を管理します。
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QSlider, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from core.data_range_values import DATA_RANGE_VALUES


class DataRangeSlider(QWidget):
    """データレンジスライダーのカスタムウィジェット

    使用可能な値: [10, 20, 50, 100, 200, 500]
    スライダーのインデックス: 0-5
    """

    # シグナル：スライダーの値(インデックス)が変更された
    valueChanged = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None):
        """ウィジェットを初期化"""
        super().__init__(parent)
        self._init_ui()
        self._setup_signals()

    def _init_ui(self) -> None:
        """UI要素を初期化する"""
        # メインレイアウト
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 水平レイアウト（スライダーとラベル）
        h_layout = QHBoxLayout()

        # スライダー
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(len(DATA_RANGE_VALUES) - 1)
        self._slider.setPageStep(1)
        self._slider.setValue(2)
        # 目盛り設定
        self._slider.setTickPosition(QSlider.TicksBelow)
        self._slider.setTickInterval(1)
        h_layout.addWidget(self._slider)

        # 値表示ラベル
        self._value_label = QLabel()
        self._value_label.setMinimumWidth(30)
        self._value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._update_label()
        h_layout.addWidget(self._value_label)

        main_layout.addLayout(h_layout)
        self.setLayout(main_layout)

    def _setup_signals(self) -> None:
        """シグナルを接続する"""
        self._slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, index: int) -> None:
        """スライダーの値が変更されたときの処理"""
        self._update_label()
        self.valueChanged.emit(index)

    def _update_label(self) -> None:
        """値表示ラベルを更新する"""
        index = self._slider.value()
        if 0 <= index < len(DATA_RANGE_VALUES):
            value = DATA_RANGE_VALUES[index]
            self._value_label.setText(str(value))

    # ============================================================================
    # スライダーの標準メソッドのプロキシ
    # ============================================================================

    def value(self) -> int:
        """現在のスライダー値(インデックス)を取得

        Returns:
            スライダーのインデックス(0-5)
        """
        return self._slider.value()

    def setValue(self, index: int) -> None:
        """スライダー値(インデックス)を設定

        Args:
            index: スライダーのインデックス(0-5)
        """
        self._slider.setValue(index)

    def minimum(self) -> int:
        """最小インデックスを取得"""
        return self._slider.minimum()

    def setMinimum(self, min_value: int) -> None:
        """最小インデックスを設定"""
        self._slider.setMinimum(min_value)

    def maximum(self) -> int:
        """最大インデックスを取得"""
        return self._slider.maximum()

    def setMaximum(self, max_value: int) -> None:
        """最大インデックスを設定"""
        self._slider.setMaximum(max_value)

    def setPageStep(self, step: int) -> None:
        """ページステップを設定"""
        self._slider.setPageStep(step)

    def setOrientation(self, orientation: Qt.Orientation) -> None:
        """スライダーの向きを設定"""
        self._slider.setOrientation(orientation)

    def setEnabled(self, enabled: bool) -> None:
        """ウィジェットの有効/無効を設定"""
        self._slider.setEnabled(enabled)

    def isEnabled(self) -> bool:
        """ウィジェットが有効かどうかを判定"""
        return self._slider.isEnabled()

    # ============================================================================
    # カスタムメソッド
    # ============================================================================

    def get_actual_value(self) -> int:
        """現在のスライダーに対応する実際のデータレンジ値を取得

        Returns:
            DATA_RANGE_VALUES の値 (10, 20, 50, 100, 200, 500など)
        """
        index = self.value()
        if 0 <= index < len(DATA_RANGE_VALUES):
            return DATA_RANGE_VALUES[index]
        return DATA_RANGE_VALUES[0]

    def set_value_from_actual(self, actual_value: int) -> None:
        """実際のデータレンジ値からインデックスを設定

        Args:
            actual_value: DATA_RANGE_VALUES に含まれる値

        Raises:
            ValueError: actual_value が DATA_RANGE_VALUES に含まれていない場合
        """
        try:
            index = DATA_RANGE_VALUES.index(actual_value)
            self.setValue(index)
        except ValueError:
            raise ValueError(
                f"値 {actual_value} は DATA_RANGE_VALUES に含まれていません。"
                f"使用可能な値: {DATA_RANGE_VALUES}"
            )

    @property
    def slider(self) -> QSlider:
        """内部のQSliderオブジェクトにアクセス（高度な用途向け）"""
        return self._slider

    @property
    def value_label(self) -> QLabel:
        """値表示ラベルにアクセス（高度な用途向け）"""
        return self._value_label
