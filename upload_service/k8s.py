from kubernetes import client, config
import os

if os.getenv("KUBERNETES_SERVICE_HOST"):
    config.load_incluster_config()
else:
    config.load_kube_config()

batch = client.BatchV1Api()

NAMESPACE = os.getenv("JOB_NAMESPACE", "default")
PROCESSOR_IMAGE = os.getenv("PROCESSOR_IMAGE", "your-repo/processor-service:latest")
S3_BUCKET = os.getenv("S3_BUCKET")

def create_processor_job(job_id: str, s3_key: str):
    job_name = f"zip-processor-{job_id}"

    job = client.V1Job(
        metadata=client.V1ObjectMeta(name=job_name),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"job": job_name}),
                spec=client.V1PodSpec(
                    restart_policy="Never",
                    containers=[
                        client.V1Container(
                            name="processor",
                            image=PROCESSOR_IMAGE,
                            env=[
                                client.V1EnvVar(name="S3_BUCKET", value=S3_BUCKET),
                                client.V1EnvVar(name="ZIP_KEY", value=s3_key),
                            ],
                        )
                    ],
                ),
            )
        )
    )

    batch.create_namespaced_job(namespace=NAMESPACE, body=job)
