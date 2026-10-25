# base32_geohash_py

Encode and decode geographic coordinates using the Base32 geohash alphabet — a 32-character variant (digits 0-9 plus lowercase consonants, with the vowels a, i, l, o removed) that is not RFC 4648 base32.

```python
from base32_geohash_py import encode, decode, encode_pair, decode_pair, BASE32

h = encode(48.8566, 2.3522, precision=8)   # -> 'u09tunqj'
(lat, lon), (lat_err, lon_err, lat_bits) = decode(h)

low, high = encode_pair(48.8566, 2.3522, precision=8)
```

## Why this exists

Geohashing is a standard way to bucket lat/lon pairs into string cells for spatial indexing and prefix matching. The alphabet is fixed by convention, so the value of a small library is correctness on the awkward edges, not novelty.

The main trade-off: this library normalises the removed vowels `a`, `i`, `l`, `o` on decode (mapping them to `s`, `t`, `u`, `v` respectively) so that user-typed input survives common typos. This means `decode("a")` and `decode("s")` return the same cell. If you need strict rejection of non-alphabet characters, validate the string against `BASE32` before calling `decode`.

## Edge cases you will hit

- `decode` accepts uppercase and the four removed vowels; `encode` always emits lowercase canonical characters.
- Precision is capped at 12 characters. Beyond that, the longitude cell width drops below ~1 cm and double precision stops being meaningful.
- The poles (lat ±90) and the antimeridian (lon ±180) are valid inputs; cells touching them have asymmetric error bounds.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

