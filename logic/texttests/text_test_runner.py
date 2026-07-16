import os
from texttests.script_parser import ScriptParser
from texttests.script_runner import ScriptRunner
from utils import safe_join


class TextTestRunner:
    """Discovers all .txt test files in a folder, runs each through the real system,
    compares actual output to expected, and reports pass/fail results."""

    def run_all(self, folder: str) -> None:
        test_files = sorted(
            f for f in os.listdir(folder) if f.endswith(".txt")
        )

        passed = 0
        failed = 0

        print("Running text tests...\n")

        for filename in test_files:
            path = safe_join(folder, filename)
            result = self._run_file(filename, path)
            if result:
                passed += 1
            else:
                failed += 1

        print("-" * 32)
        print(f"Tests:  {passed + failed}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")

    def _run_file(self, filename: str, path: str) -> bool:
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()

        board_lines, command_lines, expected = ScriptParser().parse(lines)

        collected = []
        ScriptRunner().run(board_lines, command_lines, output=collected.append)
        actual = "\n".join(collected)

        if actual == expected:
            print(f"[PASS] {filename}")
            return True

        print(f"[FAIL] {filename}")
        print(f"\nExpected:\n{expected}")
        print(f"\nActual:\n{actual}\n")
        return False
