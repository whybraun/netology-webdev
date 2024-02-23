import requests

# # Пример POST запроса
post_response = requests.post(
    url='http://127.0.0.1:5000/advertisements/',
    json={"title": "New Advertisement", "description": "Description of the new advertisement", "owner": "Jane Smith"}
)
print(post_response.json())

# Пример GET запроса
get_response = requests.get(
    url='http://127.0.0.1:5000/advertisements/1'
)
print(get_response.json())

# Пример DELETE запроса
delete_response = requests.delete(
    url='http://127.0.0.1:5000/advertisements/1'
)
print(delete_response.json())

# Пример PATCH запроса
patch_response = requests.patch(
    url='http://127.0.0.1:5000/advertisements/2',
    json={"title": "Updated Title"}
)
print(patch_response.json())
