# dolphin-id-gcp

Dolphin ID recogniser for GCP. 
In short, it prepares the label data for the GCP auto ml.

## Prerequistic

- Image data and label data (in the format of VIA v1)

Make sure that the images files and label files (in the format of VIA v1) are on local disk.
As the format changes with the versions for VIA (i.e., Version 1, 2 and 3), we fix the format for V1 for now.

[Reference](https://www.robots.ox.ac.uk/~vgg/software/via/)


## Prepare image data on Google Cloud Storage (for auto ML)

- Install GCP CLI Tools 

[Reference](https://cloud.google.com/storage/docs/gsutil_install)

- Check all the projects one can access. Make sure that `photo-id-2021` should be one of them.
 
```
$ gcloud projects list
PROJECT_ID                NAME            PROJECT_NUMBER
dolphin-for-test          Dolphin         392850099759
photo-id-2021             Photo ID        148229944099
```

- Switch to the project `photo-id-2021`

```
$ gcloud config set project photo-id-2021
Updated property [core/project].
```

- Check the project for now

```
$ gcloud config get-value project
photo-id-2021
```

- Copy the files to Google Cloud Storage

Note that to ease the implementation, we use exactly the same struct (and path) for the image/labels files on local machine and google cloud storage.
That is, if the images are stored (according to their trip/voyage, respectively) in the folder `data/src` in local, please put them in exactly the same path on google cloud storage.
As a result, the `base_data_folder` corresponds to both the local and remote folder in the script, such as `data/src` in the example.
To ease the manipulation, one can add the selection of local and remote paths in the scripts (and their corresponding structs, such as region).

```
$ tree data/src/
data/src/
├── HL20100702_01
│   ├── HL20100702_01_Gg_990702\ (100).JPG
│   ├── HL20100702_01_Gg_990702\ (101).JPG
│   ├── HL20100702_01_Gg_990702\ (102).JPG
│   ├── HL20100702_01_Gg_990702\ (103).JPG
```

```
$ gsutil -m cp -r ./data/src/* gs://risso-dolphin-id/data/src/
Copying file://./data/src/HL20100702_01/HL20100702_01_Gg_990702 (223).JPG [Content-Type=image/jpeg]...
Copying file://./data/src/HL20100702_01/HL20100702_01_Gg_990702 (219).JPG [Content-Type=image/jpeg]...
Copying file://./data/src/HL20100702_01/HL20100702_01_Gg_990702 (51).JPG [Content-Type=image/jpeg]...
Copying file://./data/src/HL20100702_01/HL20100702_01_Gg_990702 (47).JPG [Content-Type=image/jpeg]...

...

| [1.7k/1.7k files][  4.8 GiB/  4.8 GiB] 100% Done   3.4 MiB/s ETA 00:00:00
Operation completed over 1.7k objects/4.8 GiB.
```

```
$ gsutil ls gs://risso-dolphin-id/data/src/HL20100702_01/
gs://risso-dolphin-id/data/src/HL20100702_01/HL20100702_01_Gg_990702 (100).JPG
gs://risso-dolphin-id/data/src/HL20100702_01/HL20100702_01_Gg_990702 (101).JPG
gs://risso-dolphin-id/data/src/HL20100702_01/HL20100702_01_Gg_990702 (102).JPG
gs://risso-dolphin-id/data/src/HL20100702_01/HL20100702_01_Gg_990702 (103).JPG
```

## Prepare the label file for GCP auto ml

### Generate the label file needed for GCP auto ML

- Use pyenv to create virtual env with python 3.6.

```
$ brew install pyenv 
$ pyenv install 3.6.11
```

[Reference](https://github.com/pyenv/pyenv)

- Use pipenv to create virtual env with Pipfile

Switch to the project folder (i.e., `dolphin-id-gcp`) first.
Then, create the virtual env and install the dep. with pipenv.

```
$ pip3 install pipenv 
$ pipenv --python ~/.pyenv/versions/3.6.11/bin/python3.6
$ pipenv install --dev 
$ pipenv shell
```

[Reference](https://pipenv.pypa.io/en/latest/)

- Run the main script to transfer the labels in via v1 format to the one for gcp auto ml.

Note that the min. number of the regions needed to be trained for GCP auto ml is `10`.
However, as the regions/labels are not located evenly on images, it is recommended to use `12` or even `15`.

```
python3 -m parser.main \
    -f data/src \
    -b risso-dolphin-id \
    -o gcp_auto_ml_labels.csv \
    -n 12
```

- Upload the label file to Google Cloud Storage.

```
$ gsutil cp ./gcp_auto_ml_labels.csv gs://risso-dolphin-id/data/
Copying file://./gcp_auto_ml_labels.csv [Content-Type=text/csv]...
- [1 files][402.8 KiB/402.8 KiB]
Operation completed over 1 objects/402.8 KiB.
```

## Create dataset by following the GCP documents

[Reference](https://cloud.google.com/automl-tables/docs/import)

## Train the model by following the procedures

One can use the CLI tools as shown in the documents. 
Otherwise, one can train the model by following the steps on web interface.
For now, there is already a model trained with the image data with name `risso_dolphin_20210508115823` and ID `IOD6889810339504848896`,
which has accuracy `84.75%` and recall `53.48%`.

[Reference](https://cloud.google.com/vision/automl/object-detection/docs/quickstart)

## Test API 

- Create a service account to use the predict api for auto ML.
- Get the credential in the form of json file

Following the procedures on the official documents.

[Reference](https://cloud.google.com/vision/automl/docs/client-libraries)

- Export the env var `GOOGLE_APPLICATION_CREDENTIALS` for the key file (json)

```
export GOOGLE_APPLICATION_CREDENTIALS=./gcp_key.json
```

- Test the prediction with `predict.py` python script

Remember to deploy the model.

[Reference](https://cloud.google.com/vision/automl/docs/predict#automl_vision_classification_predict-python)
[API Spec](https://googleapis.dev/python/automl/latest/index.html)

```
$ python3 -m predict \
>   -f './data/src/HL20100702_01/HL20100702_01_Gg_990702 (30).JPG' \
>   -pid dolphin-170615 \
>   -loc us-central1 \
>   -mid IOD5909958562179710976 \
>   -th 0.2
Namespace(file_path='./data/src/HL20100702_01/HL20100702_01_Gg_990702 (30).JPG', location='us-central1', model_id='IOD5909958562179710976', project_id='dolphin-170615', score_threshold=0.2)
Prediction results:
payload {
  annotation_spec_id: "6860358821043240960"
  image_object_detection {
    bounding_box {
      normalized_vertices {
        x: 0.35556212067604065
        y: 0.32888874411582947
      }
      normalized_vertices {
        x: 0.42823973298072815
        y: 0.5363861918449402
      }
    }
    score: 0.9820513725280762
  }
  display_name: "20100702_06"
}
payload {
  annotation_spec_id: "6283898068739817472"
  image_object_detection {
    bounding_box {
      normalized_vertices {
        x: 0.5500895380973816
        y: 0.3398776352405548
      }
      normalized_vertices {
        x: 0.6604315638542175
        y: 0.4964011311531067
      }
    }
    score: 0.809931755065918
  }
  display_name: "ku_016"
}
payload {
  annotation_spec_id: "9166201830256934912"
  image_object_detection {
    bounding_box {
      normalized_vertices {
        x: 0.5509180426597595
        y: 0.33429571986198425
      }
      normalized_vertices {
        x: 0.6621552109718323
        y: 0.4970446228981018
      }
    }
    score: 0.3122846186161041
  }
  display_name: "20100702_05"
}
```
