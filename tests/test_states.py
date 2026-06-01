import unittest

from ev_pipeline.states import normalize_state_name, normalize_text_key


class TestStates(unittest.TestCase):
    def test_normalize_text_key_removes_accents_and_symbols(self) -> None:
        self.assertEqual(normalize_text_key("Sao-Paulo 123"), "saopaulo123")
        self.assertEqual(normalize_text_key("Rio de Janeiro"), "riodejaneiro")

    def test_normalize_state_name_maps_known_aliases(self) -> None:
        self.assertEqual(normalize_state_name("SP"), "Sao Paulo")
        self.assertEqual(normalize_state_name("sao paulo"), "Sao Paulo")
        self.assertEqual(normalize_state_name("toodejaneiro"), "Rio de Janeiro")

    def test_normalize_state_name_handles_missing_and_unknown_values(self) -> None:
        self.assertEqual(normalize_state_name(None), "Nao informado")
        self.assertEqual(normalize_state_name(""), "Nao informado")
        self.assertEqual(normalize_state_name("novo estado"), "Novo Estado")


if __name__ == "__main__":
    unittest.main()
