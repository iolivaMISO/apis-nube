
from google.cloud import pubsub_v1

project_id = 'api-nube-semana-3'
topic_name = 'my-topic'
subscriber_name = 'my-subscriber'
topic_path = f"projects/{project_id}/topics/{subscriber_name}"

topic_name = 'projects/'+ project_id +'/topics/'+topic_name.format(
    project_id=project_id,
    topic=topic_name,  # Set this to something appropriate.
)
subscription_name = 'projects/'+ project_id +'/subscriptions/'+subscriber_name.format(
    project_id=project_id,
    sub=subscriber_name,  # Set this to something appropriate.
)



def callback(message):
    print(f"Mensaje recibido: {message.data.decode()}")

    # Realiza cualquier procesamiento adicional que desees hacer con el mensaje aquí

    message.ack()  # Confirma la recepción del mensaje

def subscribe():
    # Crea un cliente de Pub/Sub
    subscriber = pubsub_v1.SubscriberClient()

    # Crea el nombre completo de la suscripción
    subscription_path = subscriber.subscription_path(topic_path, subscriber_name)

    # Inicia la suscripción y especifica la función de devolución de llamada
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

    # Espera a que la suscripción se mantenga activa
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise

subscribe()