import json
import argparse
import os
from pathlib import Path

input = {}

mythicConfig = {
    "palette": {
        "background": {
            "dark": "#303030",
            "light": "#f6f6f6"
        },
        "backgroundImage": {
            "dark": None,
            "light": None
        },
        "error": {
            "dark": "#da3237",
            "light": "#c42c32"
        },
        "info": {
            "dark": "#2184d3",
            "light": "#4990b2"
        },
        "navBarColor": {
            "dark": "#2e373c",
            "light": "#3c4d67"
        },
        "navBarIcons": {
            "dark": "#ffffff",
            "light": "#ffffff"
        },
        "navBarText": {
            "dark": "#ffffff",
            "light": "#ffffff"
        },
        "pageHeader": {
            "dark": "#706c6e",
            "light": "#706c6e"
        },
        "paper": {
            "dark": "#424242",
            "light": "#ececec"
        },
        "primary": {
            "dark": "#75859b",
            "light": "#75859b"
        },
        "secondary": {
            "dark": "#bebebe",
            "light": "#a6a5a5"
        },
        "selectedCallbackColor": {
            "dark": "#26456e",
            "light": "#c6e5f6"
        },
        "selectedCallbackHierarchyColor": {
            "dark": "#273e5d",
            "light": "#deeff8"
        },
        "success": {
            "dark": "#44b636",
            "light": "#0e7004"
        },
        "tableHeader": {
            "dark": "#484848",
            "light": "#c4c4c4"
        },
        "tableHover": {
            "dark": "#3c3c3c",
            "light": "#e8e8e8"
        },
        "text": {
            "dark": "#ffffff",
            "light": "#000000"
        },
        "warning": {
            "dark": "#f57c00",
            "light": "#ffb74d"
        }
    }
}

def toHex(val):
    return f'{int(val):02x}'
def parseInput():
    # loop twice, once to get all basic colors, then another for complex colors
    for k, v in input["colors"].items():
        if isinstance(v, str):
            input["colors"][k] = v
        if isinstance(v[0], int):
            input["colors"][k] = f"#{toHex(v[0])}{toHex(v[1])}{toHex(v[2])}"
        else:
            input["colors"][k] = v
    for k, v in input["colors"].items():
        if isinstance(v, str):
            input["colors"][k] = v
        if isinstance(v[0], int):
            input["colors"][k] = f"#{toHex(v[0])}{toHex(v[1])}{toHex(v[2])}"
        else:
            input["colors"][k] = parseArrayColor(v)
def hex_to_rgb(hex_color):
       hex_color = hex_color.lstrip("#")
       return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
def blend_rgb(rgb1, rgb2, alpha):
       r = int(rgb1[0] * (1 - alpha) + rgb2[0] * alpha)
       g = int(rgb1[1] * (1 - alpha) + rgb2[1] * alpha)
       b = int(rgb1[2] * (1 - alpha) + rgb2[2] * alpha)
       return (r, g, b)
def addHexCodes(hex1, hex2, weight):
    alpha = weight / 255
    rgb = blend_rgb(hex_to_rgb(hex1), hex_to_rgb(hex2), alpha)
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
def evaluate_prefix(expression):
    tokens = expression
    stack = []
    
    for token in reversed(tokens):
        if isinstance(token, str) and token in input["colors"]:
            stack.append(input["colors"][token])
        elif isinstance(token, int):
            stack.append(token)
        elif isinstance(token, list):
            stack.append(f"#{toHex(token[0])}{toHex(token[1])}{toHex(token[2])}")
        else:
            operand1 = stack.pop()
            operand2 = stack.pop()
            if token == '+':
                result = addHexCodes(operand1, operand2, 128)
            elif token == '~':
                operand3 = stack.pop()
                result = addHexCodes(operand1, operand2, operand3)
            stack.append(result)
            
    return stack.pop()
def parseArrayColor(color):
    if isinstance(color, str):
        if color.startswith("#"):
            return color
        return input["colors"][color]
    if isinstance(color[0], int):
        return f"#{toHex(color[0])}{toHex(color[1])}{toHex(color[2])}"
    return evaluate_prefix(color)


parser = argparse.ArgumentParser(description="Convert binary ninja theme file to Mythic theme")
parser.add_argument("-i", "--input", type=str, help="path to binary ninja theme file", required=True)
parser.add_argument("-o", "--output", type=str, help="path to output theme file for Mythic", required=False)
args = parser.parse_args()

input_file = args.input
output_file = args.output

try:
    file_paths = []
    if os.path.isfile(input_file):
        file_paths.append(input_file)
    else:
        with os.scandir(input_file) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.endswith("bntheme"):
                    file_paths.append(entry.path)
    for f in file_paths:
        with open(f, "r") as file:
            input = json.load(file)
        try:
            parseInput()
            mythicConfig["palette"]["background"]["dark"] =     parseArrayColor(input["palette"]["Base"])
            mythicConfig["palette"]["text"]["dark"] =           parseArrayColor(input["palette"]["Text"])
            mythicConfig["palette"]["error"]["dark"] =          parseArrayColor(input["theme-colors"]["redStandardHighlightColor"])
            mythicConfig["palette"]["info"]["dark"] =           parseArrayColor(input["theme-colors"]["cyanStandardHighlightColor"])
            mythicConfig["palette"]["success"]["dark"] =        parseArrayColor(input["theme-colors"]["greenStandardHighlightColor"])
            mythicConfig["palette"]["primary"]["dark"] =        parseArrayColor(input["theme-colors"]["blueStandardHighlightColor"])
            mythicConfig["palette"]["warning"]["dark"] =        parseArrayColor(input["theme-colors"]["orangeStandardHighlightColor"])
            mythicConfig["palette"]["secondary"]["dark"] =      parseArrayColor(input["theme-colors"]["scriptConsoleEchoColor"])

            mythicConfig["palette"]["navBarColor"]["dark"] =    parseArrayColor(input["theme-colors"]["backgroundHighlightDarkColor"])
            mythicConfig["palette"]["navBarIcons"]["dark"] =    parseArrayColor(input["theme-colors"]["addressColor"])
            mythicConfig["palette"]["navBarText"]["dark"] =     parseArrayColor(input["theme-colors"]["addressColor"])

            mythicConfig["palette"]["pageHeader"]["dark"] =     parseArrayColor(input["theme-colors"]["instructionHighlightColor"])
            mythicConfig["palette"]["paper"]["dark"] =          parseArrayColor(input["palette"]["AlternateBase"])
            
            mythicConfig["palette"]["selectedCallbackColor"]["dark"] = parseArrayColor(input["theme-colors"]["instructionHighlightColor"])
            mythicConfig["palette"]["selectedCallbackHierarchyColor"]["dark"] = parseArrayColor(input["theme-colors"]["instructionHighlightColor"])
            
            mythicConfig["palette"]["tableHeader"]["dark"] =    parseArrayColor(input["theme-colors"]["graphBackgroundDarkColor"])
            mythicConfig["palette"]["tableHover"]["dark"] =     parseArrayColor(input["theme-colors"]["boldBackgroundHighlightDarkColor"])
            
            
        except Exception as innerE:
            print(f)
            print(input)
            raise(innerE)
        if output_file is not None:
            with open(output_file, "w") as f:
                f.write(json.dumps(mythicConfig, indent=4))
        elif len(file_paths) > 1:
            original_path = Path(f)
            new_path = original_path.with_suffix(".json")
            with open(new_path.name, "w") as f:
                f.write(json.dumps(mythicConfig, indent=4))
        else:
            json.dumps(mythicConfig, indent=4)
except Exception as e:
    raise(e)