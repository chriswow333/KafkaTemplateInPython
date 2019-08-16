from ast import literal_eval
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback
import os 
import datetime
import time
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


key_schema_str = """
{
  "namespace": "chris.yu",
  "name": "key",
  "type": "record",
  "fields" : [
    {
      "name" : "uuid",
      "type" : "string"
    }
  ]
}
"""
value_schema_str = """
{
  "namespace": "chris.yu",
  "name": "process_value",
  "type": "record",
  "fields" : [
    {
      "name" : "data_id",
      "type" : "string"
    },
    {
      "name" : "processor",
      "type" : "string"
    },
    {
      "name" : "step",
      "type" : "int"
    },
    {
      "name" : "target_abspath",
      "type" : "string"
    },
    {
      "name" : "reference",
      "type" : "string"
    }
  ]
}
"""

class ProducerTemplate(object):
  def __init__(self, **kaws):
    self.config = kaws['config']
    self.logger = kaws['logger']
    self.kafka = self.config["kafka"]
    bootstrap_servers = self.kafka['producer']['bootstrap_servers']
    schema_registery = self.kafka['producer']['schema_registery']
    key_schema = avro.loads(key_schema_str)
    value_schema = avro.loads(value_schema_str)
    bootstrap_servers = self.kafka['producer']['bootstrap_servers']
    schema_registery = self.kafka['producer']['schema_registery']
    key_schema = avro.loads(key_schema_str)
    value_schema = avro.loads(value_schema_str)
    self.avroProducer = AvroProducer({
        'bootstrap.servers':bootstrap_servers,
        'schema.registry.url': schema_registery
        }, default_key_schema=key_schema, default_value_schema=value_schema)

  def produce(self, message):
    try:
      ts = time.time()
      current_time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
      key = {"uuid" : message["uuid"]}
      value = {
        "data_id"       :message["data_id"],
        "processor"     :message["processor"],
        "step"          :message["step"],
        "target_abspath":message["target_abspath"],
        "reference"     :message["reference"]
      }
      self.avroProducer.produce(topic=message["processor"], key=key, value=value)
      self.avroProducer.flush()

    except Exception as e:
      self.logger.error(traceback.format_exc())