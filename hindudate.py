# Version 1.2.1
# Some code beautification + docstrings

import numpy as np

TTH_DEG = 12.0
NAK_DEG = 40/3
RAS_DEG = 30.0

ERA_DICT = {
    'kali' : 0,
    'shaka' : 1,
    'vikrama' : 2,
    'vikrama-gujarat' : 3,
    'kollam' : 4,
    None: 31
}

NULL_NAK_CODE = 7
NULL_SAYANA = 12

CM_CODE_COUNT = 11
NIRCM_COUNT = 132
MAX_NAK_CODE = 6

def encode_date(era=None, year_num=None, year_name=None, sayana=None, nirayana=None, candramana=None, sak=0, tithi=None, nakshatra=None):
    """Encodes a date into a single string representation.

    Combines the encoded year and the encoded date within the year.

    Args:
        era (str, optional): The era of the year. Defaults to None.
        year_num (int, optional): The year number. Defaults to None.
        year_name (int, optional): The year name. Defaults to None.
        sayana (int, optional): The Sayana Sauramana month. Defaults to None.
        nirayana (int, optional): The Nirayana Sauramana month. Defaults to None.
        candramana (int, optional): The Chandramana month. Defaults to None.
        sak (int, optional): Samanya (0), Adhika (1), or Kshaya (2). Defaults to Samanya (0).
        tithi (int, optional): The Tithi. Defaults to None.
        nakshatra (int, optional): The Nakshatra. Defaults to None.

    Returns:
        str: The encoded date as a binary string.
    """

    return encode_year(era, year_num, year_name) + encode_date_in_year(sayana, nirayana, candramana, sak, tithi, nakshatra)

def parse_date(val):
    """Parses an encoded date binary string into its constituent parts.

    Splits the input string into year and date components and then parses each separately.

    Args:
        val (str): The encoded date string.

    Returns:
        tuple: A tuple containing the parsed era, year number, year name, Sayana month, Nirayana month,
               Chandramana month, SAK, Tithi, and Nakshatra.
    """
    yrCode = val[:26]
    dateCode = val[26:]
    
    era, year_num, year_name = parse_year(yrCode)
    sayana, nirayana, candramana, sak, tithi, nakshatra = parse_date_in_year(dateCode)

    return era, year_num, year_name, sayana, nirayana, candramana, sak, tithi, nakshatra


def encode_year(era=None, year_num=None, year_name=None):
    """Encodes the year components into a binary string.

    Encodes the era, year number, and year name into a single binary string.

    Args:
        era (str, optional): The era. Defaults to None.
        year_num (int, optional): The year number. Defaults to None.
        year_name (int, optional): The year name. Defaults to None.

    Returns:
        str: The encoded year string.
    """
    era_str = np.binary_repr(eraToCode(era), 5)

    if year_num is None:
        yrnum = np.binary_repr(2^15-1, 15)
    else:
        yrnum = np.binary_repr(year_num, 15)
    
    if year_name is None:
        yrname = "111111"
    else: yrname = np.binary_repr(year_name, 6)

    return era_str + yrnum + yrname

def eraToCode(era = None):
    """Converts an era string to its corresponding code.

    Args:
        era (str, optional): The era string. Defaults to None.

    Returns:
        int: The era code.
    """
    return ERA_DICT[era]

def codeToEra(code):
    """Converts an era code to its corresponding string.

    Args:
        code (int): The era code.

    Returns:
        str: The era string.
    """
    return next((k for k, v in ERA_DICT.items() if v == code), None)

def parse_year(val):
    """Parses an encoded year binary string into its constituent parts.

    Args:
        val (str): The encoded year string.

    Returns:
        tuple: A tuple containing the parsed era, year number, and year name.
    """
    eraCode = int(val[:5],2)
    yrnum = int(val[5:20],2)
    yrname = int(val[20:],2)

    era = codeToEra(eraCode)
    if yrnum == 2^15-1:
        year_num = None
    else:
        year_num = yrnum

    if yrname > 59:
        year_name = None
    else:
        year_name = yrname
    
    return era, year_num, year_name


def encode_date_in_year(sayana=None, nirayana=None, candramana=None, sak=0, tithi=None, nakshatra=None):
    """Encodes the date within a year into a single string representation.

    Handles different combinations of input parameters to encode the date appropriately.

    Args:
        sayana (int, optional): The Sayana month. Defaults to None.
        nirayana (int, optional): The Nirayana month. Defaults to None.
        candramana (int, optional): The Chandramana month. Defaults to None.
        sak (int, optional): Samanya (0), Adhika (1), or Kshaya (2). Defaults to Samanya (0).
        tithi (int, optional): The Tithi. Defaults to None.
        nakshatra (int, optional): The Nakshatra. Defaults to None.

    Returns:
        str: The encoded date string.
    """

    month_dec = encode_month(sayana,nirayana,candramana,sak)
        
    if nakshatra is None:
        # append tithi value (if present), tithi null (otherwise), and nakshatra null
        if tithi is None:
            tithi_dec = 31
        else:
            tithi_dec = tithi
        tithi_dec = tithi_dec * 8
        tithi_dec += NULL_NAK_CODE
        
        return month_tithi(month_dec, tithi_dec, tithi is None)
    
    if tithi is None:
        # tithi null marker + calced tithi + nakshatra code
        if nirayana is None:
            nirVal = getNirVal(month_dec)
        else: nirVal = nirayana
        tithi_dec = nirayana_nakshatra(nirVal, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi is None)
        
    if nirayana is not None:
        # tithi not null, tithi, nakshatra code
        tithi_dec = normal_tithi(nirayana, tithi, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi is None)

    if candramana is None:
        # Nirayana null, candramana also null
        # calculate nirayana from tithi + nakshatra
        nir = raviFromTN(tithi,nakshatra)
        month_dec += 11*(nir - getNirVal(month_dec))
        tithi_dec = normal_tithi(nir, tithi, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi is None)
    
    if candramana is not None:
        # Nirayana null, candramana present, dummy nirayana
        nirVal = getNirVal(month_dec)
        nirDiff = checkNir(nirVal,tithi,nakshatra)
        nir = nirVal
        
        if nirDiff == 1:
            month_dec = sankranti_add(month_dec)
            nir = nirVal + 1
        elif nirDiff == -1:
            month_dec = sankranti_minus(month_dec)
            nir = nirVal - 1            
        
        tithi_dec = normal_tithi(nir, tithi, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi is None)
    
def parse_date_in_year(val):
    """Parses the date within a year from an encoded string.

    Args:
        val (str): The encoded date string.

    Returns:
        tuple: A tuple containing the parsed Sayana month, Nirayana month, Chandramana month, SAK number,
               Tithi, and Nakshatra.
    """
    month_dec = int(val[:11],2)
    tithi_null = bool(int(val[11],2))
    tithi_dec = int(val[12:17],2)
    nkcode = int(val[17:],2)
        
    sayana, nirayana, candramana, sak = parse_months(month_dec)
    nir = getNirVal(month_dec)
    if nkcode == 7:
        nakshatra = None
    else:
        nakshatra = (nkcode + getStar1(nir,tithi_dec)) % 27
    if tithi_null:
        tithi = None
    else:
        tithi = tithi_dec
    
    return sayana, nirayana, candramana, sak, tithi, nakshatra
    
def encode_month(sayana=None, nirayana=None, candramana=None, sak=0):
    """Encodes month-related data into a decimal representation.

    Combines Sayana, Nirayana, Chandramana months, and SAK number into a single decimal.

    Args:
        sayana (int, optional): The Sayana month. Defaults to None.
        nirayana (int, optional): The Nirayana month. Defaults to None.
        candramana (int, optional): The Chandramana month. Defaults to None.
        sak (int, optional): The SAK number. Defaults to 0.

    Returns:
        int: The encoded month decimal.
    """
    if sayana is None:
        sayana = NULL_SAYANA
    
    # Instantiate decimal variable with sayana masa encoding
    decimal = sayana * NIRCM_COUNT
    
    if nirayana is not None:
        # Incorporate nirayana masa if given
        decimal += nirayana * CM_CODE_COUNT
        if candramana is None:
            # if CM null, option 0 below and return
            return decimal
        
    """
    0 - CM null
    1 - normal CM - pre-Sankranti
    2 - adhika CM
    3 - kshaya CM - pre-Sankrantis
    4 - normal CM - post-Sankranti
    5 - kshaya CM - inter-Sankranti
    6 - kshaya CM - post-Sankrantis
    7 - normal - Nirayana null
    8 - adhika - Nirayana null
    9 - kshaya - Nirayana null
    10 - Both null
    """    
    if nirayana is None:
        if candramana is None:
            # if both null, select the 10th option
            decimal += 10
        else: 
            # DUMMY NIRAYANA VAL SET HERE
            # if only nirayana null, set nirayana to prev month as dummy and mark option 7-9
            decimal += sak + 7
            decimal += ((candramana - 1) % 12) * CM_CODE_COUNT
    else:
        diff = (nirayana - candramana) % 12
        
        if diff == 11:
            # NA is prev to CM, (eg. Mesha-Vaisakha); option 1-3
            decimal += 1 + sak
            #print(1+sak)
        elif sak == 1:
            # Above should cover all adhika masas. Remaining are erroneous.
            raise Exception("Incompatible months. Adhika Masa error.")
        elif diff == 0:
            # NA is aligned with CM, (eg. Mesha-Caitra); option 4-5
            decimal += 4 
            if sak == 2:
                decimal += 1
            #print("4/5")
        elif diff == 1:
            # NA after CM, (eg. Mesha-Phalguna)
            # Must be kshaya masa
            if sak == 2:
                decimal += 6
                #print("6")
            else:
                # If diff = 1 and not kshaya masa, erroneous
                raise Exception("Incompatible months.")
        else:
            # if diff not in [11,0,1], then erroneous
            raise Exception("Incompatible months.")
    
    return decimal 

def parse_months(dec):
    """Parses an encoded month decimal into its constituent parts.

    Args:
        dec (int): The encoded month decimal.

    Returns:
        tuple: A tuple containing the parsed Sayana month, Nirayana month, Chandramana month, and SAK number.
    """
    
    # extract sayana value
    sacode = dec // NIRCM_COUNT
    dec = dec % NIRCM_COUNT
    
    # extract nirayana value
    nacode = dec // CM_CODE_COUNT
    
    # extract candramana encoding
    cmcode = dec % CM_CODE_COUNT
    
    #print(sacode,nacode,cmcode)
    
    if sacode == NULL_SAYANA:
        # capture null val
        sayana = None
    else:
        # assign correct val
        sayana = sacode
        
    if cmcode > 6:
        # catch null nirayana
        nirayana = None
    else: 
        # assign correct val
        nirayana = nacode
        
    if cmcode == 0 or cmcode == 10:
        # catch null candramana
        candramana = None
        sak = 0
    elif cmcode < 4:
        # NA prev to CM
        candramana = (nacode + 1) % 12
        sak = cmcode - 1
    elif cmcode < 6:
        # NA aligned with CM
        candramana = nacode
        sak = (cmcode - 4) * 2
    elif cmcode == 6:
        # kshaya masa, NA ahead of CM
        candramana = (nacode - 1) % 12
        sak = 2
    elif cmcode > 6:
        # null nirayana
        candramana = (nacode + 1) % 12
        sak = cmcode - 7
        
    return sayana, nirayana, candramana, sak

def nirayana_nakshatra(nirayana,nakshatra):
    """Calculates a placeholder Tithi, then a Tithi + Nakshatra decimal based on Nirayana and Nakshatra.

    Args:
        nirayana (int): The Nirayana month.
        nakshatra (int): The Nakshatra.

    Returns:
        int: The calculated Tithi decimal.
    """
    # calced tithi + nakshatra 
    tithi_dec = (((NAK_DEG*nakshatra - RAS_DEG*nirayana) % 360) // TTH_DEG) + 1
    tithi_dec = int(tithi_dec) * 8 + 2
    return tithi_dec

def normal_tithi(nirayana,tithi,nakshatra):
    """Calculates a Tithi decimal when all inputs are non-null.

    Args:
        nirayana (int): The Nirayana month.
        tithi (int): The Tithi.
        nakshatra (int): The Nakshatra.

    Returns:
        int: The calculated Tithi decimal.
    """
    # none of inputs are null
    # tithi + nakshatra code
    nkcode = getNKCode(nirayana,tithi,nakshatra)
    tithi_dec = tithi * 8 + nkcode
    return tithi_dec

def getStar1(nirayana,tithi):
    """Returns the first Nakshatra in the encoding for a given Nirayana month and Tithi combination.
    There can be at max 4 (usually 3) nakshatras for a given rashi-tithi combination.
    7 spots are alloted in the encoding, starting from two before the first of the 3 or 4 above

    Args:
        nirayana (int): The Nirayana month.
        tithi (int): The Tithi.

    Returns:
        int: The first Nakshatra in the encoding.
    """
    star1 = (((RAS_DEG*nirayana + TTH_DEG*tithi) // NAK_DEG) - 2) % 27
    return int(star1)

def getNKCode(nirayana,tithi,nakshatra):
    """Calculates the Nakshatra code.

    Args:
        nirayana (int): The Nirayana month.
        tithi (int): The Tithi.
        nakshatra (int): The Nakshatra.

    Returns:
        int: The Nakshatra code.

    Raises:
        Exception: If the Nakshatra, Tithi, and Nirayana Sauramana Masa combination is impossible.
    """
    nkcode = (nakshatra - getStar1(nirayana,tithi)) % 27
    if nkcode > MAX_NAK_CODE:
        raise Exception("Imppossible Date: Nakshatra, Tithi, Nirayana Sauramana Masa combination impossible")
    return int(nkcode)

def raviFromTN(tithi,nakshatra):
    """Calculates a possible rashi of the Sun from Tithi and Nakshatra.

    Args:
        tithi (int): The Tithi.
        nakshatra (int): The Nakshatra.

    Returns:
        int: The rashi of the Sun.
    """
    return ((NAK_DEG*nakshatra - TTH_DEG*tithi) % 360) // RAS_DEG  

def sankranti_add(month_dec):
    """Adjusts the month decimal by adding a Sankranti, while staying in same Candramana month.

    Args:
        month_dec (int): The month decimal.

    Returns:
        int: The adjusted month decimal.

    Raises:
        Exception: If the date is invalid and Sankranti cannot be forwarded.
    """
    cmcode = month_dec % 11
    if cmcode not in [1,3,5]:
        raise Exception("Invalid date. Cannot forward Sankranti.")
    
    month_dec += (cmcode - 1) / 2 + 4 - cmcode
    return int(month_dec)

def sankranti_minus(month_dec):
    """Adjusts the month decimal by subtracting a Sankranti.

    Args:
        month_dec (int): The month decimal.

    Returns:
        int: The adjusted month decimal.

    Raises:
        Exception: If the date is invalid and Sankranti cannot be reversed.
    """
    cmcode = month_dec % 11
    if cmcode not in [4,5,6]:
        raise Exception("Invalid date. Cannot reverse Sankranti.")
    
    month_dec += (cmcode - 4) * 2 + 1 - cmcode
    return int(month_dec)
    
def getNirVal(month_dec):
    """Extracts the Nirayana value from the month decimal.

    Args:
        month_dec (int): The month decimal.

    Returns:
        int: The Nirayana value.
    """
    return (month_dec % NIRCM_COUNT) // CM_CODE_COUNT

def checkNir(nirayana,tithi,nakshatra):
    """Checks the Nirayana value based on Tithi and Nakshatra.

    Args:
        nirayana (int): The Nirayana month.
        tithi (int): The Tithi.
        nakshatra (int): The Nakshatra.

    Returns:
        int: An indicator of the Nirayana adjustment (-1, 0, or 1).

    Raises:
        Exception: If the date is impossible.
    """
    nkcode = (nakshatra - getStar1(nirayana,tithi)) % 27
    if nkcode > 20:
        nkcode = (nakshatra - getStar1((nirayana - 1) % 12,tithi)) % 27
        if nkcode <= MAX_NAK_CODE:
             return -1
    elif nkcode > MAX_NAK_CODE:
        nkcode = (nakshatra - getStar1((nirayana + 1) % 12,tithi)) % 27
        if nkcode <= MAX_NAK_CODE:
             return 1
    elif nkcode <= MAX_NAK_CODE:
        return 0
    else:
        raise Exception("Impossible date") 
    
def month_tithi(month_dec, tithi_dec, tithi_null):
    """Combines the month and Tithi decimals into a single binary string.

    Args:
        month_dec (int): The month decimal.
        tithi_dec (int): The Tithi decimal.
        tithi_null (bool): Indicates if the Tithi is null.

    Returns:
        str: The combined binary string.
    """
    return np.binary_repr(month_dec, 11) + str(int(tithi_null)) + np.binary_repr(tithi_dec,8)
    

