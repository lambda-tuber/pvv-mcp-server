import pytest
import os
import zipfile
import io
from pathlib import Path
from collections import defaultdict
from unittest.mock import patch, MagicMock, mock_open
from pvv_mcp_server.avatar.mod_load_image import (
    load_image,
    _load_folder,
    _load_local_zip,
    _load_zip_from_url,
    _load_voicevox_portrait,
    _create_empty_zip_data
)


class TestLoadImage:
    """load_image関数のテストクラス"""
    
    def test_create_empty_zip_data(self):
        """空のzip_dataを作成できることを確認"""
        result = _create_empty_zip_data()
        
        # 期待されるカテゴリが全て存在すること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
        
        # 各カテゴリが空の辞書であること
        for cat in expected_categories:
            assert result[cat] == {}
    
    @patch('pvv_mcp_server.avatar.mod_load_image.Path')
    def test_load_folder_not_exists(self, mock_path):
        """存在しないフォルダを指定した場合のテスト"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance
        
        result = _load_folder("non_existent_folder", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
    
    @patch('pvv_mcp_server.avatar.mod_load_image.Path')
    def test_load_folder_no_png_files(self, mock_path):
        """PNGファイルが存在しないフォルダを指定した場合のテスト"""
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = []
        mock_path.return_value = mock_path_instance
        
        result = _load_folder("empty_folder", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'PNG_DATA')
    @patch('pvv_mcp_server.avatar.mod_load_image.Path')
    def test_load_folder_with_png_files(self, mock_path, mock_file):
        """PNGファイルが存在するフォルダを読み込むテスト"""
        # モックのPNGファイルを作成
        mock_png1 = MagicMock()
        mock_png1.name = "test1.png"
        mock_png1.parent.name = "口"
        
        mock_png2 = MagicMock()
        mock_png2.name = "test2.png"
        mock_png2.parent.name = "目"
        
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = [mock_png1, mock_png2]
        mock_path.return_value = mock_path_instance
        
        result = _load_folder("test_folder", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 「口」カテゴリにtest1.pngが登録されていること
        assert "test1.png" in result["口"]
        assert result["口"]["test1.png"] == b'PNG_DATA'
        
        # 「目」カテゴリにtest2.pngが登録されていること
        assert "test2.png" in result["目"]
        assert result["目"]["test2.png"] == b'PNG_DATA'
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'PNG_DATA')
    @patch('pvv_mcp_server.avatar.mod_load_image.Path')
    def test_load_folder_unknown_category(self, mock_path, mock_file):
        """未知のカテゴリのPNGファイルを「他」に分類するテスト"""
        mock_png = MagicMock()
        mock_png.name = "unknown.png"
        mock_png.parent.name = "不明なフォルダ"
        
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.rglob.return_value = [mock_png]
        mock_path.return_value = mock_path_instance
        
        result = _load_folder("test_folder", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 「他」カテゴリに分類されること
        assert "unknown.png" in result["他"]
        assert result["他"]["unknown.png"] == b'PNG_DATA'
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pvv_mcp_server.avatar.mod_load_image.zipfile.ZipFile')
    def test_load_local_zip_success(self, mock_zipfile, mock_file):
        """ローカルZIPファイルの読み込みが成功するテスト"""
        # モックのZIPファイルを設定
        mock_file.return_value.read.return_value = b'ZIP_DATA'
        
        # ZipFileのモック
        mock_zip_instance = MagicMock()
        mock_info1 = MagicMock()
        mock_info1.filename = "avatar/口/mouth.png"
        mock_info2 = MagicMock()
        mock_info2.filename = "avatar/目/eye.png"
        
        mock_zip_instance.infolist.return_value = [mock_info1, mock_info2]
        mock_zip_instance.__enter__.return_value = mock_zip_instance
        mock_zip_instance.open.return_value.__enter__.return_value.read.return_value = b'PNG_DATA'
        mock_zipfile.return_value = mock_zip_instance
        
        result = _load_local_zip("test.zip", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 「口」と「目」カテゴリにPNGデータが登録されていること
        assert "mouth.png" in result["口"]
        assert "eye.png" in result["目"]
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_local_zip_file_not_found(self, mock_file):
        """存在しないZIPファイルを指定した場合のテスト"""
        result = _load_local_zip("non_existent.zip", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
    
    @patch('pvv_mcp_server.avatar.mod_load_image._load_voicevox_portrait')
    def test_load_image_portrait(self, mock_portrait):
        """sourceが'portrait'の場合にVOICEVOXポートレートを読み込むテスト"""
        mock_portrait.return_value = {"他": {"portrait.png": b'PNG_DATA'}}
        
        result = load_image("portrait", speaker_id="1")
        
        # _load_voicevox_portraitが呼ばれること
        mock_portrait.assert_called_once_with("1")
        assert "portrait.png" in result["他"]
    
    @patch('pvv_mcp_server.avatar.mod_load_image._load_folder')
    @patch('os.path.isdir', return_value=True)
    def test_load_image_folder(self, mock_isdir, mock_load_folder):
        """sourceがフォルダの場合に_load_folderが呼ばれるテスト"""
        mock_load_folder.return_value = {"口": {"mouth.png": b'PNG_DATA'}}
        
        result = load_image("test_folder")
        
        # _load_folderが呼ばれること
        mock_load_folder.assert_called_once()
        assert "mouth.png" in result["口"]
    
    @patch('pvv_mcp_server.avatar.mod_load_image._load_local_zip')
    @patch('os.path.isdir', return_value=False)
    def test_load_image_local_zip(self, mock_isdir, mock_load_zip):
        """sourceがZIPファイルの場合に_load_local_zipが呼ばれるテスト"""
        mock_load_zip.return_value = {"口": {"mouth.png": b'PNG_DATA'}}
        
        result = load_image("test.zip")
        
        # _load_local_zipが呼ばれること
        mock_load_zip.assert_called_once()
        assert "mouth.png" in result["口"]
    
    @patch('pvv_mcp_server.avatar.mod_load_image._load_zip_from_url')
    def test_load_image_url_zip(self, mock_load_url):
        """sourceがURLの場合に_load_zip_from_urlが呼ばれるテスト"""
        mock_load_url.return_value = {"口": {"mouth.png": b'PNG_DATA'}}
        
        result = load_image("https://example.com/avatar.zip")
        
        # _load_zip_from_urlが呼ばれること
        mock_load_url.assert_called_once()
        assert "mouth.png" in result["口"]
    
    @patch('os.path.isdir', return_value=False)
    def test_load_image_unknown_format(self, mock_isdir):
        """不明な形式のsourceを指定した場合のテスト"""
        result = load_image("unknown_format.txt")
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)


class TestLoadZipFromUrl:
    """_load_zip_from_url関数のテストクラス"""
    
    @patch('urllib.request.urlopen')
    @patch('pvv_mcp_server.avatar.mod_load_image.zipfile.ZipFile')
    def test_load_zip_from_url_success(self, mock_zipfile, mock_urlopen):
        """URLからZIPファイルをダウンロードして読み込むテスト"""
        # モックのレスポンス
        mock_response = MagicMock()
        mock_response.read.return_value = b'ZIP_DATA'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        # ZipFileのモック
        mock_zip_instance = MagicMock()
        mock_info = MagicMock()
        mock_info.filename = "avatar/口/mouth.png"
        mock_zip_instance.infolist.return_value = [mock_info]
        mock_zip_instance.__enter__.return_value = mock_zip_instance
        mock_zip_instance.open.return_value.__enter__.return_value.read.return_value = b'PNG_DATA'
        mock_zipfile.return_value = mock_zip_instance
        
        result = _load_zip_from_url("https://example.com/avatar.zip", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 「口」カテゴリにPNGデータが登録されていること
        assert "mouth.png" in result["口"]
    
    @patch('urllib.request.urlopen', side_effect=Exception("Network Error"))
    def test_load_zip_from_url_error(self, mock_urlopen):
        """URLからのダウンロードが失敗した場合のテスト"""
        result = _load_zip_from_url("https://example.com/avatar.zip", ['後', '体', '顔', '髪', '口', '目', '眉', '他'])
        
        # 空の辞書が返されること
        assert isinstance(result, defaultdict)


class TestLoadVoicevoxPortrait:
    """_load_voicevox_portrait関数のテストクラス"""
    
    @patch('urllib.request.urlopen')
    @patch('pvv_mcp_server.mod_speaker_info.speaker_info')
    def test_load_voicevox_portrait_success(self, mock_speaker_info, mock_urlopen):
        """VOICEVOXポートレートの読み込みが成功するテスト"""
        # speaker_infoのモック
        mock_speaker_info.return_value = {"portrait": "https://example.com/portrait.png"}
        
        # urlopenのモック
        mock_response = MagicMock()
        mock_response.read.return_value = b'PNG_DATA'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        result = _load_voicevox_portrait("1")
        
        # 「他」カテゴリにportrait.pngが登録されていること
        assert "portrait.png" in result["他"]
        assert result["他"]["portrait.png"] == b'PNG_DATA'
    
    def test_load_voicevox_portrait_no_speaker_id(self):
        """speaker_idが指定されていない場合のテスト"""
        result = _load_voicevox_portrait(None)
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
    
    @patch('pvv_mcp_server.mod_speaker_info.speaker_info')
    def test_load_voicevox_portrait_no_portrait_url(self, mock_speaker_info):
        """ポートレートURLが取得できない場合のテスト"""
        mock_speaker_info.return_value = {}
        
        result = _load_voicevox_portrait("1")
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)
    
    @patch('urllib.request.urlopen', side_effect=Exception("Network Error"))
    @patch('pvv_mcp_server.mod_speaker_info.speaker_info')
    def test_load_voicevox_portrait_download_error(self, mock_speaker_info, mock_urlopen):
        """ポートレートのダウンロードが失敗した場合のテスト"""
        mock_speaker_info.return_value = {"portrait": "https://example.com/portrait.png"}
        
        result = _load_voicevox_portrait("1")
        
        # 空のzip_dataが返されること
        expected_categories = ['後', '体', '顔', '髪', '口', '目', '眉', '他']
        assert all(cat in result for cat in expected_categories)