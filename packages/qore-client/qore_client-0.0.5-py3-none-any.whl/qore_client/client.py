import os
from io import BytesIO
from typing import Any, Dict, List, Optional, Union

import boto3
import requests
from dotenv import load_dotenv
from requests import Response

load_dotenv()


class QoreClient:
    """
    Qore API Client
    ~~~~~~~~~~~~~~~

    Qore 서비스에 접근할 수 있는 파이썬 Client SDK 예시입니다.
    """

    BASE_URL = "https://api-qore.quantit.io"

    def __init__(self, api_key: str) -> None:
        """
        :param api_key: Qore API 인증에 사용되는 Bearer 토큰
        """
        self.api_key = api_key

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], List[tuple]]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        내부적으로 사용하는 공통 요청 메서드

        :param method: HTTP 메서드 (GET, POST, PATCH, DELETE 등)
        :param path: API 엔드포인트 경로 (ex: "/d/12345")
        :param params: query string으로 전송할 딕셔너리
        :param data: 폼데이터(form-data) 등으로 전송할 딕셔너리
        :param json: JSON 형태로 전송할 딕셔너리
        :param files: multipart/form-data 요청 시 사용할 파일(dict)
        :return: 응답 JSON(dict) 또는 raw 데이터
        """
        url = f"{self.BASE_URL}{path}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        response: Response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            json=json,
            files=files,
            headers=headers,
        )
        # 에러 발생 시 raise_for_status()가 예외를 던짐
        response.raise_for_status()

        # 일부 DELETE 요청은 204(No Content)일 수 있으므로, 이 경우 JSON 파싱 불가
        if response.status_code == 204 or not response.content:
            return None

        return response.json()

    def get_drive_detail(self, drive_id: str) -> Any:
        """
        드라이브 상세 조회

        :param drive_id: 조회할 드라이브의 ID
        :return: 드라이브 상세 정보 (JSON)
        """
        return self._request("GET", f"/api/drive/{drive_id}")

    def get_folder(self, folder_id: str) -> Any:
        """
        폴더 조회

        :param folder_id: 조회할 폴더의 ID
        :return: 폴더 상세 정보 (JSON)
        """
        return self._request("GET", f"/api/folder/{folder_id}")

    def get_file(self, file_id: str) -> Any:
        """
        파일 조회

        :param file_id: 조회할 파일의 ID
        :return: 파일 상세 정보 (JSON)
        """
        return self._request("GET", f"/api/file/{file_id}")

    def get_data(self, full_path: str, as_pickle: bool = False) -> Any:
        """
        파일 또는 폴더 데이터 조회

        :param full_path: 조회할 파일 또는 폴더의 전체 경로 (ex: "/Organization/Drive/Folder/File")
        :param as_pickle: True일 경우 pickle 파일을 자동으로 역직렬화하여 반환
        :return: 파일 또는 폴더 데이터 (BytesIO 객체 또는 역직렬화된 Python 객체)
        """
        s3 = boto3.client(
            "s3",
            region_name="ap-northeast-2",
            aws_access_key_id=os.getenv("QORE_AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("QORE_AWS_SECRET_ACCESS_KEY"),
        )
        response = s3.get_object(
            Bucket=os.getenv("QORE_AWS_BUCKET_NAME"), Key=full_path
        )
        data = BytesIO(response["Body"].read())

        if as_pickle:
            import pickle

            data.seek(0)  # 파일 포인터를 처음으로 되돌림
            return pickle.load(data)
        else:
            import pandas as pd

            return pd.read_csv(data, index_col=0)
