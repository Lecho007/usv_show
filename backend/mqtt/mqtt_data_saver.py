import paho.mqtt.client as mqtt

# MQTT配置
broker_address = "mqtt.wit-motion.cn"
broker_port = 31883
username = "CYL"
password = "FDA4235JHKBFSJF541KDO3NFK4"

subtopic_list = {
    "device/868327071852022/upload",
}

def save_message_to_file(filename, message):
    with open(filename, "ab") as f:
        f.write(message)
    print(f"消息已保存到 {filename}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    for subtopic in subtopic_list:
        client.subscribe(subtopic)

def on_message(client, userdata, msg):
    try:
        print(f"Received: '{msg.payload}' on topic: {msg.topic}")
        filename = msg.topic.replace('/', '_')+'.txt'
        save_message_to_file(filename, msg.payload)
    except Exception as e:
        print(f"处理消息出错: {e}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(username, password)
    
    try:
        client.connect(broker_address, broker_port, 60)
        print(f"已连接至 {broker_address}:{broker_port}")
        client.loop_forever()
    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()