from google.cloud import storage


def upload_file_to_gcs(bucket_name, source_file_path, destination_blob_name):
    """
    Sube un archivo a un bucket de Google Cloud Storage

    Args:
        bucket_name (str): Nombre del bucket
        source_file_path (str): Ruta del archivo local a subir
        destination_blob_name (str): Nombre del archivo en el bucket

    Returns:
        str: URL del archivo subido
    """

    # Crea una instancia del cliente de Google Cloud Storage
    storage_client = storage.Client()

    # Obtiene el bucket
    bucket = storage_client.bucket(bucket_name)

    # Crea un objeto Blob en el bucket
    blob = bucket.blob(destination_blob_name)

    # Carga el archivo en el objeto Blob
    blob.upload_from_filename(source_file_path)

    # Obtiene la URL pública del archivo subido
    url = blob.public_url

    return url
