
import os
import json

def read_emails_from_file(file_path):
    """
    Lee una lista de emails desde un archivo, uno por línea.
    Devuelve una lista vacía si el archivo no existe.
    """
    if not os.path.exists(file_path):
        print(f"Alerta: El archivo {file_path} no fue encontrado.")
        return []
    with open(file_path, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def save_results_to_json(data, file_path):
    """
    Guarda los datos de resultados en un archivo JSON.
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Resultados guardados en '{file_path}'.")
    except IOError as e:
        print(f"Error al guardar el archivo de resultados: {e}")

if __name__ == '__main__':
    # Pruebas básicas para el módulo

    # Crear archivos de prueba
    with open("test_valid.txt", "w") as f:
        f.write("test1@example.com\n")
        f.write("test2@example.com\n")

    with open("test_invalid.txt", "w") as f:
        f.write("test3@example.com\n")

    # Probar la lectura
    valid_emails = read_emails_from_file("test_valid.txt")
    print(f"Emails válidos leídos: {valid_emails}")
    assert len(valid_emails) == 2

    invalid_emails = read_emails_from_file("test_invalid.txt")
    print(f"Emails inválidos leídos: {invalid_emails}")
    assert len(invalid_emails) == 1

    non_existent = read_emails_from_file("non_existent.txt")
    print(f"Emails de archivo no existente: {non_existent}")
    assert len(non_existent) == 0

    # Probar la escritura
    test_data = {"summary": {"total": 3}, "details": ["detail1"]}
    save_results_to_json(test_data, "test_results.json")

    # Verificar que el archivo se escribió correctamente
    with open("test_results.json", "r") as f:
        read_data = json.load(f)
    assert read_data["summary"]["total"] == 3
    print("Prueba de escritura de JSON exitosa.")

    # Limpiar archivos de prueba
    os.remove("test_valid.txt")
    os.remove("test_invalid.txt")
    os.remove("test_results.json")
    print("Archivos de prueba eliminados.")
