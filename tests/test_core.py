import math
import unittest

from base32_geohash_py.core import (
    BASE32,
    BASE32_MAP,
    decode,
    decode_pair,
    encode,
    encode_pair,
)


class TestAlphabet(unittest.TestCase):
    def test_alphabet_is_32_chars(self):
        self.assertEqual(len(BASE32), 32)

    def test_alphabet_excludes_removed_vowels(self):
        for excluded in "ailoAIO":
            self.assertNotIn(excluded, BASE32)

    def test_map_covers_alphabet(self):
        self.assertEqual(set(BASE32_MAP.keys()), set(BASE32))
        self.assertEqual(set(BASE32_MAP.values()), set(range(32)))


class TestEncode(unittest.TestCase):
    def test_known_value_d4r2(self):
        # 57.64911, 10.40744 -> 'u4pruyd' is the canonical example
        # from the geohash reference; we use a shorter, hand-checked one.
        self.assertEqual(encode(42.6, -5.6, 6), "ezs42e")

    def test_origin(self):
        self.assertEqual(encode(0.0, 0.0, 1), "s")

    def test_north_pole(self):
        self.assertEqual(encode(90.0, 0.0, 1), "u")

    def test_south_pole(self):
        self.assertEqual(encode(-90.0, 0.0, 1), "h")

    def test_precision_one(self):
        self.assertEqual(len(encode(0, 0, 1)), 1)

    def test_default_precision_is_eleven(self):
        self.assertEqual(len(encode(0, 0)), 11)

    def test_latitude_out_of_range(self):
        with self.assertRaises(ValueError):
            encode(90.001, 0)

    def test_longitude_out_of_range(self):
        with self.assertRaises(ValueError):
            encode(0, 180.001)

    def test_precision_zero_rejected(self):
        with self.assertRaises(ValueError):
            encode(0, 0, 0)

    def test_precision_too_large_rejected(self):
        with self.assertRaises(ValueError):
            encode(0, 0, 13)


class TestDecode(unittest.TestCase):
    def test_decode_returns_tuple_of_tuples(self):
        result = decode("ezs42d")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], tuple)
        self.assertIsInstance(result[1], tuple)

    def test_decode_recovers_origin(self):
        (lat, lon), _ = decode("s")
        self.assertAlmostEqual(lat, 22.5)
        self.assertAlmostEqual(lon, 22.5)

    def test_decode_known_value(self):
        (lat, lon), _ = decode("ezs42d")
        self.assertAlmostEqual(lat, 42.6, places=1)
        self.assertAlmostEqual(lon, -5.6, places=1)

    def test_decode_error_bounds_positive(self):
        _, (le, we, _) = decode("ezs42d")
        self.assertGreater(le, 0)
        self.assertGreater(we, 0)

    def test_lat_bits_reported(self):
        _, (_, _, lat_bits) = decode("s")  # 1 char = 5 bits, lon first
        self.assertEqual(lat_bits, 2)

    def test_empty_geohash_rejected(self):
        with self.assertRaises(ValueError):
            decode("")

    def test_invalid_char_rejected(self):
        with self.assertRaises(ValueError):
            decode("ezs42!")

    def test_uppercase_decoded(self):
        lower = decode("ezs42d")[0]
        upper = decode("EZS42D")[0]
        self.assertAlmostEqual(lower[0], upper[0])
        self.assertAlmostEqual(lower[1], upper[1])

    def test_vowel_normalisation_a_to_s(self):
        # 'a' is not in the alphabet; it should normalise to 's'.
        real = decode("szs42d")[0]
        norm = decode("azs42d")[0]
        self.assertAlmostEqual(real[0], norm[0])
        self.assertAlmostEqual(real[1], norm[1])


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_preserves_point_within_cell(self):
        for lat, lon, prec in [
            (48.8566, 2.3522, 8),
            (-33.8688, 151.2093, 8),
            (40.7128, -74.0060, 8),
            (0.0, 0.0, 6),
            (-1.0, -179.5, 7),
        ]:
            with self.subTest(lat=lat, lon=lon, prec=prec):
                h = encode(lat, lon, prec)
                (dlat, dlon), (le, we, _) = decode(h)
                self.assertLessEqual(abs(dlat - lat), le + 1e-9)
                self.assertLessEqual(abs(dlon - lon), we + 1e-9)


class TestPair(unittest.TestCase):
    def test_pair_strings_differ(self):
        low, high = encode_pair(48.8566, 2.3522, 6)
        self.assertNotEqual(low, high)

    def test_pair_high_is_east_neighbour(self):
        from base32_geohash_py.core import _east_neighbour
        low, high = encode_pair(0, 0, 6)
        self.assertEqual(high, _east_neighbour(low))

    def test_decode_pair_rejects_mismatched_high(self):
        with self.assertRaises(ValueError):
            decode_pair("ezs42d", "zzzzzz")

    def test_decode_pair_accepts_genuine_pair(self):
        low, high = encode_pair(42.6, -5.6, 6)
        (lat, lon), _ = decode_pair(low, high)
        self.assertAlmostEqual(lat, 42.6, places=1)
        self.assertAlmostEqual(lon, -5.6, places=1)


if __name__ == "__main__":
    unittest.main()
