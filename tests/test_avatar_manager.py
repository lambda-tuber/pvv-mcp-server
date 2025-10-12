"""
test_avatar_manager.py
mod_avatar_managerモジュールのユニットテスト
"""

import pytest
from unittest.mock import MagicMock, patch, call
from pvv_mcp_server import mod_avatar_manager


class TestAvatarManager:
    """mod_avatar_managerのテストクラス"""
    
    @pytest.fixture(autouse=True)
    def reset_module_state(self):
        """各テスト前にモジュールのグローバル変数をリセット"""
        mod_avatar_manager._avatar_config = None
        mod_avatar_manager._avatars_config = None
        mod_avatar_manager._avatar_cache = {}
        yield
        # テスト後もクリーンアップ
        mod_avatar_manager._avatar_config = None
        mod_avatar_manager._avatars_config = None
        mod_avatar_manager._avatar_cache = {}
    
    def test_setup_disabled(self):
        """アバター無効時のsetupテスト"""
        config = {
            "enabled": False,
            "target": "TestApp",
            "avatars": {}
        }
        
        mod_avatar_manager.setup(config)
        
        assert mod_avatar_manager._avatar_config == config
        assert mod_avatar_manager._avatars_config == {}
        assert len(mod_avatar_manager._avatar_cache) == 0
    
    @patch('pvv_mcp_server.mod_avatar_manager._create_all_avatars')
    def test_setup_enabled(self, mock_create_all):
        """アバター有効時のsetupテスト"""
        config = {
            "enabled": True,
            "target": "TestApp",
            "avatars": {
                2: {"話者": "四国めたん", "表示": True}
            }
        }
        
        mod_avatar_manager.setup(config)
        
        assert mod_avatar_manager._avatar_config == config
        assert mod_avatar_manager._avatars_config == config["avatars"]
        mock_create_all.assert_called_once()
    
    @patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow')
    @patch('pvv_mcp_server.mod_avatar_manager._get_images')
    def test_create_avatar(self, mock_get_images, mock_avatar_class):
        """_create_avatar関数のテスト"""
        # モックの設定
        mock_get_images.return_value = {"立ち絵": ["image1"], "口パク": ["image2"]}
        mock_instance = MagicMock()
        mock_avatar_class.return_value = mock_instance
        
        # グローバル変数の設定
        mod_avatar_manager._avatar_config = {"target": "TestApp"}
        
        # アバター作成
        avatar_conf = {
            "話者": "四国めたん",
            "表示": True,
            "画像": {},
            "反転": False,
            "縮尺": 50,
            "位置": "right_out"
        }
        
        result = mod_avatar_manager._create_avatar(2, avatar_conf)
        
        # 検証
        assert result == mock_instance
        mock_get_images.assert_called_once_with("四国めたん", {})
        mock_avatar_class.assert_called_once()
        mock_instance.update_position.assert_called_once()
        mock_instance.show.assert_called_once()
    
    @patch('pvv_mcp_server.mod_avatar_manager.AvatarWindow')
    @patch('pvv_mcp_server.mod_avatar_manager._get_images')
    def test_create_avatar_hide(self, mock_get_images, mock_avatar_class):
        """表示=Falseの場合のアバター作成テスト"""
        mock_get_images.return_value = {"立ち絵": ["image1"]}
        mock_instance = MagicMock()
        mock_avatar_class.return_value = mock_instance
        
        mod_avatar_manager._avatar_config = {"target": "TestApp"}
        
        avatar_conf = {
            "話者": "四国めたん",
            "表示": False,
            "画像": {},
            "反転": True,
            "縮尺": 100,
            "位置": "left_in"
        }
        
        mod_avatar_manager._create_avatar(2, avatar_conf)
        
        mock_instance.hide.assert_called_once()
        mock_instance.show.assert_not_called()
    
    def test_get_images_with_existing_images(self):
        """既存画像がある場合の_get_imagesテスト"""
        images = {
            "立ち絵": ["existing1"],
            "口パク": ["existing2"]
        }
        
        result = mod_avatar_manager._get_images("test_speaker", images)
        
        assert result == images
    
    @patch('pvv_mcp_server.mod_avatar_manager.speaker_info')
    def test_get_images_from_speaker_info(self, mock_speaker_info):
        """speaker_infoから画像を取得するテスト"""
        mock_speaker_info.return_value = {
            "portrait": "base64_image_data"
        }
        
        result = mod_avatar_manager._get_images("test_speaker", {})
        
        assert result["立ち絵"] == ["base64_image_data"]
        assert result["口パク"] == ["base64_image_data"]
        mock_speaker_info.assert_called_once_with("test_speaker")
    
    @patch('pvv_mcp_server.mod_avatar_manager.speaker_info')
    def test_get_images_no_portrait(self, mock_speaker_info):
        """portraitが存在しない場合のテスト"""
        mock_speaker_info.return_value = {}
        
        result = mod_avatar_manager._get_images("test_speaker", {"custom": ["data"]})
        
        assert result == {"custom": ["data"]}
    
    @patch('pvv_mcp_server.mod_avatar_manager._get_avatar')
    @patch('pvv_mcp_server.mod_avatar_manager.QMetaObject')
    def test_set_anime_key_enabled(self, mock_qmeta, mock_get_avatar):
        """アバター有効時のset_anime_keyテスト"""
        mock_avatar = MagicMock()
        mock_get_avatar.return_value = mock_avatar
        
        mod_avatar_manager._avatar_config = {"enabled": True}
        
        mod_avatar_manager.set_anime_key(2, "口パク")
        
        mock_get_avatar.assert_called_once_with(2)
        assert mock_qmeta.invokeMethod.call_count == 2
    
    @patch('pvv_mcp_server.mod_avatar_manager._get_avatar')
    def test_set_anime_key_disabled(self, mock_get_avatar):
        """アバター無効時のset_anime_keyテスト"""
        mod_avatar_manager._avatar_config = {"enabled": False}
        
        mod_avatar_manager.set_anime_key(2, "口パク")
        
        mock_get_avatar.assert_not_called()
    
    @patch('pvv_mcp_server.mod_avatar_manager._get_avatar')
    @patch('pvv_mcp_server.mod_avatar_manager.QMetaObject')
    def test_set_anime_key_avatar_not_found(self, mock_qmeta, mock_get_avatar):
        """アバターが見つからない場合のテスト"""
        mock_get_avatar.return_value = None
        
        mod_avatar_manager._avatar_config = {"enabled": True}
        
        # 例外が発生しないことを確認
        mod_avatar_manager.set_anime_key(999, "口パク")
        
        mock_qmeta.invokeMethod.assert_not_called()
    
    def test_get_avatar_cache_hit(self):
        """キャッシュヒット時の_get_avatarテスト"""
        mock_avatar = MagicMock()
        avatar_conf = {"話者": "四国めたん", "表示": True}
        
        import json
        key = json.dumps(avatar_conf, sort_keys=True)
        mod_avatar_manager._avatar_cache[key] = mock_avatar
        mod_avatar_manager._avatars_config = {2: avatar_conf}
        
        result = mod_avatar_manager._get_avatar(2)
        
        assert result == mock_avatar
    
    def test_get_avatar_cache_miss(self):
        """キャッシュミス時の_get_avatarテスト"""
        mod_avatar_manager._avatars_config = {}
        
        result = mod_avatar_manager._get_avatar(999)
        
        assert result is None
    
    @patch('pvv_mcp_server.mod_avatar_manager._create_avatar')
    def test_create_all_avatars(self, mock_create):
        """_create_all_avatarsのテスト"""
        mod_avatar_manager._avatars_config = {
            2: {"話者": "四国めたん"},
            3: {"話者": "ずんだもん"}
        }
        
        mod_avatar_manager._create_all_avatars()
        
        assert mock_create.call_count == 2
        mock_create.assert_any_call(2, {"話者": "四国めたん"})
        mock_create.assert_any_call(3, {"話者": "ずんだもん"})
    
    def test_create_all_avatars_no_config(self):
        """アバター設定が空の場合のテスト"""
        mod_avatar_manager._avatars_config = None
        
        # 例外が発生しないことを確認
        mod_avatar_manager._create_all_avatars()