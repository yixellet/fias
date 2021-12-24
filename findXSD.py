import os

def findXSD(dir_path: str, namepart: str) -> str:
    """
    Находит файл в директории и возвращает его полный путь
    """
    
    if namepart == 'AS_ADDHOUSE_TYPES':
        needle = 'AS_HOUSE_TYPES_2'
    elif namepart.find('_PARAMS') != -1:
        needle = 'AS_PARAM_2'
    else:
        needle = namepart + '_2'

    for file in os.listdir(dir_path):
        if file[:len(needle)] == needle:
            return os.path.join(dir_path, file)
