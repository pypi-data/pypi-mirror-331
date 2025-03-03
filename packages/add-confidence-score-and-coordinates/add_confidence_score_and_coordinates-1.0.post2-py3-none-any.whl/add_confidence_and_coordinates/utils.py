import os
from fuzzywuzzy import fuzz
import re
import shutil
import subprocess
from PIL import Image, ImageEnhance, ImageFilter
import logging
import platform

GS_PATH = 'gs'

logger = logging.getLogger('ocr-json-processor-logger')

if platform.system() == 'Windows':
    GS_PATH = r"C:\Program Files\gs\gs10.03.1\bin\gswin64c.exe"

def clear_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.info(f"Failed to delete {file_path}. Reason: {e}")


def tif_to_jpeg(input_path, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    Image.MAX_IMAGE_PIXELS = None
    with Image.open(input_path) as img:
        for i in range(img.n_frames):
            img.seek(i)
            if img.mode != "RGB":
                frame = img.convert("RGB")
            else:
                frame = img.copy()
            output_path = os.path.join(
                output_folder, f"output_page-{i + 1}.jpeg")
            frame.save(output_path, "JPEG", dpi=(300, 300))


def convert_to_jpeg(input_path, output_folder, file_index=1):
    Image.MAX_IMAGE_PIXELS = None

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with Image.open(input_path) as img:

        if img.mode != "RGB":
            img = img.convert("RGB")
        output_path = os.path.join(
            output_folder, f"output_page-{file_index}.jpeg")

        img.save(output_path, "JPEG", dpi=(300, 300))


def process_image(input_path, output_folder, max_size_mb=4, quality=95):
    # Processed image prefix for saving
    processed_image_prefix = os.path.join(
        output_folder, "processed_images", "processed_page"
    )

    Image.MAX_IMAGE_PIXELS = None
    # Open and process the image
    img = Image.open(input_path)
    img = img.convert("L")
    img = img.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # Output path construction
    output_path = (
            processed_image_prefix + "-" +
            os.path.basename(input_path).split("-")[-1]
    )

    # Initially save the image with the specified quality
    img.save(output_path, quality=quality)

    img = Image.open(output_path)

    # Adjust the image size
    width, height = img.size

    # Check if the saved image exceeds the maximum size limit
    if os.path.getsize(output_path) > max_size_mb * 1024 * 1024 or width > 10000 or height > 10000:
        # while os.path.getsize(output_path) > max_size_mb * 1024 * 1024 and width > 0 and height > 0:
        while (os.path.getsize(output_path) > max_size_mb * 1024 * 1024) or (width > 10000 or height > 10000):
            # Reduce the dimensions
            width -= width // 10
            height -= height // 10
            img = img.resize((width, height), Image.Resampling.LANCZOS)

            # Try saving again with reduced dimensions
            img.save(output_path, quality=quality)

            # If still too large, reduce quality
            if os.path.getsize(output_path) > max_size_mb * 1024 * 1024:
                quality -= 5
                img.save(output_path, quality=quality)

    return output_path

def pdf_to_images(pdf_path, image_folder):
    output_prefix = os.path.join(image_folder, "output_page")

    subprocess.call(
        [
            GS_PATH,
            "-dNOPAUSE",
            "-r300",
            "-sDEVICE=jpeg",
            "-dUseCropBox",
            "-sCompression=lzw",
            "-dBATCH",
            "-o",
            output_prefix + "-%d.jpeg",
            pdf_path,
        ]
    )

def convert_polygon_list(polygon):
    converted_polygon = []
    for i in range(0, len(polygon), 2):
        point = {
            "x": float(polygon[i]),   
            "y": float(polygon[i + 1])
        }
        converted_polygon.append(point)

    return converted_polygon

def transform_leaf_nodes(data):
    if isinstance(data, dict):
        return {k: transform_leaf_nodes(v) for k, v in data.items()}
    elif isinstance(data, list):
        # Check if this is a leaf node list (contains inner lists with 3 elements)
        if data and isinstance(data[0], list) and len(data[0]) == 3:
            # Transform each inner list to the new format
            return [
                {item[0]: {"value": item[1], "page_number": item[2]}}
                for item in data
            ]
        return [transform_leaf_nodes(item) for item in data]
    return data

def calculate_net_polygon(polygons, response_type):
    if len(polygons) > 0:
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        for polygon in polygons:
            for point in polygon:
                if response_type == "textractor":
                    if point['X'] < min_x:
                        min_x = point['X']
                    if point['X'] > max_x:
                        max_x = point['X']
                    if point['Y'] < min_y:
                        min_y = point['Y']
                    if point['Y'] > max_y:
                        max_y = point['Y']
                elif response_type == "doc_intelligence":
                    if point['x'] < min_x:
                        min_x = point['x']
                    if point['x'] > max_x:
                        max_x = point['x']
                    if point['y'] < min_y:
                        min_y = point['y']
                    if point['y'] > max_y:
                        max_y = point['y']
                    
        return [
            { "x": min_x, "y": min_y },
            { "x": max_x, "y": min_y },
            { "x": max_x, "y": max_y },
            { "x": min_x, "y": max_y }
        ]
    
def check_value_type(value):
    value = value.strip().replace(',', '')
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def match_value_in_textractor_response(words, value, ocr_words_list, word_index, page_number):
    if value == '':
        return False
    try:
        if len(words) == 1 and check_value_type(value):
            ocr_word = ocr_words_list[word_index]["text"]
            cleaned_ocr_word = re.sub(r'[,$\-()]', '', ocr_word)
            if not re.match(r'^\d+\.?\d{0,2}$', cleaned_ocr_word) or cleaned_ocr_word == '':
                return False
            else:
                try:
                    value = value.replace(',', '')
                    return f"{float(cleaned_ocr_word):.2f}" == f"{float(value):.2f}".replace('-', '')
                except Exception as e:
                    print(f'\n===>Error while comparing ocr_word: {ocr_word} with value: {value}. Returned False')
                    return False
        if len(words)>0:
            x =  ocr_words_list[word_index]["text"].lower()
            if fuzz.ratio(ocr_words_list[word_index]["text"].lower(),words[0].lower()) > 95:
                output_str_lst = []
                for i in range(len(words)):
                    if word_index + i >= len(ocr_words_list):
                        return False
                    output_str_lst.append(ocr_words_list[word_index + i]["text"].lower())
                output_str = ' '.join(output_str_lst)
                if fuzz.ratio(output_str, value.lower()) > 95:
                    return True
        return False
    except Exception as e:
        print('error occured in', match_value_in_textractor_response.__name__)
        raise e


def match_value_in_doc_intelligence(words, value, azure_ocr_page, word_index, page_number):
    if value == '':
        return False
    try:
        if len(words) == 1 and check_value_type(value):
            azure_ocr_word = azure_ocr_page["words"][word_index]["content"]
            cleaned_azure_ocr_word = re.sub(r'[,$\-()]', '', azure_ocr_word)
            if not re.match(r'^\d+\.?\d{0,2}$', cleaned_azure_ocr_word) or cleaned_azure_ocr_word == '':
                return False
            else:
                try:
                    value = value.replace(',', '')
                    return f"{float(cleaned_azure_ocr_word):.2f}" == f"{float(value):.2f}".replace('-', '')
                except Exception as e:
                    print(f'\n===>Error while comparing azure_ocr_word: {azure_ocr_word} with value: {value}. Returned False')
                    return False
        if len(words)>0:
            x =  azure_ocr_page["words"][word_index]["content"].lower()
            if fuzz.ratio(azure_ocr_page["words"][word_index]["content"].lower(),words[0].lower()) > 95:
                output_str_lst = []
                for i in range(len(words)):
                    if word_index + i >= len(azure_ocr_page["words"]):
                        return False
                    output_str_lst.append(azure_ocr_page["words"][word_index + i]["content"].lower())
                output_str = ' '.join(output_str_lst)
                if fuzz.ratio(output_str, value.lower()) > 95:
                    return True
        return False
    except Exception as e:
        print('error occured in', match_value_in_doc_intelligence.__name__)
        raise e

def update_response_with_confidence_and_polygon(data, confidence_score, net_polygon_value, page_height, page_width, field_name):
    def recursive_update(d):
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    if 'value' in value and 'page_number' in value and key == field_name:
                        value['confidence_score'] = confidence_score
                        value['coordinates_list'] = net_polygon_value
                        value["page_dimensions"] = {
                        "width": page_width,
                        "height": page_height
                    }
                    recursive_update(value)
                elif isinstance(value, list):
                    for item in value:
                        recursive_update(item)

    recursive_update(data)
    return data

def page_to_dict(page):
    # Convert the Page object to a dictionary
    return {
        "text": page.text,
        "words": [words_to_dict(word) for word in page.words],
        "height":page.height,
        "width":page.width
    }

def words_to_dict(word):
    # Convert the Block object to a dictionary
    return {
        "block_type": word.raw_object["BlockType"],
        "text": word.raw_object["Text"],
        "geometry": word.raw_object["Geometry"],
        "confidence": word.raw_object["Confidence"]
    }

def textractor_ocr_to_dict(textractor_ocr):
    # Convert the textractor_ocr object to a dictionary
    return {
        "pages": [page_to_dict(textractor_ocr[page]) for page in textractor_ocr]
    }

def extract_values(data):
    extracted_data = []

    def recursive_extract(d):
        if isinstance(d, dict):
            for key, value in d.items():
                if isinstance(value, dict):
                    if 'value' in value and 'page_number' in value:
                        extracted_data.append({
                            'key': key,
                            'value': value['value'],
                            'page_number': value['page_number']
                        })
                    recursive_extract(value)
                elif isinstance(value, list):
                    for item in value:
                        recursive_extract(item)

    recursive_extract(data)
    return extracted_data