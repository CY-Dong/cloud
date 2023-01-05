import os
import uuid
import logging
import azure.functions as func
import pyodbc
import requests
from azure.storage.blob import BlobClient, BlobServiceClient, ContainerClient, ContentSettings
from azure.cosmos import CosmosClient, PartitionKey
import cv2
import pyzbar.pyzbar as pyzbar
import numpy as np
import subprocess

def main(req: func.HttpRequest) -> func.HttpResponse:

    # 讀取表單資料
    image = req.files.get("image")
    if not image:
        return func.HttpResponse("No image found in the request.", status_code=400)

    # 上傳圖片到 Azure Blob
    try:
        # 在這裡填入 Azure Blob 存儲的相關設定（如帳戶名稱、密鑰、容器名稱等）
        storage_account_name = "11177016qrcode"
        storage_account_key = "cRF8iZARPDakrmZDmdkIyY6yZwU2yll+kFRmwv75lZDDlSZAblm66nlsoraKiIVpTY2wHIDorgY1+AStAIa+Sw=="
        container_name = "qrcode"
        blob_name = "qrcode.jpg"

        blob_service_client = BlobServiceClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name),
            credential=storage_account_key,)
        container_client = ContainerClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name), container_name=container_name, credential=storage_account_key)
        #image = request.files["image"]
        blob_client = BlobClient(account_url="https://{}.blob.core.windows.net".format(storage_account_name), container_name=container_name, blob_name=image.filename, credential=storage_account_key)
        blob_client.upload_blob(image)

        # 將圖片的相關資訊（如圖片名稱、URL 等）存入資料庫
        # 這裡省略了資料庫的相關操作
        # 讀取 blob 中的數據
        blob_data = blob_client.download_blob().readall()
        image_url = blob_client.url

        #將檔案載下來
        temp = np.asarray( bytearray(blob_data), dtype="uint8") 

        # 读取图像
        read_image = cv2.imdecode(temp, cv2.IMREAD_GRAYSCALE)

        # 查找QR码
        codes = pyzbar.decode(read_image)


        # 遍历找到的所有QR码
        for code in codes:
            # 打印QR码数据
    
            if ( code.type == 'QRCODE' ) :
                if ( code.data[0:2] == b'**' ) :
                    right_code = code.data
                else :
          
                    left_code = code.data

        left_code = left_code.decode( 'utf-8' )
        print( left_code )
        number = left_code[0:10]                    #發票號碼
        date = left_code[10:17]                     #開發票日期
        random_code = left_code[17:21]              #隨機碼
        sales = left_code[21:29]                    #銷售額
        total = left_code[29:37]                    #總計額
        buyer_compilation = left_code[37:45]        #買方統編
        seller_compilation = left_code[45:53]       #賣方統編
        encryption = left_code[53:77]               #加密資訊
        product = left_code[95:len(left_code)]      #產品資訊

    except Exception as e:
        logging.error(e)
        return func.HttpResponse("Failed to download image from Azure Blob.", status_code=500)

    # 將圖片資訊存入資料庫
    try:
        # 3. 創建 CosmosClient 對象
        cosmos_account_name = "https://11177016cosmosdb.documents.azure.com:443/"
        cosmos_account_key = "oIypK85ivjY3tdxaNlZ5QLpq6IQbop3qGsCYWHZ33KaIW7K0IKsxAvaAN6JOiG47i9WkRWLdKV2tACDb9EUwPQ=="

        client = CosmosClient(cosmos_account_name, cosmos_account_key)
        # 上傳資料至指定的database內的容器

        # 4. 選擇數據庫和容器
        database_name = "qrcodeTest"
        database_client = client.get_database_client(database_name)

        #container_name = "qrcode"
        container = database_client.get_container_client(container_name)
        document = {
            "id": number,
            "date" : date,
            "product" : product
        }
        container.create_item(document)
        # 獲取圖片的 ID
        #image_id = cursor.lastrowid
    except Exception as e:
        logging.error(e)
        return func.HttpResponse("Failed to insert image into database.", status_code=500)

    # 回傳圖片資訊
    return func.HttpResponse(f"{{'id': {image_url}, 'name': '{image.filename}', 'url': '{image_url}'}}", mimetype="application/json")
