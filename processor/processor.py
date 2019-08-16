from ast import literal_eval
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback
import os 
import datetime
import time
import shutil
import json
import codecs
import xmltodict

from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
import yaml

from db import *
from producer import *

class ProcessorTemplate(object):
  def __init__(self, **kaws):
    
    self.config = kaws['config']
    self.consumer = AvroConsumer({
        'bootstrap.servers': self.config['kafka']['consumer']['bootstrap_servers'],
        'group.id': self.config['kafka']['consumer']['group_id'],
        'schema.registry.url': self.config['kafka']['consumer']['schema_registery']})

    self.consumer.subscribe([self.config['kafka']['consumer']['topic']])
    self.mysql_config = {
                "host":config["mysql"]["host"],
                "port":config["mysql"]["port"],
                "user":config["mysql"]["user"],
                "password":config["mysql"]["password"],
                "database":config["mysql"]["database"],
                "pool_size":config["mysql"]["pool_size"]
    }
    self.mysql_pool = MySQLDB(**self.mysql_config)
    self.producer = ProducerTemplate(config = self.config, logger = logger)
    
  def consume(self):
    while True:
      try:
        msg = self.consumer.poll(10)
      except SerializerError as e:
        logger.error(traceback.format_exc())
        break
      if msg is None:
        continue
      if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
          continue
        else:
          #print(msg.error())
          logger.error(msg.error())
          break
      value = msg.value() 
      key = msg.key()
      self.process(key, value)
    c.close()

  def process(self, key, value):
    try :
######  Processing when the messeage arrived.  ########
      # ...
      # ...
######  Produce the processed message to the next topic.    #########
      message = {
        "uuid"          :key["uuid",
        "data_id"       :"data_id",
        "processor"     :"processor",
        "step"          :"step",
        "target_abspath":"target_abspath",
        "reference"     :"reference"
      }
      self.producer.produce(message)
      
    except Exception as e:
      logger.error(traceback.format_exc())
    
if __name__ == "__main__":
    
  config_file = sys.argv[1]
  config = yaml.safe_load(open(config_file))

  logger = logging.getLogger("Message Event Bus")
  logger.setLevel(logging.INFO)

  handler = TimedRotatingFileHandler(filename=config["log"]["error"]["path"],
                                      when="m",
                                      interval=1,
                                      backupCount=5)
  logger.addHandler(handler)

  try:
    ProcessorTemplate(config=config).consume()
  except Exception as e: 
    logger.error(traceback.format_exc())
