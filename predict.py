import argparse

from google.cloud import automl_v1beta1 as automl

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f',
        '--file_path',
        help='Image file path',
        type=str,
        default='',
    )
    parser.add_argument(
        '-pid',
        '--project_id',
        help='GCP project ID',
        type=str,
        default='photo-id-2021',
    )
    parser.add_argument(
        '-loc',
        '--location',
        help='Location for GCP',
        type=str,
        default='us-central1',
    )
    parser.add_argument(
        '-mid',
        '--model_id',
        help='Model ID',
        type=str,
        default='IOD6889810339504848896',
    )
    parser.add_argument(
        '-th',
        '--score_threshold',
        help='Score threshold for prediction results',
        type=float,
        default=0.8,
    )
    args = parser.parse_args()
    print(args)

    file_path = args.file_path
    project_id = args.project_id
    location = args.location
    model_id = args.model_id
    score_threshold = args.score_threshold

    prediction_client = automl.PredictionServiceClient()
    model_path = automl.PredictionServiceClient.model_path(
        project=project_id,
        location=location,
        model=model_id,
    )

    with open(file_path, 'rb') as ff:
        content = ff.read()

    image = automl.Image(image_bytes=content)
    payload = automl.ExamplePayload(image=image)
    params = {'score_threshold': str(score_threshold)}

    request = automl.PredictRequest(
        name=model_path,
        payload=payload,
        params=params,
    )
    response = prediction_client.predict(request=request)

    print('Prediction results:')
    print(response)