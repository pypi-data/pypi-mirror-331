# Fast-Prometheus

A library for easily adding prometheus metrics to your project using **fastapi**, **starlette**.

### Golden signals
Golden signals are available for use by default.  
You can also add your own metrics if needed.  

Golden signals includes:  
* **Latency**  
Request processing time (request_duration_seconds)  
* **Traffic**  
Total number of requests (requests_total)  
* **Errors**  
Total number of errors (errors_total)  
* **Saturation**  
Number of active requests (active_requests_total)  
CPU load in percent. (cpu_percent)  
Memory load in percent (memory_percent)  

### Quickstart
1. Install Fast-Prometheus
```shell
pip install fast-prometheus
```
2. Creating metrics for your application
```python
from fastapi import FastAPI
from fast_prometheus import create_prometheus_metrics

app = FastAPI()
create_prometheus_metrics(app)
```
3. The create_prometheus_metrics function creates a sub-application, metrics will be available at the /metrics path.  
In the fastapi docs (openapi), this endpoint will not be shown.  
The following data will be available on /metrics by default:
```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 5352.0
python_gc_objects_collected_total{generation="1"} 4415.0
python_gc_objects_collected_total{generation="2"} 941.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 229.0
python_gc_collections_total{generation="1"} 20.0
python_gc_collections_total{generation="2"} 1.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="12",patchlevel="9",version="3.12.9"} 1.0
# HELP process_virtual_memory_bytes Virtual memory size in bytes.
# TYPE process_virtual_memory_bytes gauge
process_virtual_memory_bytes 3.50257152e+08
# HELP process_resident_memory_bytes Resident memory size in bytes.
# TYPE process_resident_memory_bytes gauge
process_resident_memory_bytes 8.4205568e+07
# HELP process_start_time_seconds Start time of the process since unix epoch in seconds.
# TYPE process_start_time_seconds gauge
process_start_time_seconds 1.74099902595e+09
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 0.96
# HELP process_open_fds Number of open file descriptors.
# TYPE process_open_fds gauge
process_open_fds 16.0
# HELP process_max_fds Maximum number of open file descriptors.
# TYPE process_max_fds gauge
process_max_fds 1.048576e+06
# HELP app_requests_total Total HTTP requests
# TYPE app_requests_total counter
app_requests_total{endpoint="/metrics",method="GET",status="200"} 1.0
# HELP app_requests_created Total HTTP requests
# TYPE app_requests_created gauge
app_requests_created{endpoint="/metrics",method="GET",status="200"} 1.7409990285706432e+09
# HELP app_request_duration_seconds Request latency in seconds
# TYPE app_request_duration_seconds histogram
app_request_duration_seconds_bucket{endpoint="/metrics",le="0.01",method="GET",status="200"} 1.0
app_request_duration_seconds_bucket{endpoint="/metrics",le="0.05",method="GET",status="200"} 1.0
app_request_duration_seconds_bucket{endpoint="/metrics",le="0.1",method="GET",status="200"} 1.0
app_request_duration_seconds_bucket{endpoint="/metrics",le="0.5",method="GET",status="200"} 1.0
app_request_duration_seconds_bucket{endpoint="/metrics",le="1.0",method="GET",status="200"} 1.0
app_request_duration_seconds_bucket{endpoint="/metrics",le="+Inf",method="GET",status="200"} 1.0
app_request_duration_seconds_count{endpoint="/metrics",method="GET",status="200"} 1.0
app_request_duration_seconds_sum{endpoint="/metrics",method="GET",status="200"} 0.00582122802734375
# HELP app_request_duration_seconds_created Request latency in seconds
# TYPE app_request_duration_seconds_created gauge
app_request_duration_seconds_created{endpoint="/metrics",method="GET",status="200"} 1.740999028570668e+09
# HELP app_errors_total Total HTTP Errors
# TYPE app_errors_total counter
# HELP app_active_requests_total Current active requests in application
# TYPE app_active_requests_total gauge
app_active_requests_total{endpoint="/metrics",method="GET"} 1.0
# HELP app_cpu_percent CPU Percent
# TYPE app_cpu_percent gauge
app_cpu_percent 0.0
# HELP app_memory_percent Memory Percent
# TYPE app_memory_percent gauge
app_memory_percent 18.5
```
