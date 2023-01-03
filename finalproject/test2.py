import os
import uuid
import logging
import azure.functions as func
import pyodbc
import requests
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient, ContentSettings

def main(req: func.HttpRequest) -> func.HttpResponse:
    # 讀取表單資料
    image = req.files.get("image")
    if not image:
        return func.HttpResponse("No image found in the request.", status_code=400)

    # 上傳圖片到 Azure Blob
    try:
        # 設定 Azure Blob 的連接字串
        connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
        # 建立 BlobServiceClient
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        # 建立 ContainerClient
        container_client = blob_service_client.get_container_client("images")
        # 建立 BlobClient
        blob_client = container_client.get_blob_client(str(uuid.uuid4()))
        # 設定圖片的 MIME 類型
        content_settings = ContentSettings(content_type=image.content_type)
        # 上傳圖片
        blob_client.upload_blob(image, content_settings=content_settings)
        # 獲取圖片的 URL
        image_url = blob_client.url
    except Exception as e:
        logging.error(e)
        return func.HttpResponse("Failed to upload image to Azure Blob.", status_code=500)

    # 將圖片資訊存入資料庫
    try:
        # 設定資料庫的連接字串
        connection_string = os.environ["SQL_CONNECTION_STRING"]
        # 建立連接
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        # 建立資料庫表格
        cursor.execute("CREATE TABLE IF NOT EXISTS images (id INTEGER PRIMARY KEY, name TEXT, url TEXT)")
        # 將圖片資訊存入資料庫
        cursor.execute("INSERT INTO images (name, url) VALUES (?, ?)", image.filename, image_url)
        # 提交交易
        conn.commit()
        # 獲取圖片的 ID
        image_id = cursor.lastrowid
    except Exception as e:
        logging.error(e)
        return func.HttpResponse("Failed to insert image into database.", status_code=500)

    # 回傳圖片資訊
    return func.HttpResponse(f"{{'id': {image_id}, 'name': '{image.filename}', 'url': '{image_url}'}}", mimetype="application/json")
