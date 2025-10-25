"""
test_avatar_manager.py
mod_avatar_managerモジュールのユニットテスト
"""

import pytest
import json
import sys
import os
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from pathlib import Path


# PySide6を完全にモック化（インポート前に実行）
sys.modules['PySide6'] = MagicMock()
sys.modules['PySide6.QtCore'] = MagicMock()
sys.modules['PySide6.QtWidgets'] = MagicMock()
sys.modules['PySide6.QtGui'] = MagicMock()

# アバターモジュールもモック化
sys.modules['pvv_mcp_server.avatar'] = MagicMock()
sys.modules['pvv_mcp_server.avatar.mod_avatar'] = MagicMock()


# テスト対象モジュールのインポート（モック設定後）
import pvv_mcp_server.mod_avatar_manager as mod_avatar_manager


@pytest.fixture
def mock_avatar_window():
    """AvatarWindowのモック"""
    mock = MagicMock()
    mock.save_config = MagicMock(return_value={
        "position": {"x": 100, "y": 200},
        "size": {"width": 300, "height": 400}
    })
    mock.load_config = MagicMock()
    mock.show = MagicMock()
    mock.hide = MagicMock()
    # isinstance チェック用の __class__ 属性
    mock.__class__.__name__ = "AvatarWindow"
    return mock


@pytest.fixture
def test_avatar_config():
    """テスト用のアバター設定"""
    return {
        "enabled": True,
        "target": "TestApp",
        "auto_save_interval": 5000,
        "save_file": "test_config.json",
        "avatars": {
            2: {
                "話者": "四国めたん",
                "表示": True,
                "画像": {},
                "反転": False,
                "縮尺": 50,
                "位置": "right_out"
            },
            14: {
                "話者": "冥鳴ひまり",
                "表示": False,
                "画像": "test.zip",
                "反転": True,
                "縮尺": 75,
                "位置": "left_out"
            }
        }
    }


@pytest.fixture(autouse=True)
def reset_module_globals():
    """各テスト前にモジュールのグローバル変数をリセット"""
    mod_avatar_manager._avatar_global_config = None
    mod_avatar_manager._avatars_config = None
    mod_avatar_manager._avatar_cache = {}
    mod_avatar_manager._auto_save_timer = None
    yield
    # テスト後もクリーンアップ
    mod_avatar_manager._avatar_global_config = None
    mod_avatar_manager._avatars_config = None
    mod_avatar_manager._avatar_cache = {}
    mod_avatar_manager._auto_save_timer = None


class TestSetup:
    """setup関数のテスト"""
    
    @patch.object(mod_avatar_manager, '_create_all_avatars')
    @patch.object(mod_avatar_manager, '_start_auto_save_timer')
    def test_setup_enabled(self, mock_timer, mock_create, test_avatar_config):
        """アバター有効時の初期化テスト"""
        mod_avatar_manager.setup(test_avatar_config)
        
        # グローバル変数が設定されていることを確認
        assert mod_avatar_manager._avatar_global_config == test_avatar_config
        assert mod_avatar_manager._avatars_config == test_avatar_config["avatars"]
        
        # アバター作成とタイマー開始が呼ばれたことを確認
        mock_create.assert_called_once()
        mock_timer.assert_called_once()
    
    @patch.object(mod_avatar_manager, '_create_all_avatars')
    @patch.object(mod_avatar_manager, '_start_auto_save_timer')
    def test_setup_disabled(self, mock_timer, mock_create):
        """アバター無効時の初期化テスト"""
        config = {"enabled": False, "avatars": {}}
        mod_avatar_manager.setup(config)
        
        # アバター作成もタイマー開始も呼ばれないことを確認
        mock_create.assert_not_called()
        mock_timer.assert_not_called()


class TestSetAnimeType:
    """set_anime_type関数のテスト"""
    
    @patch.object(mod_avatar_manager, '_get_avatar')
    def test_set_anime_type_success(self, mock_get_avatar, 
                                    test_avatar_config, mock_avatar_window):
        """正常系: アニメーションキー設定"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        mock_get_avatar.return_value = mock_avatar_window
        
        mod_avatar_manager.set_anime_type(2, "口パク")
        
        mock_get_avatar.assert_called_once_with(2)
    
    @patch.object(mod_avatar_manager, '_get_avatar')
    def test_set_anime_type_disabled(self, mock_get_avatar):
        """アバター無効時は何もしない"""
        mod_avatar_manager._avatar_global_config = {"enabled": False}
        mod_avatar_manager.set_anime_type(2, "口パク")
        
        mock_get_avatar.assert_not_called()
    
    @patch.object(mod_avatar_manager, '_get_avatar')
    def test_set_anime_type_not_found(self, mock_get_avatar, test_avatar_config):
        """アバターが見つからない場合"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        mock_get_avatar.return_value = None
        
        # 例外が発生しないことを確認
        mod_avatar_manager.set_anime_type(999, "口パク")


class TestSaveAllConfigs:
    """save_all_configs関数のテスト"""
    
    def test_save_all_configs_success(self, mock_avatar_window):
        """正常系: 全アバター設定の保存"""
        # キャッシュに2つのアバターを追加
        mock1 = MagicMock()
        mock1.save_config = MagicMock(return_value={"data1": "test1"})
        mock1.__class__.__name__ = "AvatarWindow"
        
        mock2 = MagicMock()
        mock2.save_config = MagicMock(return_value={"data2": "test2"})
        mock2.__class__.__name__ = "AvatarWindow"
        
        mod_avatar_manager._avatar_cache = {
            "avatar1": mock1,
            "avatar2": mock2
        }
        
        # AvatarWindowのisinstance判定をモック
        with patch('pvv_mcp_server.mod_avatar_manager.isinstance') as mock_isinstance:
            mock_isinstance.return_value = True
            result = mod_avatar_manager.save_all_configs()
        
        assert len(result) == 2
        assert "avatar1" in result
        assert "avatar2" in result
    
    def test_save_all_configs_empty(self):
        """キャッシュが空の場合"""
        mod_avatar_manager._avatar_cache = {}
        result = mod_avatar_manager.save_all_configs()
        
        assert result == {}
    
    def test_save_all_configs_with_error(self):
        """保存中にエラーが発生した場合"""
        error_mock = MagicMock()
        error_mock.save_config = MagicMock(side_effect=Exception("Save error"))
        error_mock.__class__.__name__ = "AvatarWindow"
        
        mod_avatar_manager._avatar_cache = {"avatar1": error_mock}
        
        with patch('pvv_mcp_server.mod_avatar_manager.isinstance', return_value=True):
            result = mod_avatar_manager.save_all_configs()
        
        # エラーが発生しても処理は継続
        assert result == {}


class TestLoadAllConfigs:
    """load_all_configs関数のテスト"""
    
    def test_load_all_configs_success(self, mock_avatar_window):
        """正常系: 全アバター設定の読み込み"""
        test_configs = {
            "avatar1": {"position": {"x": 10, "y": 20}},
            "avatar2": {"position": {"x": 30, "y": 40}}
        }
        
        mock1 = MagicMock()
        mock1.__class__.__name__ = "AvatarWindow"
        mock2 = MagicMock()
        mock2.__class__.__name__ = "AvatarWindow"
        
        mod_avatar_manager._avatar_cache = {
            "avatar1": mock1,
            "avatar2": mock2
        }
        
        with patch('pvv_mcp_server.mod_avatar_manager.isinstance', return_value=True):
            mod_avatar_manager.load_all_configs(test_configs)
        
        mock1.load_config.assert_called_once_with({"position": {"x": 10, "y": 20}})
        mock2.load_config.assert_called_once_with({"position": {"x": 30, "y": 40}})


class TestPrivateFunctions:
    """プライベート関数のテスト"""
    
    def test_start_auto_save_timer(self, test_avatar_config):
        """自動保存タイマーの開始"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        
        with patch('pvv_mcp_server.mod_avatar_manager.QTimer') as mock_qtimer_class:
            mock_timer_instance = MagicMock()
            mock_qtimer_class.return_value = mock_timer_instance
            
            mod_avatar_manager._start_auto_save_timer()
            
            # タイマーが作成され、設定されたことを確認
            mock_qtimer_class.assert_called_once()
            mock_timer_instance.timeout.connect.assert_called_once()
            mock_timer_instance.start.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open)
    @patch.object(mod_avatar_manager, 'save_all_configs')
    @patch('os.path.exists', return_value=True)
    def test_on_auto_save_success(self, mock_exists, mock_save, mock_file, 
                                  test_avatar_config):
        """自動保存のコールバック（正常系）"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        mock_save.return_value = {"avatar1": {"data": "test"}}
        
        mod_avatar_manager._on_auto_save()
        
        mock_save.assert_called_once()
        # ファイルが存在し、書き込みが行われたことを確認
        mock_file.assert_called_once_with("test_config.json", 'w', encoding='utf-8')
    
    @patch.object(mod_avatar_manager, 'save_all_configs')
    def test_on_auto_save_no_file(self, mock_save):
        """自動保存（ファイルパス未設定）"""
        mod_avatar_manager._avatar_global_config = {"save_file": None}
        mock_save.return_value = {}
        
        # 例外が発生しないことを確認
        mod_avatar_manager._on_auto_save()
        
        mock_save.assert_called_once()
    
    @patch.object(mod_avatar_manager, '_create_avatar')
    @patch.object(mod_avatar_manager, '_get_avatar')
    def test_create_all_avatars(self, mock_get, mock_create, test_avatar_config):
        """全アバターの作成"""
        mod_avatar_manager._avatars_config = test_avatar_config["avatars"]
        mock_get.return_value = None  # アバターが未作成の状態
        
        mod_avatar_manager._create_all_avatars()
        
        # avatarsの数だけcreate_avatarが呼ばれる
        assert mock_create.call_count == len(test_avatar_config["avatars"])
    
    @patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow')
    @patch.object(mod_avatar_manager, '_load_config', return_value=None)
    def test_create_avatar(self, mock_load_config, mock_avatar_class, 
                          test_avatar_config):
        """個別アバターの作成"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        mod_avatar_manager._avatars_config = test_avatar_config["avatars"]
        
        mock_instance = MagicMock()
        mock_avatar_class.return_value = mock_instance
        
        avatar_conf = test_avatar_config["avatars"][2]
        result = mod_avatar_manager._create_avatar(2, avatar_conf)
        
        # AvatarWindowが作成されたことを確認
        mock_avatar_class.assert_called_once()
        assert result == mock_instance
        # キャッシュに登録されたことを確認
        assert len(mod_avatar_manager._avatar_cache) == 1
    
    def test_get_avatar_found(self, test_avatar_config, mock_avatar_window):
        """アバターの取得（存在する場合）"""
        mod_avatar_manager._avatars_config = test_avatar_config["avatars"]
        avatar_conf = test_avatar_config["avatars"][2]
        key = json.dumps(avatar_conf, sort_keys=True)
        mod_avatar_manager._avatar_cache = {key: mock_avatar_window}
        
        result = mod_avatar_manager._get_avatar(2)
        
        assert result == mock_avatar_window
    
    def test_get_avatar_not_found(self):
        """アバターの取得（存在しない場合）"""
        mod_avatar_manager._avatars_config = {}
        
        result = mod_avatar_manager._get_avatar(999)
        
        assert result is None
    
    @patch('builtins.open', new_callable=mock_open, 
           read_data='{"avatar1": {"data": "test"}}')
    @patch('pathlib.Path.exists', return_value=True)
    def test_load_config_success(self, mock_path_exists, mock_file, 
                                 test_avatar_config):
        """設定ファイルの読み込み（正常系）"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        
        result = mod_avatar_manager._load_config()
        
        assert result is not None
        assert isinstance(result, dict)
        assert "avatar1" in result
    
    @patch('pathlib.Path.exists', return_value=False)
    def test_load_config_file_not_found(self, mock_path_exists, test_avatar_config):
        """設定ファイルの読み込み（ファイルなし）"""
        mod_avatar_manager._avatar_global_config = test_avatar_config
        
        result = mod_avatar_manager._load_config()
        
        assert result is None


class TestIntegration:
    """統合テスト"""
    
    @patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow')
    @patch.object(mod_avatar_manager, '_load_config', return_value=None)
    def test_full_workflow(self, mock_load_config, mock_avatar_class, 
                          test_avatar_config):
        """セットアップから設定保存までの一連の流れ"""
        mock_avatar = MagicMock()
        mock_avatar.save_config = MagicMock(return_value={"test": "data"})
        mock_avatar.__class__.__name__ = "AvatarWindow"
        mock_avatar_class.return_value = mock_avatar
        
        # 初期化
        mod_avatar_manager.setup(test_avatar_config)
        
        # アニメーション設定
        mod_avatar_manager.set_anime_type(2, "口パク")
        
        # 設定保存
        with patch('pvv_mcp_server.mod_avatar_manager.isinstance', return_value=True):
            configs = mod_avatar_manager.save_all_configs()
        
        # 各ステップが正常に実行されたことを確認
        assert mod_avatar_manager._avatar_global_config is not None
        # アバターが作成されたことを確認
        assert mock_avatar_class.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])