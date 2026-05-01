"""真实数据导入器 - 从CSV/Excel/JSON导入数据用于建模。

Usage in pipeline:
    from papercarator.data_importer import DataImporter
    importer = DataImporter()
    data = importer.load("path/to/data.csv")
    # data is a dict with columns, stats, preview
"""

import json
from pathlib import Path
from typing import Any, Optional

import numpy as np
from loguru import logger


class DataImporter:
    """从文件导入真实数据。"""

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json", ".tsv", ".txt"}

    def load(self, path: str | Path, sheet_name: str = None) -> dict[str, Any]:
        """加载数据文件，返回标准化字典。

        Returns:
            {
                "columns": ["col1", "col2", ...],
                "data": [[v1, v2, ...], ...],  # 2D list
                "numeric_columns": ["col1", "col3"],  # numeric only
                "stats": {"col1": {"mean": ..., "std": ..., "min": ..., "max": ...}},
                "n_rows": 100,
                "n_cols": 5,
                "preview": "first 5 rows as string",
                "source": "path/to/file.csv"
            }
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"数据文件不存在: {path}")

        ext = path.suffix.lower()
        if ext == ".csv" or ext == ".tsv":
            return self._load_csv(path, sep="\t" if ext == ".tsv" else ",")
        elif ext in (".xlsx", ".xls"):
            return self._load_excel(path, sheet_name)
        elif ext == ".json":
            return self._load_json(path)
        elif ext == ".txt":
            return self._load_txt(path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def _load_csv(self, path: Path, sep: str = ",") -> dict[str, Any]:
        """加载CSV文件。"""
        try:
            import pandas as pd
            df = pd.read_csv(path, sep=sep)
            return self._dataframe_to_dict(df, str(path))
        except ImportError:
            # 无pandas时用stdlib
            return self._load_csv_stdlib(path, sep)

    def _load_csv_stdlib(self, path: Path, sep: str = ",") -> dict[str, Any]:
        """用标准库加载CSV。"""
        import csv
        with open(path, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=sep)
            rows = list(reader)

        if not rows:
            return {"columns": [], "data": [], "n_rows": 0, "n_cols": 0, "source": str(path)}

        columns = rows[0]
        data = rows[1:]

        # Try numeric conversion
        numeric_cols = []
        numeric_data = []
        for row in data:
            num_row = []
            for v in row:
                try:
                    num_row.append(float(v))
                except ValueError:
                    num_row.append(None)
            numeric_data.append(num_row)

        for ci in range(len(columns)):
            vals = [numeric_data[ri][ci] for ri in range(len(numeric_data)) if numeric_data[ri][ci] is not None]
            if len(vals) > len(numeric_data) * 0.5:
                numeric_cols.append(columns[ci])

        stats = {}
        for col_name in numeric_cols:
            ci = columns.index(col_name)
            vals = [numeric_data[ri][ci] for ri in range(len(numeric_data)) if numeric_data[ri][ci] is not None]
            if vals:
                arr = np.array(vals)
                stats[col_name] = {
                    "mean": float(np.mean(arr)),
                    "std": float(np.std(arr)),
                    "min": float(np.min(arr)),
                    "max": float(np.max(arr)),
                    "count": len(vals),
                }

        preview_lines = [",".join(columns)]
        for row in data[:5]:
            preview_lines.append(",".join(row))

        return {
            "columns": columns,
            "data": data,
            "numeric_columns": numeric_cols,
            "stats": stats,
            "n_rows": len(data),
            "n_cols": len(columns),
            "preview": "\n".join(preview_lines),
            "source": str(path),
        }

    def _load_excel(self, path: Path, sheet_name: str = None) -> dict[str, Any]:
        """加载Excel文件。"""
        try:
            import pandas as pd
            df = pd.read_excel(path, sheet_name=sheet_name or 0)
            return self._dataframe_to_dict(df, str(path))
        except ImportError:
            raise ImportError("需要安装 pandas 和 openpyxl: pip install pandas openpyxl")

    def _load_json(self, path: Path) -> dict[str, Any]:
        """加载JSON文件。"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list) and data and isinstance(data[0], dict):
            columns = list(data[0].keys())
            rows = [[row.get(c, "") for c in columns] for row in data]
            return {
                "columns": columns,
                "data": rows,
                "numeric_columns": [],
                "stats": {},
                "n_rows": len(rows),
                "n_cols": len(columns),
                "preview": json.dumps(data[:5], ensure_ascii=False, indent=2),
                "source": str(path),
            }
        return {"columns": [], "data": data, "n_rows": 0, "n_cols": 0, "source": str(path)}

    def _load_txt(self, path: Path) -> dict[str, Any]:
        """加载纯文本（尝试自动检测分隔符）。"""
        content = path.read_text(encoding="utf-8-sig")
        for sep in ["\t", ",", ";", " "]:
            lines = content.strip().split("\n")
            if len(lines) > 1:
                fields = lines[0].split(sep)
                if len(fields) > 1:
                    return self._load_csv(path, sep=sep)
        return {"columns": [], "data": [[content]], "n_rows": 1, "n_cols": 1, "source": str(path)}

    def _dataframe_to_dict(self, df, source: str) -> dict[str, Any]:
        """将pandas DataFrame转为标准字典。"""
        columns = list(df.columns)
        numeric_cols = list(df.select_dtypes(include=[np.number]).columns)

        stats = {}
        for col in numeric_cols:
            desc = df[col].describe()
            stats[col] = {
                "mean": float(desc.get("mean", 0)),
                "std": float(desc.get("std", 0)),
                "min": float(desc.get("min", 0)),
                "max": float(desc.get("max", 0)),
                "count": int(desc.get("count", 0)),
            }

        data = df.values.tolist()
        preview = df.head().to_string()

        return {
            "columns": columns,
            "data": data,
            "numeric_columns": numeric_cols,
            "stats": stats,
            "n_rows": len(data),
            "n_cols": len(columns),
            "preview": preview,
            "source": source,
        }

    def to_model_params(self, loaded: dict[str, Any], model_type: str) -> dict[str, Any]:
        """将导入数据转换为模型参数。

        根据模型类型自动映射数据列到模型参数。
        """
        stats = loaded.get("stats", {})
        numeric_cols = loaded.get("numeric_columns", [])
        params = {}

        if model_type == "queueing":
            # 尝试从数据中提取到达率和服务率
            for col in numeric_cols:
                col_lower = col.lower()
                if any(k in col_lower for k in ["arrival", "到达", "lambda", "interarrival"]):
                    params["arrival_rate"] = stats[col]["mean"]
                elif any(k in col_lower for k in ["service", "服务", "mu", "duration"]):
                    params["service_rate"] = 1.0 / max(stats[col]["mean"], 0.001)
                elif any(k in col_lower for k in ["server", "台数", "channel"]):
                    params["servers"] = int(stats[col]["mean"])

        elif model_type == "time_series":
            # 将数据列转为时间序列观测值
            if numeric_cols:
                col = numeric_cols[0]
                values = [v for v in loaded["data"] if v[loaded["columns"].index(col)] is not None]
                params["observations"] = [float(v[loaded["columns"].index(col)]) for v in values]
                params["time_index"] = list(range(len(values)))

        elif model_type == "statistical":
            # 回归分析：最后一列作为y，其余作为X
            if len(numeric_cols) >= 2:
                y_col = numeric_cols[-1]
                x_cols = numeric_cols[:-1]
                yi = loaded["columns"].index(y_col)
                params["data_y"] = [float(row[yi]) for row in loaded["data"] if row[yi] is not None]
                xi = loaded["columns"].index(x_cols[0])
                params["data_x"] = [float(row[xi]) for row in loaded["data"] if row[xi] is not None]

        elif model_type == "clustering":
            # 聚类：所有数值列作为特征
            if len(numeric_cols) >= 2:
                indices = [loaded["columns"].index(c) for c in numeric_cols[:2]]
                data = []
                for row in loaded["data"]:
                    try:
                        data.append([float(row[i]) for i in indices])
                    except (ValueError, TypeError):
                        continue
                params["data"] = data
                params["n_samples"] = len(data)

        if params:
            logger.info(f"从数据导入 {len(params)} 个模型参数")
        return params
