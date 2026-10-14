import unittest
import os
import sys
import json
import shutil
import tempfile
import datetime
from unittest.mock import patch

import torch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Add project root to Python path
from sources.memory import Memory, parse_model_size_billions

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.runtime_dir = tempfile.mkdtemp()
        env_patch = patch.dict(os.environ, {"AGENT_RUNTIME_DIR": self.runtime_dir})
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.addCleanup(shutil.rmtree, self.runtime_dir, ignore_errors=True)
        self.system_prompt = "Test system prompt"
        self.memory = Memory(
            system_prompt=self.system_prompt,
            recover_last_session=False,
            memory_compression=False
        )

    def write_session(self, filename, content):
        session_dir = os.path.join(self.memory.conversation_folder, "casual_agent")
        os.makedirs(session_dir, exist_ok=True)
        with open(os.path.join(session_dir, filename), "w") as f:
            f.write(content)

    def test_initialization(self):
        self.assertEqual(len(self.memory.memory), 1)
        self.assertEqual(self.memory.memory[0]['role'], 'system')
        self.assertEqual(self.memory.memory[0]['content'], self.system_prompt)
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
        self.memory.push("user", "Hello")
        self.assertEqual(len(self.memory.memory), 2)
        self.assertEqual(self.memory.memory[1]['role'], "user")
        self.assertEqual(self.memory.memory[1]['content'], "Hello")

    def test_push_without_model_provider(self):
        memory = Memory(self.system_prompt, memory_compression=False, model_provider=None)
        memory.push("user", "Hello")
        self.assertEqual(memory.get()[-1], {"role": "user", "content": "Hello"})

    def test_clear(self):
        self.memory.push("user", "Hello")
        self.memory.clear()
        self.assertEqual(len(self.memory.memory), 1) # doesn't clear sys message

    def test_get_sends_only_role_and_content(self):
        self.memory.push("user", "Hello")
        self.assertEqual(self.memory.get(), [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Hello"},
        ])
        self.assertIn("time", self.memory.memory[1])

    def test_reset(self):
        self.memory.push("user", "Hello")
        new_memory = [{"role": "system", "content": "New prompt"}]
        self.memory.reset(new_memory)
        self.assertEqual(self.memory.memory, new_memory)
        new_memory[0]["content"] = "Changed by caller"
        self.assertEqual(self.memory.memory[0]["content"], "New prompt")

    def test_reset_without_argument_keeps_system_prompt(self):
        other = Memory("Other prompt", memory_compression=False)
        self.memory.push("user", "Hello")
        self.memory.reset()
        other.reset()
        self.memory.push("user", "Again")
        self.assertEqual(self.memory.get(), [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "Again"},
        ])
        self.assertEqual(other.get(), [{"role": "system", "content": "Other prompt"}])

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

    def test_load_picks_latest_session_of_same_day(self):
        for time_str in ["09-00-00", "23-59-59", "12-00-00"]:
            history = [{"role": "system", "content": "sys"}, {"role": "assistant", "content": time_str}]
            self.write_session(f"memory_2026-10-14_{time_str}.txt", json.dumps(history))
        self.memory.load_memory()
        self.assertEqual(self.memory.memory[-1]["content"], "23-59-59")

    def test_load_invalid_session_keeps_current_memory(self):
        for content in ['[{"role": "system", "con', '[]', '{}', '[{"role": "user", "content": "no system"}]']:
            with self.subTest(content=content):
                self.write_session("memory_2099-01-01_00-00-00.txt", content)
                self.memory.load_memory()
                self.assertEqual(self.memory.get(), [{"role": "system", "content": self.system_prompt}])

    def test_model_size_parsing(self):
        cases = {
            "deepseek-r1:14b": 14,
            "phi3:3.8b": 3.8,
            "meta-llama/Llama-3.1-8B-Instruct": 8,
            "gpt-4o": None,
            None: None,
        }
        for model_name, expected in cases.items():
            with self.subTest(model_name=model_name):
                self.assertEqual(parse_model_size_billions(model_name), expected)

    def test_trim_text_uses_characters_not_tokens(self):
        memory = Memory(self.system_prompt, memory_compression=False, model_provider="qwen2.5:7b")
        self.assertEqual(memory.ideal_ctx, 4096)
        self.assertEqual(len(memory.trim_text_to_max_ctx("a" * 100000)), 4096 * 4)

    def test_compress_text_stops_when_summary_does_not_shrink(self):
        memory = Memory(self.system_prompt, memory_compression=False, model_provider="llama3.2:1b")
        memory.tokenizer = memory.model = object()
        with patch.object(memory, "summarize", side_effect=lambda text: text) as summarize:
            result = memory.compress_text_to_max_ctx("a" * 100000)
        self.assertEqual(summarize.call_count, 1)
        self.assertEqual(len(result), memory.max_ctx_chars)

    def test_recovered_memory_is_compressed_after_model_initialization(self):
        self.memory.push("assistant", "Saved response. " * 100)
        self.memory.save_memory()

        # Keep the real download/restore/compress flow, but avoid network and inference.
        with patch("transformers.AutoTokenizer.from_pretrained") as tokenizer_loader, \
                patch("transformers.AutoModelForSeq2SeqLM.from_pretrained"):
            tokenizer_loader.return_value.return_value = {"input_ids": torch.ones((1, 300), dtype=torch.long)}
            tokenizer_loader.return_value.decode.return_value = "Recovered summary"
            restored = Memory(self.system_prompt, recover_last_session=True)

        self.assertEqual(restored.memory[0]["content"], self.system_prompt)
        self.assertEqual(restored.memory[1]["content"], "Recovered summary")
        self.assertTrue(restored.session_recovered)

if __name__ == '__main__':
    unittest.main()
