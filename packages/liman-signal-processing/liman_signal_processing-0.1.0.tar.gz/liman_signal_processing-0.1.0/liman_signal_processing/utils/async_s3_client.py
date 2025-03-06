import pyarrow.parquet as pq
import pyarrow.csv as pv
import pandas as pd
from io import BytesIO
from aiobotocore.session import get_session


class AsyncS3Client:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, endpoint_url):
        self.config = {
            'aws_access_key_id': aws_access_key_id,
            'aws_secret_access_key': aws_secret_access_key,
            'endpoint_url': endpoint_url
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @classmethod
    async def create(cls, aws_access_key_id, aws_secret_access_key, bucket_name, endpoint_url):
        """
        Фабричный метод для создания экземпляра AsyncS3Client.
        """
        return cls(aws_access_key_id, aws_secret_access_key, bucket_name, endpoint_url)

    async def upload_file(self, file_name, object_name):
        """
        Асинхронно загружает файл в S3.
        """
        async with self.session.create_client('s3', **self.config) as client:
            with open(file_name, 'rb') as file:
                await client.put_object(Bucket=self.bucket_name, Key=object_name, Body=file)

    async def download_file(self, object_name, file_name):
        """
        Асинхронно скачивает файл из S3.
        """
        async with self.session.create_client('s3', **self.config) as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            async with response['Body'] as stream:
                with open(file_name, 'wb') as file:
                    while True:
                        chunk = await stream.read(1024)
                        if not chunk:
                            break
                        file.write(chunk)

    async def list_objects(self, prefix=''):
        """
        Асинхронно получает список объектов в бакете.
        """
        async with self.session.create_client('s3', **self.config) as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            return [obj['Key'] for obj in response.get('Contents', [])]

    async def download_to_pyarrow(self, object_name, file_format='parquet'):
        """
        Асинхронно скачивает файл из S3 и возвращает его как объект pyarrow.Table.
        Поддерживаются форматы Parquet и CSV.
        """
        async with self.session.create_client('s3', **self.config) as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
            async with response['Body'] as stream:
                # Чтение данных в BytesIO
                data = BytesIO()
                chunk = await stream.read()
                data.write(chunk)
                data.seek(0)  # Перемотка в начало

                # Чтение данных в pyarrow.Table в зависимости от формата
                if file_format == 'parquet':
                    table = pq.read_table(data)
                elif file_format == 'csv':
                    table = pv.read_csv(data)
                else:
                    raise ValueError(f"Unsupported file format: {file_format}")

                return table

    async def download_to_pandas(self, object_name, file_format='parquet'):
        """
        Асинхронно скачивает файл из S3 и возвращает его как pandas.DataFrame.
        """
        table = await self.download_to_pyarrow(object_name, file_format)
        return table.to_pandas()