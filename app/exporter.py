#!/usr/bin/python

import time
import yaml
import logging
import argparse
import requests
from objectpath import Tree
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

DEFAULT_PORT = 9158
DEFAULT_LOG_LEVEL = 'info'


class JsonPathCollector(object):
    def __init__(self, cf):
        self._config = cf

    @staticmethod
    def parser_label(label_dict):
        lable_keys, label_values = [], []
        for k, v in label_dict.items():
            lable_keys.append(k)
            label_values.append(v)
        return lable_keys, label_values

    def collect(self):
        result = requests.get(self._config['json_data_url'], timeout=10).json()
        result_tree = Tree(result)

        global_labels = self._config.get('global_labels', {})
        global_label_keys, global_label_values = self.parser_label(global_labels)

        for metric_config in self._config['metrics']:
            metric_name = "{}_{}".format(self._config['metric_name_prefix'], metric_config['name'])
            metric_description = metric_config.get('description', '')
            metric_path = metric_config['path']

            lables = metric_config.get('labels', {})
            label_keys, label_values = self.parser_label(lables)
            label_keys.extend(global_label_keys)
            label_values.extend(global_label_values)

            logging.debug("label_keys: {}, label_values: {}".format(label_keys, label_values))

            value = result_tree.execute(metric_path)
            logging.debug("metric_name: {}, value for '{}' : {}".format(metric_name, metric_path, value))
            metric = GaugeMetricFamily(metric_name, metric_description, labels=label_keys)
            metric.add_metric(tuple(str(v) for v in label_values), value)

            yield metric


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Expose metrics bu jsonpath for configured url')
    parser.add_argument('config_file_path', help='Path of the config file', nargs='?',
                        default='/etc/prometheus-jsonpath-exporter/config.yml')
    args = parser.parse_args()
    with open(args.config_file_path) as config_file:
        config = yaml.load(config_file)
        log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.getLevelName(log_level.upper()))
        exporter_port = config.get('exporter_port', DEFAULT_PORT)
        logging.debug("Config %s", config)
        logging.info('Starting server on port %s', exporter_port)
        start_http_server(exporter_port)
        REGISTRY.register(JsonPathCollector(config))
    while True: time.sleep(1)
