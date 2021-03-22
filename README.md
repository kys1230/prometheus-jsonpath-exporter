# prometheus-jsonpath-exporter

通过 jsonpath 将 json 数据从 http url 转换为 prometheus metrics

声明: 这个工具是在 “[project-sunbird/prometheus-jsonpath-exporter](https://github.com/project-sunbird/prometheus-jsonpath-exporter)” 上基础进行了一些额外的功能.

额外功能:

1. 支持添加全局级别 label
2. 支持添加 metric 级别的 label
3. 运行 python 版本由 2.x 升级至 3.x
4. 配置文件参数支持默认值, 默认值为: "/etc/prometheus-jsonpath-exporter/config.yml"

### Config

```yml
exporter_port: 9158 # Port on which prometheus can call this exporter to get metrics
log_level: info
json_data_url: http://stubonweb.herokuapp.com/kong-cluster-status # Url to get json data used for fetching metric values
metric_name_prefix: kong_cluster # All metric names will be prefixed with this value
global_labels:
  label_name1: label_value1
  label_name2: label_value2
metrics:
- name: total_nodes # Final metric name will be kong_cluster_total_nodes
  description: Total number of nodes in kong cluster
  path: $.total
  labels:
    label_name3: label_value3
- name: alive_nodes # Final metric name will be kong_cluster_alive_nodes
  description: Number of live nodes in kong cluster
  path: count($.data[@.status is "alive"])
  labels:
    label_name4: label_value4
```

See the example below to understand how the json data and metrics will look for this config

### Run

#### Using code (local)

```
# Ensure python 3.x and pip installed
pip install -r app/requirements.txt
python app/exporter.py example/config.yml
```

#### Using docker

```
docker run -p 9158:9158 -v $(pwd)/example/config.yml:/etc/prometheus-jsonpath-exporter/config.yml kys1230/prometheus-jsonpath-exporter
```

### JsonPath Syntax

This exporter uses [objectpath](http://objectpath.org) python library. The syntax is documented [here](http://objectpath.org/reference.html)

### Example

For the above config, if the configured `json_data_url` returns

```json
{
  "data": [
    {
      "address": "x.x.x.15:7946",
      "status": "failed"
    },
    {
      "address": "x.x.x.19:7946",
      "status": "alive"
    },
    {
      "address": "x.x.x.12:7946",
      "status": "alive"
    }
  ],
  "total": 3
}
```

Metrics will available in http://localhost:9158



```
$ curl -s localhost:9158 | grep ^kong
kong_cluster_total_nodes 3.0
kong_cluster_alive_nodes 2.0
```

