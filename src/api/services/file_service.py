"""ファイルアップロードに関するビジネスロジックを提供するサービス層."""

import codecs
import csv
from statistics import variance
from tempfile import SpooledTemporaryFile
from typing import Any, Dict, List

from fastapi import HTTPException, status

KB = 1024
MB = 1024 * KB
MAX_FILESIZE = 20 * MB


def __set_reader_to_fist_row(file: SpooledTemporaryFile):
    """ファイルポインタをヘッダ行の下に移動させる関数."""
    file.seek(0)
    csv_reader = csv.reader(codecs.iterdecode(file, "utf-8"))
    header = next(csv_reader)

    return csv_reader, header


def validate_filesize(file: SpooledTemporaryFile):
    """一定のファイルサイズを超過していないかの検証を行う関数."""
    # ファイルサイズ検証
    file.seek(0, 2)  # シークしてサイズ検証
    file_size = file.tell()
    if file_size > MAX_FILESIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"アップロードファイルは{MAX_FILESIZE}MB制限です",
        )
    else:
        file.seek(0)  # シークを戻す


def aggregate_csv(file: SpooledTemporaryFile) -> Dict[Any, Dict[object, Any]]:
    """CSV形式で与えられたデータに対して統計量を算出して、辞書型で返す関数."""
    # ファイルサイズを検証
    validate_filesize(file)

    # 呼び出し可能な統計量の関数オブジェクトと出力時の辞書キー名を設定
    aggregate_functions: List[Dict[str, Any]] = [
        {"function": sum, "output_key_name": "sum"},
        {"function": variance, "output_key_name": "variance"},
    ]

    data: Dict[Any, Dict[object, Any]] = {}
    csv_reader, header = __set_reader_to_fist_row(file)
    for i, name in enumerate(header):
        _data = {}

        for fn_entity in aggregate_functions:
            try:
                fn_val = fn_entity["function"](float(r[i]) for r in csv_reader)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="半角数字として読み込めない行が含まれています",
                )

            # intとfloatで端数が同じならintに
            if fn_val == int(fn_val):
                fn_val = int(fn_val)

            _data[fn_entity["output_key_name"]] = fn_val

            # ファイルポインタをリセット
            csv_reader, _ = __set_reader_to_fist_row(file)

        data[name] = _data

    return data
