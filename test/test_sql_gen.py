import unittest
from helpers.chat.chat import ChatResponse
import uuid

class TestSQLGenerator(unittest.TestCase):
    def test_valid_sql_generation(self, **kwargs):
        inst=ChatResponse(provider=kwargs.get("provider","gemini"))
        question= kwargs.get("user_question")
        res=inst.handle_chat(question,str(uuid.uuid4()))        
        self.assertIsNotNone(res)
