import unittest
import os
import sys
import json
import datetime
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path
from sources.memory import Memory

class TestMemory(unittest.TestCase):
    def setUp(self):
        runtime_dir = tempfile.TemporaryDirectory()
        self.addCleanup(runtime_dir.cleanup)
        runtime_env = patch.dict(os.environ, {"AGENT_RUNTIME_DIR": runtime_dir.name})
        runtime_env.start()
        self.addCleanup(runtime_env.stop)
        self.system_prompt = "Test system prompt"
        self.memory = Memory(
            system_prompt=self.system_prompt,
            recover_last_session=False,
            memory_compression=False
        )

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

    def test_find_last_session_path_uses_full_timestamp(self):
        morning = "memory_2026-10-13_08-00-00.txt"
        evening = "memory_2026-10-13_20-00-00.txt"
        previous_day = "memory_2026-10-12_23-59-59.txt"
        for filenames in ([morning, evening, previous_day],
                          [evening, morning, previous_day]):
            with self.subTest(filenames=filenames), \
                    patch("sources.memory.os.listdir", return_value=filenames):
                self.assertEqual(
                    self.memory.find_last_session_path(self.memory.conversation_folder),
                    evening
                )

    def test_find_last_session_path_empty_directory(self):
        self.assertIsNone(
            self.memory.find_last_session_path(self.memory.conversation_folder)
        )

    def test_load_memory_recovers_latest_same_day_session(self):
        save_path = os.path.join(self.memory.conversation_folder, "casual_agent")
        os.makedirs(save_path)
        morning = "memory_2026-10-13_08-00-00.txt"
        evening = "memory_2026-10-13_20-00-00.txt"
        for filename, content in ((morning, "Morning response"),
                                  (evening, "Evening response")):
            transcript = [
                {"role": "system", "content": self.system_prompt},
                {"role": "assistant", "content": content},
            ]
            with open(os.path.join(save_path, filename), "w") as session:
                json.dump(transcript, session)

        with patch("sources.memory.os.listdir", return_value=[morning, evening]):
            self.memory.load_memory()

        self.assertEqual(self.memory.get(), transcript)
        self.assertTrue(os.path.isfile(os.path.join(save_path, morning)))
        self.assertTrue(os.path.isfile(os.path.join(save_path, evening)))

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
        
        new_memory = Memory(
            self.system_prompt, recover_last_session=True, memory_compression=False
        )
        new_memory.load_memory()
        self.assertEqual(len(new_memory.memory), 3)  # System + messages
        self.assertEqual(new_memory.memory[1]['content'], "Hello")

    def test_recovered_memory_is_compressed_after_model_initialization(self):
        self.memory.push("assistant", "Saved response. " * 100)
        self.memory.save_memory()

        # Keep the real download/restore/compress flow, but avoid network and inference.
        with patch("sources.memory.AutoTokenizer.from_pretrained") as tokenizer_loader, \
                patch("sources.memory.AutoModelForSeq2SeqLM.from_pretrained"):
            tokenizer_loader.return_value.return_value = {"input_ids": [1, 2, 3]}
            tokenizer_loader.return_value.decode.return_value = "Recovered summary"
            restored = Memory(self.system_prompt, recover_last_session=True)

        self.assertEqual(restored.memory[0]["content"], self.system_prompt)
        self.assertEqual(restored.memory[1]["content"], "Recovered summary")
        self.assertTrue(restored.session_recovered)

if __name__ == '__main__':
    unittest.main()