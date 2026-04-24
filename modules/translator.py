# modules/translator.py
from googletrans import Translator

class TranslationService:
    def __init__(self, target_lang='vi'):
        self.translator = Translator()
        self.target_lang = target_lang

    def set_target_language(self, new_target):
        self.target_lang = new_target

    def translate(self, text):
        # Kiểm tra trước (LBYL) thay vì để thư viện tự văng lỗi
        if not text or len(text.strip()) == 0:
            return ""
        
        result = self.translator.translate(text, dest=self.target_lang)
        
        # Kiểm tra đối tượng trả về có thuộc tính text hay không
        if result and hasattr(result, 'text'):
            return result.text
        else:
            return "[Loi: Khong nhan duoc ban dich tu server]"