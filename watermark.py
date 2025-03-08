#!/usr/bin/env python3
import os
import sys
import argparse
import json
from PIL import Image, ImageDraw, ImageFont
import glob
import math
import platform

CONFIG_PATH = os.path.expanduser("~/.watermark_config.json")

DEFAULT_CONFIG = {
    "text": "Your Name Here\nMade by Natha Kusuma",
    "opacity": 25,
    "font_size_factor": 6,
    "max_text_width": 0.7,
    "diagonal_fill": 0.8
}

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        except Exception as e:
            print(f"Error reading config: {e}")
            return DEFAULT_CONFIG
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {CONFIG_PATH}")
    except Exception as e:
        print(f"Error saving config: {e}")

def get_system_font_paths():
    paths = []
    if platform.system() == 'Windows':
        paths.append(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Fonts'))
    elif platform.system() == 'Darwin':
        paths.extend([
            '/Library/Fonts/',
            '/System/Library/Fonts/',
            os.path.expanduser('~/Library/Fonts/')
        ])
    elif platform.system() == 'Linux':
        paths.extend([
            '/usr/share/fonts/',
            '/usr/local/share/fonts/',
            os.path.expanduser('~/.fonts/'),
            os.path.expanduser('~/.local/share/fonts/')
        ])
    return paths

def find_font(font_name, size):
    try:
        return ImageFont.truetype(font_name, size)
    except IOError:
        pass
    
    font_paths = get_system_font_paths()
    extensions = ['.ttf', '.TTF', '.otf', '.OTF']
    
    for font_dir in font_paths:
        if not os.path.exists(font_dir):
            continue
            
        for root, _, files in os.walk(font_dir):
            for ext in extensions:
                font_file = f"{font_name}{ext}"
                if font_file in files:
                    try:
                        font_path = os.path.join(root, font_file)
                        return ImageFont.truetype(font_path, size)
                    except IOError:
                        continue
    return None

def calculate_diagonal_text_size(width, height, font, text, diagonal_fill):
    diagonal_length = math.sqrt(width**2 + height**2)
    
    init_font_size = getattr(font, 'size', 12)
    best_size = init_font_size
    
    min_size = 8
    max_size = int(min(width, height) / 3)
    
    for size in range(min_size, max_size, 2):
        try:
            test_font = find_font(getattr(font, 'path', getattr(font, '_filename', None)), size)
            if not test_font:
                test_font = ImageFont.load_default()
                
            text_bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).multiline_textbbox((0, 0), text, font=test_font, align="center")
            text_width = text_bbox[2] - text_bbox[0]
            
            if text_width <= diagonal_length * diagonal_fill:
                best_size = size
            else:
                break
        except:
            break
            
    return best_size

def watermark_images(directory, config):
    text = config.get("text", DEFAULT_CONFIG["text"])
    text = bytes(text, "utf-8").decode("unicode_escape")
    
    opacity = config.get("opacity", DEFAULT_CONFIG["opacity"])
    font_size_factor = config.get("font_size_factor", DEFAULT_CONFIG["font_size_factor"])
    max_text_width = config.get("max_text_width", DEFAULT_CONFIG["max_text_width"])
    diagonal_fill = config.get("diagonal_fill", DEFAULT_CONFIG["diagonal_fill"])
    
    alpha = int(255 * opacity / 100)
    
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif', '*.tiff', '*.webp']
    
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(directory, ext)))
        image_files.extend(glob.glob(os.path.join(directory, ext.upper())))
    
    if not image_files:
        print(f"No image files found in directory: {directory}")
        return
    
    print(f"Found {len(image_files)} image(s) to watermark.")
    
    output_dir = os.path.join(directory, "watermarked_images")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    common_fonts = ["Arial", "Helvetica", "Verdana", "Tahoma", "DejaVuSans", 
                   "FreeSans", "LiberationSans", "NotoSans"]
    
    for img_path in image_files:
        try:
            img = Image.open(img_path)
            width, height = img.size
            
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            initial_font_size = int(min(width, height) / font_size_factor)
            
            font = None
            for font_name in common_fonts:
                found_font = find_font(font_name, initial_font_size)
                if found_font:
                    font = found_font
                    break
            
            if font is None:
                font = ImageFont.load_default()
            
            # Calculate optimal font size for diagonal
            optimal_size = calculate_diagonal_text_size(width, height, font, text, diagonal_fill)
            
            # Update font with optimal size
            font_path = getattr(font, 'path', getattr(font, '_filename', None))
            if font_path:
                try:
                    font = ImageFont.truetype(font_path, optimal_size)
                except:
                    pass
            
            # Get text dimensions
            text_bbox = draw.multiline_textbbox((0, 0), text, font=font, align="center")
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Center position
            center_x = width / 2
            center_y = height / 2
            text_x = center_x - text_width / 2
            text_y = center_y - text_height / 2
            
            draw.multiline_text(
                (text_x, text_y), 
                text, 
                font=font, 
                fill=(255, 0, 0, alpha),
                align="center"
            )
            
            angle = math.degrees(math.atan2(height, width))
            rotated_watermark = watermark.rotate(angle, resample=Image.BICUBIC, center=(center_x, center_y))
            
            img = Image.alpha_composite(img, rotated_watermark)
            
            base_name = os.path.basename(img_path)
            save_path = os.path.join(output_dir, f"watermarked_{base_name}")
            
            if base_name.lower().endswith(('.jpg', '.jpeg')):
                img = img.convert('RGB')
            
            img.save(save_path)
            print(f"Watermarked: {base_name}")
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
    
    print(f"Watermarked images saved to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Add watermark text to images diagonally.')
    parser.add_argument('directory', nargs='?', help='Directory containing images to watermark')
    
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--set-text', help='Set watermark text')
    parser.add_argument('--set-opacity', type=int, help='Set opacity percentage (0-100)')
    parser.add_argument('--set-font-size-factor', type=int, help='Set font size factor')
    parser.add_argument('--set-max-text-width', type=float, help='Set maximum text width (0.1-1.0)')
    parser.add_argument('--set-diagonal-fill', type=float, help='Set diagonal fill factor (0.1-1.0)')
    
    parser.add_argument('-t', '--text', help='Custom text for this run only')
    parser.add_argument('-o', '--opacity', type=int, help='Opacity for this run only (0-100)')
    parser.add_argument('-f', '--font-size-factor', type=int, help='Font size factor for this run only')
    parser.add_argument('-w', '--max-text-width', type=float, help='Maximum text width for this run only')
    parser.add_argument('-d', '--diagonal-fill', type=float, help='Diagonal fill for this run only')
    
    args = parser.parse_args()
    
    config = load_config()
    
    if args.config:
        print("Current configuration:")
        print(f"Text: {config['text']}")
        print(f"Opacity: {config['opacity']}%")
        print(f"Font size factor: {config['font_size_factor']}")
        print(f"Max text width: {config.get('max_text_width', DEFAULT_CONFIG['max_text_width'])}")
        print(f"Diagonal fill: {config.get('diagonal_fill', DEFAULT_CONFIG['diagonal_fill'])}")
        return
    
    config_updated = False
    
    if args.set_text is not None:
        config['text'] = args.set_text
        config_updated = True
        
    if args.set_opacity is not None:
        if 0 <= args.set_opacity <= 100:
            config['opacity'] = args.set_opacity
            config_updated = True
        else:
            print("Opacity must be between 0 and 100")
            
    if args.set_font_size_factor is not None:
        if args.set_font_size_factor > 0:
            config['font_size_factor'] = args.set_font_size_factor
            config_updated = True
        else:
            print("Font size factor must be greater than 0")
    
    if args.set_max_text_width is not None:
        if 0.1 <= args.set_max_text_width <= 1.0:
            config['max_text_width'] = args.set_max_text_width
            config_updated = True
        else:
            print("Max text width factor must be between 0.1 and 1.0")
            
    if args.set_diagonal_fill is not None:
        if 0.1 <= args.set_diagonal_fill <= 1.0:
            config['diagonal_fill'] = args.set_diagonal_fill
            config_updated = True
        else:
            print("Diagonal fill factor must be between 0.1 and 1.0")
    
    if config_updated:
        save_config(config)
        if args.directory is None:
            return
    
    run_config = config.copy()
    if args.text is not None:
        run_config['text'] = args.text
    if args.opacity is not None and 0 <= args.opacity <= 100:
        run_config['opacity'] = args.opacity
    if args.font_size_factor is not None and args.font_size_factor > 0:
        run_config['font_size_factor'] = args.font_size_factor
    if args.max_text_width is not None and 0.1 <= args.max_text_width <= 1.0:
        run_config['max_text_width'] = args.max_text_width
    if args.diagonal_fill is not None and 0.1 <= args.diagonal_fill <= 1.0:
        run_config['diagonal_fill'] = args.diagonal_fill
    
    if args.directory is None:
        if not config_updated:
            parser.print_help()
            print("\nError: Directory is required when not setting configuration")
        return
    
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        sys.exit(1)
    
    watermark_images(args.directory, run_config)

if __name__ == "__main__":
    main()

