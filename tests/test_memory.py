import unittest
import os
import sys
import json
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path
from sources.memory import Memory
from sources.llm_provider import Provider

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.system_prompt = "Test system prompt"
        self.provider = Provider("test", "test")
        self.memory = Memory(
            system_prompt=self.system_prompt,
            recover_last_session=False,
            memory_compression=False,
            model_provider=self.provider.model
        )

    def tearDown(self):
        if os.path.exists("conversations"):
            for root, dirs, files in os.walk("conversations", topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir("conversations")

    def test_initialization(self):
        self.assertEqual(len(self.memory.memory), 1)
        self.assertEqual(self.memory.memory[0]['role'], 'system')
        self.assertEqual(self.memory.memory[0]['content'], self.system_prompt)
        self.assertIsNotNone(self.memory.session_id)
        self.assertIsInstance(self.memory.session_time, datetime.datetime)

    def test_get_filename(self):
        filename = self.memory.get_filename()
        self.assertTrue(filename.startswith("memory_"))
        self.assertTrue(filename.endswith(".txt"))
        self.assertIn(self.memory.session_time.strftime('%Y-%m-%d'), filename)

    def test_save_memory(self):
        self.memory.save_memory()
        save_path = os.path.join(self.memory.conversation_folder, "casual_agent")
        self.assertTrue(os.path.exists(save_path))
        filename = self.memory.get_filename()
        self.assertTrue(os.path.exists(os.path.join(save_path, filename)))

    def test_push(self):
        index = self.memory.push("user", "Hello")
        self.assertEqual(index, 0)
        self.assertEqual(len(self.memory.memory), 2)
        self.assertEqual(self.memory.memory[1]['role'], "user")
        self.assertEqual(self.memory.memory[1]['content'], "Hello")

    def test_clear(self):
        self.memory.push("user", "Hello")
        self.memory.clear()
        self.assertEqual(len(self.memory.memory), 1) # doesn't clear sys message

    def test_clear_section(self):
        self.memory.clear()
        mem_begin_idx = self.memory.push("user", "Hi i want you to make...")
        self.memory.push("assistant", "<code>") 
        self.memory.push("user", "sys feedback: error")
        self.memory.push("assistant", "<corrected code>")
        mem_end_idx = self.memory.push("user", "according to search...")
        self.memory.clear_section(mem_begin_idx+1, mem_end_idx-1)
        self.assertEqual(len(self.memory.memory), 3) # 3 msg with sys msg
        self.assertEqual(self.memory.memory[0]['role'], "system")

    def test_get(self):
        self.memory.push("user", "Hello")
        memory_content = self.memory.get()
        self.assertEqual(len(memory_content), 2)

    def test_reset(self):
        self.memory.push("user", "Hello")
        new_memory = [{"role": "system", "content": "New prompt"}]
        self.memory.reset(new_memory)
        self.assertEqual(self.memory.memory, new_memory)

    def test_save_and_load_memory(self):
        self.memory.push("user", "Hello")
        self.memory.push("assistant", "Hi")
        self.memory.save_memory()
        
        new_memory = Memory(self.system_prompt, recover_last_session=True, memory_compression=True, model_provider=self.provider.model)
        new_memory.load_memory()
        self.assertEqual(len(new_memory.memory), 3)  # System + messages
        self.assertEqual(new_memory.memory[1]['content'], "Hello")

if __name__ == '__main__':
    unittest.main()
