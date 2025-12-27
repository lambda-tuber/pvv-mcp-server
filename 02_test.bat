@echo off

pytest -v tests/avatar/test_avatar.py
pytest -v tests/avatar/test_avatar_dialog.py
pytest -v tests/avatar/test_avatar_part.py
pytest -v tests/avatar/test_load_image.py
pytest -v tests/avatar/test_right_click_context_menu.py
pytest -v tests/avatar/test_update_frame.py
pytest -v tests/avatar/test_update_position.py

pytest -v tests/test_avatar_manager.py
pytest -v tests/test_emotion.py
pytest -v tests/test_service.py
pytest -v tests/test_speak.py
pytest -v tests/test_speakers.py
pytest -v tests/test_speaker_info.py

