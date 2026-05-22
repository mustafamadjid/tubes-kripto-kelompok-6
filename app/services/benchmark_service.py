from time import perf_counter
from typing import Any, Callable

from app.schemas.results import BenchmarkResult


class BenchmarkService:
    def measure_operation(self, operation_name: str, callback: Callable[[], Any]) -> BenchmarkResult:
        start = perf_counter()
        callback()
        end = perf_counter()
        return BenchmarkResult(operation_name=operation_name, duration_ms=(end - start) * 1000)
