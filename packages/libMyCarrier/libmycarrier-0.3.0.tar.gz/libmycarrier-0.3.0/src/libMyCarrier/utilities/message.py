#! /usr/bin/env python3
import argparse
import json
import os
import sys
import types
import logging
import ssl


from cloudevents.conversion import to_json
from cloudevents.http import CloudEvent

m = types.ModuleType('kafka.vendor.six.moves', 'Mock module')
setattr(m, 'range', range)
sys.modules['kafka.vendor.six.moves'] = m
from kafka import KafkaProducer


def create_producer():
  broker = os.environ['BROKER_ADDR']
  sasl_un = os.environ['SASL_UN']
  sasl_pw = os.environ['SASL_PW']
  context = ssl._create_unverified_context()
  producer = KafkaProducer(bootstrap_servers=broker, sasl_mechanism="SCRAM-SHA-512", sasl_plain_username=sasl_un,
                            sasl_plain_password=sasl_pw, security_protocol="SASL_SSL", ssl_context=context)
  return producer

def message_kafka(event_type, source, data):
  attributes = {
    "type": event_type,
    "source": source,
  }
  data = data
  event = CloudEvent(attributes, data)
  message = to_json(event)
  return message


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("topic", help="Kafka topic to publish to")
  parser.add_argument("-t", "--type", help="Cloud event type to publish", required=True)
  parser.add_argument("-s", "--source", help="Origin of the event", required=True)
  parser.add_argument("-d", "--data", help="Data to publish", required=True)
  args = parser.parse_args()
  producer = create_producer()
  if producer.bootstrap_connected():
    try:
      producer.send(args.topic, message_kafka(args.type, args.source, json.loads(args.data)))
    except Exception as e:
      raise e
  else:
    logger.error("Failed to connect to Kafka broker")


if __name__ == "__main__":
  logger = logging.getLogger('kafka')
  logger.setLevel(logging.WARN)
  main()
