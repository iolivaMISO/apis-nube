from google.cloud import pubsub_v1

project_id = 'api-nube-semana-3'
topic_name = 'my-topic'
subscriber_name = 'my-subscriber'
topic_path = f"projects/{project_id}/topics/{topic_name}"

def callback(message):
    print(f"Mensaje recibido: {message.data.decode()}")

    # Realiza cualquier procesamiento adicional que desees hacer con el mensaje aquí

    message.ack()  # Confirma la recepción del mensaje

def subscribe():
    # Crea un cliente de Pub/Sub
    subscriber = pubsub_v1.SubscriberClient()

    # Crea el nombre completo de la suscripción
    subscription_path = f"projects/{project_id}/subscriptions/{subscriber_name}"

    # Inicia la suscripción y especifica la función de devolución de llamada
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Espera a que la suscripción se mantenga activa
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise

subscribe()
