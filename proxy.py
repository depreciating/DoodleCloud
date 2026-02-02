import random
import uuid

APP_ID = "936619743392459"

def get_random_resolution():
    resolutions = [
        ("1080x2161", "480"), ("1080x2158", "420"), ("1080x2290", "440"),
        ("1080x2264", "400"), ("1080x2340", "480"), ("1320x2400", "560"),
        ("1440x2768", "560"), ("1440x2368", "560"), ("1080x2400", "440"),
        ("720x1600", "320"), ("1440x3200", "560"), ("1080x1920", "480")
    ]
    return random.choice(resolutions)

def get_modern_version():
    major = random.randint(270, 316)
    minor = random.randint(0, 5)
    patch = random.randint(0, 5)
    build = random.randint(10, 50)
    code = random.randint(100, 300)
    return f"{major}.{minor}.{patch}.{build}.{code}"

def get_modern_android():
    versions = [
        "28/9", "29/10", "30/11", "31/12", "33/13", "34/14"
    ]
    return random.choice(versions)

def ua_samsung(ver, andro, res, dpi):
    models = [
        "SM-G991B; o1s; samsungexynos2100",  
        "SM-G998B; p3s; samsungexynos2100",  
        "SM-S901B; r0s; samsungexynos2200",  
        "SM-S908B; b0s; samsungexynos2200",  
        "SM-A528B; a52s; qcom",               
        "SM-A536B; a53x; samsungexynos1280",  
        "SM-G973F; beyond1; samsungexynos9820", 
        "SM-N986B; c2s; samsungexynos990",    
    ]
    model_str = random.choice(models)
    model, device, cpu = model_str.split("; ")
    return f"Instagram {ver} Android ({andro}; {dpi}dpi; {res}; samsung; {model}; {device}; {cpu}; en_US)"

def ua_xiaomi(ver, andro, res, dpi):
    models = [
        "Redmi Note 10 Pro; sweet; qcom",
        "M2102J20SG; vayu; qcom", 
        "M2012K11AG; alioth; qcom", 
        "21081111RG; xiaomi 11t; mt6893",
        "2201117TY; spes; qcom", 
        "M2007J20CG; surya; qcom", 
    ]
    model_str = random.choice(models)
    model, device, cpu = model_str.split("; ")
    return f"Instagram {ver} Android ({andro}; {dpi}dpi; {res}; Xiaomi; {model}; {device}; {cpu}; en_US)"

def ua_realme(ver, andro, res, dpi):
    models = [
        "RMX3363; RE54ABL1; qcom", 
        "RMX3081; RMX3081L1; qcom", 
        "RMX3393; RMX3393; mt6893", 
        "RMX2001; RMX2001; mt6785", 
        "RMX1931; RMX1931; qcom", 
    ]
    model_str = random.choice(models)
    model, device, cpu = model_str.split("; ")
    return f"Instagram {ver} Android ({andro}; {dpi}dpi; {res}; realme; {model}; {device}; {cpu}; en_US)"

def ua_oppo(ver, andro, res, dpi):
    models = [
        "CPH2145; OP4F2CL1; qcom", 
        "CPH2247; OP515BL1; mt6877", 
        "CPH2023; OP4C2DL1; mt6779", 
        "CPH2357; OP56E8L1; qcom", 
    ]
    model_str = random.choice(models)
    model, device, cpu = model_str.split("; ")
    return f"Instagram {ver} Android ({andro}; {dpi}dpi; {res}; OPPO; {model}; {device}; {cpu}; en_US)"

def ua_vivo(ver, andro, res, dpi):
    models = [
        "V2109; 2109; mt6833", 
        "V2050; 2050; qcom", 
        "V2025; 2025; qcom", 
        "V2130; 2130; mt6893", 
    ]
    model_str = random.choice(models)
    model, device, cpu = model_str.split("; ")
    return f"Instagram {ver} Android ({andro}; {dpi}dpi; {res}; vivo; {model}; {device}; {cpu}; en_US)"

def get_random_user_agent():
    res_pair = get_random_resolution()
    res, dpi = res_pair
    ver = get_modern_version()
    andro = get_modern_android()
    
    generators = [ua_samsung, ua_xiaomi, ua_realme, ua_oppo, ua_vivo]
    selected_gen = random.choice(generators)
    
    return selected_gen(ver, andro, res, dpi)

def get_device_headers():
    return {
        "User-Agent": get_random_user_agent(),
        "x-ig-app-id": APP_ID,
        "x-ig-device-id": str(uuid.uuid4()),
    }

if __name__ == "__main__":
    print(get_random_user_agent())