# Vedic Date Encoder/Decoder

This module provides functions for encoding and decoding Vedic dates into a compact string representation. It supports various eras, year numbering schemes, and lunar/solar month calculations.

## Features

*   **Date Encoding:** Encodes Vedic dates, including era, year, month (Sayana, Nirayana, Chandramana), Tithi, and Nakshatra, into a single string.
*   **Date Parsing:** Parses the encoded date string back into its individual components.
*   **Era Support:** Supports multiple eras including Kali, Shaka, Vikrama, and Kollam.
*   **Flexible Input:** Accepts None values for optional date components, allowing for partial date encoding/decoding.
*   **Error Handling:** Includes error checks for incompatible month combinations and impossible date scenarios.

## Usage

### Encoding a Date

```python
import hindudate

encoded_date = hindudate.encode_date(
era='kali',
year_num=5125,
sayana=2,
nirayana=10,
candramana=11,
tithi=5,
nakshatra=2
)
print(encoded_date)
```

### Parsing a Date

```python
encoded_date = "0000000101000000010110010100101110111000101101"
(
era,
year_num,
year_name,
sayana,
nirayana,
candramana,
sak,
tithi,
nakshatra,
) = hindudate.parse_date(encoded_date)

print("Era:", era)
print("Year Number:", year_num)
print("Sayana Masa:", sayana)
print("Nirayana Masa:", nirayana)
print("Candramana Masa:", nirayana)
print("Tithi:", tithi)
print("Nakshatra:", nakshatra)
```

## Functions

### `encode_date(era=None, year_num=None, year_name=None, sayana=None, nirayana=None, candramana=None, sak=0, tithi=None, nakshatra=None)`

Encodes a complete date into a string representation.

**Parameters:**

*   `era` (str, optional): The era of the year. Defaults to None.
*   `year_num` (int, optional): The year number. Defaults to None.
*   `year_name` (int, optional): The year name. Defaults to None.
*   `sayana` (int, optional): The Sayana month. Defaults to None.
*   `nirayana` (int, optional): The Nirayana month. Defaults to None.
*   `candramana` (int, optional): The Chandramana month. Defaults to None.
*   `sak` (int, optional): The Sak number. Defaults to 0.
*   `tithi` (int, optional): The Tithi. Defaults to None.
*   `nakshatra` (int, optional): The Nakshatra. Defaults to None.

**Returns:**

*   `str`: The encoded date string.

### `parse_date(val)`

Parses an encoded date string.

**Parameters:**

*   `val` (str): The encoded date string.

**Returns:**

*   `tuple`: A tuple containing the parsed era, year number, year name, Sayana month, Nirayana month, Chandramana month, Sak number, Tithi, and Nakshatra.

## Error Handling

The module raises `Exception` in the following cases:

*   `Incompatible months`: When the combination of Sayana, Nirayana, and Chandramana months is logically inconsistent.
*   `Impossible Date: Nakshatra, Tithi, Nirayana Sauramana Masa combination impossible`: When the provided Nakshatra, Tithi, and Nirayana month cannot form a valid date.
*   `Invalid date. Cannot forward/reverse Sankranti.`: During month calculations when Sankranti adjustments are not possible due to invalid input dates.

## Dependencies

*   `numpy`: Used for binary representation of numbers.



