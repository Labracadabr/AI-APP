import json
import base64


# сохранить json в удобно читаемый вид
def save_json(data: dict, filename: str):
    if not filename.endswith('.json'):
        filename += '.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(filename, 'saved')


# закодировать фото для отправки запроса
def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == '__main__':
    save_json(data={"a": 'b'}, filename='./file')
    pass
