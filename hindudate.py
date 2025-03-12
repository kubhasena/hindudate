# Version 1.2.0
# Added support for era, year, and year name (prabhavadi)

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

def encode_date(era=None, year_num=None, year_name=None, sayana=None, nirayana=None, candramana=None, sak=0, tithi=None, nakshatra=None):

    return encode_year(era, year_num, year_name) + encode_date_in_year(sayana, nirayana, candramana, sak, tithi, nakshatra)

def parse_date(val):
    yrCode = val[:26]
    dateCode = val[26:]
    
    era, year_num, year_name = parse_year(yrCode)
    sayana, nirayana, candramana, sak, tithi, nakshatra = parse_date_in_year(dateCode)

    return era, year_num, year_name, sayana, nirayana, candramana, sak, tithi, nakshatra


def encode_year(era=None, year_num=None, year_name=None):
    era_str = np.binary_repr(eraToCode(era), 5)

    if year_num == None:
        yrnum = np.binary_repr(2^15-1, 15)
    else:
        yrnum = np.binary_repr(year_num, 15)
    
    if year_name == None:
        yrname = "111111"
    else: yrname = np.binary_repr(year_name, 6)

    return era_str + yrnum + yrname

def eraToCode(era = None):
    return ERA_DICT[era]

def codeToEra(code):
    return next((k for k, v in ERA_DICT.items() if v == code), None)

def parse_year(val):
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
    
    month_dec = encode_month(sayana,nirayana,candramana,sak)
        
    if nakshatra == None:
        # append tithi value (if present), tithi null (otherwise), and nakshatra null
        if tithi == None:
            tithi_dec = 31
        else:
            tithi_dec = tithi
        tithi_dec = tithi_dec * 8
        tithi_dec += 7
        
        return month_tithi(month_dec, tithi_dec, tithi == None)
    
    if tithi == None:
        # tithi null marker + calced tithi + nakshatra code
        if nirayana == None:
            nirVal = getNirVal(month_dec)
        else: nirVal = nirayana
        tithi_dec = nirayana_nakshatra(nirVal, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi == None)
        
    if nirayana != None:
        # tithi not null, tithi, nakshatra code
        tithi_dec = normal_tithi(nirayana, tithi, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi == None)

    if candramana == None:
        # Nirayana null, candramana also null
        # calculate nirayana from tithi + nakshatra
        nir = raviFromTN(tithi,nakshatra)
        month_dec += 11*(nir - getNirVal(month_dec))
        tithi_dec = normal_tithi(nir, tithi, nakshatra)
        
        return month_tithi(month_dec, tithi_dec, tithi == None)
    
    if candramana != None:
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
        
        return month_tithi(month_dec, tithi_dec, tithi == None)
    
def parse_date_in_year(val):
    month_dec = int(val[:11],2)
    tithi_null = bool(int(val[11],2))
    tithi_dec = int(val[12:17],2)
    nkcode = int(val[17:],2)
    
    #print(month_dec,tithi_null,tithi_dec,nkcode)
    
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
    if sayana == None:
        sayana = 12
    
    # Instantiate decimal variable with sayana masa encoding
    decimal = sayana * 132
    
    if nirayana != None:
        # Incorporate nirayana masa if given
        decimal += nirayana * 11
        if candramana == None:
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
    if nirayana == None:
        if candramana == None:
            # if both null, select the 10th option
            decimal += 10
        else: 
            # DUMMY NIRAYANA VAL SET HERE
            # if only nirayana null, set nirayana to prev month as dummy and mark option 7-9
            decimal += sak + 7
            decimal += ((candramana - 1) % 12) * 11
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
    
    # extract sayana value
    sacode = dec // 132
    dec = dec % 132
    
    # extract nirayana value
    nacode = dec // 11
    
    # extract candramana encoding
    cmcode = dec % 11
    
    #print(sacode,nacode,cmcode)
    
    if sacode == 12:
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
    # tithi null marker + calced tithi + nakshatra 
    tithi_dec = (((NAK_DEG*nakshatra - RAS_DEG*nirayana) % 360) // TTH_DEG) + 1
    tithi_dec = int(tithi_dec) * 8 + 2
    return tithi_dec

def normal_tithi(nirayana,tithi,nakshatra):
    # none of inputs are null
    # tithi + nakshatra code
    nkcode = getNKCode(nirayana,tithi,nakshatra)
    tithi_dec = tithi * 8 + nkcode
    return tithi_dec

def getStar1(nirayana,tithi):
    # returns the first nakshatra in encoding for a given nirayana masa and tithi combo
    # There can be at max 4 (usually 3) nakshatras for a given rashi-tithi combo
    # 7 spots are alloted in the encoding, starting from two before the first of the 3 or 4 above
    star1 = (((RAS_DEG*nirayana + TTH_DEG*tithi) // NAK_DEG) - 2) % 27
    return int(star1)

def getNKCode(nirayana,tithi,nakshatra):
    nkcode = (nakshatra - getStar1(nirayana,tithi)) % 27
    if nkcode > 6:
        raise Exception("Imppossible Date: Nakshatra, Tithi, Nirayana Sauramana Masa combination impossible")
    return int(nkcode)

def raviFromTN(tithi,nakshatra):
    return ((NAK_DEG*nakshatra - TTH_DEG*tithi) % 360) // RAS_DEG  

def sankranti_add(month_dec):
    cmcode = month_dec % 11
    if cmcode not in [1,3,5]:
        raise Exception("Invalid date. Cannot forward Sankranti.")
    
    month_dec += (cmcode - 1) / 2 + 4 - cmcode
    return int(month_dec)

def sankranti_minus(month_dec):
    cmcode = month_dec % 11
    if cmcode not in [4,5,6]:
        raise Exception("Invalid date. Cannot reverse Sankranti.")
    
    month_dec += (cmcode - 4) * 2 + 1 - cmcode
    return int(month_dec)
    
def getNirVal(month_dec):
    return (month_dec % 132) // 11

def checkNir(nirayana,tithi,nakshatra):
    nkcode = (nakshatra - getStar1(nirayana,tithi)) % 27
    if nkcode > 20:
        nkcode = (nakshatra - getStar1((nirayana - 1) % 12,tithi)) % 27
        if nkcode <= 6:
             return -1
    elif nkcode > 6:
        nkcode = (nakshatra - getStar1((nirayana + 1) % 12,tithi)) % 27
        if nkcode <= 6:
             return 1
    elif nkcode <= 6:
        return 0
    else:
        raise Exception("Impossible date") 
    
def month_tithi(month_dec, tithi_dec, tithi_null):
    return np.binary_repr(month_dec, 11) + str(int(tithi_null)) + np.binary_repr(tithi_dec,8)
    

