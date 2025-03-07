from kafka import KafkaProducer
from kafka import KafkaConsumer
import json
from hamcrest import *

def json_serializer(data):
    return json.dumps(data).encode('utf-8')


@when('kafka - sending json to broker "{broker:String}" and topic "{topic:String}"')
def sending_json_to_kafka(context, broker, topic):
    assert_that(context.json, is_not(None))
    producer = KafkaProducer(
        bootstrap_servers=[broker],
        value_serializer=json_serializer
    )
    producer.send(topic, context.json)
    producer.flush()
    producer.close()


def json_deserializer(data):
    return json.loads(data.decode('utf-8')) if data else None


@when('kafka - consuming json from broker "{broker:String}" and topic "{topic:String}"')
def consuming_json_from_kafka(context, broker, topic):
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=[broker],
        value_deserializer=json_deserializer,
        auto_offset_reset='earliest',
        enable_auto_commit=False
    )
    messages = []
    for message in consumer:
        messages.append(message.value)
        if len(messages) >= 1:  # Stop after first message for testing
            break
    consumer.close()
    logging.info("Message from Kafka >>> {}\n".format(json.dumps(messages, indent=2)))
    context.json = messages # save for later steps
    assert_that(context.json, is_not(empty()))
