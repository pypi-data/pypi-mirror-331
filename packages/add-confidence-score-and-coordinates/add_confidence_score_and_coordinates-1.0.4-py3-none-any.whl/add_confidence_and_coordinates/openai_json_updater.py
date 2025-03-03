from fastapi import HTTPException
from .utils import extract_values, match_value_in_textractor_response, match_value_in_doc_intelligence, convert_polygon_list, calculate_net_polygon, update_response_with_confidence_and_polygon

def calculate_confidence_score_and_net_polygon_value(words, value, azure_ocr_output, page_number, response_type):
    total_confidence = 0
    count = 0
    net_polygon_value = [] 
    page_width = None
    page_height = None
    try:
        if response_type == "textractor":
            azure_ocr_words = azure_ocr_output["pages"][int(page_number)-1]["words"]
            for word_index in range(len(azure_ocr_words)):
                if match_value_in_textractor_response(words, value, azure_ocr_words, word_index, page_number):
                    total_confidence = 0
                    count = 0
                    if len(words) == 1:
                        total_confidence +=  azure_ocr_words[word_index]["confidence"]
                        coordinates_list = azure_ocr_words[word_index]['geometry']['Polygon']
                        net_polygon_value.append(coordinates_list)
                        count += 1
                    else:
                        for index in range(len(words)+1):
                            if azure_ocr_words[word_index+index].text in words:
                                total_confidence +=  azure_ocr_words[word_index + index]["confidence"]
                                coordinates_list = azure_ocr_words[word_index + index]['geometry']['Polygon']
                                net_polygon_value.append(coordinates_list)
                                count += 1
                    page_width =  azure_ocr_output["pages"][int(page_number)-1]["height"]
                    page_height =  azure_ocr_output["pages"][int(page_number)-1]["width"]
                    net_polygon_value = calculate_net_polygon(net_polygon_value, response_type)
                    return total_confidence / count if count != 0 else 0, net_polygon_value, page_width, page_height
        elif response_type == "doc_intelligence":
            if "azure_ocr_pages_response" in azure_ocr_output and str(page_number) in azure_ocr_output["azure_ocr_pages_response"]:
                azure_ocr_page = azure_ocr_output["azure_ocr_pages_response"][str(page_number)]["pages"][0]
            else:
                azure_ocr_page = azure_ocr_output['pages'][int(page_number)-1]
            for word_index in range(len(azure_ocr_page["words"])-1):
                if match_value_in_doc_intelligence(words, value, azure_ocr_page, word_index, page_number):
                    total_confidence = 0
                    count = 0
                    for index in range(len(words)):
                        total_confidence +=  azure_ocr_page["words"][word_index + index]["confidence"]
                        coordinates_list = convert_polygon_list(azure_ocr_page["words"][word_index + index]["polygon"])
                        net_polygon_value.append(coordinates_list)
                        count += 1
                    page_width =  azure_ocr_page["width"]
                    page_height =  azure_ocr_page["height"]
                    net_polygon_value = calculate_net_polygon(net_polygon_value, response_type)
                    return total_confidence / count if count != 0 else 0, net_polygon_value, page_width, page_height
        return 0, net_polygon_value, page_width, page_height
    except Exception as e:
        print('error occured in', calculate_confidence_score_and_net_polygon_value.__name__)
        raise e

def update_categories_with_confidence_score_and_coordinates(openai_json_response, extracted_key_value, azure_ocr_output, response_type):
    response = None
    try:
        for key_value in extracted_key_value:
            field_name = key_value["key"]
            field_value = key_value["value"]
            if len(str(field_value)) > 0 and len(str(field_name)) > 0:
                if isinstance(field_value, str):
                    field_value_words = field_value.split()
                    field_value_confidence_score, field_value_net_polygon_value, page_width, page_height = calculate_confidence_score_and_net_polygon_value(field_value_words, field_value, azure_ocr_output, (key_value["page_number"]), response_type)
                    response = update_response_with_confidence_and_polygon(openai_json_response, field_value_confidence_score, field_value_net_polygon_value, page_height, page_width, field_name)
                elif isinstance(field_value, dict):
                    for sub_key, sub_value in field_value.items():
                        if isinstance(sub_value, str):
                            sub_value_words = sub_value.split()
                            sub_value_confidence_score, sub_value_net_polygon_value, page_width, page_height = calculate_confidence_score_and_net_polygon_value(sub_value_words, sub_value, azure_ocr_output, (key_value["page_number"]), response_type)
                            response = update_response_with_confidence_and_polygon(openai_json_response, sub_value_confidence_score, sub_value_net_polygon_value, page_height, page_width, f"{field_name}.{sub_key}")
                elif isinstance(field_value, list):
                    for item in field_value:
                        if len(str(item)) > 0:
                            if isinstance(item, str):
                                item_words = item.split()
                                item_confidence_score, item_net_polygon_value, page_width, page_height = calculate_confidence_score_and_net_polygon_value(item_words, item, azure_ocr_output, (key_value["page_number"]), response_type)
                                response = update_response_with_confidence_and_polygon(openai_json_response, item_confidence_score, item_net_polygon_value, page_height, page_width, field_name)
                            elif isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    if isinstance(sub_value, str):
                                        sub_value_words = sub_value.split()
                                        sub_value_confidence_score, sub_value_net_polygon_value, page_width, page_height = calculate_confidence_score_and_net_polygon_value(sub_value_words, sub_value, azure_ocr_output, (key_value["page_number"]), response_type)
                                        response = update_response_with_confidence_and_polygon(openai_json_response, sub_value_confidence_score, sub_value_net_polygon_value, page_height, page_width, f"{field_name}.{sub_key}")
        return response
    except Exception as e:
        print(f'Error occured in : {update_categories_with_confidence_score_and_coordinates.__name__}', e)
        raise e

class JSONUpdater:
    def update_confidence_score_with_coordinates(self, openai_json_response, ocr_response, ocr_response_type):
        try:
            extracted_key_value = extract_values(openai_json_response)
            return update_categories_with_confidence_score_and_coordinates(
                openai_json_response, extracted_key_value, ocr_response, ocr_response_type
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import json
    with open('ocr_json_response.json') as file:
        ocr_response = json.load(file)

    ocr_response_type = 'doc_intelligence'
    with open('openai_json_response.json') as f:
        openai_json_response = json.load(f)

    json_updater = JSONUpdater()
    result = json_updater.update_confidence_score_with_coordinates(openai_json_response, ocr_response, ocr_response_type)
    print(result)